"""Grammar pipeline: left-recursion removal, left-factoring, FIRST/FOLLOW,
and LL(1) parsing-table construction, implemented as generic algorithms over
a plain CFG dictionary (not hand-derived for one specific grammar).

A grammar is represented as ``dict[nonterminal, tuple[production, ...]]``
where each production is a tuple of symbols, and an empty tuple ``()``
denotes an epsilon production. A symbol is a nonterminal iff it is a key of
the grammar dict; anything else is treated as a terminal (a token kind
produced by the lexer).
"""

from collections import defaultdict

START_SYMBOL = "S"
EPSILON = "ε"
END_MARKER = "$"

# The raw grammar, written the natural way for the collected utterances
# (before any transformation). Nonterminals are listed top-down so that the
# left-recursion algorithm needs no substitution steps.
#
#   S      utterance: optional leading exclamation, clauses, optional tail
#   UTT    clauses chained by a conjunction (left-recursive on purpose)
#   CLAUSE subject + predicate, a bare noun phrase, an imperative, or a
#          subjectless copular/adverbial fragment
#   PRED   verb phrase | copula + complement | aspect AUX + ... | NEG + ...
#   VP     French ne...pas negation or a plain verb, then objects/adverbs/PPs
#   NBAR   noun compounds (left-recursive), adjectives and numerals
#   TAIL   sentence-final particle or exclamation, then optional '?'
RAW_GRAMMAR: dict[str, tuple[tuple[str, ...], ...]] = {
    "S": (("LEAD", "UTT", "TAIL"),),
    "LEAD": (("SLANG",), ()),
    "UTT": (
        ("UTT", "CONJ", "CLAUSE"),
        ("CONJ", "CLAUSE"),
        ("CLAUSE",),
    ),
    "CLAUSE": (
        ("NP", "PRED"),
        ("NP",),
        ("VP",),
        ("COP", "COMP"),
        ("ADV", "ADJP"),
    ),
    "PRED": (
        ("VP",),
        ("COP", "COMP"),
        ("AUX", "AUXC"),
        ("NEG", "NEGC"),
        ("ADJP",),
    ),
    "AUXC": (("ADJP",), ("VP",)),
    "NEGC": (("ADJP",), ("VP",)),
    "COMP": (("ADJP",), ("ADV",), ("ADV", "ADJP")),
    "ADJP": (("ADJP", "ADJ"), ("ADJ",)),
    "VP": (
        ("NEG_PRE", "VERB", "NEG", "VP1"),
        ("VERB", "VP1"),
    ),
    "VP1": (
        ("PRON", "VPOBJ"),
        ("NPN", "VP2"),
        ("PP", "VP2"),
        ("ADV", "VP2"),
        (),
    ),
    "VPOBJ": (("NP", "VP2"), ("VP2",)),
    "VP2": (("PP", "VP2"), ()),
    "PP": (("PREP", "NP"),),
    "NP": (("PRON",), ("NPN",)),
    "NPN": (("DET", "NBAR"), ("NBAR",)),
    "NBAR": (
        ("NBAR", "NOUN"),
        ("NOUN",),
        ("ADJ", "NOUN"),
        ("ADJ", "NUM"),
        ("NUM",),
    ),
    "TAIL": (("TAILW", "QM"),),
    "TAILW": (("PART",), ("SLANG",), ()),
    "QM": (("QMARK",), ()),
}


def _fresh_name(base: str, taken: set[str]) -> str:
    name = base + "'"
    while name in taken:
        name += "'"
    return name


def eliminate_left_recursion(
    grammar: dict[str, tuple[tuple[str, ...], ...]],
) -> dict[str, tuple[tuple[str, ...], ...]]:
    """Standard textbook algorithm (Aho et al.) for immediate + indirect
    left recursion, applied in nonterminal-declaration order."""
    work: dict[str, list[tuple[str, ...]]] = {k: list(v) for k, v in grammar.items()}
    order = list(work.keys())

    for i, a_i in enumerate(order):
        for a_j in order[:i]:
            expanded = []
            for prod in work[a_i]:
                if prod and prod[0] == a_j:
                    for sub in work[a_j]:
                        expanded.append(sub + prod[1:])
                else:
                    expanded.append(prod)
            work[a_i] = expanded

        recursive, non_recursive = [], []
        for prod in work[a_i]:
            if prod and prod[0] == a_i:
                recursive.append(prod[1:])
            else:
                non_recursive.append(prod)

        if recursive:
            new_nt = _fresh_name(a_i, set(work.keys()))
            work[a_i] = [beta + (new_nt,) for beta in non_recursive] or [(new_nt,)]
            work[new_nt] = [alpha + (new_nt,) for alpha in recursive] + [()]

    return {k: tuple(v) for k, v in work.items()}


def _common_prefix_length(productions: list[tuple[str, ...]]) -> int:
    shortest = min(len(p) for p in productions)
    length = 0
    while length < shortest and len({p[length] for p in productions}) == 1:
        length += 1
    return length


def left_factor(
    grammar: dict[str, tuple[tuple[str, ...], ...]],
) -> dict[str, tuple[tuple[str, ...], ...]]:
    """Repeatedly factor out common prefixes until no nonterminal has two
    productions sharing a first symbol."""
    work: dict[str, list[tuple[str, ...]]] = {k: list(v) for k, v in grammar.items()}
    changed = True
    while changed:
        changed = False
        for nt in list(work.keys()):
            groups: dict[str, list[tuple[str, ...]]] = defaultdict(list)
            for prod in work[nt]:
                groups[prod[0] if prod else ""].append(prod)
            for first_symbol, group in groups.items():
                if first_symbol and len(group) > 1:
                    prefix_len = _common_prefix_length(group)
                    if prefix_len >= 1:
                        prefix = group[0][:prefix_len]
                        new_nt = _fresh_name(nt, set(work.keys()))
                        work[new_nt] = [p[prefix_len:] for p in group]
                        remaining = [p for p in work[nt] if p not in group]
                        remaining.append(prefix + (new_nt,))
                        work[nt] = remaining
                        changed = True
                        break
            if changed:
                break
    return {k: tuple(v) for k, v in work.items()}


def first_of_sequence(
    sequence: tuple[str, ...],
    first_sets: dict[str, set[str]],
    grammar: dict[str, tuple[tuple[str, ...], ...]],
) -> set[str]:
    result: set[str] = set()
    for symbol in sequence:
        if symbol not in grammar:
            result.add(symbol)
            return result
        result.update(first_sets[symbol] - {EPSILON})
        if EPSILON not in first_sets[symbol]:
            return result
    result.add(EPSILON)
    return result


def compute_first_sets(
    grammar: dict[str, tuple[tuple[str, ...], ...]],
) -> dict[str, set[str]]:
    first_sets: dict[str, set[str]] = {nt: set() for nt in grammar}
    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.items():
            for prod in productions:
                if not prod:
                    addition = {EPSILON}
                else:
                    addition = first_of_sequence(prod, first_sets, grammar)
                before = len(first_sets[nt])
                first_sets[nt].update(addition)
                if len(first_sets[nt]) != before:
                    changed = True
    return first_sets


def compute_follow_sets(
    grammar: dict[str, tuple[tuple[str, ...], ...]],
    first_sets: dict[str, set[str]],
    start_symbol: str = START_SYMBOL,
) -> dict[str, set[str]]:
    follow_sets: dict[str, set[str]] = {nt: set() for nt in grammar}
    follow_sets[start_symbol].add(END_MARKER)
    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.items():
            for prod in productions:
                for i, symbol in enumerate(prod):
                    if symbol not in grammar:
                        continue
                    rest = prod[i + 1:]
                    rest_first = (
                        first_of_sequence(rest, first_sets, grammar) if rest else {EPSILON}
                    )
                    before = len(follow_sets[symbol])
                    follow_sets[symbol].update(rest_first - {EPSILON})
                    if EPSILON in rest_first:
                        follow_sets[symbol].update(follow_sets[nt])
                    if len(follow_sets[symbol]) != before:
                        changed = True
    return follow_sets


class GrammarConflict(Exception):
    """Raised when the grammar is not LL(1) (two productions in one cell)."""


def build_ll1_table(
    grammar: dict[str, tuple[tuple[str, ...], ...]],
    first_sets: dict[str, set[str]],
    follow_sets: dict[str, set[str]],
) -> dict[tuple[str, str], tuple[str, ...]]:
    table: dict[tuple[str, str], tuple[str, ...]] = {}
    conflicts: list[str] = []
    for nt, productions in grammar.items():
        for prod in productions:
            prod_first = (
                first_of_sequence(prod, first_sets, grammar) if prod else {EPSILON}
            )
            terminals = prod_first - {EPSILON}
            if EPSILON in prod_first:
                terminals = terminals | follow_sets[nt]
            for terminal in terminals:
                key = (nt, terminal)
                if key in table and table[key] != prod:
                    conflicts.append(
                        f"{nt}/{terminal}: {table[key]} vs {prod}"
                    )
                table[key] = prod
    if conflicts:
        raise GrammarConflict("; ".join(conflicts))
    return table


# --- Build the pipeline once, at import time, over the raw grammar --------

NO_LEFT_RECURSION_GRAMMAR = eliminate_left_recursion(RAW_GRAMMAR)
LL1_GRAMMAR = left_factor(NO_LEFT_RECURSION_GRAMMAR)
FIRST = compute_first_sets(LL1_GRAMMAR)
FOLLOW = compute_follow_sets(LL1_GRAMMAR, FIRST, START_SYMBOL)
TABLE = build_ll1_table(LL1_GRAMMAR, FIRST, FOLLOW)

TERMINALS = sorted(
    {symbol for prods in LL1_GRAMMAR.values() for prod in prods for symbol in prod}
    - set(LL1_GRAMMAR)
)


def expected_terminals(nonterminal: str) -> list[str]:
    """Terminals with a table entry for this nonterminal (what it accepts next)."""
    return sorted(terminal for (nt, terminal) in TABLE if nt == nonterminal)


def format_grammar(grammar: dict[str, tuple[tuple[str, ...], ...]]) -> str:
    lines = []
    for nt, productions in grammar.items():
        rhs = " | ".join(" ".join(p) if p else EPSILON for p in productions)
        lines.append(f"{nt} -> {rhs}")
    return "\n".join(lines)


def format_sets(sets: dict[str, set[str]]) -> str:
    lines = []
    for nt, symbols in sets.items():
        lines.append(f"{nt}: {{ {', '.join(sorted(symbols))} }}")
    return "\n".join(lines)


def format_table(table: dict[tuple[str, str], tuple[str, ...]]) -> str:
    lines = []
    for (nt, terminal), prod in sorted(table.items()):
        rhs = " ".join(prod) if prod else EPSILON
        lines.append(f"M[{nt}, {terminal}] = {nt} -> {rhs}")
    return "\n".join(lines)
