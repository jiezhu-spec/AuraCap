from __future__ import annotations

import asyncio
import json

from backend.app.core.config import get_settings
from backend.app.services.scheduler import run_scheduled_tasks_once


async def main() -> None:
    settings = get_settings()
    if not settings.enable_scheduler:
        print("ENABLE_SCHEDULER=false, skipping scheduler tick.")
        return
    result = await run_scheduled_tasks_once(settings)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
