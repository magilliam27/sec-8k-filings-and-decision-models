# 04 Blind AI answer keys

Used for the answer keys of E2, E4, E5, E6, E8, E9 and E10, and for an
exploratory re-judge of E1.

## The problem

Grading Jev needs an answer key. Hand labels are slow: reading two long
paragraphs side by side and comparing them closely is hard work for a person.
In E2 the owner's own blind spot check of 20 items matched the AI majority on
only 11. The owner then judged that the reviewers had done the better job and
chose to grade on their key. That choice was made before any Jev answer existed.

An AI key is only useful if it is blind: the reviewers must not see the
experiment, Jev's answers, any baseline, or each other's work. This recipe is
the fixed procedure that keeps them blind.

## The procedure

1. **A label set** (`configs/filings/labels/*.yaml`) states every question and
   option. Where Jev is asked the same thing, the option texts are copied word
   for word from the frozen question file, so reviewers and Jev read the same
   rubric. A label set is never edited once labels exist against it.
2. **A blind sheet.** `label_desk sheet` reads only the id column and the item
   columns of the label set's kind from a hand-over table. Items are shuffled
   and given fresh ids (R001, ...). The map back to source ids goes in `key/`,
   for the grader only.
3. **Three reviewers.** `label_desk reviewers` writes one packet per reviewer
   per batch: `prompt.md` (the frozen reviewer instructions, filled in) and
   `items.md`. Each reviewer gets every item in its own order. Each packet goes
   to **one fresh AI agent** with exactly this prompt and nothing more:

   > Read `<absolute path to prompt.md>` and follow it exactly. Open no other
   > file.

   Never reuse an agent across packets or reviewers.
4. **Combine.** `label_desk combine` checks every answer file (each answer one
   of its options, every item answered once) and writes `ai_labels.csv`,
   `ai_answers.csv` (each question's own majority) and `ai_summary.json`. An
   item with no majority goes to the owner, never to a fourth reviewer. A
   rejected answer file is kept as evidence and the packet goes to a new agent.
   No one edits a reviewer's answers by hand.
5. **Spot check (optional).** The owner labels part of the sheet blind on the
   labelling page (`scripts/data/label_page.html`). `label_desk agree` reports
   agreement with the AI majority, its 95% interval, Cohen's kappa and every
   disagreement.

The full step list for Claude Code is in
[.claude/skills/blind-ai-reviewers/SKILL.md](../.claude/skills/blind-ai-reviewers/SKILL.md).

## The reviewer prompts

Frozen templates, filled in from the label set:

- [reviewer_v1.md](../configs/filings/labels/reviewer_v1.md): yes/no questions
  on 10-K risk pairs.
- [reviewer_v2.md](../configs/filings/labels/reviewer_v2.md): adds pick-one
  questions.
- [reviewer_events_v1.md](../configs/filings/labels/reviewer_events_v1.md):
  8-K events.

The rules every reviewer reads (from `reviewer_events_v1.md`):

```
- Read exactly one file: `$items_path`. Do not open, list or search any other
  file or folder, and do not use the web. Other files may hold other people's
  answers, and seeing them would spoil the key.
- Judge each item from a shareholder's point of view, using only its context
  and text. Do not use what you know about the company, or anything that
  happened after the filing, such as how the stock moved or how the matter
  turned out.
- Answer every item. When you are unsure, give your best reading and say why in
  the note; never leave a question blank.
- Write one file: `$answers_path`. Write nothing else.
```

## Label sets

| Label set | Questions | Key for |
|---|---|---|
| `same_risk_v1.yaml` | Is this the same risk? (yes/no) | E1 (pilot) |
| `change_v1.yaml` | Yes/no questions; code derives the change category | E2 |
| `changed_v1.yaml` | Did the risk materially change? (yes/no) | E4, E6 |
| `new_changed_v1.yaml` | Is the risk new? Did it materially change? | E5 |
| `change_direction_v1.yaml` | Worse, better or neutral; and a finer five-way kind | E8 |
| `new_changed_direction_v1.yaml` | E5's two plus E8's two, unchanged | E9 |
| `event_rating_v1.yaml` | E10's rating and size, copied from `questions_v5.yaml` | E10 |

## How well the reviewers agreed

| Key | Items | All three agreed |
|---|---|---|
| E4 changed or not | 100 | 92 |
| E5 new / changed | 300 | 294 / 291 |
| E6 changed or not | 183 | 166 |
| E8 direction / finer | 300 | 279 / 266 |
| E10 rating | 436 | 414 (every disagreement one step apart) |

## What an AI key can and cannot show

- It measures whether Jev agrees with a language model's reading. Model judging
  model can share blind spots. Word methods start at a disadvantage on such a
  key, since they cannot read a rubric.
- In E10 the key and Jev read the same rubric, so a big gap shows sensible
  reading, not value. Only an outside outcome, such as stock returns
  ([recipe 03](03-test-a-signal-on-returns.md)), shows value.
- Reviewers may know how famous stories ended. They are told to judge from the
  sheet alone, but hindsight cannot be ruled out.
- The answer keys themselves were sealed until grading and are not published
  here.

## Code entry point

```bash
python -m scripts.data.label_desk sheet --table handover.csv --id-column pair_id \
    --label-set configs/filings/labels/change_v1.yaml --sheet-id my-sheet-1 \
    --out-dir labels/my-sheet-1 [--sample 80] [--seed 0]
python -m scripts.data.label_desk reviewers --labels-dir labels/my-sheet-1 \
    [--prompt configs/filings/labels/reviewer_v2.md] [--batch-size 20]
# ... run one fresh agent per packet ...
python -m scripts.data.label_desk combine --labels-dir labels/my-sheet-1
python -m scripts.data.label_desk agree --labels-dir labels/my-sheet-1
```

- Script: [scripts/data/label_desk.py](../scripts/data/label_desk.py)
- Library: `src/sec8k/labelling.py`
- Labelling page: `scripts/data/label_page.html` (it was built to run as a
  claude.ai artifact with a label store; elsewhere it needs a small storage
  shim)
- Tests: `tests/test_filings_labelling.py`
