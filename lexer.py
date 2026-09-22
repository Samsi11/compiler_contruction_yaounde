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
    "driver": "NOUN",
    "manager": "NOUN",
    "junction": "NOUN",
    "sala": "NOUN",
    "me": "PRON",
    "you": "PRON",
    "le": "PRON",
    "for": "PREP",
    "at": "PREP",
    "a": "AUX",
    "an": "DET",
    "the": "DET",
    "my": "DET",
    "mon": "DET",
    "ma": "DET",
    "and": "CONJ",
    "but": "CONJ",
    "big": "ADJ",
    "small": "ADJ",
    "fast": "ADJ",
    "bendskin": "SLANG",
}


def tokenize(sentence: str) -> list[Token]:
    """Convert input into tokens without silently discarding invalid text."""
    parts = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?|[^\s]", sentence)
    tokens = []
    for part in parts:
        lookup = part.lower()
        kind = KEYWORDS.get(lookup, "WORD")
        if not part[0].isalpha() and part[0] != "'":
            kind = "INVALID"
        tokens.append(Token(kind, part))
    return tokens
