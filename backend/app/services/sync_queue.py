from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from backend.app.core.config import Settings
from backend.app.models.schemas import SyncEvent
from backend.app.services.syncer import SyncService


def _pending_path(settings: Settings) -> Path:
    return settings.storage_root / ".sync_pending.jsonl"


async def enqueue(settings: Settings, event: SyncEvent) -> list[dict]:
    if settings.sync_default_frequency == "ON_EVENT":
        syncer = SyncService(settings)
        results = await syncer.dispatch(event)
        return [r.model_dump() for r in results]
    path = _pending_path(settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(
        {
            "event_type": event.event_type,
            "title": event.title,
            "body": event.body,
            "artifact_path": event.artifact_path,
            "created_at": datetime.now().astimezone().isoformat(),
        },
        ensure_ascii=False,
    )
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    return []


async def flush_pending(settings: Settings) -> int:
    path = _pending_path(settings)
    if not path.exists():
        return 0
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return 0
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if not lines:
        return 0
    syncer = SyncService(settings)
    count = 0
    for line in lines:
        try:
            raw = json.loads(line)
            event = SyncEvent(
                event_type=raw["event_type"],
                title=raw["title"],
                body=raw["body"],
                artifact_path=raw.get("artifact_path"),
            )
            await syncer.dispatch(event)
            count += 1
        except (json.JSONDecodeError, KeyError):
            continue
    try:
        path.write_text("", encoding="utf-8")
    except OSError:
        pass
    return count
