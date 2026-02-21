from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


def _i18n_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "i18n"


@lru_cache(maxsize=4)
def load_i18n(locale: str) -> dict[str, str]:
    path = _i18n_dir() / f"{locale}.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def t(key: str, locale: str = "zh-CN") -> str:
    strings = load_i18n(locale)
    return strings.get(key, key)
