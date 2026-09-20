class QuotaMarket:
    def __init__(self):
        self.marketDict = dict()

    def AddQuotaLot(self, name, amount, unitPrice):
        self.marketDict[name] = {"amount": amount, "unitPrice": unitPrice}

    def TakeQuotaLot(self, name, amount):
        if self.marketDict[name]["amount"] == amount:
            lot = self.marketDict.pop(name)
            return lot["amount"], lot["amount"]*lot["unitPrice"]
        else:
            self.marketDict[name]["amount"] -= amount
            return amount, amount*self.marketDict[name]["unitPrice"]

    def SortMarketLotDict(self):
        self.marketDict = dict(sorted(self.marketDict.items(), key=lambda item: item[1]["unitPrice"]))
