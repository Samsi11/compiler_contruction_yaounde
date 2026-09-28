"""Regression tests: lexer rules, grammar algorithms, and the collected corpus.

Run with:  python -m unittest -v
"""

import unittest

import grammar
from corpus import test_entries
from lexer import tokenize
from parser import parse


class LexerTests(unittest.TestCase):
    def kinds(self, text):
        return [(t.value, t.kind) for t in tokenize(text)]

    def test_dotted_abbreviation_is_one_token(self):
        self.assertEqual(self.kinds("E.N.E.O"), [("E.N.E.O", "NOUN")])

    def test_number_with_suffix(self):
        self.assertEqual(self.kinds("2k"), [("2k", "NUM")])
        self.assertEqual(self.kinds("100k"), [("100k", "NUM")])

    def test_two_word_exclamation(self):
        self.assertEqual(self.kinds("Ndon   ya"), [("Ndon   ya", "SLANG")])

    def test_question_mark_unknown_word_and_emoji(self):
        self.assertEqual(self.kinds("yacob?"), [("yacob", "WORD"), ("?", "QMARK")])
        self.assertEqual(self.kinds("\U0001F923"), [("\U0001F923", "INVALID")])

    def test_word_boundaries(self):
        self.assertEqual(self.kinds("sala"), [("sala", "WORD")])


class GrammarAlgorithmTests(unittest.TestCase):
    def test_left_recursion_elimination(self):
        result = grammar.eliminate_left_recursion({"A": (("A", "a"), ("b",))})
        self.assertEqual(result, {"A": (("b", "A'"),), "A'": (("a", "A'"), ())})

    def test_left_factoring(self):
        result = grammar.left_factor({"S": (("a", "b"), ("a", "c"))})
        self.assertEqual(result, {"S": (("a", "S'"),), "S'": (("b",), ("c",))})

    def test_project_grammar_is_ll1_and_was_transformed(self):
        self.assertNotEqual(grammar.NO_LEFT_RECURSION_GRAMMAR, grammar.RAW_GRAMMAR)
        self.assertNotEqual(grammar.LL1_GRAMMAR, grammar.NO_LEFT_RECURSION_GRAMMAR)
        self.assertIn("$", grammar.FOLLOW["S"])
        self.assertTrue(grammar.TABLE)


class CorpusTests(unittest.TestCase):
    def test_every_collected_utterance_gets_its_expected_verdict(self):
        for entry in test_entries():
            with self.subTest(entry=entry.id, text=entry.text):
                verdict = "ACCEPT" if parse(tokenize(entry.text)).accepted else "REJECT"
                self.assertEqual(verdict, entry.expected)


if __name__ == "__main__":
    unittest.main()
