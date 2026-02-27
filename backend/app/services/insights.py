from __future__ import annotations

from datetime import date

from backend.app.core.config import Settings
from backend.app.providers.base import BaseProvider
from backend.app.services.common import load_prompt
from backend.app.services.prompt_router import locale_to_lang, resolve_insights_prompt
from backend.app.services.timeline import entries_by_day


def _build_day_payload(entries: list[dict]) -> str:
    lines = []
    for item in entries:
        lines.append(f"- {item['timestamp_display']} | {item.get('input_type', 'screenshot')} | {item['extracted_content'][:300]}")
    return "\n".join(lines)


async def run_daily_insights(settings: Settings, provider: BaseProvider, target_day: date, timezone_name: str) -> str | None:
    entries = entries_by_day(settings.timeline_file, target_day, timezone_name)
    # #region agent log
    print(f"[DEBUG] run_daily_insights: target_day={target_day} tz={timezone_name} entries_count={len(entries)}")
    # #endregion
    if not entries:
        return None

    lang = locale_to_lang(settings.output_locale)
    prompt_path = resolve_insights_prompt(lang, settings)
    prompt = load_prompt(prompt_path, "Generate concise daily insights from timeline entries.")
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
