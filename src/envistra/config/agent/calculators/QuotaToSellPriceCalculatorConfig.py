class QuotaToSellPriceCalculatorConfig:
    def __init__(self, **kwargs):
        if "approach" not in kwargs:
            raise ValueError("approach is required for QuotaToSellPriceCalculatorConfig")

        if "unitPrice" not in kwargs:
            raise ValueError("unitPrice is required for QuotaToSellPriceCalculatorConfig")

        if "changeThreshold" not in kwargs:
            raise ValueError("changeThreshold is required for QuotaToSellPriceCalculatorConfig")

        if "salesTarget" not in kwargs:
            raise ValueError("salesTarget is required for QuotaToSellPriceCalculatorConfig")

        self.approach = kwargs["approach"]
        self.unitPrice = kwargs["unitPrice"]
        self.changeThreshold = kwargs["changeThreshold"]
        self.salesTarget = kwargs["salesTarget"]
