"""The environment regime: revenue, pollution and quota-allocation settings.

**These classes hold no values.** `Loader.load_environment()` assigns every
attribute from `config/environment.json`, which is the only source. Reading one
beforehand raises `ConfigNotLoadedError` rather than returning a stale number.

That is the point of the design. The predecessor kept Python literals here
alongside the JSON, nominally as fallbacks; they drifted out of step with the
file (`CompetitionInfluence` was 0.2 here and 0.1 in the JSON), so a code path
that forgot to load config ran the model on different numbers without saying so.

The classes stay module-level singletons because the simulation reads them live
on every step — the quota manager and both environment calculators consult them
inside the step loop, so a value changed between runs in one process takes
effect immediately.
"""
from envistra.config.Errors import ConfigNotLoadedError


class _RequiresLoad(type):
    """Makes reading an unset setting fail loudly, and say what to do about it.

    `__getattr__` runs only when normal lookup fails, so once
    `load_environment()` has assigned the attributes this is never consulted.
    """

    def __getattr__(cls, name):
        # Dunder probes (copy, pickle, inspect) must keep getting AttributeError.
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(name)
        raise ConfigNotLoadedError(cls.__name__, name)


class RevenueCalculatorConfig(metaclass=_RequiresLoad):
    """Set from `environment.json` -> `revenue_calculator`.

    Approach
        "industry_based" — revenue from industry averages.
        "competitive_industry_based" — revenue also affected by competitors'
        financial efficiency within the industry.
    CompetitionInfluence
        How strongly competition moves revenue, 0.0 (none) to 1.0 (fully).
    FinEffImpactMultiplier
        How much financial-efficiency investment converts into revenue.
    """


class PollutionCalculatorConfig(metaclass=_RequiresLoad):
    """Set from `environment.json` -> `pollution_calculator`.

    Approach
        "industry_based" — pollution from the industry's mean intensity.
        "company_based" — pollution from the company's own historical ratio.
    EnvEffImpactMultiplier
        How much ecological-efficiency investment reduces pollution. At 1.0 the
        reduction is proportional to eco-efficiency.
    """


class QuotaManagerConfig(metaclass=_RequiresLoad):
    """Set from `environment.json` -> `quota_manager`.

    Approach
        "expenses_based", "historical_pollution_based", "improvement_rewarding"
        or "grandfathered_with_tightening".
    QuotaCapDecreaser
        Multiplicative annual tightening of the industry cap.
    LinearReductionFactor
        Per-step linear reduction of the cap, in the style of EU ETS Phase 4.
    RewardPoolShare
        Share of the industry cap held back for the reward pool under
        "improvement_rewarding". 0.0 allocates equally, 1.0 entirely by merit.
    TighteningStrength
        Strength of the intensity adjustment under
        "grandfathered_with_tightening". 0.0 applies none.
    PENALTY_TIERS
        Escalating price per unit of exceedance, as
        `{"until_step", "price", "description"}`, ascending, the last one
        open-ended. Escalation exists so that early non-compliance is cheap
        enough to adapt to and late non-compliance is not.
    """

    @staticmethod
    def GetQuotaPenaltyUnitPrice(step):
        """Penalty per unit of quota exceedance at this step.

        Returns the first tier the step falls below, which is why the loader
        requires the tiers to ascend.
        """
        for tier in QuotaManagerConfig.PENALTY_TIERS:
            if step < tier["until_step"]:
                return tier["price"]
        return QuotaManagerConfig.PENALTY_TIERS[-1]["price"]


class EnvironmentConfig:
    """Namespace the simulation reads through, e.g.
    `EnvironmentConfig.QuotaManager.LinearReductionFactor`.

    These are the classes themselves, not instances. The predecessor held
    instances whose attribute reads happened to fall through to the class; with
    the classes directly, every read goes through `_RequiresLoad`.
    """

    RevenueCalculator = RevenueCalculatorConfig
    PollutionCalculator = PollutionCalculatorConfig
    QuotaManager = QuotaManagerConfig
