from envistra.config.environment.EnvironmentConfig import EnvironmentConfig


class QuotaToBuyPriceCalculator:
    def __init__(self, approach, assetsPartForTrading):
        self.approach = approach
        self.assetsPartForTrading = assetsPartForTrading

    def Calculate(self,
        step,
        marketDict,
        freeAssets,
        quotaToBuyAmount
    ):
        if self.__IsPrematureTermination(
            marketDict=marketDict,
            quotaToBuyAmount=quotaToBuyAmount,
            freeAssets=freeAssets
        ):
            return dict()

        match self.approach:
            case "gap_full_cover":
                return self.__GapFullCoverApproach(
                    marketDict=marketDict,
                    quotaToBuyAmount=quotaToBuyAmount,
                    freeAssets=freeAssets
                )
            case "ignorance":
                return self.__IgnoranceApproach()
            case "economically_efficient":
                return self.__EconomicallyEfficientApproach(
                    step=step,
                    marketDict=marketDict,
                    quotaToBuyAmount=quotaToBuyAmount,
                    freeAssets=freeAssets
                )
            case _:
                raise ValueError(f"Unknown quota-to-buy price approach: {self.approach}")

    def __GapFullCoverApproach(self,
            marketDict,
            quotaToBuyAmount,
            freeAssets
        ):
        tradingAssets = self.assetsPartForTrading * freeAssets
        return self.__CreatePurchaseTransactionDictForGapFullCover(
            marketDict=marketDict,
            quotaToBuyAmount=quotaToBuyAmount,
            assets=tradingAssets
        )

    def __IgnoranceApproach(self):
        return dict()

    def __EconomicallyEfficientApproach(self,
        step,
        marketDict,
        quotaToBuyAmount,
        freeAssets
    ):
        tradingAssets = self.assetsPartForTrading * freeAssets
        purchaseDict = self.__CreatePurchaseTransactionDictForGapFullCover(
            marketDict=marketDict,
            quotaToBuyAmount=quotaToBuyAmount,
            assets=tradingAssets
        )
        # __CreatePurchaseTransactionDictForGapFullCover has already decremented every
        # lot it took from the shared market. Hand it the UNFILTERED dict so the lots
        # priced above the penalty are refunded before they are dropped.
        return self.__ReturnExpensiveLotsToMarket(
            marketDict=marketDict,
            purchaseDict=purchaseDict,
            step=step
        )

    def __CreatePurchaseTransactionDictForGapFullCover(self,
        marketDict,
        quotaToBuyAmount,
        assets
    ):
        purchaseDict = dict()
        remainingAssets = assets
        remainingAmount = quotaToBuyAmount

        for key, value in marketDict.items():
            if remainingAmount <= 0 or remainingAssets <= 0: break

            canBuyAmount = min(value["amount"], remainingAmount)
            canBuyPrice = canBuyAmount * value["unitPrice"]

            if canBuyPrice > remainingAssets:
                canBuyAmount = remainingAssets // value["unitPrice"]
                canBuyPrice = canBuyAmount * value["unitPrice"]

            if canBuyAmount > 0:
                purchaseDict[key] = { "amount": canBuyAmount, "price": canBuyPrice }
                remainingAmount -= canBuyAmount
                remainingAssets -= canBuyPrice

            if canBuyAmount > 0: marketDict[key]["amount"] -= canBuyAmount

        return purchaseDict

    def __ReturnExpensiveLotsToMarket(self,
        marketDict,
        purchaseDict,
        step
    ):
        for key, value in list(purchaseDict.items()):
            if value["price"]/value["amount"] > EnvironmentConfig.QuotaManager.GetQuotaPenaltyUnitPrice(step):
                if key in marketDict:
                    marketDict[key]["amount"] += value["amount"]
                else:
                    marketDict[key] = {"amount": value["amount"], "unitPrice": value["price"] / value["amount"]}
                purchaseDict.pop(key)

        return purchaseDict

    def __IsPrematureTermination(self,
        marketDict,
        quotaToBuyAmount,
        freeAssets
    ):
        if marketDict is None or len(marketDict) == 0:
            print("All lots are sold out already!")
            return True
        if quotaToBuyAmount <= 0 or freeAssets <= 0:
            return True
        return False
