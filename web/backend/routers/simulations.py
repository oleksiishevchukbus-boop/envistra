"""REST API endpoints for simulations."""
import asyncio
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse

from ..models import (
    SimulationCreateRequest,
    SimulationCreateResponse,
    SimulationInfo,
    SimulationListResponse,
    SimulationStatus,
)
from ..config import IMAGE_MEDIA_TYPES
from ..services import results_manager

router = APIRouter(prefix="/simulations", tags=["simulations"])

# Track running simulations
running_simulations: dict[str, dict] = {}


@router.post("", response_model=SimulationCreateResponse)
async def create_simulation(
    request: SimulationCreateRequest,
    background_tasks: BackgroundTasks
):
    """Start a new simulation."""
    from .websocket import run_simulation_with_progress

    # Generate run_id based on timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_id = f"StrategyComparison_{timestamp}"

    # Track the simulation
    running_simulations[run_id] = {
        "status": SimulationStatus.RUNNING,
        "steps": request.steps,
        "started_at": datetime.now()
    }

    # Start simulation in background
    background_tasks.add_task(run_simulation_with_progress, run_id,
                              request.steps, request.seed)

    return SimulationCreateResponse(
        run_id=run_id,
        status=SimulationStatus.RUNNING,
        websocket_url=f"/ws/simulations/{run_id}"
    )


@router.get("", response_model=SimulationListResponse)
async def list_simulations():
    """List all simulation runs."""
    simulations = results_manager.list_all_simulations()
    return SimulationListResponse(
        simulations=simulations,
        total=len(simulations)
    )


@router.get("/{run_id}", response_model=SimulationInfo)
async def get_simulation(run_id: str):
    """Get details for a specific simulation."""
    sim_info = results_manager.get_simulation(run_id)

    if not sim_info:
        raise HTTPException(status_code=404, detail=f"Simulation '{run_id}' not found")

    return sim_info


@router.delete("/{run_id}")
async def delete_simulation(run_id: str):
    """Delete a simulation run."""
    if not results_manager.delete_simulation(run_id):
        raise HTTPException(status_code=404, detail=f"Simulation '{run_id}' not found or could not be deleted")

    return {"message": f"Simulation '{run_id}' deleted successfully"}


@router.get("/{run_id}/images/{image_name}")
async def get_image(run_id: str, image_name: str):
    """Get a specific image from a simulation."""
    image_path = results_manager.get_image_path(run_id, image_name)

    if not image_path:
        raise HTTPException(status_code=404, detail=f"Image '{image_name}' not found")

    media_type = IMAGE_MEDIA_TYPES.get(image_path.suffix[1:].lower(), "application/octet-stream")
    return FileResponse(image_path, media_type=media_type)


@router.get("/{run_id}/config")
async def get_config(run_id: str):
    """Get the run configuration JSON."""
    config_path = results_manager.get_config_path(run_id)

    if not config_path:
        raise HTTPException(status_code=404, detail="Configuration not found")

    return FileResponse(config_path, media_type="application/json")


@router.get("/{run_id}/history")
async def get_history(run_id: str):
    """Get the model history CSV."""
    history_path = results_manager.get_history_path(run_id)

    if not history_path:
        raise HTTPException(status_code=404, detail="History not found")

    return FileResponse(
        history_path,
        media_type="text/csv",
        filename=f"{run_id}_history.csv"
    )
