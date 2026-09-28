"""Loader for corpus.csv, the collected survey data used as test cases."""

import csv
from dataclasses import dataclass
from pathlib import Path

CORPUS_PATH = Path(__file__).resolve().parent / "corpus.csv"


@dataclass(frozen=True)
class Entry:
    id: str
    topic: str
    contributor: str
    source_cell: str
    text: str
    gloss: str
    expected: str
    note: str


def load_corpus(path: Path = CORPUS_PATH) -> list[Entry]:
    with path.open(encoding="utf-8", newline="") as handle:
        return [
            Entry(
                row["id"], row["topic"], row["contributor"], row["source_cell"],
                row["text"], row["gloss"], row["expected"], row["note"],
            )
            for row in csv.DictReader(handle)
        ]


def test_entries(entries: list[Entry] | None = None) -> list[Entry]:
    """Entries that are parsed: everything except rows excluded as unusable."""
    return [e for e in (entries or load_corpus()) if e.expected in ("ACCEPT", "REJECT")]


def find_entry(text: str) -> Entry | None:
    """The corpus entry with this exact text (parsed entries win over excluded ones)."""
    wanted = " ".join(text.split()).lower()
    entries = load_corpus()
    ordered = sorted(entries, key=lambda e: e.expected not in ("ACCEPT", "REJECT"))
    return next((e for e in ordered if " ".join(e.text.split()).lower() == wanted), None)


def gloss_for(text: str) -> str | None:
    """The contributor's own plain-English translation, if this text is in the corpus."""
    entry = find_entry(text)
    return entry.gloss if entry and entry.gloss else None
