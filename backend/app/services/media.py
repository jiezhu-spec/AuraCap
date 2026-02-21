from __future__ import annotations

import base64
from datetime import datetime

import httpx

from backend.app.core.config import Settings
from backend.app.models.schemas import CaptureRequest, MediaType, SourceType, TransportMode


def _strip_base64_prefix(raw: str) -> str:
    if "," in raw and raw.strip().startswith("data:"):
        return raw.split(",", 1)[1]
    return raw


def _validate_mime(media_type: MediaType, mime_type: str, settings: Settings) -> None:
    image_allow = {v.strip() for v in settings.allowed_image_mime.split(",") if v.strip()}
    audio_allow = {v.strip() for v in settings.allowed_audio_mime.split(",") if v.strip()}
    if media_type == MediaType.SCREENSHOT and mime_type not in image_allow:
        raise ValueError(f"UNSUPPORTED_MEDIA: {mime_type}")
    if media_type == MediaType.AUDIO and mime_type not in audio_allow:
        raise ValueError(f"UNSUPPORTED_MEDIA: {mime_type}")


def build_from_json(
    source: SourceType,
    media_type: MediaType,
    mime_type: str,
    media_base64: str,
    locale: str,
    timezone: str,
    captured_at: datetime | None,
    metadata: dict,
    settings: Settings,
) -> CaptureRequest:
    if len(media_base64) > settings.max_base64_chars:
        raise ValueError("PAYLOAD_TOO_LARGE")
    _validate_mime(media_type, mime_type, settings)

    payload = base64.b64decode(_strip_base64_prefix(media_base64), validate=True)
    return CaptureRequest(
        source=source,
        media_type=media_type,
        transport_mode=TransportMode.BASE64_JSON,
        mime_type=mime_type,
        payload_ref="inline_base64",
        payload_bytes=payload,
        locale=locale,
        timezone=timezone,
        captured_at=captured_at or datetime.now().astimezone(),
        metadata=metadata,
    )


def build_from_upload(
    source: SourceType,
    media_type: MediaType,
    mime_type: str,
    payload_bytes: bytes,
    locale: str,
    timezone: str,
    captured_at: datetime | None,
    metadata: dict,
    settings: Settings,
) -> CaptureRequest:
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(payload_bytes) > max_bytes:
        raise ValueError("PAYLOAD_TOO_LARGE")
    _validate_mime(media_type, mime_type, settings)

    return CaptureRequest(
        source=source,
        media_type=media_type,
        transport_mode=TransportMode.FILE_UPLOAD,
        mime_type=mime_type,
        payload_ref="multipart_upload",
        payload_bytes=payload_bytes,
        locale=locale,
        timezone=timezone,
        captured_at=captured_at or datetime.now().astimezone(),
        metadata=metadata,
    )


async def fetch_remote_payload(url: str, timeout_seconds: int) -> bytes:
    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.content
