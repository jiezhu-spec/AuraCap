from __future__ import annotations

from datetime import datetime
from pathlib import Path

from backend.app.core.config import Settings
from backend.app.services.timeline import append_timeline, list_timeline_entries


def test_append_and_list_timeline(tmp_path: Path) -> None:
    timeline_file = tmp_path / "timeline.md"
    settings = Settings(
        timeline_file=timeline_file,
        storage_root=tmp_path,
        insights_dir=tmp_path / "insights",
        summary_dir=tmp_path / "summary",
        customized_dir=tmp_path / "customized",
    )

    append_timeline(
        settings=settings,
        source="ios_shortcut",
        input_type="screenshot",
        extracted_content="hello",
        locale="zh-CN",
        timezone="UTC",
        metadata={"k": "v"},
        trace={"request_id": "abc"},
        timestamp=datetime.fromisoformat("2026-02-21T12:00:00+00:00"),
    )

    items = list_timeline_entries(timeline_file)
    assert len(items) == 1
    assert items[0]["extracted_content"] == "hello"
    assert "id" in items[0]
    assert items[0]["id"] and items[0]["id"].startswith("entry-")
