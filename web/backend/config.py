"""Backend configuration.

Output settings come from `config/simulation.json` rather than being hardcoded,
so the backend serves whatever the simulation actually writes.
"""
from pathlib import Path

from envistra.config import Loader

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

_plots = Loader.load_simulation()["plots"]

#: Where runs are written. Relative paths resolve against the repository root,
#: so the backend finds the same folder a CLI run does.
RESULTS_FOLDER = Path(_plots["resultsFolder"])
if not RESULTS_FOLDER.is_absolute():
    RESULTS_FOLDER = PROJECT_ROOT / RESULTS_FOLDER
RESULTS_FOLDER.mkdir(parents=True, exist_ok=True)

#: Every chart format a run may write, by extension. The format is a setting the
#: UI can change between runs, so results are listed and served by each file's
#: own extension rather than by one format fixed at startup.
IMAGE_MEDIA_TYPES = {
    "jpg": "image/jpeg",
    "png": "image/png",
    "svg": "image/svg+xml",
    "pdf": "application/pdf",
}

API_PREFIX = "/api"
CORS_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
