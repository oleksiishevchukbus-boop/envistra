from envistra.config.ConfigHelpers import require_kwarg


class StrategyEntity:
    """Configuration entity that defines an agent's behavioral strategy.

    A strategy bundles together all the config components that determine
    how an agent estimates, invests, and trades quotas.

    Attributes:
        name: Human-readable strategy name for UI display
        description: Brief description of the strategy's approach
        color: Hex color code for UI visualization (e.g., "#DF4E4E")
    """

    # List of required configuration components
    REQUIRED_ESTIMATOR_CONFIGS = [
        'ExpensesEstimatorConfig',
        'InvestmentEstimatorConfig',
        'PollutionEstimatorConfig',
        'ExpensesReEstimationConfig',
    ]

    REQUIRED_CALCULATOR_CONFIGS = [
        'QuotaToSellAmountCalculatorConfig',
        'QuotaToSellPriceCalculatorConfig',
        'QuotaToBuyAmountCalculatorConfig',
        'QuotaToBuyPriceCalculatorConfig',
    ]

    def __init__(self, name: str = "", description: str = "", color: str = "#888888", **kwargs):
        self.name = name
        self.description = description
        self.color = color
        self._init_configs(kwargs, self.REQUIRED_ESTIMATOR_CONFIGS)
        self._init_configs(kwargs, self.REQUIRED_CALCULATOR_CONFIGS)

    def _init_configs(self, kwargs, config_names):
        """Initialize required config attributes from kwargs."""
        for config_name in config_names:
            setattr(self, config_name, require_kwarg(kwargs, config_name, 'StrategyEntity'))
