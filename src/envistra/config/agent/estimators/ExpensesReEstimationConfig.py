class ExpensesReEstimationConfig:
    def __init__(self, **kwargs):
        if "approach" not in kwargs:
            raise ValueError("approach is required for ExpensesReEstimationConfig")

        self.approach = kwargs["approach"]  # "none", "gap_proportional", "cost_benefit", "threshold_based", "adaptive"

        # Gap-proportional params
        self.maxReductionRate = kwargs.get('maxReductionRate', 0.0)

        # Cost-benefit params
        self.profitMargin = kwargs.get('profitMargin', 1.0)
        self.maxReductionCap = kwargs.get('maxReductionCap', 0.0)

        # Adaptive params
        self.baseRate = kwargs.get('baseRate', 0.0)
        self.trendSensitivity = kwargs.get('trendSensitivity', 0.0)
