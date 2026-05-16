from __future__ import annotations

import asyncio
import json
from pathlib import Path

import httpx
import pytest

from backend.app.core.config import Settings, get_settings
from backend.app.models.schemas import MediaType, ProcessResult, TransportMode
from backend.app.services.media import validate_media_payload
from scripts import process_github_dispatch as dispatch


def test_load_event_payload_keeps_workflow_and_repository_contracts(tmp_path: Path) -> None:
    workflow_event = tmp_path / "workflow.json"
    workflow_event.write_text(
        json.dumps({"inputs": {"asset_id": "123", "media_type": "screenshot"}}),
        encoding="utf-8",
    )
    repository_event = tmp_path / "repository.json"
    repository_event.write_text(
        json.dumps({"client_payload": {"asset_id": 456, "media_type": "audio"}}),
        encoding="utf-8",
    )

    assert dispatch._load_event_payload(str(workflow_event))["asset_id"] == "123"
    assert dispatch._load_event_payload(str(repository_event))["asset_id"] == 456


def test_resolve_payload_uses_asset_id_before_payload_ref(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_find(*args, **kwargs) -> dict:
        return {"id": 123, "size": 4}

    async def fake_download(*args, **kwargs) -> bytes:
        return b"data"

    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setattr(dispatch, "_find_inbox_asset", fake_find)
    monkeypatch.setattr(dispatch, "_download_release_asset", fake_download)

    result = asyncio.run(
        dispatch._resolve_payload_bytes(
            {"asset_id": "123", "payload_ref": "https://example.com/media.png"},
            Settings(),
        )
    )

    assert result.content == b"data"
    assert result.mode == TransportMode.GITHUB_RELEASE_ASSET
    assert result.payload_ref == "release_asset:123"
    assert result.asset_id == 123


def test_repository_dispatch_numeric_asset_id(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_find(*args, **kwargs) -> dict:
        return {"id": 456, "size": 5}

    async def fake_download(*args, **kwargs) -> bytes:
        return b"audio"

    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setattr(dispatch, "_find_inbox_asset", fake_find)
    monkeypatch.setattr(dispatch, "_download_release_asset", fake_download)

    result = asyncio.run(dispatch._resolve_payload_bytes({"asset_id": 456}, Settings()))

    assert result.content == b"audio"
    assert result.mode == TransportMode.GITHUB_RELEASE_ASSET
    assert result.asset_id == 456


def test_inbox_asset_must_belong_to_release() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/releases/tags/auracap-inbox"):
            return httpx.Response(200, json={"id": 99})
        if request.url.path.endswith("/releases/99/assets"):
            return httpx.Response(200, json=[{"id": 321, "size": 3}])
        return httpx.Response(404, json={})

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(RuntimeError, match="not in inbox release"):
                await dispatch._find_inbox_asset(
                    "owner",
                    "repo",
                    123,
                    "token",
                    "auracap-inbox",
                    30,
                    client=client,
                )

    asyncio.run(run())


def test_unverified_asset_is_not_deleted(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fail_find(*args, **kwargs) -> dict:
        raise RuntimeError("release asset 123 is not in inbox release auracap-inbox")

    async def fail_delete(*args, **kwargs) -> None:
        raise AssertionError("unverified assets must not be deleted")

    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setattr(dispatch, "_find_inbox_asset", fail_find)
    monkeypatch.setattr(dispatch, "_delete_verified_release_asset", fail_delete)

    with pytest.raises(RuntimeError, match="not in inbox release"):
        asyncio.run(dispatch._resolve_release_asset_payload(123, Settings(), "token"))


def test_transient_asset_download_error_keeps_verified_asset(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_find(*args, **kwargs) -> dict:
        return {"id": 123, "size": 4}

    async def fail_download(*args, **kwargs) -> bytes:
        raise RuntimeError("failed to download release asset 123: 500 unavailable")

    async def fail_delete(*args, **kwargs) -> None:
        raise AssertionError("transient download errors should not delete verified assets")

    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setattr(dispatch, "_find_inbox_asset", fake_find)
    monkeypatch.setattr(dispatch, "_download_release_asset", fail_download)
    monkeypatch.setattr(dispatch, "_delete_verified_release_asset", fail_delete)

    with pytest.raises(RuntimeError, match="failed to download"):
        asyncio.run(dispatch._resolve_release_asset_payload(123, Settings(), "token"))


def test_oversized_verified_asset_is_deleted(monkeypatch: pytest.MonkeyPatch) -> None:
    deleted: list[int] = []

    async def fake_find(*args, **kwargs) -> dict:
        return {"id": 123, "size": 2 * 1024 * 1024}

    async def fake_delete(settings: Settings, owner: str, repo: str, asset_id: int, token: str) -> None:
        deleted.append(asset_id)

    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setattr(dispatch, "_find_inbox_asset", fake_find)
    monkeypatch.setattr(dispatch, "_delete_verified_release_asset", fake_delete)

    with pytest.raises(RuntimeError, match="PAYLOAD_TOO_LARGE"):
        asyncio.run(dispatch._resolve_release_asset_payload(123, Settings(max_upload_mb=1), "token"))

    assert deleted == [123]


def test_release_asset_download_rejects_content_length_over_limit() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-length": "2"}, content=b"")

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(RuntimeError, match="PAYLOAD_TOO_LARGE"):
                await dispatch._download_release_asset(
                    "owner",
                    "repo",
                    123,
                    "token",
                    30,
                    max_bytes=1,
                    client=client,
                )

    asyncio.run(run())


def test_release_asset_download_rejects_stream_over_limit() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"too-large")

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(RuntimeError, match="PAYLOAD_TOO_LARGE"):
                await dispatch._download_release_asset(
                    "owner",
                    "repo",
                    123,
                    "token",
                    30,
                    max_bytes=3,
                    client=client,
                )

    asyncio.run(run())


def test_payload_ref_is_unsupported() -> None:
    with pytest.raises(RuntimeError, match="payload_ref is no longer supported"):
        asyncio.run(
            dispatch._resolve_payload_bytes(
                {"payload_ref": "https://example.com/media.png"},
                Settings(),
            )
        )


def test_media_validation_keeps_official_github_only_combinations() -> None:
    settings = Settings()

    validate_media_payload(MediaType.SCREENSHOT, "image/png", b"image", settings)
    validate_media_payload(MediaType.AUDIO, "audio/m4a", b"audio", settings)


def test_main_rejects_unsupported_mime_before_pipeline(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    event_path = tmp_path / "event.json"
    event_path.write_text(
        json.dumps({"inputs": {"asset_id": "123", "media_type": "screenshot", "mime_type": "application/pdf"}}),
        encoding="utf-8",
    )

    async def fake_resolve(payload: dict, settings: Settings) -> dispatch.ResolvedPayload:
        return dispatch.ResolvedPayload(b"payload", TransportMode.GITHUB_RELEASE_ASSET, "release_asset:123", 123)

    deleted: list[int] = []

    async def no_delete(*args, **kwargs) -> None:
        deleted.append(args[3])

    class FailPipeline:
        def __init__(self, settings: Settings) -> None:
            raise AssertionError("pipeline should not run for unsupported MIME")

    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setenv("STORAGE_ROOT", str(tmp_path))
    monkeypatch.setenv("TIMELINE_FILE", str(tmp_path / "timeline.md"))
    monkeypatch.setenv("INSIGHTS_DIR", str(tmp_path / "insights"))
    monkeypatch.setenv("SUMMARY_DIR", str(tmp_path / "summary"))
    monkeypatch.setenv("CUSTOMIZED_DIR", str(tmp_path / "customized"))
    monkeypatch.setattr(dispatch, "_resolve_payload_bytes", fake_resolve)
    monkeypatch.setattr(dispatch, "_delete_verified_release_asset", no_delete)
    monkeypatch.setattr(dispatch, "PipelineService", FailPipeline)
    get_settings.cache_clear()

    try:
        with pytest.raises(ValueError, match="UNSUPPORTED_MEDIA"):
            asyncio.run(dispatch._main(str(event_path)))
    finally:
        get_settings.cache_clear()

    assert deleted == [123]


def test_main_keeps_asset_when_pipeline_returns_failed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    event_path = tmp_path / "event.json"
    event_path.write_text(
        json.dumps({"inputs": {"asset_id": "123", "media_type": "screenshot", "mime_type": "image/png"}}),
        encoding="utf-8",
    )

    async def fake_resolve(payload: dict, settings: Settings) -> dispatch.ResolvedPayload:
        return dispatch.ResolvedPayload(b"payload", TransportMode.GITHUB_RELEASE_ASSET, "release_asset:123", 123)

    async def fail_delete(*args, **kwargs) -> None:
        raise AssertionError("failed pipeline results should keep the asset for retry")

    class FailedPipeline:
        def __init__(self, settings: Settings) -> None:
            pass

        async def process_capture(self, request) -> ProcessResult:
            return ProcessResult(
                request_id="req",
                timeline_path=str(tmp_path / "timeline.md"),
                extracted_content="",
                status="failed",
                error_code="AUTH_FAILED",
            )

    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setenv("STORAGE_ROOT", str(tmp_path))
    monkeypatch.setenv("TIMELINE_FILE", str(tmp_path / "timeline.md"))
    monkeypatch.setenv("INSIGHTS_DIR", str(tmp_path / "insights"))
    monkeypatch.setenv("SUMMARY_DIR", str(tmp_path / "summary"))
    monkeypatch.setenv("CUSTOMIZED_DIR", str(tmp_path / "customized"))
    monkeypatch.setattr(dispatch, "_resolve_payload_bytes", fake_resolve)
    monkeypatch.setattr(dispatch, "_delete_verified_release_asset", fail_delete)
    monkeypatch.setattr(dispatch, "PipelineService", FailedPipeline)
    get_settings.cache_clear()

    try:
        assert asyncio.run(dispatch._main(str(event_path))) == 1
    finally:
        get_settings.cache_clear()


def test_workflow_marks_payload_ref_unsupported() -> None:
    workflow = Path(".github/workflows/ingest_dispatch.yml").read_text(encoding="utf-8")

    assert "payload_ref:" in workflow
    assert "deprecated and unsupported; use asset_id" in workflow
    assert "ALLOW_GITHUB_DISPATCH_REMOTE_URL" not in workflow
