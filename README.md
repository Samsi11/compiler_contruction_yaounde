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

The program reads example sentences from `test_cases.txt`, prints their tokens,
and reports whether each sentence matches this grammar:

```text
S  -> NP VP
S  -> NP VP CONJ S
NP -> NOUN | PRON | PRON NOUN | DET NOUN | DET ADJ NOUN | ADJ NOUN | SLANG NOUN
VP -> VERB NP | VERB NP PP | VERB NP PP PP | AUX VERB NP
PP -> PREP NP
```

Keywords are matched case-insensitively. Unknown words are reported as `WORD`,
while punctuation and other invalid characters are preserved and rejected by
the parser instead of being silently ignored.

The program first analyzes the examples in `test_cases.txt`, then opens an
interactive prompt. Enter a phrase after `Phrase>` and type `q` to quit.
For accepted phrases, it also displays a simple plain-language English
interpretation.
