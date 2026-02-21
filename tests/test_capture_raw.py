from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.core.config import get_settings
from backend.app.main import app


def test_capture_raw_endpoint(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("STORAGE_ROOT", str(tmp_path))
    monkeypatch.setenv("TIMELINE_FILE", str(tmp_path / "timeline.md"))
    monkeypatch.setenv("INSIGHTS_DIR", str(tmp_path / "insights"))
    monkeypatch.setenv("SUMMARY_DIR", str(tmp_path / "summary"))
    monkeypatch.setenv("CUSTOMIZED_DIR", str(tmp_path / "customized"))
    monkeypatch.setenv("TEXT_PROVIDER", "mock")
    monkeypatch.setenv("MM_PROVIDER", "mock")
    monkeypatch.setenv("ASR_PROVIDER", "mock")
    get_settings.cache_clear()

    client = TestClient(app)
    response = client.post(
        "/v1/capture/raw?media_type=screenshot&mime_type=image/png&source=ios_shortcut&locale=zh-CN&timezone=UTC",
        content=b"fake-image-bytes",
        headers={"content-type": "image/png"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert "request_id" in body
