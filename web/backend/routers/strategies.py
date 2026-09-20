"""Strategy configuration endpoints.

A strategy is addressed by its display name. Storage is one file per strategy,
keyed by filename stem, which is also what company configs reference — so the
`id` is returned alongside the name, and a rename changes the name only.

`/reset` is gone. It restored hardcoded Python defaults, and those were deleted
deliberately: they had drifted out of step with the JSON. `git checkout config/`
is the honest equivalent.
"""
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services.strategy_manager import get_strategy_manager

router = APIRouter(prefix="/strategies", tags=["strategies"])

HEX = r"^#[0-9A-Fa-f]{6}$"


class StrategySummary(BaseModel):
    id: str
    name: str
    description: str = ""
    color: str = "#888888"
    summary: Dict[str, Any]


class StrategyListResponse(BaseModel):
    strategies: list[StrategySummary]
    total: int


class StrategyResponse(BaseModel):
    id: str
    name: str
    description: str = ""
    color: str = "#888888"
    estimators: Dict[str, Any]
    calculators: Dict[str, Any]


class StrategyCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    description: str = Field(default="", max_length=200)
    color: str = Field(default="#888888", pattern=HEX)
    estimators: Dict[str, Any]
    calculators: Dict[str, Any]


class StrategyUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    description: Optional[str] = Field(default=None, max_length=200)
    color: Optional[str] = Field(default=None, pattern=HEX)
    estimators: Optional[Dict[str, Any]] = None
    calculators: Optional[Dict[str, Any]] = None


class StrategyCloneRequest(BaseModel):
    new_name: str = Field(min_length=1, max_length=50)


class MessageResponse(BaseModel):
    message: str


@router.get("", response_model=StrategyListResponse)
async def list_strategies():
    items = get_strategy_manager().list()
    return StrategyListResponse(strategies=items, total=len(items))


@router.get("/{name}", response_model=StrategyResponse)
async def get_strategy(name: str):
    strategy = get_strategy_manager().get(name)
    if strategy is None:
        raise HTTPException(status_code=404, detail=f"Strategy '{name}' not found")
    return strategy


@router.post("", response_model=StrategyResponse)
async def create_strategy(request: StrategyCreateRequest):
    return get_strategy_manager().create(request.model_dump())


@router.put("/{name}", response_model=StrategyResponse)
async def update_strategy(name: str, request: StrategyUpdateRequest):
    changes = request.model_dump(exclude_none=True)
    updated = get_strategy_manager().update(name, changes)
    if updated is None:
        raise HTTPException(status_code=404, detail=f"Strategy '{name}' not found")
    return updated


@router.delete("/{name}", response_model=MessageResponse)
async def delete_strategy(name: str):
    """Refused while any company still references this strategy."""
    manager = get_strategy_manager()
    if manager.get(name) is None:
        raise HTTPException(status_code=404, detail=f"Strategy '{name}' not found")
    manager.delete(name)
    return MessageResponse(message=f"Strategy '{name}' deleted")


@router.post("/{name}/clone", response_model=StrategyResponse)
async def clone_strategy(name: str, request: StrategyCloneRequest):
    cloned = get_strategy_manager().clone(name, request.new_name)
    if cloned is None:
        raise HTTPException(status_code=404, detail=f"Strategy '{name}' not found")
    return cloned


@router.post("/reload", response_model=MessageResponse)
async def reload_strategies():
    """Re-read the strategy directory from disk."""
    loaded = get_strategy_manager().reload()
    return MessageResponse(message=f"Reloaded {len(loaded)} strategies")
