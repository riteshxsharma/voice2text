from __future__ import annotations

from dataclasses import dataclass


PHRASE_MAP = {
    "begin equation": "BLOCK_OPEN",
    "end equation": "BLOCK_CLOSE",
    "open parenthesis": "(",
    "close parenthesis": ")",
    "open brace": "{",
    "close brace": "}",
    "new line": "\n",
    "alpha": r"\alpha",
    "beta": r"\beta",
    "gamma": r"\gamma",
    "pi": r"\pi",
    "equals": "=",
    "slash": "\\",
}

LONGEST_PHRASES = sorted(PHRASE_MAP, key=lambda item: len(item.split()), reverse=True)
CONTROL_TOKENS = {"BLOCK_OPEN", "BLOCK_CLOSE", "\n"}


@dataclass
class ConversionResult:
    emacs_text: str
    latex_text: str


def _tokenize(text: str) -> list[str]:
    words = text.replace("\r", " ").replace("\n", " ").lower().split()
    tokens: list[str] = []
    index = 0

    while index < len(words):
        matched = False
        for phrase in LONGEST_PHRASES:
            parts = phrase.split()
            if words[index : index + len(parts)] == parts:
                tokens.append(PHRASE_MAP[phrase])
                index += len(parts)
                matched = True
                break
        if matched:
            continue
        tokens.append(words[index])
        index += 1

    return tokens


def _combine_fractions(tokens: list[str]) -> list[str]:
    combined: list[str] = []
    index = 0

    while index < len(tokens):
        token = tokens[index]
        if (
            token == "over"
            and combined
            and index + 1 < len(tokens)
            and combined[-1] not in CONTROL_TOKENS
            and tokens[index + 1] not in CONTROL_TOKENS
        ):
            numerator = combined.pop()
            denominator = tokens[index + 1]
            combined.append(rf"\frac{{{numerator}}}{{{denominator}}}")
            index += 2
            continue
        combined.append(token)
        index += 1

    return combined


def _render(tokens: list[str]) -> str:
    lines: list[str] = []
    current: list[str] = []

    for token in tokens:
        if token == "BLOCK_OPEN":
            if current:
                lines.append(" ".join(current).strip())
                current = []
            lines.append(r"\[")
            continue
        if token == "BLOCK_CLOSE":
            if current:
                lines.append(" ".join(current).strip())
                current = []
            lines.append(r"\]")
            continue
        if token == "\n":
            lines.append(" ".join(current).strip())
            current = []
            continue
        current.append(token)

    if current:
        lines.append(" ".join(current).strip())

    cleaned = [line for line in lines if line]
    return "\n".join(cleaned).strip() + ("\n" if cleaned else "")


def convert_transcript(text: str) -> ConversionResult:
    tokens = _tokenize(text)
    tokens = _combine_fractions(tokens)
    rendered = _render(tokens)
    return ConversionResult(emacs_text=rendered, latex_text=rendered)
