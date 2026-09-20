class RevenueCalculatorConfig:
    # Approach determines how revenue is calculated for agents
    # "industry_based": Revenue based on industry averages
    # "competitive_industry_based": Revenue affected by competition within industry
    Approach = "competitive_industry_based"

    # How much competition affects revenue (0.0 = no effect, 1.0 = fully competitive)
    # At 0.2, competition has a moderate influence on agent revenue outcomes
    CompetitionInfluence = 0.2

    # Multiplier for financial efficiency impact on revenue
    # Higher values mean financial efficiency improvements yield more revenue benefit
    FinEffImpactMultiplier = 1.2


class PollutionCalculatorConfig:
    # Approach determines how pollution is calculated for agents
    # "industry_based": Pollution based on industry averages
    # "company_based": Pollution based on individual company historical ratios
    Approach = "company_based"

    # Multiplier for ecological efficiency impact on pollution reduction
    # At 1.0, eco-efficiency investments directly reduce pollution proportionally
    EnvEffImpactMultiplier = 1.0


class QuotaManagerConfig:
    # "expenses_based", "historical_pollution_based", "improvement_rewarding", "grandfathered_with_tightening"
    Approach = "historical_pollution_based"

    # Annual quota cap reduction rate (10% decrease per year simulating tightening regulations)
    # A value of 0.9 means the quota cap is multiplied by 0.9 each year
    QuotaCapDecreaser = 0.935

    # Linear reduction factor per step (1.25% reduction, based on EU ETS Phase 4 targets)
    # This represents the annual linear reduction in the total quota cap
    LinearReductionFactor = 0.0125

    # Share of industry cap allocated to reward pool (improvement_rewarding approach)
    # 0.0 = all equal, 1.0 = all reward-based
    RewardPoolShare = 0.3

    # Strength of intensity-based tightening (grandfathered_with_tightening approach)
    # 0.0 = no adjustment, 1.0 = full intensity adjustment
    TighteningStrength = 0.5

    # Penalty tiers configuration (escalating penalties encourage early compliance)
    # Structure: {"until_step": threshold, "price": penalty per unit, "description": rationale}
    PENALTY_TIERS = [
        {"until_step": 3, "price": 1.25, "description": "Grace period - low penalty to allow adjustment"},
        {"until_step": 8, "price": 2.5, "description": "Transition period - medium penalty"},
        {"until_step": float('inf'), "price": 5.0, "description": "Full enforcement - high penalty"},
    ]

    @staticmethod
    def GetQuotaPenaltyUnitPrice(step):
        """Get the penalty price per unit of quota exceedance based on simulation step.

        Penalties escalate over time to simulate increasing regulatory strictness:
        - Steps 0-2: Grace period (1.25 per unit)
        - Steps 3-7: Transition period (2.5 per unit)
        - Steps 8+: Full enforcement (5.0 per unit)
        """
        for tier in QuotaManagerConfig.PENALTY_TIERS:
            if step < tier["until_step"]:
                return tier["price"]
        return QuotaManagerConfig.PENALTY_TIERS[-1]["price"]


class EnvironmentConfig:
    RevenueCalculator = RevenueCalculatorConfig()
    PollutionCalculator = PollutionCalculatorConfig()
    QuotaManager = QuotaManagerConfig()
