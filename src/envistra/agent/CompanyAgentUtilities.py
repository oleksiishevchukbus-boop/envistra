import numpy as np
from envistra.config.GlobalConfig import GlobalConfig


class CompanyAgentUtilities:
    @staticmethod
    def FinEffCalc(finEffCoef, finEffInvest):
        mult = GlobalConfig.Startup.EfficiencyValueMultiplier * finEffCoef * finEffInvest
        divider = np.exp(mult)
        return 1-1/divider

    @staticmethod
    def EcoEffCalc(ecoEffCoef, ecoEffInvest):
        mult = GlobalConfig.Startup.EfficiencyValueMultiplier * ecoEffCoef * ecoEffInvest
        divider = np.exp(mult)
        return 1-1/divider
