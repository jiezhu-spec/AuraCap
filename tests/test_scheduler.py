from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path

from backend.app.core.config import Settings
from backend.app.services.scheduler import run_scheduled_tasks_once
from backend.app.services.timeline import append_timeline


def test_scheduler_runs_with_mock_provider(tmp_path: Path) -> None:
    settings = Settings(
        text_provider="mock",
        mm_provider="mock",
        asr_provider="mock",
        storage_root=tmp_path,
        timeline_file=tmp_path / "timeline.md",
        insights_dir=tmp_path / "insights",
        summary_dir=tmp_path / "summary",
        customized_dir=tmp_path / "customized",
        insights_cron="* * * * *",
        summary_cron="* * * * *",
        enable_custom_operation=False,
        enable_insights=True,
        enable_summary=True,
    )
    settings.insights_dir.mkdir(parents=True, exist_ok=True)
    settings.summary_dir.mkdir(parents=True, exist_ok=True)
    settings.customized_dir.mkdir(parents=True, exist_ok=True)

    append_timeline(
        settings=settings,
        source="ios_shortcut",
        input_type="screenshot",
        extracted_content="done task A",
        locale="zh-CN",
        timezone="UTC",
        metadata={},
        trace={},
        timestamp=datetime.fromisoformat("2026-02-21T03:00:00+00:00"),
    )

    result = asyncio.run(run_scheduled_tasks_once(settings, now=datetime.fromisoformat("2026-02-21T04:00:00+00:00")))
    assert "insight" in result
    assert "summary" in result
