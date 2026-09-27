# Yaounde Urban Language Analyzer

A small Python compiler prototype for a Yaounde urban-language sentence pattern.
It demonstrates lexical analysis and context-free grammar parsing.

## Requirements

- Python 3.9 or newer

## Run

From this folder, open the desktop interface with:

```powershell
py gui.py
```

The interface lets you enter a phrase or choose an example, analyze it with
the button or Ctrl+Enter, and inspect the parser result, plain-language
interpretation (for accepted phrases), and token table. It uses Tkinter,
which is included with most Python desktop installations.

To use the original command-line interface instead, run:

```powershell
py main.py
```

The program reads example sentences from `test_cases.txt`, prints the
full grammar pipeline (raw CFG, left-recursion elimination, left-factoring,
FIRST/FOLLOW sets, LL(1) parsing table), a corpus-wide token
frequency/variation report, and then tokenizes + parses each sentence:

```text
S  -> NP VP
S  -> NP VP CONJ S
NP -> NOUN | PRON | PRON NOUN | DET NOUN | DET ADJ NOUN | ADJ NOUN | SLANG NOUN
VP -> VERB NP | VERB NP PP | VERB NP PP PP | AUX VERB NP
PP -> PREP NP
```

`grammar.py` runs this raw CFG through left-recursion elimination and
left-factoring (the `S`/`VP` alternatives share a common prefix, so this step
is not a no-op) to produce an LL(1)-ready grammar, then computes FIRST/FOLLOW
sets and builds the LL(1) parsing table used by the table-driven parser in
`parser.py`.

## Vocabulary

Token categories (NOUN, VERB, SLANG, ...) are generated from
`vocabulary.csv` (columns: `word,kind,lang`) rather than hardcoded — add
real collected words there and the lexer's regex rules regenerate
automatically. `lang` tags each word as `EN`/`FR`/`PDG` and feeds the
code-mixing statistics in `analysis.py`. The current file is a small seed
list; entries not yet drawn from the group's own recorded transcripts should
be verified (or replaced) before being treated as authoritative in the
report.

Keywords are matched case-insensitively. Unrecognized words are reported as
`WORD`, while punctuation and other invalid characters are preserved and
rejected by the parser instead of being silently ignored.

The program first analyzes the examples in `test_cases.txt`, then opens an
interactive prompt. Enter a phrase after `Phrase>` and type `q` to quit.
For accepted phrases, it also displays a simple plain-language English
interpretation.
