"""Loads the workbooks and builds one agent entity per company config.

This is where configuration meets data: `config/companies/*.json` supplies the
roster and its parameters, `data/**/*.xlsx` supplies each company's starting
position and the industry-level ratios the environment calculators sample from.

A workbook's identity is its path, `data/<industry>/<dataSource>.xlsx`: the
top-level folder is the industry and the filename is the data source. The
`Name` and `Industry` columns inside the files are overwritten on read.

Call order matters and is enforced by `envistra.bootstrap.initialize_model`:
`Read` must precede the ratio getters, and all of them must precede
`CreateCompanyEntities` / `CreateEnvironmentCalculators`.
"""
import copy
import glob
import os

import pandas as pd

from envistra.config import Loader
from envistra.config.Errors import ConfigError
from envistra.config.GlobalConfig import GlobalConfig
from envistra.config.environment.EnvironmentConfig import EnvironmentConfig
from envistra.agent.CompanyEntity import CompanyEntity
from envistra.agent.calculators.AgentCalculators import AgentCalculators
from envistra.agent.calculators.QuotaToBuyAmountCalculator import QuotaToBuyAmountCalculator
from envistra.agent.calculators.QuotaToBuyPriceCalculator import QuotaToBuyPriceCalculator
from envistra.agent.calculators.QuotaToSellAmountCalculator import QuotaToSellAmountCalculator
from envistra.agent.calculators.QuotaToSellPriceCalculator import QuotaToSellPriceCalculator
from envistra.agent.estimators.AgentEstimators import AgentEstimators
from envistra.agent.estimators.ExpensesEstimator import ExpensesEstimator
from envistra.agent.estimators.ExpensesReEstimator import ExpensesReEstimator
from envistra.agent.estimators.InvestmentEstimator import InvestmentEstimator
from envistra.agent.estimators.PollutionEstimator import PollutionEstimator
from envistra.environment.calculators.EnvironmentCalculators import EnvironmentCalculators
from envistra.environment.calculators.PollutionCalculator import PollutionCalculator
from envistra.environment.calculators.RevenueCalculator import RevenueCalculator

#: Scaled into model units on read. TotalCurrentAssets is scaled but never read;
#: it must still be present, which data/README.md records.
SCALED_COLUMNS = ["Pollution", "TotalAssets", "TotalCurrentAssets",
                  "TotalOperatingExpenses", "COGS", "Revenue"]


def _workbooks():
    # Excel leaves a `~$Name.xlsx` lock file beside a workbook while it is open;
    # it matches the pattern but is not a workbook.
    pattern = os.path.join(GlobalConfig.DataFolder, "**", "*.xlsx")
    return [f for f in glob.glob(pattern, recursive=True)
            if not os.path.basename(f).startswith("~$")]


def _sourceName(file):
    """A workbook's data source is its filename without the extension.

    Any `Name` column inside the file is ignored — so copying a workbook under a
    new filename adds a new source. Filenames must be unique across folders. Note Windows drops a trailing dot from a
    filename, which is why `NRG ENERGY, INC.` became `NRG ENERGY, INC`.
    """
    return os.path.splitext(os.path.basename(file))[0]


def _relative(file):
    return os.path.relpath(file, GlobalConfig.DataFolder).replace(os.sep, "/")


def _industry(file):
    """A workbook's industry is the top-level folder it sits in under `data/`.

    Deeper subfolders are allowed and carry no meaning. Adding a folder adds an
    industry: its own quota cap, ratios and competitors.
    """
    parts = _relative(file).split("/")
    if len(parts) < 2:
        raise ConfigError(file, "a workbook must sit in a folder under data/ — "
                                "the folder is its industry")
    return parts[0]


def _bySource(files):
    """`{source: [files]}`. Companies reference only the filename, so the same
    filename in two folders is one source twice — a conflict."""
    grouped = {}
    for file in sorted(files):
        grouped.setdefault(_sourceName(file), []).append(file)
    return grouped


def ListDataSources():
    """Every data source in the workbooks, as `[{name, industry, files}]`.

    These are the values a company config's `dataSource` may take. Both come
    from the path, so no workbook is opened. More than one entry in `files`
    means the same filename sits in several folders, which `DataReader.Read`
    rejects. Returns an empty list when no workbooks are present — the data is
    untracked, so a caller must cope.
    """
    sources = [{"name": name,
                "industry": _industry(files[0]),
                "files": [_relative(f) for f in files]}
               for name, files in _bySource(_workbooks()).items()]
    return sorted(sources, key=lambda s: (s["industry"], s["name"]))


class DataReader:
    def __init__(self, companies):
        #: Every company config that was found.
        self.companies = companies
        #: Those that actually become agents. A disabled company is skipped
        #: entirely, so it does not trade and does not move the quota market.
        self.activeCompanies = Loader.enabled(companies)

    def Read(self):
        """Load every workbook under the data folder and scale to model units."""
        files = _workbooks()
        if not files:
            raise ConfigError(GlobalConfig.DataFolder,
                              "no .xlsx workbooks found — see data/README.md")

        grouped = _bySource(files)
        clashes = {name: fs for name, fs in grouped.items() if len(fs) > 1}
        if clashes:
            raise ConfigError(GlobalConfig.DataFolder, "\n  ".join(
                f"{name!r} is the filename of several workbooks: "
                + ", ".join(_relative(f) for f in fs) for name, fs in clashes.items())
                + "\n  a data source is the filename, so each must be unique")

        # `Name` (the join key) and `Industry` (the groupby key) come from the
        # path; any such columns inside the workbook are overwritten.
        self.df = pd.concat([pd.read_excel(fs[0]).assign(Name=name, Industry=_industry(fs[0]))
                             for name, fs in grouped.items()], ignore_index=True)
        self.df[SCALED_COLUMNS] *= GlobalConfig.Startup.MoneyValueMultiplier

        # Fail here, naming the company, rather than deep inside entity creation.
        # Only the active ones: a company may be disabled precisely because its
        # workbook is not available.
        Loader.verify_data_links(self.activeCompanies, self.df["Name"].unique())
        return self.df

    def PrepareStartingData(self):
        """The one row per company that seeds the simulation."""
        year = GlobalConfig.Startup.Year
        self.startingData = self.df[self.df["Year"] == year]

        counts = self.startingData["Name"].value_counts()
        needed = {c.dataSource for c in self.activeCompanies}
        missing = sorted(needed - set(counts.index))
        duplicated = sorted(n for n in needed if counts.get(n, 0) > 1)
        if missing or duplicated:
            detail = []
            if missing:
                detail.append(f"no {year} row for: " + ", ".join(repr(n) for n in missing))
            if duplicated:
                detail.append(f"more than one {year} row for: "
                              + ", ".join(f"{n!r} ({counts[n]})" for n in duplicated))
            raise ConfigError(GlobalConfig.DataFolder,
                              "\n  ".join(detail)
                              + "\n  every company needs exactly one row for the start year")
        return self.startingData

    def GetExpensesToAssetsRatio(self, approach="mean"):
        """Industry-level expenses/assets, used to seed each expenses estimator."""
        self.df['ExpensesToAssetsRatio'] = (
            (self.df["COGS"] + self.df["TotalOperatingExpenses"]) / self.df["TotalAssets"])
        grouped = self.df.groupby('Industry')['ExpensesToAssetsRatio']
        match approach:
            case "mean":
                self.industryBasedExpensesToAssetsRatio = grouped.mean()
            case "median":
                self.industryBasedExpensesToAssetsRatio = grouped.median()
            case _:
                raise ValueError(f"Unknown expenses-to-assets approach: {approach}")
        return self.industryBasedExpensesToAssetsRatio

    def GetPollutionToExpensesRatio(self, approach="mean"):
        """Pollution intensity, keyed by industry or by company.

        Which one depends on `PollutionCalculator.Approach`, and the calculator
        indexes the result the matching way — so the two reads must agree.
        """
        self.df['PollutionToExpensesRatio'] = (
            self.df["Pollution"] / (self.df["COGS"] + self.df["TotalOperatingExpenses"]))

        match EnvironmentConfig.PollutionCalculator.Approach:
            case "industry_based":
                grouped = self.df.groupby('Industry')['PollutionToExpensesRatio']
                match approach:
                    case "mean":
                        self.pollutionToExpensesRatio = grouped.mean()
                    case "median":
                        self.pollutionToExpensesRatio = grouped.median()
                    case _:
                        raise ValueError(f"Unknown pollution-to-expenses approach: {approach}")

            case "company_based":
                # Keyed by agent name, not by data company: several agents may
                # share one dataSource, so the same ratio is fanned out to each.
                bySource = self.df.groupby('Name')['PollutionToExpensesRatio'].mean()
                self.pollutionToExpensesRatio = {
                    company.name: bySource[company.dataSource]
                    for company in self.activeCompanies
                }

            case _:
                raise ValueError("Unknown pollution calculator approach: "
                                 f"{EnvironmentConfig.PollutionCalculator.Approach}")

        return self.pollutionToExpensesRatio

    def GetRevenueToExpensesDistributionParams(self):
        """Industry mean and variance of revenue/expenses, sampled by RevenueCalculator."""
        self.df['RevenueToExpensesRatio'] = (
            self.df["Revenue"] / (self.df["COGS"] + self.df["TotalOperatingExpenses"]))
        grouped = self.df.groupby('Industry')['RevenueToExpensesRatio']
        self.industryBasedRevenueToExpensesDistributionMean = grouped.mean()
        self.industryBasedRevenueToExpensesDistributionVariance = grouped.var()
        return (self.industryBasedRevenueToExpensesDistributionMean,
                self.industryBasedRevenueToExpensesDistributionVariance)

    def CreateCompanyEntities(self):
        """One entity per company config, seeded from its start-year row."""
        self.companyEntities = []
        for company in self.activeCompanies:
            row = self.startingData[self.startingData["Name"] == company.dataSource]
            industry = row["Industry"].item()

            agentEstimators = AgentEstimators(
                Expenses=ExpensesEstimator(
                    approach=company.ExpensesEstimatorConfig.approach,
                    expensesToAssetsRatio=self.industryBasedExpensesToAssetsRatio[industry],
                    changeThreshold_Upper=company.ExpensesEstimatorConfig.changeThreshold_Upper,
                    changeThreshold_Lower=company.ExpensesEstimatorConfig.changeThreshold_Lower,
                    featuresImpact=company.ExpensesEstimatorConfig.featuresImpact,
                    smoothingAlpha=company.ExpensesEstimatorConfig.smoothingAlpha,
                ),
                Investment=InvestmentEstimator(
                    company.InvestmentEstimatorConfig.approach,
                    company.InvestmentEstimatorConfig.investmentRatios,
                ),
                # The config's model is a prototype; each agent trains its own copy.
                Pollution=PollutionEstimator(
                    company.PollutionEstimatorConfig.approach,
                    copy.deepcopy(company.PollutionEstimatorConfig.MlpModel),
                ),
                ExpensesReEstimation=ExpensesReEstimator(
                    company.ExpensesReEstimationConfig.approach,
                    company.ExpensesReEstimationConfig,
                ),
            )

            agentCalculators = AgentCalculators(
                QuotaToSellAmount=QuotaToSellAmountCalculator(
                    company.QuotaToSellAmountCalculatorConfig.approach,
                    company.QuotaToSellAmountCalculatorConfig.quotaReserve,
                ),
                QuotaToSellPrice=QuotaToSellPriceCalculator(
                    company.QuotaToSellPriceCalculatorConfig.approach,
                    company.QuotaToSellPriceCalculatorConfig.unitPrice,
                    company.QuotaToSellPriceCalculatorConfig.changeThreshold,
                    company.QuotaToSellPriceCalculatorConfig.salesTarget,
                ),
                QuotaToBuyAmount=QuotaToBuyAmountCalculator(
                    company.QuotaToBuyAmountCalculatorConfig.approach,
                    company.QuotaToBuyAmountCalculatorConfig.quotaReserve,
                ),
                QuotaToBuyPrice=QuotaToBuyPriceCalculator(
                    company.QuotaToBuyPriceCalculatorConfig.approach,
                    company.QuotaToBuyPriceCalculatorConfig.assetsPartForTrading,
                ),
            )

            self.companyEntities.append(CompanyEntity(
                name=company.name,
                industry=industry,

                assets=row["TotalAssets"].item(),
                expenses=row["TotalOperatingExpenses"].item() + row["COGS"].item(),
                revenue=row["Revenue"].item(),
                pollution=row["Pollution"].item(),

                finEffInvest=company.finEffInvest,
                ecoEffInvest=company.ecoEffInvest,
                finEffCoef=company.finEffCoef,
                ecoEffCoef=company.ecoEffCoef,

                AgentEstimators=agentEstimators,
                AgentCalculators=agentCalculators,
            ))
        return self.companyEntities

    def CreateEnvironmentCalculators(self):
        self.environmentCalculators = EnvironmentCalculators(
            Revenue=RevenueCalculator(
                EnvironmentConfig.RevenueCalculator.Approach,
                self.industryBasedRevenueToExpensesDistributionMean,
                self.industryBasedRevenueToExpensesDistributionVariance,
            ),
            Pollution=PollutionCalculator(
                EnvironmentConfig.PollutionCalculator.Approach,
                self.pollutionToExpensesRatio,
            ),
        )
        return self.environmentCalculators
