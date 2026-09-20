class ExpensesEstimatorConfig:
    def __init__(self, **kwargs):
        if "approach" not in kwargs:
            raise ValueError("approach is required for ExpensesEstimatorConfig")
        if "changeThreshold_Upper" not in kwargs:
            raise ValueError("changeThreshold_Upper is required for ExpensesEstimatorConfig")
        if "changeThreshold_Lower" not in kwargs:
            raise ValueError("changeThreshold_Lower is required for ExpensesEstimatorConfig")
        if "featuresImpact" not in kwargs:
            raise ValueError("featuresImpact is required for ExpensesEstimatorConfig")


        self.approach = kwargs["approach"]
        self.changeThreshold_Upper = kwargs["changeThreshold_Upper"]
        self.changeThreshold_Lower = kwargs["changeThreshold_Lower"]
        self.featuresImpact = kwargs["featuresImpact"]
        self.smoothingAlpha = kwargs.get("smoothingAlpha", 0.7)
