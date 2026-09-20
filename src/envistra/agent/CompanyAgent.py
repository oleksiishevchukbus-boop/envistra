import mesa

from envistra.config.Enums import CompanyAgentFields
from .CompanyAgentUtilities import CompanyAgentUtilities


class CompanyAgent(mesa.Agent):
    quotaExceedancePenalty = None
    tradedQuotaRevenue = None
    def __init__(self, model, entity):
        super().__init__(model)
        self.__InitGeneralData(entity)
        self.__InitFinancialAndPollutionData(entity)
        self.__InitEfficiencyData(entity)
        self.__InitRatios(entity)
        self.AgentEstimators = entity.AgentEstimators
        self.AgentCalculators = entity.AgentCalculators

        self.__InitOperationalData()
        self.__InitQuotaTradingData()
        self.__InitInvestmentIncreaseData()
        self.__InitTestData()

    def EstimateExpenses(self):
        self.expenses = self.AgentEstimators.Expenses.Estimate(assets=self.assets,
            expenses=self.expenses,
            netRevenue = self.netRevenue,
            prevStepNetRevenue = self.__GetPrevStepValue(CompanyAgentFields.NET_REVENUE),
            quotaExceedance = None if self.model.steps < 3 else self.finalQuota - self.pollution,
            prevStepQuotaExceedance = None if self.model.steps < 3 else self.__GetPrevStepValue(CompanyAgentFields.FINAL_QUOTA) - self.__GetPrevStepValue(CompanyAgentFields.POLLUTION)
        )

    def EstimateInvestments(self):
        freeAssets = self.assets - self.expenses

        revenueHistory = None
        if self.model.steps >= 3:
            historyData = self.model.GetHistoryForAgent(self.unique_id)
            revenueHistory = historyData[CompanyAgentFields.NET_REVENUE].tail(3).tolist()

        self.finEffInvestIncrease, self.ecoEffInvestIncrease = self.AgentEstimators.Investment.Estimate(
            netRevenue=self.netRevenue,
            freeAssets=freeAssets,
            revenueHistory=revenueHistory
        )

    def EstimatePollution(self):
        historyData = self.model.GetHistoryForAgent(self.unique_id)
        self.AgentEstimators.Pollution.TryFitMlpModel(
            self.model.steps,
            historyData
        )

        self.expectedPollution = self.AgentEstimators.Pollution.Estimate(
            step=self.model.steps,
            expenses=self.expenses,
            prevStepExpenses=self.__GetPrevStepValue(CompanyAgentFields.EXPENSES),
            prevStepPollution=self.__GetPrevStepValue(CompanyAgentFields.POLLUTION),
            ecoEff=self.ecoEff
        )

    def SendExpensesReport(self):
        prevStepExpenses = self.__GetPrevStepValue(CompanyAgentFields.EXPENSES)
        quotaToSend = self.expectedPollution if self.model.steps == 1 else self.__GetPrevStepValue(CompanyAgentFields.QUOTA)
        # On step 1, self.pollution is the initial entity value (not yet modified by ProducePollution)
        prevStepPollution = self.pollution if self.model.steps == 1 else self.__GetPrevStepValue(CompanyAgentFields.POLLUTION)

        self.model.QuotaManager.ReceiveReport(
            name=self.name,
            industry=self.industry,
            expenses=self.expenses,
            prevStepExpenses=prevStepExpenses,

            prevStepQuota=quotaToSend,
            pollutionToExpensesRatio=self.pollutionToExpensesRatio,
            prevStepPollution=prevStepPollution
        )

    def ReceiveQuota(self):
        reportsDict = self.model.QuotaManager.companyReports
        self.quota = reportsDict[self.name]["quota"]
        self.quotaShare = reportsDict[self.name]["quotaShare"]
        self.__InitQuotaTradingData()

    def SellQuota(self):
        self.quotaToSellAmount = self.AgentCalculators.QuotaToSellAmount.Calculate(
            quotaAmount=self.quota,
            expectedPollution=self.expectedPollution
        )

        if self.quotaToSellAmount > 0:
            historyData = self.model.GetHistoryForAgent(self.unique_id)
            self.quotaUnitPrice = self.AgentCalculators.QuotaToSellPrice.Calculate(historyData=historyData)
            self.model.QuotaMarket.AddQuotaLot(self.name, self.quotaToSellAmount, self.quotaUnitPrice)

    def BuyQuota(self):
        if self.quotaToSellAmount == 0:
            self.quotaToBuyAmount = self.AgentCalculators.QuotaToBuyAmount.Calculate(
                quotaAmount=self.quota,
                expectedPollution=self.expectedPollution
            )

        if self.quotaToBuyAmount > 0:
            freeAssets = self.assets - self.expenses - self.finEffInvestIncrease - self.ecoEffInvestIncrease
            self.quotaPurchaseTransactionDict = self.AgentCalculators.QuotaToBuyPrice.Calculate(
                step=self.model.steps,
                marketDict=self.model.QuotaMarket.marketDict,
                freeAssets=freeAssets,
                quotaToBuyAmount=self.quotaToBuyAmount,
            )
            self.__ApplyQuotaPurchaseTransactions(self.quotaPurchaseTransactionDict)

    def ReEstimateExpenses(self):
        """
        Re-estimate operating expenses after quota trading to decrease pollution generation.
        This step allows agents to adjust their expenses based on their final quota position.
        """
        # Calculate final quota after trading
        currentFinalQuota = self.quota - self.soldQuotaAmount + self.boughtQuotaAmount

        # Re-estimate expenses using the configured approach
        newExpenses, reduction = self.AgentEstimators.ExpensesReEstimation.ReEstimate(
            expenses=self.expenses,
            expectedPollution=self.expectedPollution,
            finalQuota=currentFinalQuota
        )

        self.expensesReduction = reduction
        self.expenses = newExpenses

        # Re-estimate expected pollution if expenses were reduced
        if reduction > 0:
            self.expectedPollution = self.AgentEstimators.Pollution.Estimate(
                step=self.model.steps,
                expenses=self.expenses,
                prevStepExpenses=self.__GetPrevStepValue(CompanyAgentFields.EXPENSES),
                prevStepPollution=self.__GetPrevStepValue(CompanyAgentFields.POLLUTION),
                ecoEff=self.ecoEff
            )

    def ProduceRevenue(self):
        competitorsFinEffList = self.model.GetAgentsFinEff(self.industry)
        self.revenue, self.revenueToExpensesRatio = self.model.EnvironmentCalculators.Revenue.Calculate(
            expenses=self.expenses,
            finEff=self.finEff,
            industry=self.industry,
            competitorsFinEffList=competitorsFinEffList
        )

    def ProducePollution(self):
        self.pollution, self.pollutionToExpensesRatio = self.model.EnvironmentCalculators.Pollution.Calculate(
            expenses=self.expenses,
            ecoEff=self.ecoEff,
            companyName=self.name,
            industry=self.industry
        )

    def PayQuotaExceedancePenalty(self):
        self.finalQuota = self.quota - self.soldQuotaAmount + self.boughtQuotaAmount
        self.quotaExceedancePenalty = self.model.QuotaManager.CalculatePenalty(
            step=self.model.steps,
            quota=self.finalQuota,
            pollution=self.pollution
        )
        # Track penalty history for adaptive approach
        self.penaltyHistory.append(self.quotaExceedancePenalty)

    def ImplementInvestments(self):
        self.__ImplementFinInvest()
        self.__ImplementEcoInvest()

    def ImplementOperations(self):
        self.operationalNetRevenue = self.revenue - self.expenses
        self.netRevenue = self.operationalNetRevenue + self.soldQuotaRevenue - self.boughtQuotaExpenses - self.quotaExceedancePenalty
        self.assets = self.assets + self.netRevenue - self.finEffInvestIncrease - self.ecoEffInvestIncrease
        if self.assets < 0:
            print(f"Agent {self.name} is bankrupt!")
            self.assets = 0

# ---------------------------------------------------------------------------------
# Private methods
# These methods are not intended to be used outside of this class.
# They are used to implement the agent's internal logic and calculations.
# ---------------------------------------------------------------------------------

    def __ApplyQuotaPurchaseTransactions(self, quotaPurchaseTransactionDict):
        for agentName, transactionDetails in quotaPurchaseTransactionDict.items():
            self.boughtQuotaAmount += transactionDetails["amount"]
            self.boughtQuotaExpenses += transactionDetails["price"]
            agent = self.model.GetAgentBy("name", agentName)
            agent.soldQuotaAmount += transactionDetails["amount"]
            agent.soldQuotaRevenue += transactionDetails["price"]

    def __ImplementFinInvest(self):
        self.finEffInvest += self.finEffInvestIncrease
        self.finEff = CompanyAgentUtilities.FinEffCalc(self.finEffCoef, self.finEffInvest)

    def __ImplementEcoInvest(self):
        self.ecoEffInvest += self.ecoEffInvestIncrease
        self.ecoEff = CompanyAgentUtilities.EcoEffCalc(self.ecoEffCoef, self.ecoEffInvest)

    def __GetPrevStepValue(self, key, stepDiff=1):
        step = self.model.steps - stepDiff
        if step < 0:
            raise ValueError("Step cannot be negative. Please check the stepDiff value.")
        elif step == 0:
            step = 1

        value = self.model.GetHistoryForAgent(self.unique_id).loc[step, key]
        return value

    def __InitGeneralData(self, entity):
        self.name = entity.name
        self.industry = entity.industry
        self.quota = self.finalQuota = 0
        self.quotaShare = 0
        # self.country = data.country

    def __InitFinancialAndPollutionData(self, entity):
        self.assets = entity.assets
        self.expenses = entity.expenses
        self.revenue = entity.revenue
        self.operationalRevenue = entity.revenue
        self.operationalNetRevenue = entity.revenue - entity.expenses
        self.netRevenue = entity.revenue - entity.expenses
        self.pollution = entity.pollution

    def __InitEfficiencyData(self, entity):
        self.finEffCoef = entity.finEffCoef
        self.finEffInvest = entity.finEffInvest
        self.finEff = CompanyAgentUtilities.FinEffCalc(self.finEffCoef, self.finEffInvest)

        self.ecoEffCoef = entity.ecoEffCoef
        self.ecoEffInvest = entity.ecoEffInvest
        self.ecoEff = CompanyAgentUtilities.EcoEffCalc(self.ecoEffCoef, self.ecoEffInvest)

    def __InitRatios(self, entity):
        self.revenueToExpensesRatio = entity.revenueToExpensesRatio
        self.pollutionToExpensesRatio = entity.pollutionToExpensesRatio

    def __InitOperationalData(self):
        self.quotaUnitPrice = 0
        self.expensesReduction = 0
        self.penaltyHistory = []
        self.expectedPollution = 0

    def __InitQuotaTradingData(self):
        self.soldQuotaAmount = 0
        self.boughtQuotaAmount = 0

        self.soldQuotaRevenue = 0
        self.boughtQuotaExpenses = 0

        self.quotaToSellAmount = 0
        self.quotaToBuyAmount = 0

    def __InitInvestmentIncreaseData(self):
        self.finEffInvestIncrease = 0
        self.ecoEffInvestIncrease = 0

    def __InitTestData(self):
        self.netRevenueChangeRatio = 0
