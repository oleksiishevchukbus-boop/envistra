"""Builds a ready-to-step model from the configuration and the data.

This replaces the predecessor's `Startup.py`, which re-exported some sixty
symbols so a runner could say `from utilities.Startup import *`. Callers here
import what they need explicitly; this module offers one function.
"""
import random

import numpy as np

from envistra.config import Loader
from envistra.model import CompanyAgentModel
from envistra.utilities.DataReader import DataReader


def initialize_model(config_path=None, seed=None):
    """Load configuration, read the data, and construct the model.

    Returns `(model, dataReader, companies, environmentCalculators)`.

    Configuration is loaded first because the data reader branches on
    `PollutionCalculator.Approach` while deciding how to key the pollution
    ratios — and reading that before the environment is loaded now raises.

    Pass `seed` to make a run reproducible. There are two independent sources of
    randomness and both must be pinned: Mesa's own RNG drives the shuffled buy
    order, and `RevenueCalculator` samples `random.gauss` from the `random`
    module. Seeding one and not the other looks deterministic and is not.
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    environment, strategies, companies, simulation = Loader.load_all(config_path)

    dataReader = DataReader(companies)
    dataReader.Read()
    dataReader.GetExpensesToAssetsRatio()
    dataReader.GetRevenueToExpensesDistributionParams()
    dataReader.GetPollutionToExpensesRatio()
    dataReader.PrepareStartingData()

    companyEntities = dataReader.CreateCompanyEntities()
    environmentCalculators = dataReader.CreateEnvironmentCalculators()

    model = CompanyAgentModel(companyEntities, seed=seed,
                              EnvironmentCalculators=environmentCalculators)
    model.simulationConfig = simulation
    return model, dataReader, companies, environmentCalculators
