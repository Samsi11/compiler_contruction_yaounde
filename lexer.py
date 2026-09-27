"""Lexer for the Yaounde urban-language analyzer.

The lexical specification is data-driven: token *types* (NOUN, VERB, SLANG,
...) are each compiled into their own regex alternation straight from
``vocabulary.csv``, plus generic regex classes for numbers, unknown words,
and punctuation. This mirrors a LEX/FLEX rule set (ordered regex rules, each
tagged with the token type it produces) rather than a single catch-all
pattern followed by a dictionary lookup.
"""

import csv
import re
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VOCAB_PATH = BASE_DIR / "vocabulary.csv"


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    lang: str = "EN"

    def as_tuple(self) -> tuple[str, str]:
        return self.kind, self.value


def load_vocabulary(path: Path = VOCAB_PATH) -> dict[str, tuple[str, str]]:
    """word -> (POS kind, language tag), read from the editable CSV."""
    vocab: dict[str, tuple[str, str]] = {}
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            vocab[row["word"].strip().lower()] = (row["kind"].strip(), row["lang"].strip())
    return vocab


VOCABULARY = load_vocabulary()

# Language tag for the fallback categories below (unknown words, numbers).
UNKNOWN_LANG = "UNK"


def _build_master_pattern(vocab: dict[str, tuple[str, str]]) -> re.Pattern:
    """Compile one regex rule per token type, generated from the vocabulary."""
    by_kind: dict[str, list[str]] = {}
    for word, (kind, _lang) in vocab.items():
        by_kind.setdefault(kind, []).append(word)

    rules: list[str] = []
    for kind, words in by_kind.items():
        alternation = "|".join(re.escape(w) for w in sorted(words, key=len, reverse=True))
        # Word-boundary lookaround so "a" never matches inside "sala" or "an".
        rules.append(rf"(?P<{kind}>(?<![A-Za-zÀ-ÿ])(?i:{alternation})(?![A-Za-zÀ-ÿ]))")

    rules.append(r"(?P<NUMBER>\d+(?:[.,]\d+)?(?:frs|FCFA|f)?)")
    rules.append(r"(?P<WORD>[A-Za-zÀ-ÿ]+(?:'[A-Za-z]+)?)")
    rules.append(r"(?P<PUNCT>[^\sA-Za-zÀ-ÿ0-9])")
    return re.compile("|".join(rules))


MASTER_PATTERN = _build_master_pattern(VOCABULARY)


def tokenize(sentence: str) -> list[Token]:
    """Scan input into tokens without silently discarding invalid text."""
    tokens: list[Token] = []
    for match in MASTER_PATTERN.finditer(sentence):
        kind = match.lastgroup
        value = match.group()
        if kind == "PUNCT":
            tokens.append(Token("INVALID", value, UNKNOWN_LANG))
        elif kind == "NUMBER":
            tokens.append(Token("NUMBER", value, UNKNOWN_LANG))
        elif kind == "WORD":
            tokens.append(Token("WORD", value, UNKNOWN_LANG))
        else:
            _pos, lang = VOCABULARY[value.lower()]
            tokens.append(Token(kind, value, lang))
    return tokens
