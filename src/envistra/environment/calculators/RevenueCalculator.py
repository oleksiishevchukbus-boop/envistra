import random
import numpy as np
from envistra.config.environment.EnvironmentConfig import EnvironmentConfig


# TODO: (for __CompetitiveApproach) Consider mean|median for stdFinEff
# TODO: Look for other ways of FinalMean calculation
class RevenueCalculator:
    def __init__(self, approach, mean, std):
        self.approach = approach
        self.mean = mean
        self.std = std

    def Calculate(self,
        expenses,
        finEff,
        industry,
        competitorsFinEffList
    ):
        match self.approach:
            case "industry_based":
                return self.__IndustryBasedApproach(
                    expenses=expenses,
                    finEff=finEff,
                    industry=industry
                )
            case "competitive_industry_based":
                return self.__CompetitiveIndustryBasedApproach(
                    expenses=expenses,
                    finEff=finEff,
                    industry=industry,
                    competitorsFinEffList=competitorsFinEffList
                )
            case _:
                raise ValueError(f"Unknown revenue calculation approach: {self.approach}")

    def __IndustryBasedApproach(self,
        expenses,
        finEff,
        industry
    ):
        finalMean = self.mean[industry] * (1 + finEff * EnvironmentConfig.RevenueCalculator.FinEffImpactMultiplier)
        revenueToExpensesRatio = random.gauss(finalMean, self.std[industry])
        revenue = revenueToExpensesRatio * expenses
        return revenue, revenueToExpensesRatio

    def __CompetitiveIndustryBasedApproach(self,
        expenses,
        finEff,
        industry,
        competitorsFinEffList
    ):
        stdFinEff = np.median(competitorsFinEffList)
        maxFinEff = np.max(competitorsFinEffList)
        deltaFinEff = finEff - stdFinEff
        competitionComponent = EnvironmentConfig.RevenueCalculator.CompetitionInfluence * (deltaFinEff / maxFinEff)

        finalMean = self.mean[industry] * (1 + finEff * EnvironmentConfig.RevenueCalculator.FinEffImpactMultiplier + competitionComponent)
        revenueToExpensesRatio = random.gauss(finalMean, self.std[industry])
        revenue = revenueToExpensesRatio * expenses
        return revenue, revenueToExpensesRatio
