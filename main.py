"""Command-line entry point for the Yaounde Urban Language Analyzer.

    python main.py                 parse every collected utterance, then prompt
    python main.py --grammar       also print the grammar pipeline and LL(1) table
    python main.py --stats         also print token frequency / variation statistics
    python main.py --all           both of the above
    python main.py --no-interactive  skip the final prompt
"""

import sys

from analysis import analyze_corpus, format_report
from corpus import gloss_for, load_corpus, test_entries
from grammar import (
    FIRST,
    FOLLOW,
    LL1_GRAMMAR,
    NO_LEFT_RECURSION_GRAMMAR,
    RAW_GRAMMAR,
    TABLE,
    format_grammar,
    format_sets,
    format_table,
)
from lexer import tokenize
from parser import parse

sys.stdout.reconfigure(encoding="utf-8")


def analyze(sentence: str) -> bool:
    """Print tokens and the parse verdict; return True if accepted."""
    tokens = tokenize(sentence)
    result = parse(tokens)
    print(f"  Tokens: {[(t.value, t.kind, t.lang) for t in tokens]}")
    print(f"  Result: {result.message}")
    gloss = gloss_for(sentence)
    if gloss:
        print(f"  Contributor's translation: {gloss}")
    return result.accepted


def print_grammar_pipeline() -> None:
    print("=== Grammar pipeline ===")
    print()
    print("1. Raw CFG (as derived from the collected utterance patterns):")
    print(format_grammar(RAW_GRAMMAR))
    print()
    print("2. After left-recursion elimination (UTT, ADJP, NBAR were left-recursive):")
    print(format_grammar(NO_LEFT_RECURSION_GRAMMAR))
    print()
    print("3. After left-factoring (CLAUSE, COMP, NBAR shared prefixes):")
    print(format_grammar(LL1_GRAMMAR))
    print()
    print("4. FIRST sets:")
    print(format_sets(FIRST))
    print()
    print("5. FOLLOW sets:")
    print(format_sets(FOLLOW))
    print()
    print("6. LL(1) parsing table:")
    print(format_table(TABLE))
    print()


def print_corpus_stats() -> None:
    print("=== Token frequency & variation analysis ===")
    print()
    print(format_report(analyze_corpus(test_entries())))
    print()


def run_corpus() -> None:
    entries = test_entries()
    print(f"=== Parsing {len(entries)} collected utterances ===")
    print()
    accepted = mismatches = 0
    for entry in entries:
        print(f"{entry.id} [{entry.topic}, {entry.contributor}]: '{entry.text}'")
        ok = analyze(entry.text)
        accepted += ok
        verdict = "ACCEPT" if ok else "REJECT"
        if verdict != entry.expected:
            mismatches += 1
            print(f"  !! expected {entry.expected} but got {verdict}")
        elif entry.note:
            print(f"  Note: {entry.note}")
        print()
    excluded = len(load_corpus()) - len(entries)
    print(f"Accepted {accepted}, rejected {len(entries) - accepted} "
          f"(of {len(entries)} parsed; {excluded} unusable form entries excluded); "
          f"{mismatches} differ from the expected label.")
    print()


def interactive_mode() -> None:
    print("Enter a phrase to compile, or type 'q' to quit.")
    while True:
        try:
            sentence = input("Phrase> ").strip()
        except EOFError:
            print()
            break
        if sentence.lower() in {"q", "quit", "exit"}:
            break
        if sentence:
            analyze(sentence)
            print()


def main() -> None:
    args = set(sys.argv[1:])
    print("=== Yaounde Urban Language Analyzer ===")
    print()
    if args & {"--grammar", "--all"}:
        print_grammar_pipeline()
    if args & {"--stats", "--all"}:
        print_corpus_stats()
    run_corpus()
    if "--no-interactive" not in args:
        interactive_mode()


if __name__ == "__main__":
    main()
