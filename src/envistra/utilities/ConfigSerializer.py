"""Builds the reproducibility record written beside each run's results.

`run_config.json` captures everything that determined a run: the global scaling
constants, the environment regime, and every company's full resolved
configuration. It is written, never read back.
"""
from datetime import datetime

from envistra.config.GlobalConfig import GlobalConfig
from envistra.config.environment.EnvironmentConfig import (
    PollutionCalculatorConfig,
    QuotaManagerConfig,
    RevenueCalculatorConfig,
)


def serialize_expenses_estimator_config(config) -> dict:
    return {
        "approach": config.approach,
        "changeThreshold_Upper": config.changeThreshold_Upper,
        "changeThreshold_Lower": config.changeThreshold_Lower,
        # The predecessor omitted smoothingAlpha although the estimator consumes
        # it, so the record did not describe the run.
        "smoothingAlpha": config.smoothingAlpha,
        "featuresImpact": config.featuresImpact,
    }


def serialize_investment_estimator_config(config) -> dict:
    return {
        "approach": config.approach,
        "investmentRatios": config.investmentRatios,
        "smoothingAlpha": config.smoothingAlpha,
        "baseQuotaPrice": config.baseQuotaPrice,
        "adaptiveBlendRatio": config.adaptiveBlendRatio,
    }


def serialize_pollution_estimator_config(config) -> dict:
    """The MLPRegressor is not serialisable; its hyperparameters are.

    Reads the instance's resolved `mlp` dict, so a strategy that overrides a
    hyperparameter is recorded with the override. The predecessor read the class
    defaults, which silently discarded any override.
    """
    mlp = dict(config.mlp)
    mlp["hidden_layer_sizes"] = list(mlp["hidden_layer_sizes"])
    return {"approach": config.approach, "mlp": mlp}


def serialize_expenses_re_estimation_config(config) -> dict:
    return {
        "approach": config.approach,
        "maxReductionRate": config.maxReductionRate,
        "profitMargin": config.profitMargin,
        "maxReductionCap": config.maxReductionCap,
        "baseRate": config.baseRate,
        "trendSensitivity": config.trendSensitivity,
    }


def serialize_quota_amount_config(config) -> dict:
    return {"approach": config.approach, "quotaReserve": config.quotaReserve}


def serialize_quota_to_buy_price_config(config) -> dict:
    return {"approach": config.approach, "assetsPartForTrading": config.assetsPartForTrading}


def serialize_quota_to_sell_price_config(config) -> dict:
    return {
        "approach": config.approach,
        "unitPrice": config.unitPrice,
        "changeThreshold": config.changeThreshold,
        "salesTarget": config.salesTarget,
    }


def serialize_company_config(company) -> dict:
    """One company's fully resolved configuration.

    `strategy` is recorded from the company's own config. The predecessor could
    not do this — its entity discarded the strategy — so it guessed the name back
    from approach values and an investment-ratio threshold, returning "Unknown"
    for anything beyond the original four strategies.
    """
    return {
        "name": company.name,
        "dataSource": company.dataSource,
        "strategy": {"id": company.strategyId, "name": company.strategyName},
        "color": company.color,
        "efficiency_params": {
            "finEffInvest": company.finEffInvest,
            "ecoEffInvest": company.ecoEffInvest,
            "finEffCoef": company.finEffCoef,
            "ecoEffCoef": company.ecoEffCoef,
        },
        "estimators": {
            "expenses": serialize_expenses_estimator_config(company.ExpensesEstimatorConfig),
            "investment": serialize_investment_estimator_config(company.InvestmentEstimatorConfig),
            "pollution": serialize_pollution_estimator_config(company.PollutionEstimatorConfig),
            "expenses_re_estimation": serialize_expenses_re_estimation_config(
                company.ExpensesReEstimationConfig),
        },
        "calculators": {
            "quota_to_buy_amount": serialize_quota_amount_config(
                company.QuotaToBuyAmountCalculatorConfig),
            "quota_to_buy_price": serialize_quota_to_buy_price_config(
                company.QuotaToBuyPriceCalculatorConfig),
            "quota_to_sell_amount": serialize_quota_amount_config(
                company.QuotaToSellAmountCalculatorConfig),
            "quota_to_sell_price": serialize_quota_to_sell_price_config(
                company.QuotaToSellPriceCalculatorConfig),
        },
    }


def serialize_environment_config() -> dict:
    """The environment regime as it stood for this run."""
    penalty_tiers = [
        {
            # JSON has no infinity; the loader reads this sentinel back.
            "until_step": "inf" if tier["until_step"] == float("inf") else tier["until_step"],
            "price": tier["price"],
            "description": tier["description"],
        }
        for tier in QuotaManagerConfig.PENALTY_TIERS
    ]
    return {
        "revenue_calculator": {
            "approach": RevenueCalculatorConfig.Approach,
            "competition_influence": RevenueCalculatorConfig.CompetitionInfluence,
            "fin_eff_impact_multiplier": RevenueCalculatorConfig.FinEffImpactMultiplier,
        },
        "pollution_calculator": {
            "approach": PollutionCalculatorConfig.Approach,
            "env_eff_impact_multiplier": PollutionCalculatorConfig.EnvEffImpactMultiplier,
        },
        "quota_manager": {
            "approach": QuotaManagerConfig.Approach,
            "quota_cap_decreaser": QuotaManagerConfig.QuotaCapDecreaser,
            "linear_reduction_factor": QuotaManagerConfig.LinearReductionFactor,
            "reward_pool_share": QuotaManagerConfig.RewardPoolShare,
            "tightening_strength": QuotaManagerConfig.TighteningStrength,
            "penalty_tiers": penalty_tiers,
        },
    }


def serialize_global_config() -> dict:
    return {
        "money_value_multiplier": GlobalConfig.Startup.MoneyValueMultiplier,
        "efficiency_value_multiplier": GlobalConfig.Startup.EfficiencyValueMultiplier,
        "start_year": GlobalConfig.Startup.Year,
        "data_folder": GlobalConfig.DataFolder,
    }


def build_run_metadata(companies, simulation_steps, start_year=None, mlp_metrics=None,
                       seed=None) -> dict:
    """Assemble the full record for one run.

    Takes the company entities directly. The predecessor took a roster and looked
    each name up in a separate config dict, silently dropping any it could not
    find — so `agent_count` could exceed the number of agents actually recorded.
    """
    start_year = GlobalConfig.Startup.Year if start_year is None else start_year
    metadata = {
        "execution": {
            "timestamp": datetime.now().isoformat(),
            "simulation_steps": simulation_steps,
            "start_year": start_year,
            "end_year": start_year + simulation_steps - 1,
            "agent_count": len(companies),
            # None means the run was not reproducible: Mesa's shuffled buy order
            # and RevenueCalculator's Gaussian both ran unseeded.
            "seed": seed,
        },
        "global_config": serialize_global_config(),
        "environment_config": serialize_environment_config(),
        "agents": {c.name: serialize_company_config(c) for c in companies},
    }

    if mlp_metrics:
        metadata["mlp_metrics"] = {
            "per_agent": mlp_metrics,
            "aggregate": _compute_aggregate_metrics(mlp_metrics),
        }
    return metadata


def _compute_aggregate_metrics(mlp_metrics: dict) -> dict:
    if not mlp_metrics:
        return {}

    def spread(key):
        values = [m[key] for m in mlp_metrics.values()]
        return {"mean": sum(values) / len(values), "min": min(values), "max": max(values)}

    return {"r2": spread("r2"), "mae": spread("mae"), "rmse": spread("rmse")}
