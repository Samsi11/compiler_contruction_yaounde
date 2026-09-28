"""Lexer for the Yaounde urban-language analyzer.

The lexical specification is data-driven: each token *type* (NOUN, VERB,
SLANG, ...) is compiled into its own regex alternation straight from
``vocabulary.csv``, followed by generic regex rules for numeric literals,
the question mark, unknown words, and any other character. This mirrors a
LEX/FLEX rule set: ordered regex rules, each tagged with the token type it
produces, first match wins.
"""

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

BASE_DIR = Path(__file__).resolve().parent
VOCAB_PATH = BASE_DIR / "vocabulary.csv"

UNKNOWN_LANG = "UNK"
LETTERS = "A-Za-zÀ-ÿ"


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    lang: str = "EN"

    def as_tuple(self) -> tuple[str, str]:
        return self.kind, self.value


class VocabEntry(NamedTuple):
    kind: str
    lang: str
    concept: str


def normalize(word: str) -> str:
    return " ".join(word.lower().split())


def load_vocabulary(path: Path = VOCAB_PATH) -> dict[str, VocabEntry]:
    """normalized word -> (POS kind, language tag, concept), from the editable CSV."""
    vocab: dict[str, VocabEntry] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            vocab[normalize(row["word"])] = VocabEntry(
                row["kind"].strip(), row["lang"].strip(), (row.get("concept") or "").strip()
            )
    return vocab


VOCABULARY = load_vocabulary()

# Fixed rules that come after the vocabulary-generated ones: (group, regex).
FALLBACK_RULES = [
    ("NUMLIT", rf"\d+(?:[.,]\d+)?(?i:frs|fcfa|f|k)?(?![{LETTERS}0-9])"),
    ("QMARK", r"\?"),
    ("WORD", rf"[{LETTERS}]+(?:'[{LETTERS}]+)?"),
    ("PUNCT", r"\S"),
]


def build_rules(vocab: dict[str, VocabEntry]) -> list[tuple[str, str]]:
    """One (token type, regex) rule per vocabulary token type, then the fallbacks."""
    by_kind: dict[str, list[str]] = {}
    for word, entry in vocab.items():
        by_kind.setdefault(entry.kind, []).append(word)

    rules: list[tuple[str, str]] = []
    for kind, words in by_kind.items():
        alternation = "|".join(
            re.escape(w).replace(r"\ ", r"\s+") for w in sorted(words, key=len, reverse=True)
        )
        # Lookaround keeps a short word like "a" from matching inside "sala".
        rules.append((kind, rf"(?<![{LETTERS}])(?i:{alternation})(?![{LETTERS}])"))
    return rules + FALLBACK_RULES


RULES = build_rules(VOCABULARY)
MASTER_PATTERN = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in RULES))


def tokenize(sentence: str) -> list[Token]:
    """Scan input into tokens; characters no rule accepts become INVALID tokens."""
    tokens: list[Token] = []
    for match in MASTER_PATTERN.finditer(sentence):
        group = match.lastgroup
        value = match.group()
        if group == "PUNCT":
            tokens.append(Token("INVALID", value, UNKNOWN_LANG))
        elif group == "NUMLIT":
            tokens.append(Token("NUM", value, UNKNOWN_LANG))
        elif group in ("QMARK", "WORD"):
            tokens.append(Token(group, value, UNKNOWN_LANG))
        else:
            tokens.append(Token(group, value, VOCABULARY[normalize(value)].lang))
    return tokens
