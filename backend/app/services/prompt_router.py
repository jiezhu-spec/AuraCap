"""Prompt routing by media type and language."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from backend.app.core.config import Settings
from backend.app.models.schemas import MediaType
from backend.app.providers.base import BaseProvider, ProviderError

_LANG_DETECT_CJK_THRESHOLD = 0.15  # 15% CJK chars -> zh


def locale_to_lang(locale: str) -> Literal["zh", "en"]:
    """Map locale (e.g. zh-CN, en-US) to prompt language. Non-zh/en fallback to en."""
    prefix = locale.split("-")[0].lower() if locale else ""
    if prefix == "zh":
        return "zh"
    return "en"


def detect_lang_from_transcript(transcript: str) -> Literal["zh", "en"]:
    """Heuristic: CJK character ratio above threshold -> zh, else en."""
    if not transcript or not transcript.strip():
        return "en"
    total = 0
    cjk = 0
    for c in transcript:
        if c.isalnum() or "\u4e00" <= c <= "\u9fff":
            total += 1
            if "\u4e00" <= c <= "\u9fff":
                cjk += 1
    if total == 0:
        return "en"
    if cjk / total >= _LANG_DETECT_CJK_THRESHOLD:
        return "zh"
    return "en"


def resolve_timeline_prompt(
    media_type: MediaType,
    lang: Literal["zh", "en"],
    settings: Settings,
) -> Path:
    """Return path for timeline prompt; fallback to settings.timeline_prompt_file if missing."""
    path = settings.prompts_dir / f"timeline_{media_type.value}_{lang}.md"
    if path.exists():
        return path
    return settings.timeline_prompt_file


def resolve_insights_prompt(lang: Literal["zh", "en"], settings: Settings) -> Path:
    """Return path for insights prompt; fallback to settings.insights_prompt_file if missing."""
    path = settings.prompts_dir / f"insights_{lang}.md"
    if path.exists():
        return path
    return settings.insights_prompt_file


def resolve_summary_prompt(lang: Literal["zh", "en"], settings: Settings) -> Path:
    """Return path for summary prompt; fallback to settings.summary_prompt_file if missing."""
    path = settings.prompts_dir / f"summary_{lang}.md"
    if path.exists():
        return path
    return settings.summary_prompt_file


_LANG_DETECT_PROMPT = (
    "Look at this image. What is the primary language of the visible text? "
    "Reply with exactly one word: zh or en. Nothing else."
)


async def detect_lang_from_screenshot(
    mm_provider: BaseProvider,
    mime_type: str,
    payload: bytes,
) -> Literal["zh", "en"] | None:
    """
    VL call to detect screenshot language. Returns None on ProviderError or parse failure (soft-fail).
    """
    try:
        raw = await mm_provider.analyze_multimodal(
            prompt=_LANG_DETECT_PROMPT,
            mime_type=mime_type,
            payload=payload,
        )
    except ProviderError:
        return None

    if not raw:
        return None
    s = raw.strip().lower()
    # Check zh/chinese first (chinese contains "en")
    if "zh" in s or "chinese" in s:
        return "zh"
    if "en" in s or "english" in s:
        return "en"
    return None
