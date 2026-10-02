"""Run-wide settings — `config/simulation.json`, currently chart output.

Every run re-reads the file, so a change applies to the next simulation without
a restart. The exception is `resultsFolder`: the backend fixes it at startup and
lists runs from it, so changing it here would hide every existing run. It is
returned but cannot be changed through the API.
"""
from typing import List, Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from envistra.config import Loader, Writer
from envistra.config.Errors import ConfigError

router = APIRouter(prefix="/settings", tags=["settings"])


class PlotSettings(BaseModel):
    #: Dots per inch: the image's resolution, and so its quality and file size.
    dpi: int = Field(ge=10, le=2400)
    #: [width, height] in inches.
    figsize: List[float] = Field(min_length=2, max_length=2)
    #: Every chart is saved once per format listed.
    format: List[Literal["jpg", "png", "svg", "pdf"]] = Field(min_length=1)
    #: Read-only through the API; see the module docstring.
    resultsFolder: str


class SettingsDocument(BaseModel):
    plots: PlotSettings


def _path():
    return Loader.config_dir() / "simulation.json"


def _stored():
    path = _path()
    return Loader._read(path) if path.is_file() else {}


def _effective():
    """The stored settings resolved over the defaults, as a run would see them."""
    plots = Loader.parse_simulation(_path(), _stored())["plots"]
    return {"plots": {**plots, "figsize": list(plots["figsize"])}}


@router.get("", response_model=SettingsDocument)
async def get_settings():
    return _effective()


@router.put("", response_model=SettingsDocument)
async def update_settings(request: SettingsDocument):
    """Replace the chart settings. Validated before anything is written."""
    plots = request.plots.model_dump()
    current = _effective()["plots"]["resultsFolder"]
    if plots["resultsFolder"] != current:
        raise ConfigError(_path(), "resultsFolder is fixed when the server starts — edit "
                                   "config/simulation.json and restart to change it",
                          field="plots.resultsFolder")

    document = {**_stored(), "plots": plots}
    Writer.save_simulation(document, _path())
    return _effective()
