from __future__ import annotations

import json
import re
import uuid
from datetime import date, datetime
from pathlib import Path

from backend.app.core.config import Settings
from backend.app.models.schemas import TimelineEntry
from backend.app.services.common import resolve_timezone


def _format_timestamp(ts: datetime, timezone_name: str, fmt: str) -> tuple[str, str]:
    tz = resolve_timezone(timezone_name)
    local_dt = ts.astimezone(tz)
    return local_dt.isoformat(), local_dt.strftime(fmt)


def append_timeline(
    settings: Settings,
    source: str,
    input_type: str,
    extracted_content: str,
    locale: str,
    timezone: str,
    metadata: dict,
    trace: dict,
    timestamp: datetime | None = None,
) -> TimelineEntry:
    ts = timestamp or datetime.now().astimezone()
    ts_iso, ts_display = _format_timestamp(ts, timezone or settings.default_timezone, settings.timestamp_format)
    entry = TimelineEntry(
        id=uuid.uuid4().hex,
        timestamp=datetime.fromisoformat(ts_iso),
        timestamp_display=ts_display,
        locale=locale,
        timezone=timezone or settings.default_timezone,
        input_type=input_type,
        source=source,
        extracted_content=extracted_content,
        metadata=metadata,
        trace=trace,
    )
    block = {
        "id": f"entry-{entry.id}",
        "timestamp": entry.timestamp.isoformat(),
        "timestamp_display": entry.timestamp_display,
        "extracted_content": entry.extracted_content,
    }

    with settings.timeline_file.open("a", encoding="utf-8") as f:
        f.write(f"### entry-{entry.id}\n")
        f.write("```json\n")
        f.write(json.dumps(block, ensure_ascii=False, indent=2))
        f.write("\n```\n\n")

    return entry


def list_timeline_entries(timeline_file: Path) -> list[dict]:
    if not timeline_file.exists():
        return []
    text = timeline_file.read_text(encoding="utf-8")
    chunks = text.split("```json")
    entries: list[dict] = []
    for i in range(1, len(chunks)):
        chunk = chunks[i]
        if "```" not in chunk:
            continue
        raw = chunk.split("```", 1)[0].strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if "id" not in data:
            prev = chunks[i - 1]
            matches = re.findall(r"### (entry-[a-f0-9]{32})", prev)
            data["id"] = matches[-1] if matches else None
        entries.append(data)
    return entries


def entries_by_day(timeline_file: Path, target_day: date, timezone_name: str) -> list[dict]:
    tz = resolve_timezone(timezone_name)
    results: list[dict] = []
    for item in list_timeline_entries(timeline_file):
        ts = datetime.fromisoformat(item["timestamp"]).astimezone(tz)
        if ts.date() == target_day:
            results.append(item)
    return results


def entries_by_range(timeline_file: Path, start_day: date, end_day: date, timezone_name: str) -> list[dict]:
    tz = resolve_timezone(timezone_name)
    results: list[dict] = []
    for item in list_timeline_entries(timeline_file):
        ts = datetime.fromisoformat(item["timestamp"]).astimezone(tz).date()
        if start_day <= ts <= end_day:
            results.append(item)
    return results
