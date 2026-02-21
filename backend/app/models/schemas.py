from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class SourceType(str, Enum):
    IOS_SHORTCUT = "ios_shortcut"
    GITHUB_ACTION = "github_action"
    SELF_HOST = "self_host"


class MediaType(str, Enum):
    SCREENSHOT = "screenshot"
    AUDIO = "audio"


class TransportMode(str, Enum):
    BASE64_JSON = "base64_json"
    FILE_UPLOAD = "file_upload"
    REMOTE_URL = "remote_url"
    GITHUB_RELEASE_ASSET = "github_release_asset"


class AudioMode(str, Enum):
    TRANSCRIBE_THEN_ANALYZE = "TRANSCRIBE_THEN_ANALYZE"
    DIRECT_MULTIMODAL = "DIRECT_MULTIMODAL"


class CaptureJSONRequest(BaseModel):
    source: SourceType = SourceType.IOS_SHORTCUT
    media_type: MediaType
    mime_type: str
    media_base64: str = Field(min_length=16)
    locale: str = "zh-CN"
    timezone: str = "local"
    captured_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CaptureDispatchRequest(BaseModel):
    source: SourceType = SourceType.GITHUB_ACTION
    media_type: MediaType
    transport_mode: TransportMode
    payload_ref: str
    mime_type: str
    locale: str = "zh-CN"
    timezone: str = "local"
    captured_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CaptureRequest(BaseModel):
    source: SourceType
    media_type: MediaType
    transport_mode: TransportMode
    mime_type: str
    payload_ref: str
    payload_bytes: bytes
    locale: str
    timezone: str
    captured_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProcessResult(BaseModel):
    request_id: str
    timeline_path: str
    extracted_content: str
    insight_path: str | None = None
    summary_path: str | None = None
    customized_path: str | None = None
    sync_results: list[dict[str, Any]] = Field(default_factory=list)
    status: Literal["success", "failed"] = "success"
    error_code: str | None = None


class TimelineEntry(BaseModel):
    id: str
    timestamp: datetime
    timestamp_display: str
    locale: str
    timezone: str
    input_type: MediaType
    source: SourceType
    extracted_content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    trace: dict[str, Any] = Field(default_factory=dict)


class SyncEvent(BaseModel):
    event_type: Literal["timeline", "insight", "summary", "customized", "error"]
    title: str
    body: str
    artifact_path: str | None = None


class DeliveryResult(BaseModel):
    channel: str
    success: bool
    detail: str


class HealthResponse(BaseModel):
    app: str
    status: str
