"""Command-line entry point for the Yaounde Urban Language Analyzer."""

from pathlib import Path

from lexer import tokenize
from parser import parse


BASE_DIR = Path(__file__).resolve().parent


def analyze(sentence: str) -> None:
    tokens = tokenize(sentence)
    token_pairs = [token.as_tuple() for token in tokens]
    result = parse(tokens)
    print(f"  Tokens: {token_pairs}")
    print(f"  Result: {result.message}")


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

    for number, sentence in enumerate(sentences, start=1):
        print(f"Test Case {number}: '{sentence}'")
        analyze(sentence)
        print()

    interactive_mode()


if __name__ == "__main__":
    main()
