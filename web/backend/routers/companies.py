"""Company (agent) configuration endpoints.

New surface: the predecessor had no agent API, because the roster was a
hardcoded Python list. One file per company now means the number of files is the
number of agents, so creating and deleting here changes the simulation itself.

A company is addressed by its `name`, which is also the agent label in results
and plot legends.
"""
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services.company_manager import get_company_manager

router = APIRouter(prefix="/companies", tags=["companies"])

HEX = r"^#[0-9A-Fa-f]{6}$"


class CompanyParameters(BaseModel):
    finEffCoef: float = Field(ge=0)
    ecoEffCoef: float = Field(ge=0)
    finEffInvest: float = Field(ge=0)
    ecoEffInvest: float = Field(ge=0)


class CompanyResponse(BaseModel):
    id: str
    name: str
    dataSource: str
    strategy: str
    strategyName: Optional[str] = None
    enabled: bool = True
    plot: bool = True
    #: As stored: null means "assign one".
    color: Optional[str] = None
    #: What the company is actually drawn in, after assignment.
    effectiveColor: Optional[str] = None
    parameters: Dict[str, Any]


class CompanyListResponse(BaseModel):
    companies: list[CompanyResponse]
    total: int
    enabled: int
    plotted: int


class CompanyCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    #: Must match a workbook filename (without .xlsx). Not checked here — the data may not
    #: be present — so a mismatch surfaces when a simulation next runs.
    dataSource: str = Field(min_length=1)
    strategy: str = Field(min_length=1, description="Strategy filename id, e.g. 'business'")
    parameters: CompanyParameters
    enabled: bool = True
    plot: bool = True
    color: Optional[str] = Field(default=None, pattern=HEX)


class CompanyUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=80)
    dataSource: Optional[str] = Field(default=None, min_length=1)
    strategy: Optional[str] = None
    parameters: Optional[CompanyParameters] = None
    enabled: Optional[bool] = None
    plot: Optional[bool] = None
    color: Optional[str] = Field(default=None, pattern=HEX)


class MessageResponse(BaseModel):
    message: str


@router.get("", response_model=CompanyListResponse)
async def list_companies():
    items = get_company_manager().list()
    return CompanyListResponse(
        companies=items,
        total=len(items),
        enabled=sum(1 for c in items if c["enabled"]),
        plotted=sum(1 for c in items if c["plot"]),
    )


@router.get("/{name}", response_model=CompanyResponse)
async def get_company(name: str):
    company = get_company_manager().get(name)
    if company is None:
        raise HTTPException(status_code=404, detail=f"Company '{name}' not found")
    return company


@router.post("", response_model=CompanyResponse)
async def create_company(request: CompanyCreateRequest):
    """Add an agent. The simulation gains a participant on the next run."""
    return get_company_manager().create(request.model_dump(exclude_none=True))


@router.put("/{name}", response_model=CompanyResponse)
async def update_company(name: str, request: CompanyUpdateRequest):
    """Merge changes. `enabled` changes the market; `plot` changes only charts."""
    changes = request.model_dump(exclude_none=True)
    updated = get_company_manager().update(name, changes)
    if updated is None:
        raise HTTPException(status_code=404, detail=f"Company '{name}' not found")
    return updated


@router.delete("/{name}", response_model=MessageResponse)
async def delete_company(name: str):
    """Refused if it would leave no enabled company."""
    manager = get_company_manager()
    if manager.get(name) is None:
        raise HTTPException(status_code=404, detail=f"Company '{name}' not found")
    manager.delete(name)
    return MessageResponse(message=f"Company '{name}' deleted")


@router.post("/reload", response_model=MessageResponse)
async def reload_companies():
    loaded = get_company_manager().reload()
    return MessageResponse(message=f"Reloaded {len(loaded)} companies")
