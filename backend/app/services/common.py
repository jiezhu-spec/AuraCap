from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def resolve_timezone(name: str) -> ZoneInfo:
    if name == "local":
        local_tz = datetime.now().astimezone().tzinfo
        if isinstance(local_tz, ZoneInfo):
            return local_tz
        if local_tz and getattr(local_tz, "key", None):
            return ZoneInfo(local_tz.key)
        return ZoneInfo("UTC")
    return ZoneInfo(name)


def load_prompt(path: Path, fallback: str) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8").strip() or fallback
    return fallback


def dump_json(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)
