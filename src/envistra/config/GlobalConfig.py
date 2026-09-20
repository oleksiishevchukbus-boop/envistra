"""Dataset calibration constants.

These are properties of the source data and of the model's unit system, not
settings tuned per run — which is why they stay in Python while the environment
regime, the strategies and the companies live in JSON under `config/`.

The agent roster used to live here too, as `StartupConfig.AgentList`. It is now
derived from the files in `config/companies/`, one per agent; see
`envistra.config.Loader`.
"""


class StartupConfig:
    #: Scales the workbooks' reporting-currency figures into model units.
    #: Applied to Pollution as well as the money columns — inherited behaviour.
    MoneyValueMultiplier = 10e-9

    #: Scales the efficiency exponent in FinEffCalc / EcoEffCalc.
    EfficiencyValueMultiplier = 8e-3

    #: The data year the simulation starts from. Every company must have a row
    #: for this year, or entity creation fails.
    Year = 2010


class GlobalConfig:
    #: Root of the workbook tree, relative to the process working directory,
    #: so the model must be run from the repository root.
    DataFolder = "data"

    Startup = StartupConfig()
