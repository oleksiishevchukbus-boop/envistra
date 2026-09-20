class QuotaToSellAmountCalculator:
    def __init__(self, approach, quotaReserve):
        self.approach = approach
        self.quotaReserve = quotaReserve

    def Calculate(self, quotaAmount, expectedPollution):
        match self.approach:
            case "reserve_based":
                return self.__ReserveBasedApproach(quotaAmount, expectedPollution)
            case _:
                raise ValueError(f"Unknown quota-to-sell amount approach: {self.approach}")

    def __ReserveBasedApproach(self, quotaAmount, expectedPollution):
        quotaToSellAmount = quotaAmount - expectedPollution
        reserve = quotaToSellAmount * self.quotaReserve
        quotaToSellAmount -= reserve
        return quotaToSellAmount if quotaToSellAmount > 0 else 0
