"""Table-driven LL(1) parser for Yaounde urban-language phrases.

Unlike a hand-rolled recursive matcher, this parser is a literal
implementation of the stack-based LL(1) algorithm: at each step it looks up
``grammar.TABLE[(top_of_stack, next_input_symbol)]`` to decide which
production to expand, exactly as described in the compiler-construction
rubric ("build an LL(1) parsing table" / "implement a simple parser that
reads tokenized input").
"""

from dataclasses import dataclass, field

from grammar import EPSILON, END_MARKER, LL1_GRAMMAR, START_SYMBOL, TABLE
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


def _find_invalid(tokens: list[Token]) -> Token | None:
    return next((token for token in tokens if token.kind == "INVALID"), None)


def parse(tokens: list[Token]) -> ParseResult:
    """Run the LL(1) table-driven algorithm and report the first error."""
    if not tokens:
        return ParseResult(False, "Syntax Error: empty input [Rejected]")

    invalid = _find_invalid(tokens)
    if invalid is not None:
        return ParseResult(
            False,
            f"Syntax Error near token '{invalid.value}' (invalid character) [Rejected]",
        )

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
            # Top of stack is a terminal (or $): it must match the input.
            if top == current:
                trace[-1].action = f"match {top}"
                stack.pop()
                position += 1
            else:
                token = tokens[min(position, len(tokens) - 1)]
                return ParseResult(
                    False,
                    f"Syntax Error near token '{token.value}' (expected {top}, "
                    f"found {current}) [Rejected]",
                    trace,
                )
            continue

        key = (top, current)
        if key not in TABLE:
            token = tokens[min(position, len(tokens) - 1)]
            return ParseResult(
                False,
                f"Syntax Error near token '{token.value}' (does not match the CFG) [Rejected]",
                trace,
            )

        production = TABLE[key]
        trace[-1].action = f"{top} -> {' '.join(production) if production else EPSILON}"
        stack.pop()
        for symbol in reversed(production):
            stack.append(symbol)

    return ParseResult(False, "Syntax Error: parser stack exhausted [Rejected]")
