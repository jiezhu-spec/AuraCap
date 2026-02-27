from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path

from backend.app.core.config import Settings
from backend.app.providers.base import BaseProvider
from backend.app.services.common import load_prompt
from backend.app.services.prompt_router import locale_to_lang, resolve_summary_prompt
from backend.app.services.timeline import entries_by_range

LOG_PATH = Path(__file__).resolve().parents[3] / ".cursor" / "debug-ee3959.log"


def _debug_log(msg: str, data: dict, hypothesis_id: str = "") -> None:
    try:
        payload = {"id": f"log_{id(data)}", "timestamp": int(datetime.now().timestamp() * 1000), "location": "summary.py", "message": msg, "data": data, "hypothesisId": hypothesis_id}
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass


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
    # #region agent log
    _debug_log("summary_timeline", {"start_day": str(start_day), "now_day": str(now_day), "timeline_count": len(timeline_items), "timeline_exists": settings.timeline_file.exists()}, "H2")
    # #endregion
    if not timeline_items:
        return None

    timeline_text = "\n".join(
        f"- {item['timestamp_display']} | {item.get('input_type', 'screenshot')} | {item['extracted_content'][:300]}" for item in timeline_items
    )
    insights_text = _collect_insight_text(settings, start_day, now_day)

    lang = locale_to_lang(settings.output_locale)
    prompt_path = resolve_summary_prompt(lang, settings)
    prompt = load_prompt(prompt_path, "Summarize trajectory, risks, and next actions.")
    merged = f"# Timeline\n{timeline_text}\n\n# Insights\n{insights_text}"
    # #region agent log
    _debug_log("summary_before_llm", {"prompt_len": len(prompt), "merged_len": len(merged)}, "H3")
    # #endregion
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
