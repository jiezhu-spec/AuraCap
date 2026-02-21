from __future__ import annotations

from fastapi import Depends, FastAPI

from backend.app.api.capture import router as capture_router
from backend.app.api.webhook import router as webhook_router
from backend.app.core.config import Settings, get_settings
from backend.app.core.logging import configure_logging
from backend.app.models.schemas import HealthResponse
from backend.app.services.scheduler import run_scheduled_tasks_once

configure_logging()
app = FastAPI(title="AuraCap Backend", version="0.1.0")

app.include_router(capture_router)
app.include_router(webhook_router)


@app.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(app=settings.app_name, status="ok")


@app.post("/v1/tasks/run-scheduled")
async def run_scheduled(settings: Settings = Depends(get_settings)) -> dict:
    return await run_scheduled_tasks_once(settings)


def run() -> None:
    import uvicorn

    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=False)
