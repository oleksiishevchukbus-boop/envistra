"""The data sources available — one per workbook filename, what a `dataSource` may name.

A top-level path rather than `/companies/data-sources`, which `/companies/{name}`
would shadow. Read on every request: the workbooks are small, and a newly added
one then appears without a restart.
"""
from fastapi import APIRouter
from pydantic import BaseModel

from envistra.utilities.DataReader import ListDataSources

router = APIRouter(prefix="/data-sources", tags=["data-sources"])


class DataSource(BaseModel):
    name: str
    #: The workbook's top-level folder under data/.
    industry: str
    #: Workbooks with this filename, relative to the data folder. More than one
    #: (same filename, different folders) is a conflict: no simulation starts.
    files: list[str]


class DataSourceListResponse(BaseModel):
    #: Empty when no workbooks are present; the data is not tracked.
    dataSources: list[DataSource]
    total: int
    #: How many filenames occur in more than one folder.
    conflicts: int


@router.get("", response_model=DataSourceListResponse)
async def list_data_sources():
    sources = ListDataSources()
    return DataSourceListResponse(
        dataSources=sources,
        total=len(sources),
        conflicts=sum(1 for s in sources if len(s["files"]) > 1),
    )
