from __future__ import annotations

import re
from typing import Dict


_EN_NUMBERS: Dict[str, str] = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
}

_HI_NUMBERS: Dict[str, str] = {
    "ek": "1",
    "do": "2",
    "teen": "3",
    "char": "4",
    "paanch": "5",
    "chhe": "6",
    "saat": "7",
    "aath": "8",
    "nau": "9",
    "das": "10",
}

_TE_NUMBERS: Dict[str, str] = {
    "okati": "1",
    "rendu": "2",
    "moodu": "3",
    "nalugu": "4",
    "aidu": "5",
    "aaru": "6",
    "edu": "7",
    "enimidi": "8",
    "tommidi": "9",
    "padi": "10",
}


def translate_numbers(text: str) -> str:
    words = text.split()
    out = []

    for word in words:
        if word in _EN_NUMBERS:
            out.append(_EN_NUMBERS[word])
            continue
        if word in _HI_NUMBERS:
            out.append(_HI_NUMBERS[word])
            continue
        if word in _TE_NUMBERS:
            out.append(_TE_NUMBERS[word])
            continue
        out.append(word)

    return " ".join(out)


def has_multilingual_numbers(text: str) -> bool:
    vocab = set(_EN_NUMBERS) | set(_HI_NUMBERS) | set(_TE_NUMBERS)
    tokens = re.findall(r"[a-zA-Z]+", text)
    return any(token in vocab for token in tokens)
