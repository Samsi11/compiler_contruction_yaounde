"""Lexer for a small Yaounde urban-language prototype."""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Token:
    kind: str
    value: str

    def as_tuple(self) -> tuple[str, str]:
        return self.kind, self.value


KEYWORDS = {
    "drop": "VERB",
    "block": "VERB",
    "take": "VERB",
    "Driver": "NOUN",
    "manager": "NOUN",
    "junction": "NOUN",
    "sala": "NOUN",
    "me": "PRON",
    "you": "PRON",
    "Le": "PRON",
    "for": "PREP",
    "at": "PREP",
    "a": "AUX",
    "an": "DET",
    "the": "DET",
    "my": "DET",
    "mon": "DET",
    "ma": "DET",
    "Bendskin": "SLANG",
}


def tokenize(sentence: str) -> list[Token]:
    """Convert whitespace-separated words into classified tokens."""
    words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", sentence)
    return [Token(KEYWORDS.get(word, "WORD"), word) for word in words]
