from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from backend.app.core.config import Settings
from backend.app.core.i18n import t
from backend.app.models.schemas import SyncEvent
from backend.app.providers.factory import ProviderBundle
from backend.app.services.custom_operation import run_custom_operation
from backend.app.services.insights import run_daily_insights
from backend.app.services.summary import run_periodic_summary
from backend.app.services.tagging import run_daily_tagging
from backend.app.services.task_index import run_daily_task_index, run_weekly_task_index
from backend.app.services.sync_queue import enqueue as sync_enqueue, flush_pending
from backend.app.services.timeline import entries_by_day

logger = logging.getLogger(__name__)


def _state_file(settings: Settings) -> Path:
    return settings.storage_root / ".scheduler_state.json"


def _load_state(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_state(path: Path, state: dict) -> None:
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _expand_token(token: str, minimum: int, maximum: int) -> set[int]:
    values: set[int] = set()
    if token == "*":
        return set(range(minimum, maximum + 1))
    for part in token.split(","):
        p = part.strip()
        if "/" in p:
            base, step = p.split("/", 1)
            step_i = int(step)
            base_values = set(range(minimum, maximum + 1)) if base == "*" else _expand_token(base, minimum, maximum)
            for val in sorted(base_values):
                if (val - minimum) % step_i == 0:
                    values.add(val)
            continue
        if "-" in p:
            start, end = p.split("-", 1)
            values.update(range(int(start), int(end) + 1))
            continue
        values.add(int(p))
    return {v for v in values if minimum <= v <= maximum}


def _matches_cron(cron_expr: str, dt: datetime) -> bool:
    fields = cron_expr.split()
    if len(fields) != 5:
        return False
    minute, hour, day, month, weekday = fields
    cron_wd = dt.isoweekday() % 7  # 0=Sun, 1=Mon, ..., 6=Sat (standard cron convention)
    weekday_set = _expand_token(weekday, 0, 7)
    if 7 in weekday_set:
        weekday_set.add(0)  # standard cron: 7 is alias for Sunday (0)
    checks = [
        dt.minute in _expand_token(minute, 0, 59),
        dt.hour in _expand_token(hour, 0, 23),
        dt.day in _expand_token(day, 1, 31),
        dt.month in _expand_token(month, 1, 12),
        cron_wd in weekday_set,
    ]
    return all(checks)


async def _dispatch_scheduler_artifact(
    path_str: str | None,
    event_type: str,
    title_suffix: str,
    settings: Settings,
) -> None:
    if not path_str:
        return
    try:
        body = Path(path_str).read_text(encoding="utf-8")
    except OSError as exc:
        logger.warning("sync_skip_read_failed", extra={"path": path_str, "error": str(exc)})
        return
    title_key = f"{event_type}_title"
    title = f"{t(title_key, settings.output_locale)} {title_suffix}"
    event = SyncEvent(event_type=event_type, title=title, body=body, artifact_path=path_str)
    await sync_enqueue(settings, event)


def _should_run(cron_expr: str, last_run_iso: str | None, now: datetime) -> bool:
    if last_run_iso is None:
        return _matches_cron(cron_expr, now)
    last = datetime.fromisoformat(last_run_iso)
    if now <= last:
        return False
    cursor = last.replace(second=0, microsecond=0)
    end = now.replace(second=0, microsecond=0)
    while cursor <= end:
        if cursor > last and _matches_cron(cron_expr, cursor):
            return True
        cursor = cursor + timedelta(minutes=1)
    return False


async def run_scheduled_tasks_once(settings: Settings, now: datetime | None = None) -> dict[str, str | None]:
    now = now or datetime.now().astimezone()
    state_path = _state_file(settings)
    state = _load_state(state_path)

    providers = ProviderBundle(settings)
    results: dict[str, str | None] = {
        "insight": None,
        "summary": None,
        "custom": None,
        "task_index_daily": None,
        "task_index_weekly": None,
    }

    insights_target_day = (now - timedelta(days=settings.insights_target_day_offset)).date()
    run_insight = (
        not settings.extract_only
        and settings.enable_insights
        and (settings.force_scheduled_tasks or _should_run(settings.insights_cron, state.get("insights_last"), now))
    )
    if run_insight:
        results["insight"] = await run_daily_insights(
            settings=settings,
            provider=providers.text,
            target_day=insights_target_day,
            timezone_name=settings.default_timezone,
        )
        state["insights_last"] = now.isoformat()
        if results["insight"]:
            await _dispatch_scheduler_artifact(
                results["insight"], "insight", insights_target_day.isoformat(), settings
            )

    run_task_index_daily = (
        not settings.extract_only
        and settings.enable_task_index
        and (settings.force_scheduled_tasks or _should_run(settings.insights_cron, state.get("task_index_daily_last"), now))
    )
    if run_task_index_daily:
        await run_daily_tagging(
            settings=settings,
            provider=providers.text,
            target_day=insights_target_day,
            timezone_name=settings.default_timezone,
        )
        results["task_index_daily"] = run_daily_task_index(
            settings=settings,
            target_day=insights_target_day,
            timezone_name=settings.default_timezone,
        )
        state["task_index_daily_last"] = now.isoformat()

    run_summary = (
        not settings.extract_only
        and settings.enable_summary
        and (settings.force_scheduled_tasks or _should_run(settings.summary_cron, state.get("summary_last"), now))
    )
    if run_summary:
        results["summary"] = await run_periodic_summary(
            settings=settings,
            provider=providers.text,
            now_day=now.date(),
            timezone_name=settings.default_timezone,
        )
        state["summary_last"] = now.isoformat()
        if results["summary"]:
            out_path = Path(results["summary"])
            await _dispatch_scheduler_artifact(
                results["summary"], "summary", out_path.stem.replace("_", " ~ "), settings
            )

    run_task_index_weekly = (
        not settings.extract_only
        and settings.enable_task_index
        and (settings.force_scheduled_tasks or _should_run(settings.summary_cron, state.get("task_index_weekly_last"), now))
    )
    if run_task_index_weekly:
        results["task_index_weekly"] = run_weekly_task_index(
            settings=settings,
            now_day=now.date(),
            timezone_name=settings.default_timezone,
        )
        state["task_index_weekly_last"] = now.isoformat()

    if settings.enable_custom_operation and settings.custom_operation_mode == "CRON":
        run_custom = settings.force_scheduled_tasks or _should_run(
            settings.custom_operation_cron, state.get("custom_last"), now
        )
        if run_custom:
            day_entries = entries_by_day(settings.timeline_file, insights_target_day, settings.default_timezone)
            input_text = "\n".join(item["extracted_content"] for item in day_entries)
            if input_text.strip():
                results["custom"] = await run_custom_operation(
                    settings=settings,
                    provider=providers.text,
                    input_text=input_text,
                )
                if results["custom"]:
                    stamp = Path(results["custom"]).stem.replace("custom_", "")
                    await _dispatch_scheduler_artifact(
                        results["custom"], "customized", stamp, settings
                    )
            state["custom_last"] = now.isoformat()

    if settings.sync_enable and settings.sync_default_frequency in ("DAILY", "CRON"):
        run_sync = settings.force_scheduled_tasks or _should_run(
            settings.sync_default_cron, state.get("sync_last"), now
        )
        if run_sync:
            await flush_pending(settings)
            state["sync_last"] = now.isoformat()

    _save_state(state_path, state)
    return results
