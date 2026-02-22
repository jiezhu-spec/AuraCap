from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path

from backend.app.core.config import Settings, get_settings
from backend.app.services.scheduler import _matches_cron, run_scheduled_tasks_once
from backend.app.services.timeline import append_timeline


def test_weekday_cron_matches_sunday() -> None:
    """Verify weekday field follows standard cron (0=Sunday)."""
    # 2026-02-22 is Sunday; 2026-02-23 is Monday
    sunday_0200 = datetime(2026, 2, 22, 2, 0, 0, tzinfo=timezone.utc)
    monday_0200 = datetime(2026, 2, 23, 2, 0, 0, tzinfo=timezone.utc)
    assert _matches_cron("0 2 * * 0", sunday_0200)
    assert not _matches_cron("0 2 * * 0", monday_0200)


def test_scheduler_enable_scheduler_false(monkeypatch, capsys) -> None:
    """Verify run_scheduler_tick early return when ENABLE_SCHEDULER=false."""
    monkeypatch.setenv("ENABLE_SCHEDULER", "false")
    get_settings.cache_clear()
    from scripts.run_scheduler_tick import main

    asyncio.run(main())
    out, _ = capsys.readouterr()
    assert "skipping" in out


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
        insights_target_day_offset=0,
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
