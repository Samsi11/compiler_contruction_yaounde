"""Token frequency and lexical-variation statistics over a corpus.

Covers the "analyze token frequency and variation" rubric line: how often
each word/category appears, how lexically diverse the corpus is (type-token
ratio), and how much code-mixing (French/Pidgin/slang alongside English) is
actually present.
"""

from collections import Counter
from dataclasses import dataclass

from lexer import Token, tokenize


@dataclass
class CorpusReport:
    sentence_count: int
    token_count: int
    word_frequency: Counter
    pos_distribution: Counter
    language_distribution: Counter
    type_token_ratio: float
    code_mixing_ratio: float
    code_mixed_sentences: list[str]


def analyze_corpus(sentences: list[str]) -> CorpusReport:
    all_tokens: list[Token] = []
    code_mixed_sentences: list[str] = []

    for sentence in sentences:
        tokens = tokenize(sentence)
        all_tokens.extend(tokens)
        languages = {t.lang for t in tokens if t.kind not in ("INVALID", "WORD", "NUMBER")}
        if len(languages) > 1:
            code_mixed_sentences.append(sentence)

    word_frequency = Counter(t.value.lower() for t in all_tokens if t.kind != "INVALID")
    pos_distribution = Counter(t.kind for t in all_tokens)
    language_distribution = Counter(
        t.lang for t in all_tokens if t.kind not in ("INVALID",)
    )

    classified = [t for t in all_tokens if t.kind not in ("INVALID",)]
    non_english = [t for t in classified if t.lang not in ("EN", "UNK")]
    code_mixing_ratio = len(non_english) / len(classified) if classified else 0.0

    distinct_words = len(word_frequency)
    total_words = sum(word_frequency.values())
    type_token_ratio = distinct_words / total_words if total_words else 0.0

    return CorpusReport(
        sentence_count=len(sentences),
        token_count=len(all_tokens),
        word_frequency=word_frequency,
        pos_distribution=pos_distribution,
        language_distribution=language_distribution,
        type_token_ratio=type_token_ratio,
        code_mixing_ratio=code_mixing_ratio,
        code_mixed_sentences=code_mixed_sentences,
    )


def format_report(report: CorpusReport, top_n: int = 15) -> str:
    lines = [
        f"Sentences analyzed : {report.sentence_count}",
        f"Total tokens        : {report.token_count}",
        f"Type-token ratio    : {report.type_token_ratio:.3f} "
        "(distinct words / total words -- higher = more lexically varied)",
        f"Code-mixing ratio   : {report.code_mixing_ratio:.1%} of classified tokens "
        "are French/Pidgin/slang rather than English",
        "",
        "POS distribution:",
    ]
    for kind, count in report.pos_distribution.most_common():
        lines.append(f"  {kind:<8} {count}")

    lines.append("")
    lines.append("Language distribution:")
    for lang, count in report.language_distribution.most_common():
        lines.append(f"  {lang:<8} {count}")

    lines.append("")
    lines.append(f"Top {top_n} most frequent words:")
    for word, count in report.word_frequency.most_common(top_n):
        lines.append(f"  {word:<15} {count}")

    if report.code_mixed_sentences:
        lines.append("")
        lines.append("Sentences exhibiting code-mixing:")
        for sentence in report.code_mixed_sentences:
            lines.append(f"  - {sentence}")

    return "\n".join(lines)
