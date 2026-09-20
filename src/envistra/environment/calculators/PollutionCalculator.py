from envistra.config.environment.EnvironmentConfig import EnvironmentConfig


# TODO: Perform research about theoretical ratio value (1% air pollution => 0.002 fin. assets)
class PollutionCalculator:
    def __init__(self, approach, ratio):
        self.approach = approach
        self.ratio = ratio

    def Calculate(self, expenses, ecoEff, companyName, industry):
        match self.approach:
            case "industry_based":
                return self.__IndustryBasedApproach(
                    expenses=expenses,
                    ecoEff=ecoEff,
                    industry=industry
                )
            case "company_based":
                return self.__CompanyBasedApproach(
                    expenses=expenses,
                    ecoEff=ecoEff,
                    companyName=companyName
                )
            case _:
                raise ValueError(f"Unknown pollution calculation approach: {self.approach}")

    def __IndustryBasedApproach(self, expenses, ecoEff, industry):
        pollutionToExpensesRatio = self.ratio[industry] * (1 - ecoEff * EnvironmentConfig.PollutionCalculator.EnvEffImpactMultiplier)
        pollution = expenses * pollutionToExpensesRatio
        return pollution, pollutionToExpensesRatio

    def __CompanyBasedApproach(self, expenses, ecoEff, companyName):
        pollutionToExpensesRatio = self.ratio[companyName] * (1 - ecoEff * EnvironmentConfig.PollutionCalculator.EnvEffImpactMultiplier)
        pollution = expenses * pollutionToExpensesRatio
        return pollution, pollutionToExpensesRatio
