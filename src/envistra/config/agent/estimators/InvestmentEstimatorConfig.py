class InvestmentEstimatorConfig:
    def __init__(self, **kwargs):
        if "approach" not in kwargs:
            raise ValueError("approach is required for InvestmentEstimatorConfig")
        if "investmentRatios" not in kwargs:
            raise ValueError("investmentRatios is required for InvestmentEstimatorConfig")

        self.approach = kwargs["approach"]
        self.investmentRatios = kwargs["investmentRatios"]

        # Optional parameters for specific approaches
        self.smoothingAlpha = kwargs.get("smoothingAlpha", 0.3)
        self.baseQuotaPrice = kwargs.get("baseQuotaPrice", 2.5)
        self.adaptiveBlendRatio = kwargs.get("adaptiveBlendRatio", 0.5)
