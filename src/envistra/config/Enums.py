from enum import Enum

class CompanyAgentFields(str, Enum):
    # generalCompanyData
    NAME = "Name"
    INDUSTRY = "Industry"

    # basicEconomicalData
    ASSETS = "Assets"
    EXPENSES = "Expenses"
    EXPENSES_REDUCTION = "ExpensesReduction"
    REVENUE_TO_EXPENSES_RATIO = "RevenueToExpensesRatio"
    REVENUE = "Revenue"

    OPERATIONAL_NET_REVENUE = "OperationalNetRevenue"
    NET_REVENUE = "NetRevenue"
    POLLUTION_TO_EXPENSES_RATIO = "PollutionToExpensesRatio"
    POLLUTION = "Pollution"
    QUOTA_EXCEEDANCE_PENALTY = "QuotaExceedancePenalty"

    # investmentAndEfficiencyData
    FIN_EFF = "FinEff"
    FIN_EFF_INVEST = "FinEffInvest"
    FIN_EFF_INVEST_INCREASE = "FinEffInvestIncrease"

    ECO_EFF = "EcoEff"
    ECO_EFF_INVEST = "EcoEffInvest"
    ECO_EFF_INVEST_INCREASE = "EcoEffInvestIncrease"

    # quotaRelatedData
    EXPECTED_POLLUTION = "ExpectedPollution"
    QUOTA = "Quota"
    QUOTA_SHARE = "QuotaShare"
    FINAL_QUOTA = "FinalQuota"

    # quotaTradeData
    QUOTA_TO_SELL_AMOUNT = "QuotaToSellAmount"
    QUOTA_TO_BUY_AMOUNT = "QuotaToBuyAmount"
    QUOTA_UNIT_PRICE = "QuotaUnitPrice"

    SOLD_QUOTA_AMOUNT = "SoldQuotaAmount"
    SOLD_QUOTA_REVENUE = "SoldQuotaRevenue"

    BOUGHT_QUOTA_AMOUNT = "BoughtQuotaAmount"
    BOUGHT_QUOTA_EXPENSES = "BoughtQuotaExpenses"

    # testData
    NET_REVENUE_CHANGE_RATIO = "NetRevenueChangeRatio"

    def __str__(self):
        return str(self.value)