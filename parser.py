"""A small context-free grammar parser for Yaounde urban-language phrases."""

from lexer import Token


GRAMMAR = {
    "S": (
        ("NP", "VP"),
        ("NP", "VP", "CONJ", "S"),
    ),
    "NP": (
        ("NOUN",),
        ("PRON",),
        ("PRON", "NOUN"),
        ("DET", "NOUN"),
        ("DET", "ADJ", "NOUN"),
        ("ADJ", "NOUN"),
        ("SLANG", "NOUN"),
    ),
    "VP": (
        ("VERB", "NP"),
        ("VERB", "NP", "PP"),
        ("VERB", "NP", "PP", "PP"),
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

    memo: dict[tuple[str, int], set[int]] = {}

    def match(symbol: str, position: int) -> set[int]:
        key = (symbol, position)
        if key in memo:
            return memo[key]
        if symbol not in GRAMMAR:
            if position < len(tokens) and tokens[position].kind == symbol:
                result = {position + 1}
            else:
                result = set()
            memo[key] = result
            return result

        results: set[int] = set()
        for production in GRAMMAR[symbol]:
            positions = {position}
            for part in production:
                next_positions = set()
                for current in positions:
                    next_positions.update(match(part, current))
                positions = next_positions
            results.update(positions)
        memo[key] = results
        return results

    if len(tokens) not in match("S", 0):
        invalid = next((token for token in tokens if token.kind == "INVALID"), None)
        token = invalid or tokens[-1]
        if invalid:
            detail = "invalid character"
        else:
            detail = "does not match the CFG"
        return ParseResult(
            False,
            f"Syntax Error near token '{token.value}' ({detail}) [Rejected]",
        )

    return ParseResult(True, "Syntax Valid (Accepted by CFG)")
