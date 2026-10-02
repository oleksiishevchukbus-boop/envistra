"""Manages scanning and organizing simulation results."""
import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from envistra.utilities.PlotBuilder import PREVIEW_ORDER, slugify

from ..config import IMAGE_MEDIA_TYPES, RESULTS_FOLDER
from ..models import ImageInfo, SimulationInfo, SimulationStatus, SimulationType


#: Present in a run folder while the runner is still writing into it. Such a
#: run cannot be renamed or deleted.
IN_PROGRESS_MARKER = ".in_progress"

#: Per-run UI state that is not part of the reproducibility record, which
#: stays in run_config.json untouched. Moves with the folder on rename.
META_FILE = "run_meta.json"

MAX_NAME_LENGTH = 80

_URL_UNSAFE = re.compile(r"[#%&+;]")


class RunNotFound(Exception):
    pass


class RunConflict(Exception):
    """The run is in progress, or a rename target already exists."""


class InvalidRunName(Exception):
    pass


def _run_folder(run_id: str) -> Optional[Path]:
    """The run's folder, or None. `run_id` comes from the URL, so anything that
    does not resolve to a direct child of the results folder is refused."""
    try:
        root = RESULTS_FOLDER.resolve()
        folder = (RESULTS_FOLDER / run_id).resolve()
    except OSError:
        return None
    if folder.parent != root or not folder.is_dir():
        return None
    return folder


def split_run_id(run_id: str) -> tuple[str, str]:
    """`("AES test", "_2026-10-03_00-31-14")` from `AES test_2026-10-03_00-31-14`.

    A run folder is `<name>_<date>_<time>`. The name is what the UI shows and
    what a rename replaces; the timestamp suffix is kept, so folder names stay
    unique and the run's date survives. A folder without one is all name.
    """
    parts = run_id.rsplit("_", 2)
    if len(parts) == 3:
        try:
            datetime.strptime(f"{parts[1]}_{parts[2]}", "%Y-%m-%d_%H-%M-%S")
            return parts[0], f"_{parts[1]}_{parts[2]}"
        except ValueError:
            pass
    return run_id, ""


def _read_meta(folder: Path) -> dict:
    try:
        with open(folder / META_FILE, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _write_meta(folder: Path, meta: dict) -> None:
    tmp = folder / (META_FILE + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
    os.replace(tmp, folder / META_FILE)


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

    # One entry per chart, whatever formats it was written in: a run may save
    # each chart several times (png + pdf, say), and the format setting may
    # differ between runs. The entry previews the best browser-viewable copy
    # and links every copy for download.
    by_chart = {}
    for f in folder_path.iterdir():
        ext = f.suffix[1:].lower()
        if f.is_file() and ext in IMAGE_MEDIA_TYPES:
            by_chart.setdefault(f.stem, {})[ext] = f.name

    images = []
    for stem, files in by_chart.items():
        preview_ext = next(e for e in PREVIEW_ORDER if e in files)
        preview = files[preview_ext]
        images.append(ImageInfo(
            name=stem.replace("_", " "),
            filename=preview,
            path=f"/api/simulations/{run_id}/images/{preview}",
            category=get_image_category(preview),
            previewable=preview_ext != "pdf",
            formats={ext: f"/api/simulations/{run_id}/images/{name}"
                     for ext, name in sorted(files.items(), key=lambda kv: PREVIEW_ORDER.index(kv[0]))},
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
    in_progress = (folder_path / IN_PROGRESS_MARKER).exists()

    return SimulationInfo(
        run_id=run_id,
        name=split_run_id(run_id)[0],
        favorite=bool(_read_meta(folder_path).get("favorite", False)),
        status=SimulationStatus.RUNNING if in_progress else SimulationStatus.COMPLETED,
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

    # Favourites first, then newest first within each group.
    simulations.sort(key=lambda x: x.created_at, reverse=True)
    simulations.sort(key=lambda x: not x.favorite)

    return simulations


def get_simulation(run_id: str) -> Optional[SimulationInfo]:
    """Get info for a specific simulation."""
    folder_path = _run_folder(run_id)
    return scan_simulation_folder(folder_path) if folder_path else None


def get_image_path(run_id: str, image_name: str) -> Optional[Path]:
    """Get the full path to an image file.

    `run_id` and `image_name` arrive from the URL, so the resolved path is
    checked to be inside the results folder before it is served.
    """
    folder = _run_folder(run_id)
    if folder is None:
        return None
    try:
        image_path = (folder / image_name).resolve()
        image_path.relative_to(folder)
    except (ValueError, OSError):
        return None

    return image_path if image_path.is_file() else None


def get_config_path(run_id: str) -> Optional[Path]:
    """Get the path to the run config JSON."""
    folder = _run_folder(run_id)
    path = folder / "run_config.json" if folder else None
    return path if path and path.exists() else None


def get_history_path(run_id: str) -> Optional[Path]:
    """Get the path to the model history CSV."""
    folder = _run_folder(run_id)
    path = folder / "model_history.csv" if folder else None
    return path if path and path.exists() else None


def delete_simulation(run_id: str) -> None:
    """Delete a run's folder. Refused while the run is still being written."""
    folder = _run_folder(run_id)
    if folder is None:
        raise RunNotFound(run_id)
    if (folder / IN_PROGRESS_MARKER).exists():
        raise RunConflict("this run is still in progress")
    try:
        shutil.rmtree(folder)
    except OSError as exc:
        raise RunConflict(f"could not delete the folder — is a file in it open? ({exc})")


def update_simulation(run_id: str, name: Optional[str] = None,
                      favorite: Optional[bool] = None) -> SimulationInfo:
    """Set the favourite flag and/or rename the run, folder included.

    A rename keeps the timestamp suffix: `AES test_2026-10-03_00-31-14`. The
    name goes through the same Windows-safe slug as chart filenames. Returns the
    run as it is afterwards — its `run_id` is new if it was renamed.
    """
    folder = _run_folder(run_id)
    if folder is None:
        raise RunNotFound(run_id)
    if (folder / IN_PROGRESS_MARKER).exists():
        raise RunConflict("this run is still in progress")

    target = folder
    if name is not None:
        # Windows-safe like chart filenames, and URL-safe too: the folder name
        # is the run's id in every /api/simulations/<id>/... address.
        cleaned = _URL_UNSAFE.sub("-", slugify(name.strip()))
        if not any(ch.isalnum() for ch in name):
            raise InvalidRunName("a run name needs at least one letter or digit")
        if len(cleaned) > MAX_NAME_LENGTH:
            raise InvalidRunName(f"a run name is at most {MAX_NAME_LENGTH} characters")
        target = folder.parent / (cleaned + split_run_id(folder.name)[1])

    if favorite is not None:
        _write_meta(folder, {**_read_meta(folder), "favorite": favorite})

    if target != folder:
        if target.exists():
            raise RunConflict(f"a run named '{target.name}' already exists")
        try:
            folder.rename(target)
        except OSError as exc:
            raise RunConflict(f"could not rename the folder — is a file in it open? ({exc})")

    return scan_simulation_folder(target)
