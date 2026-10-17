# 05 Freeze before you look

Used in every experiment here.

## The problem

With a model that gives probabilities, there are many ways to win after the
fact: try 30 wordings and keep the best, pick a cut-off on the labels you are
graded on, choose the baseline that loses, or move the goalposts once the
returns are in. Each looks like a result and is not. This project saw it
happen once on purpose: a tuning run's best of 30 question variants beat word
counts on labels it had already seen (AUC 0.946 against 0.887), and the same
question on 183 fresh risks did not (E6: gap +0.032, interval −0.024 to
+0.090).

The cure is to write everything down first, then make it impossible to change
quietly.

## The parts

### 1. A card per experiment, written before the work

Each `experiments/<id>/CARD.md` is written before any label, Jev answer or
return exists. It fixes:

- the question file and model version (`jev-1.13.0`, never a moving alias);
- the data version, with its manifest hash;
- the free baseline Jev must beat, and its exact formula;
- the main test, the statistic, the bootstrap (draws, cells, seed), and the
  pass rule ("interval clear of zero");
- what is reported alongside, and what a pass or a fail leads to;
- the cost ceiling, and who must approve going over it.

Anything decided later is added under a dated heading saying what existed at
that moment ("before any Jev score or return exists"). A change to the
question, the data or the key is a new experiment id, never an edit to a graded
card. E3 was withdrawn before any work, and its card stays as a record.

[experiments/LEDGER.md](../experiments/LEDGER.md) holds one line per
experiment and every decision with its date and who made it.

### 2. Frozen files, checked by hash

- **Question files are never edited.** `questions_v1.yaml` to
  `questions_v5.yaml` each say so in their header. A new wording is a new file.
  `sec8k.jev.load_question_set` refuses a moving model alias, and every
  answer whose model differs from the pinned one stops the run
  (`ModelDriftError`).
- **Every answer is cached** in an append-only JSONL file, keyed by a hash of
  the state, the question (including the option order shown) and the model.
  A rerun never re-asks and never pays twice. A torn last line is set aside; a
  damaged earlier line stops the run.
- **Options are shuffled per item** by a fixed rule
  (`sec8k.change.option_order`), so option order cannot steer answers and
  is reproducible.
- **Datasets are published with a manifest** (`sec8k._vendor.input_manifest`)
  listing every file's sha256 and size, plus the producing command. Scoring
  scripts refuse data that differs from its manifest.
- **Baselines are frozen before any Jev call**, and the scores before any label
  or return is opened. Each card records the hashes, for example E11's
  `jev/scores.csv` eb56f1c8…d05b and `jev/baselines.csv` 9a6296a9…1bdda.
- **The Loughran-McDonald dictionary is pinned** by its sha256; any other file
  is refused.

### 3. Separate lanes and a blind wall

The work ran in four lanes that each wrote only their own folders:

| Lane | Owns | Never sees |
|---|---|---|
| Data | `data/`: pulls, parser checks, dataset versions | Jev answers, labels, returns |
| Questions | `experiments/<id>/jev/`: frozen questions, baselines, Jev's answers | Labels (`labels/`), prices |
| Labelling desk | `experiments/<id>/labels/`: blind sheets, AI reviewers, sealed keys | Jev answers and baselines |
| Lead | Cards, the ledger, `grading/` | Reads both sides, only at grading |

For returns tests the wall also covers prices: events are published without
prices, Jev is scored without prices, and only the Lead joins prices to events
at grading.

### 4. Grade with your own code, then check it again

From E4 on, the Lead (the role that owns cards and grading) graded each
experiment with a script written for it, separate from the repository code,
and recomputed at least one number by hand (for E11,
Boeing's 8-K of 23 December 2019: −2.80% over 2 days against SPY). Later, a
verification pack reran the grading from the frozen files
([grading/VERIFY.md](../grading/VERIFY.md)), and a separate recheck with
independently written code reproduced E11's numbers to four decimals
([docs/independent_recheck.md](../docs/independent_recheck.md)). When that
recheck found a mismatch in a descriptive table (a 10-day column that ran 11
days), the card was corrected in public and the first summary kept as
`summary_v1.json`.

## Checklist

- [ ] Card written, with the main test and pass rule, before anything is scored.
- [ ] Question file committed and never edited; model pinned by version.
- [ ] Baseline computed and hashed before any Jev call.
- [ ] Jev scored and hashed before any label or return is opened.
- [ ] Labels made blind ([recipe 04](04-blind-ai-answer-keys.md)), or the
      outcome joined only at grading.
- [ ] Grading by separate code; one number rechecked by hand.
- [ ] Verdict reported as written, pass or fail; changes are new ids.

## Code entry point

- Question sets and answer cache: `src/sec8k/jev.py`
  (`load_question_set`, `AnswerCache`, `cache_key`, `ModelDriftError`)
- Option shuffling: `src/sec8k/change.py` (`option_order`)
- Manifests: `src/sec8k/_vendor/input_manifest.py`,
  `scripts/data/write_input_manifest.py`
- Hash check of every card and manifest: `grading/scripts/check_hashes.py`
- Rerun comparison: `grading/scripts/compare_json.py`
- Tests: `tests/test_filings_jev.py` (cache, aliases, torn lines)
