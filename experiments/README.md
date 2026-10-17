# Experiments

One folder per experiment, E1 to E11, plus the research ledger.

- `LEDGER.md`: one line per experiment with its verdict, the dataset versions,
  and every decision with its date and who made it.
- `<id>/CARD.md`: the experiment card. The design part was written before any
  label, Jev answer or return existed; later additions are dated. The Result
  section was added at grading.
- `<id>/grading/summary.json`: the graded numbers, where the experiment
  produced one (E4 to E11; E1 to E3 have none here).

The cards were copied from the original research folder. Two kinds of edits
were made for publication, and nothing else changed:

- the owner's first name is replaced by "the owner";
- the ledger's links point to the card folders here.

Cards also name files that are not in this repository: blind sheets,
`grading/design.csv`, per-item `graded_*.csv`, Jev's answer caches, and the
sealed answer keys under `labels/sealed/`. Some of those hold filing texts or
were sealed until grading. E1 and E2 point to an earlier pilot folder
(`jev_pilot/`), and the ledger names a tuning folder (`jev_tuning/`); neither is published.
The frozen Jev scores and baselines for E10 and E11, and E11's event list and
price joins, are in [`../results/`](../results/).

Experiment ids follow the order the cards were written. A rerun with a changed
question, dataset or answer key gets a new id; a graded card is never edited.
