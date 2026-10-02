"""FastAPI application entry point."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import envistra
from envistra.config.Errors import ConfigError

from .config import API_PREFIX, CORS_ORIGINS
from .routers import (companies, data_sources, environment, settings, simulations, strategies,
                      websocket)

app = FastAPI(
    # Imported rather than re-typed, so the program's identity has one source.
    title=f"{envistra.SHORT_NAME} Web API",
    description=envistra.FULL_NAME_EN,
    version=envistra.__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ConfigError)
async def config_error_handler(request: Request, exc: ConfigError):
    """A rejected configuration is the caller's fault, not a server fault.

    The loader's messages name the file and field and suggest a correction, so
    they are worth passing through rather than collapsing into a 500.
    """
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "path": exc.path, "field": exc.field},
    )


app.include_router(simulations.router, prefix=API_PREFIX)
app.include_router(strategies.router, prefix=API_PREFIX)
app.include_router(companies.router, prefix=API_PREFIX)
app.include_router(data_sources.router, prefix=API_PREFIX)
app.include_router(environment.router, prefix=API_PREFIX)
app.include_router(settings.router, prefix=API_PREFIX)
app.include_router(websocket.router)


@app.get("/")
async def root():
    return {
        "name": f"{envistra.SHORT_NAME} Web API",
        "version": envistra.__version__,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
