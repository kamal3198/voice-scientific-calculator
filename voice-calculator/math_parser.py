from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Optional

from language_detector import detect_language
from number_translator import has_multilingual_numbers, translate_numbers
from text_cleaner import clean_text


@dataclass
class ParseResult:
    intent: str
    expression: str | None = None
    raw_text: str | None = None
    incomplete: bool = False
    needs_ollama: bool = False


_WORD_UNITS: Dict[str, int] = {
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

_WORD_TENS: Dict[str, int] = {
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}

_WORD_SCALES: Dict[str, int] = {
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

        if token in _WORD_UNITS:
            value = _WORD_UNITS[token]
        elif token in _WORD_TENS:
            value = _WORD_TENS[token]
        elif token in _WORD_SCALES:
            scale = _WORD_SCALES[token]
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
        if token in _WORD_UNITS or token in _WORD_TENS or token in _WORD_SCALES or token == "point":
            buffer.append(token)
        else:
            flush_buffer()
            out.append(token)

    flush_buffer()
    return " ".join(out)


def _normalize_phrases(text: str) -> str:
    replacements = [
        ("multiplied by", "*"),
        ("multiply by", "*"),
        ("times", "*"),
        ("into", "*"),
        ("divided by", "/"),
        ("divide by", "/"),
        ("over", "/"),
        ("plus", "+"),
        ("minus", "-"),
        ("modulus", "%"),
        ("mod", "%"),
        ("remainder", "%"),
        ("to the power of", "**"),
        ("power of", "**"),
        ("power", "**"),
        ("square root of", "sqrt "),
        ("square root", "sqrt "),
        ("factorial of", "factorial "),
        ("degrees", ""),
        ("degree", ""),
        ("equal to", "="),
    ]

    normalized = text
    for src, dst in replacements:
        normalized = normalized.replace(src, dst)

    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def _handle_powers(text: str) -> str:
    text = re.sub(r"\b(\w+)\s+squared\b", r"\1**2", text)
    text = re.sub(r"\b(\w+)\s+square\b", r"\1**2", text)
    text = re.sub(r"\b(\w+)\s+cubed\b", r"\1**3", text)
    text = re.sub(r"\b(\w+)\s+cube\b", r"\1**3", text)
    return text


def _handle_percent(text: str) -> str:
    text = re.sub(r"(\d+(?:\.\d+)?)\s*percent of\s*(\d+(?:\.\d+)?)", r"(\1/100)*\2", text)
    text = re.sub(r"(\d+(?:\.\d+)?)\s*percent", r"(\1/100)", text)
    return text


def _handle_trig_degrees(text: str) -> str:
    pattern = r"\b(sin|cos|tan)\s+(-?\d+(?:\.\d+)?)\b"
    return re.sub(pattern, r"\1(\2*pi/180)", text)


def _fix_x_as_multiply(text: str) -> str:
    tokens = text.split()
    out: list[str] = []

    def is_number(tok: str) -> bool:
        return re.fullmatch(r"-?\d+(?:\.\d+)?", tok) is not None

    for i, token in enumerate(tokens):
        if token != "x":
            out.append(token)
            continue

        prev_tok = tokens[i - 1] if i > 0 else ""
        next_tok = tokens[i + 1] if i + 1 < len(tokens) else ""

        if is_number(prev_tok) and is_number(next_tok):
            out.append("*")
            continue

        if is_number(prev_tok) and next_tok:
            out.append("*")
            continue

        out.append("x")

    return " ".join(out)


def _detect_incomplete(text: str) -> bool:
    if not text:
        return True
    return bool(re.search(r"[+\-*/%]$", text)) or text.endswith("**")


def _needs_ollama(text: str) -> bool:
    words = re.findall(r"[a-zA-Z]+", text)
    allowed = {"sin", "cos", "tan", "sqrt", "log", "factorial", "pi", "e", "x"}
    return any(w not in allowed for w in words)


def normalize_expression(text: str) -> str:
    normalized = _replace_word_numbers(text)
    normalized = _normalize_phrases(normalized)
    normalized = _handle_powers(normalized)
    normalized = _handle_percent(normalized)
    normalized = _fix_x_as_multiply(normalized)
    normalized = _handle_trig_degrees(normalized)
    return normalized


def parse(text: str) -> ParseResult:
    raw = text.lower().strip()

    if "repeat result" in raw or "repeat" in raw or "last result" in raw:
        return ParseResult(intent="repeat", raw_text=text)

    if "clear history" in raw or "reset history" in raw:
        return ParseResult(intent="clear_history", raw_text=text)

    if "show history" in raw or "history" in raw:
        return ParseResult(intent="show_history", raw_text=text)

    if any(word in raw for word in ["exit", "quit", "close", "stop program"]):
        return ParseResult(intent="exit", raw_text=text)

    raw = raw.replace("equals", "=")
    raw = raw.replace("equal to", "=")

    cleaned = clean_text(raw)

    if not cleaned:
        return ParseResult(intent="empty", raw_text=text)

    if cleaned.startswith("plot ") or cleaned.startswith("graph "):
        expr = cleaned.replace("plot ", "", 1).replace("graph ", "", 1).strip()
        expr = normalize_expression(_apply_language_translation(expr))
        return ParseResult(intent="plot", expression=expr, raw_text=text, incomplete=_detect_incomplete(expr))

    if cleaned.startswith("solve "):
        expr = cleaned.replace("solve ", "", 1).strip()
        expr = normalize_expression(_apply_language_translation(expr))
        return ParseResult(intent="solve", expression=expr, raw_text=text, incomplete=_detect_incomplete(expr))

    if cleaned.startswith("differentiate ") or cleaned.startswith("derive "):
        expr = cleaned.replace("differentiate ", "", 1).replace("derive ", "", 1).strip()
        expr = normalize_expression(_apply_language_translation(expr))
        return ParseResult(intent="differentiate", expression=expr, raw_text=text, incomplete=_detect_incomplete(expr))

    if cleaned.startswith("integrate "):
        expr = cleaned.replace("integrate ", "", 1).strip()
        expr = normalize_expression(_apply_language_translation(expr))
        return ParseResult(intent="integrate", expression=expr, raw_text=text, incomplete=_detect_incomplete(expr))

    translated = _apply_language_translation(cleaned)
    normalized = normalize_expression(translated)

    if "=" in normalized:
        return ParseResult(intent="solve", expression=normalized, raw_text=text, incomplete=_detect_incomplete(normalized))

    return ParseResult(
        intent="calculate",
        expression=normalized,
        raw_text=text,
        incomplete=_detect_incomplete(normalized),
        needs_ollama=_needs_ollama(normalized),
    )


def _apply_language_translation(text: str) -> str:
    language = detect_language(text)
    if language in {"hi", "te"} or has_multilingual_numbers(text):
        return translate_numbers(text)
    return translate_numbers(text)
