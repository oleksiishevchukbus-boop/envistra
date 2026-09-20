class QuotaToBuyAmountCalculatorConfig:
    def __init__(self, **kwargs):
        if "approach" not in kwargs:
            raise ValueError("approach is required for QuotaToBuyAmountCalculatorConfig")
        if "quotaReserve" not in kwargs:
            raise ValueError("quotaReserve is required for QuotaToBuyAmountCalculatorConfig")

        self.approach = kwargs["approach"]
        self.quotaReserve = kwargs["quotaReserve"]
