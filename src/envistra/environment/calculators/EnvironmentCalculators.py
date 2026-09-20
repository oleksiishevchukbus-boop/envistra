class EnvironmentCalculators:
    def __init__(self, **kwargs):
        if "Revenue" not in kwargs:
            raise ValueError("RevenueCalculator must be provided for EnvironmentCalculators")
        else:
            self.Revenue = kwargs["Revenue"]

        if "Pollution" not in kwargs:
            raise ValueError("PollutionCalculator must be provided for EnvironmentCalculators")
        else:
            self.Pollution = kwargs["Pollution"]
