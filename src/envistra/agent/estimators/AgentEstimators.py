from .ExpensesEstimator import ExpensesEstimator
from .InvestmentEstimator import InvestmentEstimator
from .PollutionEstimator import PollutionEstimator
from .ExpensesReEstimator import ExpensesReEstimator


class AgentEstimators:
    def __init__(self, **kwargs):
        if "Expenses" not in kwargs:
            print("ExpensesEstimator not provided, using default")
            self.Expenses = ExpensesEstimator()
        else:
            self.Expenses = kwargs["Expenses"]

        if "Investment" not in kwargs:
            print("InvestmentEstimator not provided, using default")
            self.Investment = InvestmentEstimator()
        else:
            self.Investment = kwargs["Investment"]

        if "Pollution" not in kwargs:
            print("PollutionEstimator not provided, using default")
            self.Pollution = PollutionEstimator()
        else:
            self.Pollution = kwargs["Pollution"]

        if "ExpensesReEstimation" not in kwargs:
            print("ExpensesReEstimator not provided, using default")
            self.ExpensesReEstimation = ExpensesReEstimator("none", None)
        else:
            self.ExpensesReEstimation = kwargs["ExpensesReEstimation"]
