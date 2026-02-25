from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Literal

from backend.app.core.config import Settings
from backend.app.services.timeline import entries_by_day, entries_by_range


@dataclass
class TagEntry:
    tag: str
    weight: int
    entries: list[dict]


@dataclass
class TaskIndex:
    window: str
    start: date
    end: date
    dominant_tag: str | None
    tags: list[TagEntry]
    untagged_entries: list[dict]
    path: Path
    generated_at: str


def _load_entry_tags(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        return {k: v if isinstance(v, list) else [] for k, v in data.items()}
    except (json.JSONDecodeError, TypeError):
        return {}


def _entry_preview(item: dict, max_len: int = 300) -> dict:
    content = (item.get("extracted_content") or "")[:max_len]
    return {
        "entry_id": item.get("id", ""),
        "timestamp_display": item.get("timestamp_display", ""),
        "content_preview": content,
    }


def _build_index(
    settings: Settings,
    entries: list[dict],
) -> tuple[list[TagEntry], list[dict], str | None]:
    with_id = [e for e in entries if e.get("id")]
    if not with_id:
        return [], [], None

    tags_data = _load_entry_tags(settings.entry_tags_file)
    tag_to_entries: dict[str, list[dict]] = {}
    untagged: list[dict] = []

    for item in with_id:
        eid = item["id"]
        item_tags = tags_data.get(eid) or []
        if not item_tags:
            untagged.append(item)
            continue
        preview = _entry_preview(item)
        for t in item_tags:
            t = str(t).strip().lower()
            if not t:
                continue
            if t not in tag_to_entries:
                tag_to_entries[t] = []
            tag_to_entries[t].append(preview)

    top_n = max(1, settings.task_index_top_n)
    sorted_tags = sorted(
        tag_to_entries.items(),
        key=lambda x: len(x[1]),
        reverse=True,
    )[:top_n]

    tag_entries = [
        TagEntry(tag=t, weight=len(ents), entries=ents)
        for t, ents in sorted_tags
    ]
    dominant = tag_entries[0].tag if tag_entries else None
    return tag_entries, untagged, dominant


def run_daily_task_index(
    settings: Settings,
    target_day: date,
    timezone_name: str,
) -> str | None:
    entries = entries_by_day(settings.timeline_file, target_day, timezone_name)
    tag_entries, untagged, dominant = _build_index(settings, entries)
    if not tag_entries and not untagged:
        return None

    out_dir = settings.task_index_dir / "daily"
    out_dir.mkdir(parents=True, exist_ok=True)
    base = out_dir / target_day.isoformat()

    _write_task_index(settings, base, "daily", target_day, target_day, tag_entries, untagged, dominant)
    return str(base.with_suffix(".md"))


def run_weekly_task_index(
    settings: Settings,
    now_day: date,
    timezone_name: str,
) -> str | None:
    start_day = now_day - timedelta(days=settings.summary_window_days - 1)
    entries = entries_by_range(settings.timeline_file, start_day, now_day, timezone_name)
    tag_entries, untagged, dominant = _build_index(settings, entries)
    if not tag_entries and not untagged:
        return None

    out_dir = settings.task_index_dir / "weekly"
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{start_day.isoformat()}_{now_day.isoformat()}"
    base = out_dir / stem

    _write_task_index(settings, base, "weekly", start_day, now_day, tag_entries, untagged, dominant)
    return str(base.with_suffix(".md"))


def _write_task_index(
    settings: Settings,
    base: Path,
    window: str,
    start_day: date,
    end_day: date,
    tag_entries: list[TagEntry],
    untagged: list[dict],
    dominant: str | None,
) -> None:
    now = datetime.now().astimezone()
    generated_at = now.isoformat()

    json_data = {
        "window": window,
        "start": start_day.isoformat(),
        "end": end_day.isoformat(),
        "dominant_tag": dominant,
        "tags": [
            {"tag": te.tag, "weight": te.weight, "entries": te.entries}
            for te in tag_entries
        ],
        "untagged_entries": [_entry_preview(e) for e in untagged],
        "generated_at": generated_at,
    }
    (base.with_suffix(".json")).write_text(
        json.dumps(json_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    md_lines = [
        f"# Task Index {start_day.isoformat()} ~ {end_day.isoformat()}",
        "",
        f"**Dominant tag**: {dominant or '(none)'}",
        "",
    ]
    for te in tag_entries:
        md_lines.append(f"## {te.tag} ({te.weight})")
        md_lines.append("")
        for e in te.entries:
            cp = e["content_preview"]
            md_lines.append(f"- {e['timestamp_display']} | {cp}")
        md_lines.append("")
    if untagged:
        md_lines.append("## _untagged")
        md_lines.append("")
        for e in untagged:
            prev = _entry_preview(e)
            md_lines.append(f"- {prev['timestamp_display']} | {prev['content_preview']}")
        md_lines.append("")

    (base.with_suffix(".md")).write_text("\n".join(md_lines), encoding="utf-8")


def load_task_index(path: Path) -> TaskIndex | None:
    json_path = path.with_suffix(".json") if path.suffix == ".md" else path
    if not json_path.exists():
        return None
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if "start" not in data or "end" not in data:
        return None
    try:
        start_d = datetime.fromisoformat(data["start"]).date()
        end_d = datetime.fromisoformat(data["end"]).date()
    except (ValueError, TypeError):
        return None
    tags = [
        TagEntry(tag=t["tag"], weight=t["weight"], entries=t.get("entries", []))
        for t in data.get("tags", [])
    ]
    return TaskIndex(
        window=data.get("window", ""),
        start=start_d,
        end=end_d,
        dominant_tag=data.get("dominant_tag"),
        tags=tags,
        untagged_entries=data.get("untagged_entries", []),
        path=json_path,
        generated_at=data.get("generated_at", ""),
    )


def get_task_index_for_extraction(
    settings: Settings,
    window: Literal["daily", "weekly"],
    start_day: date,
    end_day: date | None = None,
) -> TaskIndex | None:
    if window == "daily":
        path = settings.task_index_dir / "daily" / f"{start_day.isoformat()}.json"
    else:
        if end_day is None:
            return None
        path = settings.task_index_dir / "weekly" / f"{start_day.isoformat()}_{end_day.isoformat()}.json"
    return load_task_index(path)
