"""Manages scanning and organizing simulation results."""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config import IMAGE_FORMAT, RESULTS_FOLDER
from ..models import ImageInfo, SimulationInfo, SimulationStatus, SimulationType


# Categories group the charts for the UI by matching on their titles, which
# are declared once in envistra.utilities.PlotSuite and used as filenames.
IMAGE_CATEGORIES = {
    "basics": {
        "label": "Basic Metrics",
        "patterns": ["Assets", "Expenses", "Expenses Reduction", "Revenue",
                     "Operational Net Revenue", "Net Revenue"]
    },
    "pollution": {
        "label": "Pollution",
        "patterns": ["Pollution", "Expected Pollution", "Pollution Difference"]
    },
    "quota": {
        "label": "Quota",
        "patterns": ["Quota", "Quota Share", "Base Quota Exceedance", "Quota Exceedance",
                     "Quota Exceedance Penalty"]
    },
    "quota_trade": {
        "label": "Quota Trading",
        "patterns": ["Quota to Trade Amount", "Quota Traded Amount",
                     "Quota Trade Revenue", "Quota Unit Price"]
    },
    "ratios": {
        "label": "Ratios",
        "patterns": ["Revenue To Expenses Ratio", "Pollution To Expenses Ratio"]
    },
    "efficiency": {
        "label": "Efficiency",
        "patterns": ["Financial Efficiency", "Ecological Efficiency",
                     "Financial Efficiency Investments", "Ecological Efficiency Investments"]
    }
}


def get_image_category(filename: str) -> str:
    """Determine the category of an image based on its filename."""
    name = filename.rsplit(".", 1)[0].replace("_", " ")

    for category, info in IMAGE_CATEGORIES.items():
        for pattern in info["patterns"]:
            if pattern.lower() in name.lower():
                return category

    return "other"


def parse_run_id_timestamp(run_id: str) -> Optional[datetime]:
    """Parse timestamp from run_id like 'StrategyComparison_2024-01-15_14-30-22'."""
    try:
        parts = run_id.rsplit("_", 2)
        if len(parts) >= 3:
            date_str = parts[-2]
            time_str = parts[-1]
            dt_str = f"{date_str}_{time_str}"
            return datetime.strptime(dt_str, "%Y-%m-%d_%H-%M-%S")
    except (ValueError, IndexError):
        pass

    # Fallback to folder modification time
    folder_path = RESULTS_FOLDER / run_id
    if folder_path.exists():
        return datetime.fromtimestamp(folder_path.stat().st_mtime)

    return datetime.now()


def get_simulation_type_from_run_id(run_id: str) -> SimulationType:
    """Determine simulation type from run_id prefix."""
    if run_id.startswith("StrategyComparison"):
        return SimulationType.STRATEGY_COMPARISON
    elif run_id.startswith("SingleAgent") or run_id.startswith("Main"):
        return SimulationType.SINGLE_AGENT
    return SimulationType.STRATEGY_COMPARISON


def scan_simulation_folder(folder_path: Path) -> SimulationInfo:
    """Scan a simulation folder and return its info."""
    run_id = folder_path.name

    # Get images
    images = []
    for img_file in folder_path.glob(f"*.{IMAGE_FORMAT}"):
        category = get_image_category(img_file.name)
        images.append(ImageInfo(
            name=img_file.stem.replace("_", " "),
            filename=img_file.name,
            path=f"/api/simulations/{run_id}/images/{img_file.name}",
            category=category
        ))

    # Sort images by category order
    category_order = list(IMAGE_CATEGORIES.keys()) + ["other"]
    images.sort(key=lambda x: (category_order.index(x.category) if x.category in category_order else 999, x.name))

    # Check for config and history files
    config_available = (folder_path / "run_config.json").exists()
    history_available = (folder_path / "model_history.csv").exists()

    # Try to read config for additional info
    steps = None
    execution_time = None
    if config_available:
        try:
            with open(folder_path / "run_config.json", "r") as f:
                config = json.load(f)
                steps = config.get("execution", {}).get("simulation_steps")
        except (json.JSONDecodeError, IOError):
            pass

    created_at = parse_run_id_timestamp(run_id)

    return SimulationInfo(
        run_id=run_id,
        status=SimulationStatus.COMPLETED,
        simulation_type=get_simulation_type_from_run_id(run_id),
        steps=steps,
        start_year=2010,
        created_at=created_at,
        completed_at=created_at,
        execution_time_seconds=execution_time,
        images=images,
        config_available=config_available,
        history_available=history_available
    )


def list_all_simulations() -> list[SimulationInfo]:
    """List all simulation runs from the results folder."""
    simulations = []

    if not RESULTS_FOLDER.exists():
        return simulations

    for folder in RESULTS_FOLDER.iterdir():
        if folder.is_dir() and not folder.name.startswith("."):
            try:
                sim_info = scan_simulation_folder(folder)
                simulations.append(sim_info)
            except Exception:
                # Skip folders that can't be parsed
                continue

    # Sort by creation date, newest first
    simulations.sort(key=lambda x: x.created_at, reverse=True)

    return simulations


def get_simulation(run_id: str) -> Optional[SimulationInfo]:
    """Get info for a specific simulation."""
    folder_path = RESULTS_FOLDER / run_id

    if not folder_path.exists() or not folder_path.is_dir():
        return None

    return scan_simulation_folder(folder_path)


def get_image_path(run_id: str, image_name: str) -> Optional[Path]:
    """Get the full path to an image file.

    `run_id` and `image_name` arrive from the URL, so the resolved path is
    checked to be inside the results folder before it is served.
    """
    try:
        folder = (RESULTS_FOLDER / run_id).resolve()
        image_path = (folder / image_name).resolve()
        image_path.relative_to(RESULTS_FOLDER.resolve())
    except (ValueError, OSError):
        return None

    return image_path if image_path.is_file() else None


def get_config_path(run_id: str) -> Optional[Path]:
    """Get the path to the run config JSON."""
    path = RESULTS_FOLDER / run_id / "run_config.json"
    return path if path.exists() else None


def get_history_path(run_id: str) -> Optional[Path]:
    """Get the path to the model history CSV."""
    path = RESULTS_FOLDER / run_id / "model_history.csv"
    return path if path.exists() else None


def delete_simulation(run_id: str) -> bool:
    """Delete a simulation folder."""
    import shutil

    folder_path = RESULTS_FOLDER / run_id

    if not folder_path.exists():
        return False

    try:
        shutil.rmtree(folder_path)
        return True
    except Exception:
        return False
