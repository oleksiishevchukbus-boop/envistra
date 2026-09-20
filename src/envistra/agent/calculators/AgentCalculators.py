class AgentCalculators:
    def __init__(self, **kwargs):
        if "QuotaToSellAmount" not in kwargs:
            raise ValueError("QuotaToSellAmount is required for AgentCalculators")
        if "QuotaToSellPrice" not in kwargs:
            raise ValueError("QuotaToSellPrice is required for AgentCalculators")

        if "QuotaToBuyAmount" not in kwargs:
            raise ValueError("QuotaToBuyAmount is required for AgentCalculators")
        if "QuotaToBuyPrice" not in kwargs:
            raise ValueError("QuotaToBuyPrice is required for AgentCalculators")


        self.QuotaToSellAmount = kwargs["QuotaToSellAmount"]
        self.QuotaToSellPrice = kwargs["QuotaToSellPrice"]

        self.QuotaToBuyAmount = kwargs["QuotaToBuyAmount"]
        self.QuotaToBuyPrice = kwargs["QuotaToBuyPrice"]
