from sklearn.neural_network import MLPRegressor


class PollutionEstimatorConfig:
    """Pollution estimator configuration, including the MLP hyperparameters.

    The MLPRegressor itself is not configuration — it is an object, and it
    cannot be represented in JSON. Only its hyperparameters are configurable;
    the model is constructed from them here.

    The instance built here is a prototype. Each agent receives a deep copy at
    entity-construction time and trains that, so this one is never fitted.
    """

    # 5 million iterations ensures convergence for small datasets (10 years x 15 companies)
    MAX_ITER = 5_000_000

    # - Two hidden layers (50, 25): Balance expressiveness vs overfitting for small data
    # - LBFGS solver: Quasi-Newton method, performs well for small datasets
    # - Identity activation: Linear activation for pollution regression (linear relationships)
    # - Adaptive learning rate: Adjusts automatically for better convergence
    # - Random state 42: Ensures reproducibility across runs
    DEFAULT_MLP_CONFIG = {
        "hidden_layer_sizes": (50, 25),
        "solver": "lbfgs",
        "activation": "identity",
        "learning_rate": "adaptive",
        "learning_rate_init": 0.1,
        "random_state": 42,
        "max_iter": MAX_ITER,
    }

    def __init__(self, **kwargs):
        if "approach" not in kwargs:
            raise ValueError("approach is required for PollutionEstimatorConfig")

        self.approach = kwargs["approach"]

        # Hyperparameters, as given in JSON, over the defaults above.
        self.mlp = dict(self.DEFAULT_MLP_CONFIG)
        self.mlp.update(kwargs.get("mlp") or {})

        # JSON has no tuples; sklearn accepts either, but keep the type stable
        # so a config comparison does not report a spurious difference.
        if isinstance(self.mlp.get("hidden_layer_sizes"), list):
            self.mlp["hidden_layer_sizes"] = tuple(self.mlp["hidden_layer_sizes"])

        self.MlpModel = kwargs.get("MlpModel") or MLPRegressor(**self.mlp, warm_start=True)
