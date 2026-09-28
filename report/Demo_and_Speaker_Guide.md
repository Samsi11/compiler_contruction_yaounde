# Demo and Speaker Guide — 9 minutes, 3 speakers, 3 minutes each

Slide notes already carry this script (View → Notes Page in PowerPoint, or the Presenter View notes pane). This file is a backup and a question-prep sheet.

## Running order

| Speaker | Slides | Topic | Target time |
|---|---|---|---|
| Speaker 1 | 1–4 | Title, the problem, survey → tokens, frequency & variation | ~3:00 |
| Speaker 2 | 5–8 | Grammar pipeline, left recursion/factoring, LL(1) table, the parser | ~3:00 |
| Speaker 3 | 9–12 | Live demo, results, why it's complex, conclusion | ~3:00 |

Total speaking ≈ 9:00, leaving about 1 minute of slack for handovers and the 10-minute slot.

## Before you start

1. Open `py gui.py` and leave it running in the background — don't launch it live, it takes a few seconds and eats your time.
2. Pre-load nothing; use the dropdown live so the audience sees you navigate it.
3. Have a terminal ready with `py main.py --no-interactive` already run once, scrolled to the bottom, as a fallback if the GUI misbehaves.
4. Know the four demo utterances by their IDs: **E05** (accepted, 3 languages), **F04** (accepted, parse tree), **T03** (rejected, `la`), and optionally **R03** or **E06** if time allows.

## Timing checkpoints

- End of slide 4 (Speaker 1 done): ~3:00 elapsed
- End of slide 8 (Speaker 2 done): ~6:00 elapsed
- End of slide 12 (Speaker 3 done): ~9:00 elapsed

If you're running long, cut the "Concept variation" bullet on slide 4 and the second worked example in slide 6 — say "see the report for the full detail" and move on.

## Likely questions and short answers

**Why LL(1) and not SLR(1)?**
The brief allows either. LL(1) was enough for our grammar — it built with zero conflicts, so there was no need for the more complex bottom-up construction.

**Why is your grammar only accepting 62%?**
Because the grammar models the most common shapes in our data, not every possible sentence. The 19 rejections are documented, each with the specific reason (unknown word, ambiguous word role, or an unmodelled construction like serial verbs).

**Isn't 62% designed to look good since you built the grammar from the same data?**
Yes — we say this openly in the report and the deck (slide 10). It measures how well the rules fit the sample, not how they'd generalize. A held-out test set is listed as future work.

**Why does `la` get rejected sometimes?**
Our lexicon gives each word exactly one tag. `la` is tagged as the French article (DET). When it's actually a postposed "there" (as in "Le pater la" = "the president [is] there"), the tag is wrong for that context, and the parser correctly reports a syntax error. Fixing this needs contextual/probabilistic tagging, not just a bigger dictionary.

**Is this real linguistic data?**
It's a written survey completed by 9 people on 14 September 2026, not audio transcription. We say this plainly — the brief expects transcribed speech, and we're honest that ours is typed. The phrases are still real, unedited, and full of the same code-mixing and mistakes.

**What's the difference between FIRST and FOLLOW?**
FIRST(X) is which token types can start something derived from X. FOLLOW(X) is which token types can legally come right after X. The parsing table combines both to decide, for each (symbol, next-token) pair, which rule to expand.

**How many tests do you have, and what do they check?**
9 automated tests: lexer edge cases (dotted abbreviations, numeric suffixes, emoji), the two grammar algorithms on small example grammars, and one that re-parses all 50 real utterances and fails if any verdict changes from what's recorded in the corpus.

**What would you do with more time?**
Collect actual spoken/transcribed data, add contextual tagging to resolve ambiguous words like `la`/`chop`/`dey`/`na`, and try a parser that tolerates ambiguity (Earley or GLR) to compare coverage against our current strict LL(1) parser.

**Who did what?** (fill in honestly before presenting)
- Data collection / survey: ...
- Lexer / vocabulary: ...
- Grammar / parser: ...
- GUI / report: ...
(Everyone should be able to answer basic questions about every part, since the whole team presents.)

## If the live demo fails

Don't troubleshoot live. Say: "Let me show you from our report instead," and open the PDF to the relevant figure:
- Figure 8/9 — parse trace and tree for F04
- Figure 12 — All results table
- Figures 14–16 — rejected examples with reasons
Then continue with slide 10 as planned.
