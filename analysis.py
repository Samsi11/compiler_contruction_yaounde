"""Token frequency and lexical-variation statistics over the collected corpus.

Covers the "analyze token frequency and variation" rubric line: how often
each word/category appears, how lexically diverse the corpus is, how much
code-mixing is present, which words are out of vocabulary, and how the same
concept (money, expensive, leave, ...) is expressed across languages.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass

from corpus import Entry
from lexer import VOCABULARY, normalize, tokenize

NOT_WORDS = ("INVALID", "QMARK")
LANGUAGES = ("EN", "FR", "PDG", "SLG")


@dataclass
class TopicStats:
    sentences: int
    tokens: int
    code_mixed_sentences: int


@dataclass
class CorpusReport:
    sentence_count: int
    token_count: int
    avg_sentence_length: float
    word_frequency: Counter
    pos_distribution: Counter
    language_distribution: Counter
    type_token_ratio: float
    code_mixing_ratio: float
    code_mixed_sentence_count: int
    out_of_vocabulary: Counter
    topics: dict[str, TopicStats]
    concept_variation: dict[str, Counter]


def analyze_corpus(entries: list[Entry]) -> CorpusReport:
    all_tokens = []
    topic_sentences: Counter = Counter()
    topic_tokens: Counter = Counter()
    topic_mixed: Counter = Counter()
    mixed_total = 0
    concept_variation: dict[str, Counter] = defaultdict(Counter)

    for entry in entries:
        tokens = tokenize(entry.text)
        all_tokens.extend(tokens)
        languages = {t.lang for t in tokens if t.lang in LANGUAGES}
        topic_sentences[entry.topic] += 1
        topic_tokens[entry.topic] += len(tokens)
        if len(languages) > 1:
            mixed_total += 1
            topic_mixed[entry.topic] += 1
        for token in tokens:
            vocab = VOCABULARY.get(normalize(token.value))
            if vocab and vocab.concept and token.kind == vocab.kind:
                concept_variation[vocab.concept][(token.value.lower(), token.lang)] += 1

    words = [t for t in all_tokens if t.kind not in NOT_WORDS]
    word_frequency = Counter(t.value.lower() for t in words)
    classified = [t for t in all_tokens if t.lang in LANGUAGES]
    non_english = [t for t in classified if t.lang != "EN"]

    return CorpusReport(
        sentence_count=len(entries),
        token_count=len(all_tokens),
        avg_sentence_length=len(all_tokens) / len(entries) if entries else 0.0,
        word_frequency=word_frequency,
        pos_distribution=Counter(t.kind for t in all_tokens),
        language_distribution=Counter(t.lang for t in classified),
        type_token_ratio=len(word_frequency) / len(words) if words else 0.0,
        code_mixing_ratio=len(non_english) / len(classified) if classified else 0.0,
        code_mixed_sentence_count=mixed_total,
        out_of_vocabulary=Counter(t.value.lower() for t in all_tokens if t.kind == "WORD"),
        topics={
            topic: TopicStats(topic_sentences[topic], topic_tokens[topic], topic_mixed[topic])
            for topic in topic_sentences
        },
        concept_variation={c: v for c, v in concept_variation.items() if len(v) > 1},
    )


def format_report(report: CorpusReport, top_n: int = 15) -> str:
    lines = [
        f"Utterances analyzed : {report.sentence_count}",
        f"Total tokens        : {report.token_count} "
        f"(average {report.avg_sentence_length:.1f} per utterance)",
        f"Type-token ratio    : {report.type_token_ratio:.3f} "
        "(distinct words / total words; higher = more lexically varied)",
        f"Code-mixing ratio   : {report.code_mixing_ratio:.1%} of language-tagged tokens "
        "are French/Pidgin/slang rather than English",
        f"Code-mixed utterances: {report.code_mixed_sentence_count} of {report.sentence_count} "
        "contain words from two or more languages",
        "",
        "Token types (POS):",
    ]
    for kind, count in report.pos_distribution.most_common():
        lines.append(f"  {kind:<9} {count}")

    lines += ["", "Language of tagged tokens (EN English, FR French, PDG Pidgin, SLG local slang):"]
    for lang, count in report.language_distribution.most_common():
        lines.append(f"  {lang:<9} {count}")

    lines += ["", f"Top {top_n} most frequent words:"]
    for word, count in report.word_frequency.most_common(top_n):
        lines.append(f"  {word:<15} {count}")

    lines += ["", "By topic (utterances / tokens / code-mixed utterances):"]
    for topic, stats in sorted(report.topics.items()):
        lines.append(
            f"  {topic:<13} {stats.sentences:>3} / {stats.tokens:>3} / {stats.code_mixed_sentences:>3}"
        )

    lines += ["", "Concept variation (same meaning, different surface forms):"]
    for concept, forms in sorted(report.concept_variation.items()):
        rendered = ", ".join(f"{word} [{lang}] x{count}" for (word, lang), count in forms.most_common())
        lines.append(f"  {concept:<13} {rendered}")

    lines += ["", "Out-of-vocabulary words (tagged WORD):"]
    if report.out_of_vocabulary:
        for word, count in report.out_of_vocabulary.most_common():
            lines.append(f"  {word:<15} {count}")
    else:
        lines.append("  none")

    return "\n".join(lines)
