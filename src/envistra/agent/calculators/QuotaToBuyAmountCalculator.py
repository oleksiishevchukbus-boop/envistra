class QuotaToBuyAmountCalculator:
    def __init__(self, approach, quotaReserve):
        self.approach = approach
        self.quotaReserve = quotaReserve

    def Calculate(self, quotaAmount, expectedPollution):
        match self.approach:
            case "reserve_based":
                return self.__ReserveBasedApproach(
                    quotaAmount=quotaAmount,
                    expectedPollution=expectedPollution
                )
            case _:
                raise ValueError(f"Unknown quota-to-buy amount approach: {self.approach}")

    def __ReserveBasedApproach(self, quotaAmount, expectedPollution):
        quotaToBuyAmount = expectedPollution - quotaAmount
        quotaToBuyAmount += self.quotaReserve * quotaToBuyAmount
        return quotaToBuyAmount if quotaToBuyAmount > 0 else 0
