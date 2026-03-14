from __future__ import annotations

from typing import Optional

from config import LANGUAGE_DETECT_ENABLED, LANGUAGE_DETECT_FALLBACK

try:
    from langdetect import detect
except Exception:  # pragma: no cover
    detect = None


def detect_language(text: str) -> str:
    if not LANGUAGE_DETECT_ENABLED or detect is None:
        return LANGUAGE_DETECT_FALLBACK

    try:
        return detect(text)
    except Exception:
        return LANGUAGE_DETECT_FALLBACK
