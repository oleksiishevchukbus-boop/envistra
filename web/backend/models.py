"""Pydantic models for API request/response schemas."""
from datetime import datetime
from enum import Enum
from typing import Dict, Optional
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
    #: The preview copy — see `formats` for every copy of this chart.
    filename: str
    path: str
    category: str
    #: False when the chart was written only as PDF, which a browser cannot
    #: embed as an image; the UI then offers it to open or download.
    previewable: bool = True
    #: Every format this chart was written in, extension -> URL.
    formats: Dict[str, str] = {}


class SimulationInfo(BaseModel):
    #: The folder name under results/ — `<name>_<date>_<time>`.
    run_id: str
    #: The folder name without its timestamp suffix; a rename replaces it.
    name: str = ""
    #: Listed first. Stored in the run's run_meta.json.
    favorite: bool = False
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


class SimulationUpdateRequest(BaseModel):
    #: Renames the run's folder, keeping its timestamp suffix.
    name: Optional[str] = Field(default=None, max_length=200)
    favorite: Optional[bool] = None


class SimulationListResponse(BaseModel):
    simulations: list[SimulationInfo]
    total: int
