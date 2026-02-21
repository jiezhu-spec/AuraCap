from __future__ import annotations

from datetime import date

from backend.app.core.config import Settings
from backend.app.providers.base import BaseProvider
from backend.app.services.common import load_prompt
from backend.app.services.timeline import entries_by_day


def _build_day_payload(entries: list[dict]) -> str:
    lines = []
    for item in entries:
        lines.append(f"- {item['timestamp_display']} | {item['input_type']} | {item['extracted_content'][:300]}")
    return "\n".join(lines)


async def run_daily_insights(settings: Settings, provider: BaseProvider, target_day: date, timezone_name: str) -> str | None:
    entries = entries_by_day(settings.timeline_file, target_day, timezone_name)
    if not entries:
        return None

    prompt = load_prompt(settings.insights_prompt_file, "Generate concise daily insights from timeline entries.")
    body = _build_day_payload(entries)
    result = await provider.analyze_text(prompt=prompt, text=body)

    out_path = settings.insights_dir / f"{target_day.isoformat()}.md"
    out_path.write_text(
        "\n".join(
            [
                f"# Daily Insights {target_day.isoformat()}",
                "",
                "## Source",
                body,
                "",
                "## Insights",
                result,
                "",
            ]
        ),
        encoding="utf-8",
    )
    return str(out_path)
