from envistra.config.ConfigHelpers import require_kwarg


class CompanyAgentConfigEntity:
    """Configuration for one company agent, built from one config/companies/*.json.

    Carries the company's identity, its link to the source data, and its four
    personal efficiency parameters, and flattens the eight estimator/calculator
    configs off its Strategy so consumers read them from one object.

    The Strategy's identity is kept (`strategyId`, `strategyName`). The
    predecessor discarded it, which forced its run-config writer to guess the
    strategy back by sniffing approach values — a guess that returned "Unknown"
    for any strategy beyond the original four.
    """

    #: Personal parameters, required of every company file.
    REQUIRED_PARAMS = ['finEffInvest', 'ecoEffInvest', 'finEffCoef', 'ecoEffCoef']

    #: Copied off the Strategy this company references.
    STRATEGY_CONFIGS = [
        'QuotaToSellAmountCalculatorConfig',
        'QuotaToSellPriceCalculatorConfig',
        'QuotaToBuyAmountCalculatorConfig',
        'QuotaToBuyPriceCalculatorConfig',
        'ExpensesEstimatorConfig',
        'InvestmentEstimatorConfig',
        'PollutionEstimatorConfig',
        'ExpensesReEstimationConfig',
    ]

    def __init__(self, **kwargs):
        #: Agent label — DataCollector "Name", plot legends, results folders.
        self.name = require_kwarg(kwargs, 'name', 'CompanyAgentConfigEntity')

        #: Join key into the workbooks' "Name" column. Several companies may
        #: share one dataSource: the four AES CORP variants differ only by
        #: strategy, which is what the strategy comparison exercises.
        self.dataSource = require_kwarg(kwargs, 'dataSource', 'CompanyAgentConfigEntity')

        for param in self.REQUIRED_PARAMS:
            setattr(self, param, require_kwarg(kwargs, param, 'CompanyAgentConfigEntity'))

        strategy = require_kwarg(kwargs, 'Strategy', 'CompanyAgentConfigEntity')
        self.strategyId = require_kwarg(kwargs, 'strategyId', 'CompanyAgentConfigEntity')
        self.strategyName = strategy.name
        for config_name in self.STRATEGY_CONFIGS:
            setattr(self, config_name, getattr(strategy, config_name))

    def __repr__(self):
        return (f"CompanyAgentConfigEntity(name={self.name!r}, "
                f"dataSource={self.dataSource!r}, strategy={self.strategyId!r})")
