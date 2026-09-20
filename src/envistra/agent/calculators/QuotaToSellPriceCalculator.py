import numpy as np

from envistra.config.Enums import CompanyAgentFields


class QuotaToSellPriceCalculator:
    def __init__(self,
        approach,
        unitPrice,
        changeThreshold,
        salesTarget
    ):
        self.approach = approach
        self.unitPrice = unitPrice
        self.changeThreshold = changeThreshold
        self.salesTarget = salesTarget

    def Calculate(self, historyData):
        match self.approach:
            case "general":
                return self.__GeneralApproach()
            case "history_based":
                return self.__HistoryBasedApproach(historyData)
            case _:
                raise ValueError(f"Unknown quota-to-sell price approach: {self.approach}")

    def __GeneralApproach(self):
        return self.unitPrice

    def __HistoryBasedApproach(self, historyData):
        def GetLastSellInfo(historyData):
            nonZeroSoldQuota = historyData[historyData[CompanyAgentFields.QUOTA_TO_SELL_AMOUNT] > 0].index
            if len(nonZeroSoldQuota) > 0:
                lastSoldQuotaStep = nonZeroSoldQuota[-1]
                lastQuotaToTradeAmount = historyData.loc[lastSoldQuotaStep, CompanyAgentFields.QUOTA_TO_SELL_AMOUNT]
                lastSoldQuotaAmount = historyData.loc[lastSoldQuotaStep, CompanyAgentFields.SOLD_QUOTA_AMOUNT]
                return lastSoldQuotaAmount, lastQuotaToTradeAmount
            return None, None

        lastSoldQuotaAmount, lastQuotaToSellAmount = GetLastSellInfo(historyData)

        if lastQuotaToSellAmount is None:
            return self.__GeneralApproach()

        salesTargetAmount = self.salesTarget * lastQuotaToSellAmount
        soldToTargetDiff = lastSoldQuotaAmount - salesTargetAmount
        unitPriceChangeInPercent = soldToTargetDiff / salesTargetAmount

        if abs(unitPriceChangeInPercent) > self.changeThreshold:
            unitPriceChangeInPercent = np.sign(unitPriceChangeInPercent) * self.changeThreshold

        self.unitPrice += unitPriceChangeInPercent * self.unitPrice

        return self.unitPrice
