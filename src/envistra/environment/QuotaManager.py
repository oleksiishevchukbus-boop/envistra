import pandas as pd
from envistra.config.environment.EnvironmentConfig import EnvironmentConfig


# TODO: Consider leverage quota penalty
class QuotaManager:
    def __init__(self, approach, companies):
        self.approach = approach
        self.prevRatios = {}
        self.__InitCap__(companies)

    def InitCompanyReportDict(self):
        if hasattr(self, 'companyReports') and self.companyReports:
            self.prevRatios = {
                name: data["pollutionToExpensesRatio"]
                for name, data in self.companyReports.items()
            }
        self.companyReports = {}

    def ReceiveReport(self,
        name,
        industry,
        expenses,
        prevStepExpenses,
        prevStepQuota,
        pollutionToExpensesRatio,
        prevStepPollution=0
    ):
        self.companyReports[name] = {
            "industry": industry,
            "expenses": expenses,
            "prevStepExpenses": prevStepExpenses,

            "prevStepQuota": prevStepQuota,
            "pollutionToExpensesRatio": pollutionToExpensesRatio,
            "prevStepPollution": prevStepPollution
        }

    def CalculateQuotas(self):
        match self.approach:
            case "expenses_based":
                return self.__ExpensesBasedApproach()
            case "historical_pollution_based":
                return self.__HistoricalPollutionBasedApproach()
            case "improvement_rewarding":
                return self.__ImprovementRewardingApproach()
            case "grandfathered_with_tightening":
                return self.__GrandfatheredWithTighteningApproach()
            case _:
                raise ValueError(f"Unknown quota allocation approach: {self.approach}")

    def CalculatePenalty(self, step, quota, pollution):
        diff = pollution - quota
        if diff <= 0: return 0
        else: return EnvironmentConfig.QuotaManager.GetQuotaPenaltyUnitPrice(step) * diff

    def ApplyLinearReductionFactor(self):
        self.industryQuotaCap["industryQuotaCap"] = self.industryQuotaCap["industryQuotaCap"] * (1 - EnvironmentConfig.QuotaManager.LinearReductionFactor)

    def __ExpensesBasedApproach(self):
        # Group expenses by industry
        industryExpenses = {}
        for name, data in self.companyReports.items():
            industry = data["industry"]
            expenses = data["expenses"]

            if industry not in industryExpenses:
                industryExpenses[industry] = {}
            industryExpenses[industry][name] = expenses

        # Calculate quota shares and add quota field to each company
        for industry, companies in industryExpenses.items():
            totalIndustryExpenses = sum(companies.values())
            industryCap = self.industryQuotaCap.loc[industry, "industryQuotaCap"]

            for companyName, expenses in companies.items():
                quotaShare = expenses / totalIndustryExpenses
                quota = quotaShare * industryCap
                self.companyReports[companyName]["quota"] = quota
                self.companyReports[companyName]["quotaShare"] = quotaShare

    def __HistoricalPollutionBasedApproach(self):
        # Group previous actual pollution by industry
        industryPollution = {}
        for name, data in self.companyReports.items():
            industry = data["industry"]
            pollution = data["prevStepPollution"]

            if industry not in industryPollution:
                industryPollution[industry] = {}
            industryPollution[industry][name] = pollution

        # Calculate quota shares based on historical pollution
        for industry, companies in industryPollution.items():
            totalIndustryPollution = sum(companies.values())
            industryCap = self.industryQuotaCap.loc[industry, "industryQuotaCap"]

            for companyName, pollution in companies.items():
                quotaShare = pollution / totalIndustryPollution if totalIndustryPollution > 0 else 0
                quota = quotaShare * industryCap
                self.companyReports[companyName]["quota"] = quota
                self.companyReports[companyName]["quotaShare"] = quotaShare

    def __ImprovementRewardingApproach(self):
        rewardPoolShare = EnvironmentConfig.QuotaManager.RewardPoolShare

        # Group by industry
        industryAgents = {}
        for name, data in self.companyReports.items():
            industry = data["industry"]
            if industry not in industryAgents:
                industryAgents[industry] = {}
            industryAgents[industry][name] = data

        for industry, agents in industryAgents.items():
            industryCap = self.industryQuotaCap.loc[industry, "industryQuotaCap"]

            # --- Base pool: historical pollution-based split ---
            basePool = industryCap * (1 - rewardPoolShare)
            totalPollution = sum(d["prevStepPollution"] for d in agents.values())

            # --- Reward pool: ratio improvement-based split ---
            rewardPool = industryCap * rewardPoolShare
            improvements = {}
            for name, data in agents.items():
                currentRatio = data["pollutionToExpensesRatio"]
                prevRatio = self.prevRatios.get(name, currentRatio)  # no prev → 0 improvement
                improvements[name] = max(0, prevRatio - currentRatio)  # decrease = improvement
            totalImprovement = sum(improvements.values())

            for name, data in agents.items():
                # Base share from historical pollution
                baseShare = data["prevStepPollution"] / totalPollution if totalPollution > 0 else 0
                baseQuota = baseShare * basePool

                # Reward share from ratio improvement
                rewardShare = improvements[name] / totalImprovement if totalImprovement > 0 else 0
                rewardQuota = rewardShare * rewardPool

                quota = baseQuota + rewardQuota
                quotaShare = quota / industryCap if industryCap > 0 else 0
                self.companyReports[name]["quota"] = quota
                self.companyReports[name]["quotaShare"] = quotaShare

    def __GrandfatheredWithTighteningApproach(self):
        tighteningStrength = EnvironmentConfig.QuotaManager.TighteningStrength

        # Group by industry
        industryAgents = {}
        for name, data in self.companyReports.items():
            industry = data["industry"]
            if industry not in industryAgents:
                industryAgents[industry] = {}
            industryAgents[industry][name] = data

        for industry, agents in industryAgents.items():
            industryCap = self.industryQuotaCap.loc[industry, "industryQuotaCap"]

            totalExpenses = sum(d["expenses"] for d in agents.values())
            ratios = {name: d["pollutionToExpensesRatio"] for name, d in agents.items()}
            avgRatio = sum(ratios.values()) / len(ratios) if len(ratios) > 0 else 1

            adjustedAllocations = {}
            for name, data in agents.items():
                expenseShare = data["expenses"] / totalExpenses if totalExpenses > 0 else 0
                relativeIntensity = ratios[name] / avgRatio if avgRatio > 0 else 1
                tighteningFactor = 1 - tighteningStrength * (relativeIntensity - 1)
                tighteningFactor = max(0.1, min(2.0, tighteningFactor))
                adjustedAllocations[name] = expenseShare * tighteningFactor

            # Normalize to sum to 1
            totalAdjusted = sum(adjustedAllocations.values())
            for name in agents:
                quotaShare = adjustedAllocations[name] / totalAdjusted if totalAdjusted > 0 else 0
                quota = quotaShare * industryCap
                self.companyReports[name]["quota"] = quota
                self.companyReports[name]["quotaShare"] = quotaShare

    def __InitCap__(self, companies):
        data = []
        for company in companies:
            data.append({
                "industry": company.industry,
                "pollution": company.pollution
            })
        df = pd.DataFrame(data)
        self.industryQuotaCap = EnvironmentConfig.QuotaManager.QuotaCapDecreaser * df.groupby("industry").sum()
        self.industryQuotaCap = self.industryQuotaCap.rename(columns={"pollution": "industryQuotaCap"})
