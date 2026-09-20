"""Environment regime endpoints.

`/reset` is gone, for the same reason as on strategies: the Python defaults it
restored were deleted deliberately, having drifted out of step with the JSON.

The loader now requires every key within a block, so a PUT that sends a partial
`quota_manager` is rejected rather than silently keeping stale values — which is
why the models below include `reward_pool_share` and `tightening_strength`, both
missing from the predecessor's.
"""
from typing import Any, Dict, List, Union

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..services.environment_manager import get_environment_manager

router = APIRouter(prefix="/environment", tags=["environment"])


class PenaltyTier(BaseModel):
    #: The last tier is the string "inf"; JSON has no infinity.
    until_step: Union[int, float, str]
    price: float = Field(ge=0)
    description: str


class RevenueCalculatorConfig(BaseModel):
    approach: str
    competition_influence: float = Field(ge=0, le=1)
    fin_eff_impact_multiplier: float = Field(gt=0)


class PollutionCalculatorConfig(BaseModel):
    approach: str
    env_eff_impact_multiplier: float = Field(gt=0)


class QuotaManagerConfig(BaseModel):
    approach: str
    quota_cap_decreaser: float = Field(gt=0, le=1)
    linear_reduction_factor: float = Field(ge=0, le=1)
    reward_pool_share: float = Field(ge=0, le=1)
    tightening_strength: float = Field(ge=0, le=1)
    penalty_tiers: List[PenaltyTier]


class EnvironmentConfigResponse(BaseModel):
    revenue_calculator: RevenueCalculatorConfig
    pollution_calculator: PollutionCalculatorConfig
    quota_manager: QuotaManagerConfig


class MessageResponse(BaseModel):
    message: str


@router.get("", response_model=EnvironmentConfigResponse)
async def get_environment():
    """The regime as stored on disk."""
    return get_environment_manager().get()


@router.put("", response_model=EnvironmentConfigResponse)
async def update_environment(changes: Dict[str, Any]):
    """Replace whole top-level blocks, then apply.

    Rejected documents leave both the file and the running configuration as they
    were: validation happens before anything is written or applied.
    """
    return get_environment_manager().update(changes)


@router.post("/reload", response_model=MessageResponse)
async def reload_environment():
    get_environment_manager().reload()
    return MessageResponse(message="Environment configuration reloaded")
