from __future__ import annotations

import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from backend.app.core.config import Settings, get_settings
from backend.app.core.security import signature_header, verify_signature
from backend.app.models.schemas import CaptureJSONRequest, MediaType, ProcessResult, SourceType
from backend.app.services.media import build_from_json, build_from_upload
from backend.app.services.pipeline import PipelineService

router = APIRouter(prefix="/v1/capture", tags=["capture"])


@router.post("/json", response_model=ProcessResult)
async def ingest_base64_json(
    payload: CaptureJSONRequest,
    request: Request,
    signature: str | None = Depends(signature_header),
    settings: Settings = Depends(get_settings),
) -> ProcessResult:
    verify_signature(settings, await request.body(), signature)
    try:
        capture_request = build_from_json(
            source=payload.source,
            media_type=payload.media_type,
            mime_type=payload.mime_type,
            media_base64=payload.media_base64,
            locale=payload.locale,
            timezone=payload.timezone,
            captured_at=payload.captured_at,
            metadata=payload.metadata,
            settings=settings,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    service = PipelineService(settings)
    return await service.process_capture(capture_request)


@router.post("/upload", response_model=ProcessResult)
async def ingest_upload(
    request: Request,
    file: UploadFile = File(...),
    media_type: MediaType = Form(...),
    source: SourceType = Form(default=SourceType.IOS_SHORTCUT),
    locale: str = Form(default="zh-CN"),
    timezone: str = Form(default="local"),
    metadata_json: str = Form(default="{}"),
    signature: str | None = Depends(signature_header),
    settings: Settings = Depends(get_settings),
) -> ProcessResult:
    verify_signature(settings, await request.body(), signature)
    try:
        metadata = json.loads(metadata_json or "{}")
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid metadata_json") from exc

    payload_bytes = await file.read()
    try:
        capture_request = build_from_upload(
            source=source,
            media_type=media_type,
            mime_type=file.content_type or "application/octet-stream",
            payload_bytes=payload_bytes,
            locale=locale,
            timezone=timezone,
            captured_at=None,
            metadata=metadata,
            settings=settings,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    service = PipelineService(settings)
    return await service.process_capture(capture_request)


@router.post("/raw", response_model=ProcessResult)
async def ingest_raw(
    request: Request,
    media_type: MediaType,
    source: SourceType = SourceType.IOS_SHORTCUT,
    locale: str = "zh-CN",
    timezone: str = "local",
    mime_type: str | None = None,
    signature: str | None = Depends(signature_header),
    settings: Settings = Depends(get_settings),
) -> ProcessResult:
    raw = await request.body()
    verify_signature(settings, raw, signature)
    if not raw:
        raise HTTPException(status_code=400, detail="Empty request body")

    try:
        capture_request = build_from_upload(
            source=source,
            media_type=media_type,
            mime_type=(mime_type or request.headers.get("content-type", "application/octet-stream").split(";")[0]),
            payload_bytes=raw,
            locale=locale,
            timezone=timezone,
            captured_at=None,
            metadata={},
            settings=settings,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    service = PipelineService(settings)
    return await service.process_capture(capture_request)
