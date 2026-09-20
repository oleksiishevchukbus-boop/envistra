import numpy as np


class ExpensesEstimator:
    def __init__(self,
        approach,
        expensesToAssetsRatio,
        changeThreshold_Upper,
        changeThreshold_Lower,
        featuresImpact,
        smoothingAlpha=0.7
    ):
        self.approach = approach
        self.expensesToAssetsRatio = expensesToAssetsRatio
        self.changeThreshold_Upper = changeThreshold_Upper
        self.changeThreshold_Lower = changeThreshold_Lower
        self.featuresImpact = featuresImpact
        self.smoothingAlpha = smoothingAlpha
        self._prevExpenseChange = 0  # For smoothing in performance_based_relative approach

    def Estimate(self, **kwargs):
        match self.approach:
            case "general":
                return self.__GeneralApproach(assets=kwargs["assets"])
            case "performance_based":
                return self.__PerformanceBasedApproach(assets=kwargs["assets"],
                                                       expenses=kwargs["expenses"],
                                                       netRevenue=kwargs["netRevenue"],
                                                       prevStepNetRevenue=kwargs["prevStepNetRevenue"],
                                                       quotaExceedance=kwargs["quotaExceedance"],
                                                       prevStepQuotaExceedance=kwargs["prevStepQuotaExceedance"])
            case "performance_based_relative":
                return self.__PerformanceBasedRelativeApproach(assets=kwargs["assets"],
                                                            expenses=kwargs["expenses"],
                                                            netRevenue=kwargs["netRevenue"],
                                                            prevStepNetRevenue=kwargs["prevStepNetRevenue"],
                                                            quotaExceedance=kwargs["quotaExceedance"],
                                                            prevStepQuotaExceedance=kwargs["prevStepQuotaExceedance"])
            case _:
                raise ValueError(f"Unknown expenses estimation approach: {self.approach}")


    def __GeneralApproach(self, assets):
        expenses = self.expensesToAssetsRatio * assets
        return expenses

    def __PerformanceBasedApproach(self,
        assets,
        expenses,
        netRevenue, prevStepNetRevenue,
        quotaExceedance, prevStepQuotaExceedance
    ):
        if assets <= 0:
            return 0

        if netRevenue == 0 and prevStepNetRevenue == 0:
            return expenses

        if netRevenue < 0 and prevStepNetRevenue < 0:
            netRevenueChange = netRevenue/ assets
        else:
            netRevenueChange = (netRevenue - prevStepNetRevenue) / assets

        quotaExceedanceChange = 0
        if prevStepQuotaExceedance is not None:
            if quotaExceedance < 0 and prevStepQuotaExceedance < 0:
                quotaExceedanceChange = quotaExceedance / assets
            else:
                quotaExceedanceChange = (quotaExceedance - prevStepQuotaExceedance) / assets

        expensesChange_NetRevenueFactor = netRevenueChange * self.featuresImpact["netRevenue"]
        expensesChange_QuotaExceedanceFactor = quotaExceedanceChange * self.featuresImpact["quotaExceedance"]
        expensesChange = expensesChange_NetRevenueFactor + expensesChange_QuotaExceedanceFactor

        if abs(expensesChange) > self.changeThreshold_Upper:
            expensesChange = np.sign(expensesChange) * self.changeThreshold_Upper
        elif abs(expensesChange) < self.changeThreshold_Lower:
            expensesChange = np.sign(expensesChange) * self.changeThreshold_Lower

        newExpenses = expenses + expensesChange * expenses
        newExpenses = max(0, min(assets, newExpenses))

        return newExpenses

    def __PerformanceBasedRelativeApproach(self,
        assets,
        expenses,
        netRevenue, prevStepNetRevenue,
        quotaExceedance, prevStepQuotaExceedance
    ):
        """
        Fixed version of performance-based approach with:
        1. Consistent relative change calculation (always uses change, not absolute position)
        2. Normalization by previous value instead of assets
        3. Exponential smoothing to reduce volatility
        """
        if assets <= 0:
            return 0
        if expenses == 0:
            return self.expensesToAssetsRatio * assets

        # Consistent relative change calculation for net revenue
        if prevStepNetRevenue != 0:
            netRevenueChange = (netRevenue - prevStepNetRevenue) / abs(prevStepNetRevenue)
        elif netRevenue != 0:
            netRevenueChange = np.sign(netRevenue) * self.changeThreshold_Lower
        else:
            netRevenueChange = 0

        # Consistent relative change for quota exceedance
        quotaExceedanceChange = 0
        if prevStepQuotaExceedance is not None:
            if abs(prevStepQuotaExceedance) > 0.001:  # Avoid division by near-zero
                quotaExceedanceChange = (quotaExceedance - prevStepQuotaExceedance) / abs(prevStepQuotaExceedance)
            elif quotaExceedance != 0:
                quotaExceedanceChange = np.sign(quotaExceedance) * self.changeThreshold_Lower

        # Calculate raw change using strategy weights
        rawChange = (netRevenueChange * self.featuresImpact["netRevenue"] +
                     quotaExceedanceChange * self.featuresImpact["quotaExceedance"])

        # Apply exponential smoothing
        smoothedChange = self.smoothingAlpha * rawChange + (1 - self.smoothingAlpha) * self._prevExpenseChange
        self._prevExpenseChange = smoothedChange

        # Apply thresholds
        if abs(smoothedChange) > self.changeThreshold_Upper:
            smoothedChange = np.sign(smoothedChange) * self.changeThreshold_Upper
        elif abs(smoothedChange) < self.changeThreshold_Lower:
            smoothedChange = 0  # Below threshold = no change

        # Apply change
        newExpenses = expenses * (1 + smoothedChange)
        return max(0, min(assets, newExpenses))

