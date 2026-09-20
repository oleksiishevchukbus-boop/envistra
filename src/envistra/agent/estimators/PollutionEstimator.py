from envistra.config.Enums import CompanyAgentFields


class PollutionEstimator:
    def __init__(self, approach, MlpModel):
        self.approach = approach
        self.MlpModel = MlpModel

    def Estimate(self,
        step,
        expenses,
        prevStepExpenses,
        prevStepPollution,
        ecoEff,
    ):
        match self.approach:
            case "general":
                return self.__GeneralApproach(prevStepPollution, expenses, prevStepExpenses)
            case "MLP_based":
                if step < 2:
                    return self.__GeneralApproach(prevStepPollution, expenses, prevStepExpenses)
                return self.__MLPRegressorApproach([[expenses, ecoEff]])
            case _:
                raise ValueError(f"Unknown pollution estimation approach: {self.approach}")

    def TryFitMlpModel(self,
            steps,
            historyData
        ):
        if self.approach == "MLP_based" and steps > 1:
            x = historyData[[CompanyAgentFields.EXPENSES, CompanyAgentFields.ECO_EFF]].values
            y = historyData[[CompanyAgentFields.POLLUTION]].values.ravel()
            self.MlpModel.fit(x, y)

    def __GeneralApproach(self,
        prevStepPollution,
        expenses,
        prevStepExpenses
    ):
        if expenses == 0:
            return 0
        expensesChange = (expenses - prevStepExpenses) / expenses
        plannedPollution = prevStepPollution + expensesChange * prevStepPollution
        return plannedPollution

    def __MLPRegressorApproach(self, x):
        y = self.MlpModel.predict(x)
        return y[0]
