# Yaounde Urban Language Analyzer

A small Python compiler prototype for a Yaounde urban-language sentence pattern.
It demonstrates lexical analysis and context-free grammar parsing.

## Requirements

- Python 3.9 or newer

## Run

From this folder, run:

```powershell
py main.py
```

The program reads example sentences from `test_cases.txt`, prints their tokens,
and reports whether each sentence matches this grammar:

```text
S  -> NP VP
NP -> NOUN | PRON | PRON NOUN | DET NOUN | SLANG NOUN
VP -> VERB NP | VERB NP PP | AUX VERB NP
PP -> PREP NP
```

The program first analyzes the examples in `test_cases.txt`, then opens an
interactive prompt. Enter a phrase after `Phrase>` and type `q` to quit.
