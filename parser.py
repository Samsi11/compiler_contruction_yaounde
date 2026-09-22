"""A small context-free grammar parser for Yaounde urban-language phrases."""

from lexer import Token


GRAMMAR = {
    "S": (("NP", "VP"),),
    "NP": (
        ("NOUN",),
        ("PRON",),
        ("PRON", "NOUN"),
        ("DET", "NOUN"),
        ("SLANG", "NOUN"),
    ),
    "VP": (
        ("VERB", "NP"),
        ("VERB", "NP", "PP"),
        ("AUX", "VERB", "NP"),
    ),
    "PP": (("PREP", "NP"),),
}


class ParseResult:
    def __init__(self, accepted: bool, message: str):
        self.accepted = accepted
        self.message = message


def parse(tokens: list[Token]) -> ParseResult:
    """Validate a sentence against the grammar and report the first error."""
    if not tokens:
        return ParseResult(False, "Syntax Error: empty input [Rejected]")

    def match(symbol: str, position: int) -> set[int]:
        if symbol not in GRAMMAR:
            if position < len(tokens) and tokens[position].kind == symbol:
                return {position + 1}
            return set()

        results: set[int] = set()
        for production in GRAMMAR[symbol]:
            positions = {position}
            for part in production:
                next_positions = set()
                for current in positions:
                    next_positions.update(match(part, current))
                positions = next_positions
            results.update(positions)
        return results

    if len(tokens) not in match("S", 0):
        token = tokens[-1]
        return ParseResult(
            False,
            f"Syntax Error near token '{token.value}' "
            f"(does not match the CFG) [Rejected]",
        )

    return ParseResult(True, "Syntax Valid (Accepted by CFG)")
