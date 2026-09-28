"""Table-driven LL(1) parser for Yaounde urban-language utterances.

A literal implementation of the stack-based LL(1) algorithm: at each step it
looks up ``grammar.TABLE[(top_of_stack, next_input_symbol)]`` to decide which
production to expand, and matches terminals against the token kinds produced
by the lexer.
"""

from dataclasses import dataclass, field

from grammar import (
    END_MARKER,
    EPSILON,
    LL1_GRAMMAR,
    START_SYMBOL,
    TABLE,
    expected_terminals,
)
from lexer import Token


@dataclass
class ParseStep:
    stack: tuple[str, ...]
    remaining_input: tuple[str, ...]
    action: str


@dataclass
class ParseResult:
    accepted: bool
    message: str
    trace: list[ParseStep] = field(default_factory=list)
    error_token: Token | None = None


def _describe(token: Token) -> str:
    if token.kind == "INVALID":
        return "invalid character"
    if token.kind == "WORD":
        return "unknown word, not in the vocabulary"
    return f"unexpected {token.kind}"


def _reject(tokens: list[Token], position: int, expected: list[str], trace: list[ParseStep]) -> ParseResult:
    expected_text = ", ".join(expected)
    if position >= len(tokens):
        return ParseResult(
            False,
            f"Syntax Error at end of input (expected one of: {expected_text}) [Rejected]",
            trace,
        )
    token = tokens[position]
    return ParseResult(
        False,
        f"Syntax Error near token '{token.value}' ({_describe(token)}; "
        f"expected one of: {expected_text}) [Rejected]",
        trace,
        token,
    )


def parse(tokens: list[Token]) -> ParseResult:
    """Run the LL(1) table-driven algorithm and report the first error."""
    if not tokens:
        return ParseResult(False, "Syntax Error: empty input [Rejected]")

    input_symbols = [token.kind for token in tokens] + [END_MARKER]
    stack: list[str] = [END_MARKER, START_SYMBOL]
    trace: list[ParseStep] = []
    position = 0

    while stack:
        top = stack[-1]
        current = input_symbols[position]
        trace.append(ParseStep(tuple(stack), tuple(input_symbols[position:]), ""))

        if top == END_MARKER and current == END_MARKER:
            trace[-1].action = "accept"
            return ParseResult(True, "Syntax Valid (Accepted by CFG)", trace)

        if top not in LL1_GRAMMAR:
            if top == current:
                trace[-1].action = f"match {top}"
                stack.pop()
                position += 1
                continue
            trace[-1].action = "error"
            return _reject(tokens, position, [top], trace)

        production = TABLE.get((top, current))
        if production is None:
            trace[-1].action = "error"
            return _reject(tokens, position, expected_terminals(top), trace)

        trace[-1].action = f"{top} -> {' '.join(production) if production else EPSILON}"
        stack.pop()
        for symbol in reversed(production):
            stack.append(symbol)

    return ParseResult(False, "Syntax Error: parser stack exhausted [Rejected]", trace)
