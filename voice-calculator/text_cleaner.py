from __future__ import annotations

import re
from typing import Iterable


_FILLER_PHRASES = [
    "what",
    "is",
    "calculate",
    "please",
    "equal",
    "equals",
    "result",
    "the",
    "is equal to",
]


def clean_text(text: str, extra_phrases: Iterable[str] | None = None) -> str:
    cleaned = text.lower().strip()

    for phrase in _FILLER_PHRASES:
        cleaned = cleaned.replace(phrase, " ")

    if extra_phrases:
        for phrase in extra_phrases:
            cleaned = cleaned.replace(phrase, " ")

    cleaned = re.sub(r"[?]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned
