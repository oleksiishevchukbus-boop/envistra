class ExpensesReEstimator:
    def __init__(self, approach, config):
        self.approach = approach
        self.config = config

    def ReEstimate(self, **kwargs):
        """
        Main method to re-estimate expenses based on the configured approach.

        Returns:
            tuple: (newExpenses, reductionAmount)
        """
        match self.approach:
            case "none":
                return self.__NoneApproach(expenses=kwargs["expenses"])
            case "gap_proportional":
                return self.__GapProportionalApproach(
                    expenses=kwargs["expenses"],
                    expectedPollution=kwargs["expectedPollution"],
                    finalQuota=kwargs["finalQuota"]
                )
            case _:
                return self.__NoneApproach(expenses=kwargs["expenses"])

    def __NoneApproach(self, expenses):
        """
        No re-estimation - returns original expenses unchanged.
        """
        return expenses, 0

    def __GapProportionalApproach(self, expenses, expectedPollution, finalQuota):
        """
        Reduce expenses linearly based on quota gap ratio.
        The larger the gap between expected pollution and quota, the more reduction.
        """
        quotaGap = max(0, expectedPollution - finalQuota)

        if expectedPollution <= 0 or quotaGap <= 0:
            return expenses, 0

        gapRatio = quotaGap / expectedPollution

        if gapRatio < self.config.maxReductionRate:
            reductionFactor = gapRatio
        else:   
            reductionFactor = self.config.maxReductionRate
        reduction = expenses * reductionFactor

        return expenses - reduction, reduction
