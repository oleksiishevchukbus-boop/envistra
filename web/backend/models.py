"""Pydantic models for API request/response schemas."""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class SimulationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationType(str, Enum):
    STRATEGY_COMPARISON = "strategy_comparison"
    SINGLE_AGENT = "single_agent"


class SimulationCreateRequest(BaseModel):
    steps: int = Field(default=20, ge=1, le=50, description="Number of simulation steps")
    #: Pin the run so it can be reproduced. Omit for a fresh, unrepeatable run;
    #: run_config.json records whichever was used.
    seed: Optional[int] = Field(default=None, description="Random seed, for a reproducible run")


class SimulationCreateResponse(BaseModel):
    run_id: str
    status: SimulationStatus
    websocket_url: str


class ImageInfo(BaseModel):
    name: str
    filename: str
    path: str
    category: str


class SimulationInfo(BaseModel):
    run_id: str
    status: SimulationStatus
    simulation_type: SimulationType
    steps: Optional[int] = None
    start_year: int = 2010
    created_at: datetime
    completed_at: Optional[datetime] = None
    execution_time_seconds: Optional[float] = None
    images: list[ImageInfo] = []
    config_available: bool = False
    history_available: bool = False


class SimulationListResponse(BaseModel):
    simulations: list[SimulationInfo]
    total: int
