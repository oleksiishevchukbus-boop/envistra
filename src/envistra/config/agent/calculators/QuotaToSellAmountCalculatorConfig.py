class QuotaToSellAmountCalculatorConfig:
    def __init__(self, **kwargs):
        if "approach" not in kwargs:
            raise ValueError("approach is required for QuotaToSellAmountCalculatorConfig")
        if "quotaReserve" not in kwargs:
            raise ValueError("quotaReserve is required for QuotaToSellAmountCalculatorConfig")

        self.approach = kwargs["approach"]
        self.quotaReserve = kwargs["quotaReserve"]
