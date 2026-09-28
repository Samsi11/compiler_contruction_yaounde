# Yaounde Urban Language Analyzer

Lexical and syntactic analysis of informal urban speech in Yaounde
(English, French, Pidgin and local slang), built for CS4110 Compiler
Construction. A regex-based lexer feeds a table-driven LL(1) parser that
checks each collected utterance against a context-free grammar.

## Requirements

- Python 3.9 or newer (Tkinter is needed only for the desktop interface)

## Run

```powershell
py gui.py                      # desktop interface
py main.py                     # parse every collected utterance, then an interactive prompt
py main.py --all               # also print the grammar pipeline and token statistics
py main.py --grammar           # raw CFG -> left-recursion removal -> left-factoring, FIRST/FOLLOW, LL(1) table
py main.py --stats             # token frequency and variation analysis
py main.py --no-interactive    # skip the final prompt
py -m unittest -v              # regression tests
```

## Data

`corpus.csv` holds the survey responses (9 contributors, referred to as
P01-P09). Each row keeps the text exactly as typed, the contributor's own
plain-English translation, the topic, and the label the grammar is expected
to give it (`ACCEPT` or `REJECT`) with a note explaining every rejection.
Rows marked `EXCLUDED` (empty answers, or columns filled in swapped) are kept
for transparency but are not parsed.

`vocabulary.csv` (`word,kind,lang,concept,note`) is the lexicon:

- `kind` is the token type: NOUN, VERB, PRON, DET, ADJ, ADV, AUX, COP, NEG,
  NEG_PRE, PREP, CONJ, NUM, SLANG (exclamations and discourse words), PART
  (sentence-final particles).
- `lang` is EN, FR, PDG (Pidgin), SLG (local slang) or UNK (uncertain).
- `concept` groups words that mean the same thing in different languages,
  used by the variation analysis.

Add new words there and the lexer's regex rules regenerate automatically.

## How it works

1. **Lexer** (`lexer.py`): one regex rule per token type, generated from
   `vocabulary.csv` (multi-word entries such as `ndon ya` allowed), then
   fallback rules for numbers (`400`, `2k`, `5000frs`), `?`, unknown words
   (`WORD`) and any other character (`INVALID`). Nothing is silently dropped.
2. **Grammar** (`grammar.py`): the raw CFG is written the natural way, then
   generic algorithms remove left recursion (`UTT`, `ADJP`, `NBAR`), left-factor
   shared prefixes (`CLAUSE`, `COMP`, `NBAR`), compute FIRST and FOLLOW sets and
   build the LL(1) table. A conflict in the table raises an error.
3. **Parser** (`parser.py`): stack-based table-driven LL(1) parser with a full
   step trace and error messages that name the offending token and the tokens
   that would have been accepted.
4. **Analysis** (`analysis.py`): token and type frequencies, type-token ratio,
   code-mixing ratio, per-topic figures, out-of-vocabulary words and concept
   variation.

The grammar models the common shapes in the data: imperatives, subject +
verb phrase, copular and predicate-adjective clauses, Pidgin aspect markers
(`don`, `di`, `fit`, `do`), French `ne ... pas` negation, double objects
(`fund me fapnkolo`), clauses joined by `make` / `et`, noun-phrase fragments,
leading exclamations and sentence-final particles. Utterances outside these
shapes are rejected on purpose; `corpus.csv` records why for each one.

The lexicon gives each word a single tag, so words with several roles
(`la` article or postposed "there", `chop` verb or noun, `dey`, `na`) cannot be
resolved by this LL(1) parser. Those rejections are documented in the corpus
notes.
