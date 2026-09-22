"""Command-line entry point for the Yaounde Urban Language Analyzer."""

from pathlib import Path

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
    token_pairs = [token.as_tuple() for token in tokens]
    result = parse(tokens)
    print(f"  Tokens: {token_pairs}")
    print(f"  Result: {result.message}")
    if result.accepted:
        print(f"  Plain language: {translate_to_plain_language(sentence)}")
    else:
        print("  Plain language: Unable to translate an invalid phrase.")


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
