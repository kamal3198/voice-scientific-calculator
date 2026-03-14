from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Optional

from config import WAKE_WORDS


@dataclass
class ParsedCommand:
    intent: str
    expression: str | None = None
    raw_text: str | None = None
    variable: str | None = None


_UNITS: Dict[str, int] = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
}

_TENS: Dict[str, int] = {
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}

_SCALES: Dict[str, int] = {
    "hundred": 100,
    "thousand": 1000,
}


def _words_to_number(tokens: list[str]) -> Optional[float]:
    current = 0
    total = 0
    decimal_part = []
    is_decimal = False

    for token in tokens:
        if token == "point":
            is_decimal = True
            continue

        if token in _UNITS:
            value = _UNITS[token]
        elif token in _TENS:
            value = _TENS[token]
        elif token in _SCALES:
            scale = _SCALES[token]
            if current == 0:
                current = 1
            current *= scale
            if scale >= 1000:
                total += current
                current = 0
            continue
        else:
            return None

        if is_decimal:
            decimal_part.append(str(value))
        else:
            current += value

    number = total + current
    if decimal_part:
        return float(f"{number}.{' '.join(decimal_part).replace(' ', '')}")
    return float(number)


def _replace_word_numbers(text: str) -> str:
    tokens = text.split()
    out = []
    buffer: list[str] = []

    def flush_buffer() -> None:
        nonlocal buffer
        if not buffer:
            return
        value = _words_to_number(buffer)
        if value is not None:
            out.append(str(value))
        else:
            out.extend(buffer)
        buffer = []

    for token in tokens:
        if token in _UNITS or token in _TENS or token in _SCALES or token == "point":
            buffer.append(token)
        else:
            flush_buffer()
            out.append(token)

    flush_buffer()
    return " ".join(out)


def _cleanup_text(text: str) -> str:
    cleaned = text.lower().strip()
    cleaned = cleaned.replace("?", "")
    cleaned = cleaned.replace("=", " equals ")
    cleaned = cleaned.replace("what is", "")
    cleaned = cleaned.replace("calculate", "")
    cleaned = cleaned.replace("please", "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _normalize_math(text: str) -> str:
    replacements = [
        ("multiplied by", "*"),
        ("times", "*"),
        ("divided by", "/"),
        ("divide by", "/"),
        ("over", "/"),
        ("plus", "+"),
        ("minus", "-"),
        ("mod", "%"),
        ("modulus", "%"),
    ]

    normalized = text
    for src, dst in replacements:
        normalized = normalized.replace(src, dst)

    normalized = normalized.replace("to the power of", "**")
    normalized = normalized.replace("power of", "**")
    normalized = normalized.replace("power", "**")

    normalized = normalized.replace("square root of", "sqrt ")
    normalized = normalized.replace("square root", "sqrt ")
    normalized = normalized.replace("factorial of", "factorial ")

    normalized = normalized.replace("degrees", "degree")

    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def _handle_percent(text: str) -> str:
    # "20 percent of 50" -> "20/100*50"
    text = re.sub(r"(\d+(?:\.\d+)?)\s*percent of\s*(\d+(?:\.\d+)?)", r"(\1/100)*\2", text)
    # "50 percent" -> "50/100"
    text = re.sub(r"(\d+(?:\.\d+)?)\s*percent", r"(\1/100)", text)
    return text


def _handle_powers(text: str) -> str:
    # "x squared" -> "x**2", "x cubed" -> "x**3"
    text = re.sub(r"(\w+)\s+squared", r"\1**2", text)
    text = re.sub(r"(\w+)\s+cubed", r"\1**3", text)
    return text


def _handle_trig_degrees(text: str) -> str:
    # "sin 30 degree" -> "sin(30*pi/180)"
    pattern = r"\b(sin|cos|tan)\s+(\d+(?:\.\d+)?)\s*degree\b"
    return re.sub(pattern, r"\1(\2*pi/180)", text)


def parse_command(raw_text: str) -> ParsedCommand:
    text = _cleanup_text(raw_text)

    if not text:
        return ParsedCommand(intent="empty", raw_text=raw_text)

    if any(text.startswith(wake) for wake in WAKE_WORDS):
        text = text

    if any(word in text for word in ["exit", "quit", "close", "stop program"]):
        return ParsedCommand(intent="exit", raw_text=raw_text)

    if "repeat result" in text or "last result" in text:
        return ParsedCommand(intent="repeat", raw_text=raw_text)

    if "clear history" in text or "reset history" in text:
        return ParsedCommand(intent="clear_history", raw_text=raw_text)

    if "show history" in text or "history" in text:
        return ParsedCommand(intent="show_history", raw_text=raw_text)

    if text.startswith("plot "):
        expr = text.replace("plot ", "", 1).strip()
        return ParsedCommand(intent="plot", expression=expr, raw_text=raw_text)

    if text.startswith("solve "):
        expr = text.replace("solve ", "", 1).strip()
        return ParsedCommand(intent="solve", expression=expr, raw_text=raw_text)

    if text.startswith("differentiate ") or text.startswith("derive "):
        expr = text.replace("differentiate ", "", 1).replace("derive ", "", 1).strip()
        return ParsedCommand(intent="differentiate", expression=expr, raw_text=raw_text)

    if text.startswith("integrate "):
        expr = text.replace("integrate ", "", 1).strip()
        return ParsedCommand(intent="integrate", expression=expr, raw_text=raw_text)

    text = _replace_word_numbers(text)
    text = _normalize_math(text)
    text = _handle_percent(text)
    text = _handle_powers(text)
    text = _handle_trig_degrees(text)

    # Convert "equals" into equation for solve
    if " equals " in f" {text} ":
        left, right = text.split(" equals ", 1)
        return ParsedCommand(intent="solve", expression=f"{left} = {right}", raw_text=raw_text)

    return ParsedCommand(intent="calculate", expression=text, raw_text=raw_text)
