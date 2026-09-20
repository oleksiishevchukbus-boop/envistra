from .estimators import AgentEstimators
from .calculators import AgentCalculators


class CompanyEntity:
    # country = "DefaultCountry"

    def __init__(self, **kwargs):
        self.__InitName(kwargs)
        self.__InitIndustry(kwargs)
        self.__InitAssets(kwargs)
        self.__InitExpenses(kwargs)
        self.__InitRevenue(kwargs)
        self.__InitPollution(kwargs)

        self.__InitFinEffInvest(kwargs)
        self.__InitEcoEffInvest(kwargs)
        self.__InitFinEffCoef(kwargs)
        self.__InitEcoEffCoef(kwargs)

        self.__InitAgentEstimators(kwargs)
        self.__InitAgentCalculators(kwargs)

        for key, value in kwargs.items():
            setattr(self, key, value)
        self.__CalculateRatios()

    def __CalculateRatios(self):
        self.revenueToExpensesRatio = self.revenue / self.expenses
        self.pollutionToExpensesRatio = self.pollution / self.expenses

    def __InitName(self, kwargs):
        if "name" not in kwargs:
            raise ValueError("'name' is required for CompanyEntity")
        self.name = kwargs["name"]

    def __InitIndustry(self, kwargs):
        if "industry" not in kwargs:
            raise ValueError("'industry' is required for CompanyEntity")
        self.industry = kwargs["industry"]

    def __InitAssets(self, kwargs):
        if "assets" not in kwargs:
            raise ValueError("'assets' is required for CompanyEntity")
        self.assets = kwargs["assets"]

    def __InitExpenses(self, kwargs):
        if "expenses" not in kwargs:
            raise ValueError("'expenses' is required for CompanyEntity")
        self.expenses = kwargs["expenses"]

    def __InitRevenue(self, kwargs):
        if "revenue" not in kwargs:
            raise ValueError("'revenue' is required for CompanyEntity")
        self.revenue = kwargs["revenue"]

    def __InitPollution(self, kwargs):
        if "pollution" not in kwargs:
            raise ValueError("'pollution' is required for CompanyEntity")
        self.pollution = kwargs["pollution"]

    def __InitFinEffInvest(self, kwargs):
        if "finEffInvest" not in kwargs:
            raise ValueError("'finEffInvest' is required for CompanyEntity")
        else:
            self.finEffInvest = kwargs["finEffInvest"]

    def __InitEcoEffInvest(self, kwargs):
        if "ecoEffInvest" not in kwargs:
            raise ValueError("'ecoEffInvest' is required for CompanyEntity")
        else:
            self.ecoEffInvest = kwargs["ecoEffInvest"]

    def __InitFinEffCoef(self, kwargs):
        if "finEffCoef" not in kwargs:
            raise ValueError("'finEffCoef' is required for CompanyEntity")
        else:
            self.finEffCoef = kwargs["finEffCoef"]

    def __InitEcoEffCoef(self, kwargs):
        if "ecoEffCoef" not in kwargs:
            raise ValueError("'ecoEffCoef' is required for CompanyEntity")
        else:
            self.ecoEffCoef = kwargs["ecoEffCoef"]

    def __InitAgentEstimators(self, kwargs):
        if "AgentEstimators" not in kwargs:
            print("'AgentEstimators' not provided, using default")
            self.AgentEstimators = AgentEstimators()
        else:
            self.AgentEstimators = kwargs["AgentEstimators"]

    def __InitAgentCalculators(self, kwargs):
        if "AgentCalculators" not in kwargs:
            print("'AgentCalculators' not provided, using default")
            self.AgentCalculators = AgentCalculators()
        else:
            self.AgentCalculators = kwargs["AgentCalculators"]
