"""Discovery, validation and construction of the JSON configuration.

The JSON files under `config/` are the source of truth. There are no Python
fallback literals: the predecessor kept three separate copies of "the defaults"
which had already drifted apart, and a missing key silently picked whichever
copy the code path happened to reach.

Three kinds of file:

    config/environment.json        the regulatory regime, one file
    config/strategies/<id>.json    one per strategy, id is the filename stem
    config/companies/<id>.json     one per agent; the agent count is the file count

A company names its strategy by id and adds its own four efficiency parameters.
Several companies may name the same strategy, and several may share one
dataSource — the four AES CORP variants do both.
"""
import colorsys
import json
import os
import re
from pathlib import Path

from envistra.config.Errors import ConfigError, bad_value, check_keys
from envistra.config.agent.CompanyAgentConfigEntity import CompanyAgentConfigEntity
from envistra.config.agent.calculators.QuotaToBuyAmountCalculatorConfig import QuotaToBuyAmountCalculatorConfig
from envistra.config.agent.calculators.QuotaToBuyPriceCalculatorConfig import QuotaToBuyPriceCalculatorConfig
from envistra.config.agent.calculators.QuotaToSellAmountCalculatorConfig import QuotaToSellAmountCalculatorConfig
from envistra.config.agent.calculators.QuotaToSellPriceCalculatorConfig import QuotaToSellPriceCalculatorConfig
from envistra.config.agent.estimators.ExpensesEstimatorConfig import ExpensesEstimatorConfig
from envistra.config.agent.estimators.ExpensesReEstimationConfig import ExpensesReEstimationConfig
from envistra.config.agent.estimators.InvestmentEstimatorConfig import InvestmentEstimatorConfig
from envistra.config.agent.estimators.PollutionEstimatorConfig import PollutionEstimatorConfig
from envistra.config.environment.EnvironmentConfig import (
    PollutionCalculatorConfig,
    QuotaManagerConfig,
    RevenueCalculatorConfig,
)
from envistra.config.strategies.StrategyEntity import StrategyEntity

_HEX_COLOR = re.compile(r"#[0-9A-Fa-f]{6}")

# Only the approaches that are actually implemented. The predecessor's validator
# accepted seven investment approaches where two exist; the estimators now raise
# on an unknown approach, so accepting the rest would only move the failure.
APPROACHES = {
    "expenses": ("general", "performance_based", "performance_based_relative"),
    "investment": ("revenue_based", "performance_based"),
    "pollution": ("general", "MLP_based"),
    "expenses_re_estimation": ("none", "gap_proportional"),
    "quota_to_sell_amount": ("reserve_based",),
    "quota_to_sell_price": ("general", "history_based"),
    "quota_to_buy_amount": ("reserve_based",),
    "quota_to_buy_price": ("ignorance", "economically_efficient", "gap_full_cover"),
    "revenue_calculator": ("industry_based", "competitive_industry_based"),
    "pollution_calculator": ("industry_based", "company_based"),
    "quota_manager": ("expenses_based", "historical_pollution_based",
                      "improvement_rewarding", "grandfathered_with_tightening"),
}


def config_dir(path=None):
    """Locate `config/`: explicit argument, then $ENVISTRA_CONFIG_DIR, then the
    repository root, then the working directory."""
    if path is not None:
        return Path(path)
    env = os.environ.get("ENVISTRA_CONFIG_DIR")
    if env:
        return Path(env)
    # src/envistra/config/Loader.py -> repository root
    repo_root = Path(__file__).resolve().parents[3]
    if (repo_root / "config").is_dir():
        return repo_root / "config"
    return Path.cwd() / "config"


def _read(path):
    if not path.is_file():
        raise ConfigError(path, "file not found")
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise ConfigError(path, f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(path, f"expected a JSON object, got {type(data).__name__}")
    return data


def _approach(path, block, data, context):
    value = data["approach"]
    if value not in APPROACHES[block]:
        raise bad_value(path, f"{context}.approach", value,
                        " | ".join(APPROACHES[block]))
    return value


def _number(path, field, value, low=None, high=None):
    # bool is an int subclass; `true` must not pass as 1.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise bad_value(path, field, value, "a number")
    if low is not None and value < low:
        raise bad_value(path, field, value, f">= {low}")
    if high is not None and value > high:
        raise bad_value(path, field, value, f"<= {high}")
    return value


# --------------------------------------------------------------------------- #
# Environment
# --------------------------------------------------------------------------- #

def load_environment(path=None):
    """Read config/environment.json and apply it to the config classes.

    The classes are module-level singletons that the simulation reads live on
    every step, so applying in place is the contract `src/` already expects.
    """
    path = Path(path) if path else config_dir() / "environment.json"
    data = _read(path)
    check_keys(path, data, required=("revenue_calculator", "pollution_calculator", "quota_manager"))

    rc = data["revenue_calculator"]
    check_keys(path, rc, ("approach", "competition_influence", "fin_eff_impact_multiplier"),
               context="revenue_calculator")
    RevenueCalculatorConfig.Approach = _approach(path, "revenue_calculator", rc, "revenue_calculator")
    RevenueCalculatorConfig.CompetitionInfluence = _number(
        path, "revenue_calculator.competition_influence", rc["competition_influence"], 0, 1)
    RevenueCalculatorConfig.FinEffImpactMultiplier = _number(
        path, "revenue_calculator.fin_eff_impact_multiplier", rc["fin_eff_impact_multiplier"], 0)

    pc = data["pollution_calculator"]
    check_keys(path, pc, ("approach", "env_eff_impact_multiplier"), context="pollution_calculator")
    PollutionCalculatorConfig.Approach = _approach(path, "pollution_calculator", pc, "pollution_calculator")
    PollutionCalculatorConfig.EnvEffImpactMultiplier = _number(
        path, "pollution_calculator.env_eff_impact_multiplier", pc["env_eff_impact_multiplier"], 0)

    qm = data["quota_manager"]
    check_keys(path, qm, ("approach", "quota_cap_decreaser", "linear_reduction_factor",
                          "reward_pool_share", "tightening_strength", "penalty_tiers"),
               context="quota_manager")
    QuotaManagerConfig.Approach = _approach(path, "quota_manager", qm, "quota_manager")
    QuotaManagerConfig.QuotaCapDecreaser = _number(
        path, "quota_manager.quota_cap_decreaser", qm["quota_cap_decreaser"], 0, 1)
    QuotaManagerConfig.LinearReductionFactor = _number(
        path, "quota_manager.linear_reduction_factor", qm["linear_reduction_factor"], 0, 1)
    QuotaManagerConfig.RewardPoolShare = _number(
        path, "quota_manager.reward_pool_share", qm["reward_pool_share"], 0, 1)
    QuotaManagerConfig.TighteningStrength = _number(
        path, "quota_manager.tightening_strength", qm["tightening_strength"], 0, 1)
    QuotaManagerConfig.PENALTY_TIERS = _penalty_tiers(path, qm["penalty_tiers"])

    return data


def _penalty_tiers(path, tiers):
    """Parse the escalating penalty schedule.

    `until_step` is the string "inf" for the final tier, because JSON has no
    infinity. The tiers must ascend: the lookup returns the first tier whose
    threshold the step is below, so an out-of-order list silently prices
    exceedance wrongly.
    """
    field = "quota_manager.penalty_tiers"
    if not isinstance(tiers, list) or not tiers:
        raise bad_value(path, field, tiers, "a non-empty list")

    parsed, previous = [], float("-inf")
    for i, tier in enumerate(tiers):
        where = f"{field}[{i}]"
        check_keys(path, tier, ("until_step", "price", "description"), context=where)

        until = tier["until_step"]
        if until == "inf":
            until = float("inf")
        else:
            until = _number(path, f"{where}.until_step", until)
        if until <= previous:
            raise bad_value(path, f"{where}.until_step", tier["until_step"],
                            "a value greater than the previous tier "
                            "(tiers must ascend; the lookup takes the first match)")
        previous = until

        parsed.append({
            "until_step": until,
            "price": _number(path, f"{where}.price", tier["price"], 0),
            "description": tier["description"],
        })

    if parsed[-1]["until_step"] != float("inf"):
        raise bad_value(path, f"{field}[-1].until_step", tiers[-1]["until_step"],
                        '"inf" — the last tier must be open-ended')
    return parsed


# --------------------------------------------------------------------------- #
# Strategies
# --------------------------------------------------------------------------- #

def load_strategies(path=None):
    """Read every config/strategies/*.json. Returns {id: StrategyEntity}.

    The id is the filename stem. Any number of strategies is supported — the
    predecessor mapped strategies onto four fixed class attributes through a
    hardcoded name table, so a fifth was silently dropped before it could run.
    """
    directory = Path(path) if path else config_dir() / "strategies"
    if not directory.is_dir():
        raise ConfigError(directory, "strategy directory not found")

    files = sorted(directory.glob("*.json"))
    if not files:
        raise ConfigError(directory, "no strategy files found")

    strategies = {}
    for file in files:
        strategies[file.stem] = _build_strategy(file, _read(file))
    return strategies


def _build_strategy(path, data):
    check_keys(path, data, required=("name", "estimators", "calculators"),
               optional=("description", "color"))

    est, calc = data["estimators"], data["calculators"]
    check_keys(path, est, ("expenses", "investment", "pollution", "expenses_re_estimation"),
               context="estimators")
    check_keys(path, calc, ("quota_to_sell_amount", "quota_to_sell_price",
                            "quota_to_buy_amount", "quota_to_buy_price"),
               context="calculators")

    e = est["expenses"]
    check_keys(path, e, ("approach", "changeThreshold_Upper", "changeThreshold_Lower", "featuresImpact"),
               optional=("smoothingAlpha",), context="estimators.expenses")
    check_keys(path, e["featuresImpact"], ("netRevenue", "quotaExceedance"),
               context="estimators.expenses.featuresImpact")
    expenses = ExpensesEstimatorConfig(
        approach=_approach(path, "expenses", e, "estimators.expenses"),
        changeThreshold_Upper=_number(path, "estimators.expenses.changeThreshold_Upper", e["changeThreshold_Upper"]),
        changeThreshold_Lower=_number(path, "estimators.expenses.changeThreshold_Lower", e["changeThreshold_Lower"]),
        featuresImpact=e["featuresImpact"],
        **({"smoothingAlpha": _number(path, "estimators.expenses.smoothingAlpha", e["smoothingAlpha"], 0, 1)}
           if "smoothingAlpha" in e else {}),
    )
    if e["changeThreshold_Lower"] >= e["changeThreshold_Upper"]:
        raise bad_value(path, "estimators.expenses.changeThreshold_Lower", e["changeThreshold_Lower"],
                        f"a value below changeThreshold_Upper ({e['changeThreshold_Upper']})")

    i = est["investment"]
    check_keys(path, i, ("approach", "investmentRatios"),
               optional=("smoothingAlpha", "baseQuotaPrice", "adaptiveBlendRatio"),
               context="estimators.investment")
    check_keys(path, i["investmentRatios"],
               ("revenueToInvestmentRatio", "minimalInvestment", "finInvestment", "ecoInvestment"),
               context="estimators.investment.investmentRatios")
    investment = InvestmentEstimatorConfig(
        approach=_approach(path, "investment", i, "estimators.investment"),
        investmentRatios=i["investmentRatios"],
        **{k: i[k] for k in ("smoothingAlpha", "baseQuotaPrice", "adaptiveBlendRatio") if k in i},
    )

    p = est["pollution"]
    check_keys(path, p, ("approach",), optional=("mlp",), context="estimators.pollution")
    if "mlp" in p:
        check_keys(path, p["mlp"], (), optional=PollutionEstimatorConfig.DEFAULT_MLP_CONFIG.keys(),
                   context="estimators.pollution.mlp")
    pollution = PollutionEstimatorConfig(
        approach=_approach(path, "pollution", p, "estimators.pollution"),
        mlp=p.get("mlp"),
    )

    r = est["expenses_re_estimation"]
    check_keys(path, r, ("approach",),
               optional=("maxReductionRate", "profitMargin", "maxReductionCap",
                         "baseRate", "trendSensitivity"),
               context="estimators.expenses_re_estimation")
    re_estimation = ExpensesReEstimationConfig(
        approach=_approach(path, "expenses_re_estimation", r, "estimators.expenses_re_estimation"),
        **{k: v for k, v in r.items() if k != "approach"},
    )

    sell_amount = _amount_calculator(path, calc["quota_to_sell_amount"], "quota_to_sell_amount",
                                     QuotaToSellAmountCalculatorConfig)
    buy_amount = _amount_calculator(path, calc["quota_to_buy_amount"], "quota_to_buy_amount",
                                    QuotaToBuyAmountCalculatorConfig)

    sp = calc["quota_to_sell_price"]
    check_keys(path, sp, ("approach", "unitPrice", "changeThreshold", "salesTarget"),
               context="calculators.quota_to_sell_price")
    sell_price = QuotaToSellPriceCalculatorConfig(
        approach=_approach(path, "quota_to_sell_price", sp, "calculators.quota_to_sell_price"),
        unitPrice=_number(path, "calculators.quota_to_sell_price.unitPrice", sp["unitPrice"], 0),
        changeThreshold=_number(path, "calculators.quota_to_sell_price.changeThreshold", sp["changeThreshold"], 0),
        salesTarget=_number(path, "calculators.quota_to_sell_price.salesTarget", sp["salesTarget"], 0, 1),
    )

    bp = calc["quota_to_buy_price"]
    check_keys(path, bp, ("approach", "assetsPartForTrading"), context="calculators.quota_to_buy_price")
    buy_price = QuotaToBuyPriceCalculatorConfig(
        approach=_approach(path, "quota_to_buy_price", bp, "calculators.quota_to_buy_price"),
        assetsPartForTrading=_number(path, "calculators.quota_to_buy_price.assetsPartForTrading",
                                     bp["assetsPartForTrading"], 0, 1),
    )

    return StrategyEntity(
        name=data["name"],
        description=data.get("description", ""),
        color=data.get("color", "#888888"),
        ExpensesEstimatorConfig=expenses,
        InvestmentEstimatorConfig=investment,
        PollutionEstimatorConfig=pollution,
        ExpensesReEstimationConfig=re_estimation,
        QuotaToSellAmountCalculatorConfig=sell_amount,
        QuotaToSellPriceCalculatorConfig=sell_price,
        QuotaToBuyAmountCalculatorConfig=buy_amount,
        QuotaToBuyPriceCalculatorConfig=buy_price,
    )


def _amount_calculator(path, data, block, cls):
    context = f"calculators.{block}"
    check_keys(path, data, ("approach", "quotaReserve"), context=context)
    return cls(
        approach=_approach(path, block, data, context),
        quotaReserve=_number(path, f"{context}.quotaReserve", data["quotaReserve"], 0, 1),
    )


# --------------------------------------------------------------------------- #
# Companies
# --------------------------------------------------------------------------- #

PERSONAL_PARAMS = ("finEffCoef", "ecoEffCoef", "finEffInvest", "ecoEffInvest")


def load_companies(strategies, path=None):
    """Read every config/companies/*.json, in filename order.

    The number of files is the number of agents. Each names a strategy by id and
    a dataSource that must exist in the workbooks — which `verify_data_links`
    checks once the data is loaded.
    """
    directory = Path(path) if path else config_dir() / "companies"
    if not directory.is_dir():
        raise ConfigError(directory, "company directory not found")

    files = sorted(directory.glob("*.json"))
    if not files:
        raise ConfigError(directory, "no company files found — there would be no agents")

    companies, seen = [], {}
    for file in files:
        company = _build_company(file, _read(file), strategies)
        if company.name in seen:
            raise ConfigError(file, f"company name {company.name!r} is already used by {seen[company.name]}",
                              field="name")
        seen[company.name] = file.name
        companies.append(company)

    _assign_missing_colors(companies)
    return companies


def _assign_missing_colors(companies):
    """Give every company without a `color` a distinct, evenly-spaced hue.

    Deterministic for a given set of company files, not random per run: two runs
    of the same configuration must produce comparable plots. Companies that
    declare a colour keep it and are immune to a file being added; generated
    hues may shift when the set changes.
    """
    uncolored = [c for c in companies if c.color is None]
    if not uncolored:
        return
    taken = {c.color.upper() for c in companies if c.color}
    step = 1.0 / len(uncolored)
    for i, company in enumerate(uncolored):
        # Walk the hue circle, alternating lightness so neighbours stay distinct
        # even when there are many of them.
        r, g, b = colorsys.hls_to_rgb((i * step) % 1.0, 0.45 + 0.12 * (i % 2), 0.70)
        candidate = "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))
        while candidate in taken:  # never collide with an explicit colour
            r, g, b = colorsys.hls_to_rgb(((i + 0.5) * step) % 1.0, 0.55, 0.70)
            candidate = "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))
            taken.add(candidate)
        taken.add(candidate)
        company.color = candidate


def _build_company(path, data, strategies):
    check_keys(path, data, required=("name", "dataSource", "strategy", "parameters"),
               optional=("color", "plot"))

    plot = data.get("plot", True)
    if not isinstance(plot, bool):
        raise bad_value(path, "plot", plot, "true or false")

    color = data.get("color")
    if color is not None and not _HEX_COLOR.fullmatch(str(color)):
        raise bad_value(path, "color", color, 'a hex colour such as "#4E6EDF"')

    strategy_id = data["strategy"]
    if strategy_id not in strategies:
        raise bad_value(path, "strategy", strategy_id,
                        "one of: " + ", ".join(sorted(strategies)))

    params = data["parameters"]
    check_keys(path, params, PERSONAL_PARAMS, context="parameters")
    for key in PERSONAL_PARAMS:
        _number(path, f"parameters.{key}", params[key], 0)

    return CompanyAgentConfigEntity(
        color=color,
        plot=plot,
        name=data["name"],
        dataSource=data["dataSource"],
        strategyId=strategy_id,
        Strategy=strategies[strategy_id],
        **params,
    )


def plotted(companies):
    """The companies that appear in charts.

    Every company takes part in the simulation regardless — the quota market's
    supply and demand depend on the whole set — so this filters what is drawn,
    not what is run. A company with no `plot` key is drawn.
    """
    return [company for company in companies if company.plot]


def verify_data_links(companies, available_names):
    """Check every company's dataSource exists in the loaded data.

    Called by the data reader rather than at parse time, because the workbooks
    are not committed and may be absent. Without this the failure surfaces much
    later as an opaque "array of size 1" error from entity construction.
    """
    available = set(available_names)
    missing = sorted({c.dataSource for c in companies if c.dataSource not in available})
    if missing:
        raise ConfigError(
            config_dir() / "companies",
            "dataSource not found in the loaded data: " + ", ".join(repr(m) for m in missing)
            + "\n  available: " + ", ".join(repr(n) for n in sorted(available))
            + "\n  (are the workbooks present under data/? see data/README.md)",
            field="dataSource",
        )


# --------------------------------------------------------------------------- #

DEFAULT_PLOTS = {"dpi": 600, "figsize": [12, 5], "format": "jpg", "resultsFolder": "results"}


def load_simulation(path=None):
    """Read config/simulation.json — run-wide settings such as plot output.

    Every key is optional; the defaults above apply. Unlike the environment,
    these are presentation settings, so a missing file is not an error.
    """
    path = Path(path) if path else config_dir() / "simulation.json"
    data = _read(path) if path.is_file() else {}
    check_keys(path, data, required=(), optional=("plots",))

    plots = dict(DEFAULT_PLOTS)
    given = data.get("plots", {})
    check_keys(path, given, required=(), optional=DEFAULT_PLOTS.keys(), context="plots")
    plots.update(given)

    _number(path, "plots.dpi", plots["dpi"], 10, 2400)
    if not (isinstance(plots["figsize"], list) and len(plots["figsize"]) == 2):
        raise bad_value(path, "plots.figsize", plots["figsize"], "a [width, height] pair")
    for i, side in enumerate(plots["figsize"]):
        _number(path, f"plots.figsize[{i}]", side, 1)
    if plots["format"] not in ("jpg", "png", "svg", "pdf"):
        raise bad_value(path, "plots.format", plots["format"], "jpg | png | svg | pdf")

    plots["figsize"] = tuple(plots["figsize"])
    return {"plots": plots}


def load_all(path=None):
    """Load the whole configuration.

    Returns (environment, strategies, companies, simulation).
    """
    directory = config_dir(path)
    environment = load_environment(directory / "environment.json")
    strategies = load_strategies(directory / "strategies")
    companies = load_companies(strategies, directory / "companies")
    simulation = load_simulation(directory / "simulation.json")
    return environment, strategies, companies, simulation
