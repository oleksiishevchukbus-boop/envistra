import numpy as np


class InvestmentEstimator:
    def __init__(self,
        approach,
        ratios
    ):
        self.approach = approach
        self.ratios = ratios
        self._prevInvestment = 0  # For smoothed approach

    def Estimate(self, **kwargs):
        match self.approach:
            case "revenue_based":
                return self.__RevenueBasedApproach(
                    netRevenue=kwargs["netRevenue"],
                    freeAssets=kwargs["freeAssets"])
            case "performance_based":
                return self.__PerformanceBasedApproach(
                    netRevenue=kwargs["netRevenue"],
                    freeAssets=kwargs["freeAssets"],
                    revenueHistory=kwargs.get("revenueHistory"))
            case _:
                raise ValueError(f"Unknown investment estimation approach: {self.approach}")

    def __RevenueBasedApproach(self, netRevenue, freeAssets):
        """Original approach: fixed ratio investment based on min(freeAssets, netRevenue)."""
        investmentAssets = min(freeAssets, netRevenue)
        investments = max(0, self.ratios["revenueToInvestmentRatio"] * investmentAssets)

        if investments == 0 and freeAssets > 0:
            investments = self.ratios["minimalInvestment"] * freeAssets

        finInvestments = self.ratios["finInvestment"] * investments
        ecoInvestments = self.ratios["ecoInvestment"] * investments
        return finInvestments, ecoInvestments

    def __PerformanceBasedApproach(self, netRevenue, freeAssets, revenueHistory):
        """Adaptive investment ratio based on revenue growth trend."""
        investmentAssets = min(freeAssets, netRevenue)

        # Calculate growth rate from history
        adaptive_ratio = self.ratios["revenueToInvestmentRatio"]
        if revenueHistory is not None and len(revenueHistory) >= 3:
            first_val = revenueHistory[0]
            last_val = revenueHistory[-1]
            if abs(first_val) > 1e-6:
                growth_rate = (last_val - first_val) / abs(first_val)
                adaptive_ratio = self.ratios["revenueToInvestmentRatio"] * (1 + 0.5 * growth_rate)
                adaptive_ratio = np.clip(adaptive_ratio, 0.02, 0.15)

        investments = max(0, adaptive_ratio * investmentAssets)

        if investments == 0 and freeAssets > 0:
            investments = self.ratios["minimalInvestment"] * freeAssets

        finInvestments = self.ratios["finInvestment"] * investments
        ecoInvestments = self.ratios["ecoInvestment"] * investments
        return finInvestments, ecoInvestments
