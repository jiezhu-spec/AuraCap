from __future__ import annotations

from datetime import date, timedelta

from backend.app.core.config import Settings
from backend.app.providers.base import BaseProvider
from backend.app.services.common import load_prompt
from backend.app.services.timeline import entries_by_range


def _collect_insight_text(settings: Settings, start_day: date, end_day: date) -> str:
    chunks: list[str] = []
    day = start_day
    while day <= end_day:
        p = settings.insights_dir / f"{day.isoformat()}.md"
        if p.exists():
            chunks.append(p.read_text(encoding="utf-8"))
        day += timedelta(days=1)
    return "\n\n".join(chunks)


async def run_periodic_summary(settings: Settings, provider: BaseProvider, now_day: date, timezone_name: str) -> str | None:
    start_day = now_day - timedelta(days=settings.summary_window_days - 1)
    timeline_items = entries_by_range(settings.timeline_file, start_day, now_day, timezone_name)
    if not timeline_items:
        return None

    timeline_text = "\n".join(
        f"- {item['timestamp_display']} | {item['input_type']} | {item['extracted_content'][:300]}" for item in timeline_items
    )
    insights_text = _collect_insight_text(settings, start_day, now_day)

    prompt = load_prompt(settings.summary_prompt_file, "Summarize trajectory, risks, and next actions.")
    merged = f"# Timeline\n{timeline_text}\n\n# Insights\n{insights_text}"
    output = await provider.analyze_text(prompt=prompt, text=merged)

    out_path = settings.summary_dir / f"{start_day.isoformat()}_{now_day.isoformat()}.md"
    out_path.write_text(
        "\n".join(
            [
                f"# Summary {start_day.isoformat()} ~ {now_day.isoformat()}",
                "",
                "## Window",
                f"{start_day.isoformat()} to {now_day.isoformat()}",
                "",
                "## Summary",
                output,
                "",
            ]
        ),
        encoding="utf-8",
    )
    return str(out_path)
