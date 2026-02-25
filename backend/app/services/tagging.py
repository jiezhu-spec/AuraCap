from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path

from backend.app.core.config import Settings
from backend.app.providers.base import BaseProvider
from backend.app.services.common import load_prompt
from backend.app.services.prompt_router import locale_to_lang, resolve_tagging_prompt
from backend.app.services.timeline import entries_by_day

logger = logging.getLogger(__name__)


def _build_tagging_payload(entries: list[dict]) -> str:
    lines = []
    for item in entries:
        eid = item.get("id") or ""
        ts = item.get("timestamp_display", "")
        itype = item.get("input_type", "screenshot")
        content = (item.get("extracted_content") or "")[:300]
        lines.append(f"- {eid} | {ts} | {itype} | {content}")
    return "\n".join(lines)


def _load_entry_tags(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return {k: v if isinstance(v, list) else [] for k, v in data.items()}
    except json.JSONDecodeError:
        pass
    return {}


def _save_entry_tags(path: Path, data: dict[str, list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _extract_json_object(s: str) -> dict | None:
    """Try to extract the first {...} JSON object from s, even when surrounded by prose or fences."""
    try:
        data = json.loads(s)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    start = s.find("{")
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape = False
    for i, c in enumerate(s[start:], start):
        if escape:
            escape = False
            continue
        if c == "\\" and in_string:
            escape = True
            continue
        if c == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                try:
                    data = json.loads(s[start : i + 1])
                    if isinstance(data, dict):
                        return data
                except json.JSONDecodeError:
                    return None
    return None


def _parse_tagging_response(raw: str, expected_ids: set[str]) -> dict[str, list[str]] | None:
    data = _extract_json_object(raw.strip())
    if data is None:
        return None
    result: dict[str, list[str]] = {}
    for k, v in data.items():
        if k not in expected_ids:
            continue
        if isinstance(v, list):
            tags = [str(t).strip().lower() for t in v if t][:3]
        elif isinstance(v, str):
            tags = [v.strip().lower()] if v.strip() else []
        else:
            tags = []
        if tags:
            result[k] = tags
    return result if result else None


async def run_daily_tagging(
    settings: Settings,
    provider: BaseProvider,
    target_day: date,
    timezone_name: str,
) -> int:
    entries = entries_by_day(settings.timeline_file, target_day, timezone_name)
    with_id = [e for e in entries if e.get("id")]
    if not with_id:
        return 0

    existing = _load_entry_tags(settings.entry_tags_file)
    to_tag = [e for e in with_id if e["id"] not in existing]
    if not to_tag:
        return 0

    lang = locale_to_lang(settings.output_locale)
    prompt_path = resolve_tagging_prompt(lang, settings)
    prompt = load_prompt(prompt_path, "Assign 1-3 semantic tags per entry. Output strict JSON only.")
    body = _build_tagging_payload(to_tag)

    try:
        raw = await provider.analyze_text(prompt=prompt, text=body)
    except Exception as exc:
        logger.warning("tagging_api_failed", extra={"error": str(exc)})
        return 0

    expected = {e["id"] for e in to_tag}
    parsed = _parse_tagging_response(raw, expected)
    if not parsed:
        logger.warning("tagging_parse_failed", extra={"raw_len": len(raw)})
        return 0

    merged = dict(existing)
    for k, v in parsed.items():
        merged[k] = v

    _save_entry_tags(settings.entry_tags_file, merged)
    return len(parsed)
