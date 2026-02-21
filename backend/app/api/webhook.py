from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request

from backend.app.core.config import Settings, get_settings
from backend.app.core.security import signature_header, verify_signature
from backend.app.models.schemas import CaptureDispatchRequest, CaptureRequest, ProcessResult, TransportMode
from backend.app.services.media import fetch_remote_payload
from backend.app.services.pipeline import PipelineService

router = APIRouter(prefix="/v1/webhook", tags=["webhook"])


@router.post("/dispatch", response_model=ProcessResult)
async def ingest_dispatch(
    payload: CaptureDispatchRequest,
    request: Request,
    signature: str | None = Depends(signature_header),
    settings: Settings = Depends(get_settings),
) -> ProcessResult:
    verify_signature(settings, await request.body(), signature)

    if payload.transport_mode != TransportMode.REMOTE_URL:
        raise HTTPException(status_code=400, detail="dispatch only supports remote_url")

    try:
        content = await fetch_remote_payload(payload.payload_ref, settings.provider_timeout_seconds)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"failed to download payload_ref: {exc}") from exc

    capture_request = CaptureRequest(
        source=payload.source,
        media_type=payload.media_type,
        transport_mode=payload.transport_mode,
        mime_type=payload.mime_type,
        payload_ref=payload.payload_ref,
        payload_bytes=content,
        locale=payload.locale,
        timezone=payload.timezone,
        captured_at=payload.captured_at or datetime.now().astimezone(),
        metadata=payload.metadata,
    )

    service = PipelineService(settings)
    return await service.process_capture(capture_request)
