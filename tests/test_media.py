from __future__ import annotations

import base64

from backend.app.core.config import Settings
from backend.app.models.schemas import MediaType, SourceType
from backend.app.services.media import build_from_json


def test_build_from_json_success() -> None:
    raw = b"hello-auracap"
    encoded = base64.b64encode(raw).decode("utf-8")
    settings = Settings()

    request = build_from_json(
        source=SourceType.IOS_SHORTCUT,
        media_type=MediaType.SCREENSHOT,
        mime_type="image/png",
        media_base64=encoded,
        locale="zh-CN",
        timezone="local",
        captured_at=None,
        metadata={},
        settings=settings,
    )

    assert request.payload_bytes == raw
    assert request.transport_mode.value == "base64_json"


def test_build_from_json_reject_large_payload() -> None:
    settings = Settings(max_base64_chars=8)
    try:
        build_from_json(
            source=SourceType.IOS_SHORTCUT,
            media_type=MediaType.SCREENSHOT,
            mime_type="image/png",
            media_base64="a" * 100,
            locale="zh-CN",
            timezone="local",
            captured_at=None,
            metadata={},
            settings=settings,
        )
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "PAYLOAD_TOO_LARGE" in str(exc)
