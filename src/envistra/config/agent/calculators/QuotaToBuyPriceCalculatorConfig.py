class QuotaToBuyPriceCalculatorConfig:
    def __init__(self, **kwargs):
        if "approach" not in kwargs:
            raise ValueError("approach is required for QuotaToBuyPriceCalculatorConfig")

        if "assetsPartForTrading" not in kwargs:
            raise ValueError("assetsPartForTrading is required for QuotaToBuyPriceCalculatorConfig")

        self.approach = kwargs["approach"]
        self.assetsPartForTrading = kwargs["assetsPartForTrading"]
