import mesa

from envistra.config.Enums import CompanyAgentFields
from envistra.config.environment.EnvironmentConfig import EnvironmentConfig

from envistra.agent.CompanyAgent import CompanyAgent
from envistra.environment.QuotaManager import QuotaManager
from envistra.environment.QuotaMarket import QuotaMarket


class CompanyAgentModel(mesa.Model):
    def __init__(self, companyEntities, **kwargs):
        super().__init__()
        for companyEntity in companyEntities:
            agent = CompanyAgent(self, companyEntity)

        self.QuotaManager = QuotaManager(EnvironmentConfig.QuotaManager.Approach, companyEntities)
        self.__InitEnvironment(kwargs)
        self.__InitAgentDataCollector()

    def step(self):
        self.datacollector.collect(self)
        self.agents.do("EstimateExpenses")
        self.agents.do("EstimateInvestments")
        self.agents.do("EstimatePollution")

        self.QuotaManager.InitCompanyReportDict()
        self.agents.do("SendExpensesReport")
        self.QuotaManager.CalculateQuotas()

        self.agents.do("ReceiveQuota")
        self.agents.do("SellQuota")
        self.QuotaMarket.SortMarketLotDict()
        self.agents.shuffle_do("BuyQuota")
        self.__InitQuotaMarket()

        self.agents.do("ReEstimateExpenses")

        self.agents.do("ProduceRevenue")
        self.agents.do("ProducePollution")

        self.agents.do("PayQuotaExceedancePenalty")
        self.agents.do("ImplementInvestments")
        self.agents.do("ImplementOperations")
        self.QuotaManager.ApplyLinearReductionFactor()
        # self.datacollector.collect(self)

    def GetAgentBy(self, attr, value):
        for agent in self.agents:
            if getattr(agent, attr, None) == value: return agent

    def GetHistoryForAgent(self, agentId):
        data = self.datacollector.get_agent_vars_dataframe()
        return data.xs(agentId, level='AgentID')

    def GetAgentsFinEff(self, industry=None):
        if industry:
            return [agent.finEff for agent in self.agents if agent.industry == industry]
        return [agent.finEff for agent in self.agents]

    def GetAgentsEcoEff(self, industry=None):
        if industry:
            return [agent.ecoEff for agent in self.agents if agent.industry == industry]
        return [agent.ecoEff for agent in self.agents]

    def __InitEnvironment(self, kwargs):
        self.__InitQuotaMarket()

        if "EnvironmentCalculators" not in kwargs:
            raise ValueError("EnvironmentCalculators must be provided in kwargs")
        else:
            self.EnvironmentCalculators = kwargs["EnvironmentCalculators"]

    def __InitQuotaMarket(self):
        self.QuotaMarket = QuotaMarket()

    def __InitAgentDataCollector(self):
        generalCompanyData = {
            CompanyAgentFields.NAME: "name",
            CompanyAgentFields.INDUSTRY: "industry",
            # "Country": "country"
        }
        basicEconomicalData = {
            CompanyAgentFields.ASSETS: "assets",
            CompanyAgentFields.EXPENSES: "expenses",
            CompanyAgentFields.EXPENSES_REDUCTION: "expensesReduction",
            CompanyAgentFields.REVENUE_TO_EXPENSES_RATIO: "revenueToExpensesRatio",
            CompanyAgentFields.REVENUE: "revenue",
            CompanyAgentFields.OPERATIONAL_NET_REVENUE: "operationalNetRevenue",
            CompanyAgentFields.NET_REVENUE: "netRevenue",
            CompanyAgentFields.POLLUTION_TO_EXPENSES_RATIO: "pollutionToExpensesRatio",
            CompanyAgentFields.POLLUTION: "pollution",
            CompanyAgentFields.QUOTA_EXCEEDANCE_PENALTY: "quotaExceedancePenalty"
        }
        investmentAndEfficiencyData = {
            CompanyAgentFields.FIN_EFF: "finEff",
            CompanyAgentFields.FIN_EFF_INVEST: "finEffInvest",
            CompanyAgentFields.FIN_EFF_INVEST_INCREASE: "finEffInvestIncrease",

            CompanyAgentFields.ECO_EFF: "ecoEff",
            CompanyAgentFields.ECO_EFF_INVEST: "ecoEffInvest",
            CompanyAgentFields.ECO_EFF_INVEST_INCREASE: "ecoEffInvestIncrease"
        }
        quotaRelatedData = {
            CompanyAgentFields.EXPECTED_POLLUTION: "expectedPollution",
            CompanyAgentFields.QUOTA: "quota",
            CompanyAgentFields.QUOTA_SHARE: "quotaShare",
            CompanyAgentFields.FINAL_QUOTA: "finalQuota"
        }
        quotaTradeData = {
            CompanyAgentFields.QUOTA_TO_SELL_AMOUNT: "quotaToSellAmount",
            CompanyAgentFields.QUOTA_TO_BUY_AMOUNT: "quotaToBuyAmount",

            CompanyAgentFields.QUOTA_UNIT_PRICE: "quotaUnitPrice",
            CompanyAgentFields.SOLD_QUOTA_AMOUNT: "soldQuotaAmount",
            CompanyAgentFields.SOLD_QUOTA_REVENUE: "soldQuotaRevenue",

            CompanyAgentFields.BOUGHT_QUOTA_AMOUNT: "boughtQuotaAmount",
            CompanyAgentFields.BOUGHT_QUOTA_EXPENSES: "boughtQuotaExpenses"
        }
        testData = {
            CompanyAgentFields.NET_REVENUE_CHANGE_RATIO: "netRevenueChangeRatio",
        }

        self.datacollector = mesa.DataCollector(
            agent_reporters=generalCompanyData | basicEconomicalData | quotaRelatedData | quotaTradeData | investmentAndEfficiencyData | testData)
