"""Command-line entry point for the Yaounde Urban Language Analyzer."""

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from analysis import analyze_corpus, format_report
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


BASE_DIR = Path(__file__).resolve().parent


PLAIN_WORDS = {
    "drop": "take",
    "block": "stop",
    "take": "take",
    "for": "to",
    "at": "at",
    "me": "me",
    "you": "you",
    "driver": "driver",
    "manager": "manager",
    "junction": "junction",
    "sala": "work",
    "bendskin": "motorcycle taxi",
    "mon": "my",
    "ma": "my",
    "le": "the",
}


def translate_to_plain_language(sentence: str) -> str:
    """Provide a readable English interpretation for recognized words."""
    words = sentence.split()
    translated = [PLAIN_WORDS.get(word.lower(), word) for word in words]
    result = " ".join(translated).lower()
    result = result.replace("motorcycle taxi junction", "the motorcycle taxi stop")
    result = result.replace("driver take me", "driver, take me")
    result = result.replace("the manager a stop my work", "the manager has stopped my work")
    return result[:1].upper() + result[1:] + ("." if result else "")


def analyze(sentence: str) -> None:
    tokens = tokenize(sentence)
    token_rows = [(t.value, t.kind, t.lang) for t in tokens]
    result = parse(tokens)
    print(f"  Tokens: {token_rows}")
    print(f"  Result: {result.message}")
    if result.accepted:
        print(f"  Plain language: {translate_to_plain_language(sentence)}")
    else:
        print("  Plain language: Unable to translate an invalid phrase.")


def print_grammar_pipeline() -> None:
    print("=== Grammar pipeline ===")
    print()
    print("1. Raw CFG (as derived from collected sentence patterns):")
    print(format_grammar(RAW_GRAMMAR))
    print()
    print("2. After left-recursion elimination:")
    print(format_grammar(NO_LEFT_RECURSION_GRAMMAR))
    print()
    print("3. After left-factoring (LL(1)-ready grammar):")
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


def print_corpus_stats(sentences: list[str]) -> None:
    print("=== Token frequency & variation analysis ===")
    print()
    report = analyze_corpus(sentences)
    print(format_report(report))
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
    print("=== Yaounde Urban Language Analyzer ===")
    print()

    test_file = BASE_DIR / "test_cases.txt"
    sentences = [
        line.strip()
        for line in test_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]

    print_grammar_pipeline()
    print_corpus_stats(sentences)

    print("=== Parsing test cases ===")
    print()
    for number, sentence in enumerate(sentences, start=1):
        print(f"Test Case {number}: '{sentence}'")
        analyze(sentence)
        print()

    interactive_mode()


if __name__ == "__main__":
    main()
