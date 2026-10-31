# Scoring

## Weights

Default weights per project type live in `roster.json` (`boards.<type>.full`). They sum to 100 for the full board. When the board changes (`--quick`, `--seats`, an on-call seat added), `score.py` renormalises the seated seats' weights to 100. An on-call seat added by hand gets `on_call_default_weight` (15) before renormalising.

| Type | Evidence | Methods | Ethics | Patient | Feasibility | On-call |
|---|---|---|---|---|---|---|
| question | 25 | 20 | 15 | 15 | 25 | |
| protocol | 20 | 30 | 20 | 15 | 15 | |
| grant | 20 | 25 | 10 | | 25 | Outsider 20 |
| manuscript | 20 | 30 | 10 | | | Editor 30, Outsider 10 |
| medtech | 20 | | 20 | 20 | | Economist 25, Informatics 15 |

The Chair may shift up to 10 points between seats when the project clearly demands it (for example, a first-in-human device study moves weight to Evidence). Record the change and the reason in `brief.md`, and put the final weights in `scores.json`.

## scores.json

Write it after Round 2, using each seat's REVISED SCORES (Round 1 scores if quick mode had no rescore).

```json
{
  "type": "protocol",
  "options": { "A": "Two-site RCT", "B": "Retrospective cohort first", "C": "Do not proceed" },
  "weights": { "evidence": 20, "methods": 30, "ethics": 20, "patient": 15, "feasibility": 15 },
  "seats": {
    "evidence":    { "scores": { "A": 6.5, "B": 7.0, "C": 3.0 }, "vetoes": [] },
    "methods":     { "scores": { "A": 8.0, "B": 6.0, "C": 2.0 } },
    "ethics":      { "scores": { "A": 5.0, "B": 7.5, "C": 5.0 }, "vetoes": ["A"] },
    "patient":     { "scores": { "A": 5.5, "B": 8.0, "C": 4.0 } },
    "feasibility": { "scores": { "A": 4.0, "B": 8.5, "C": 6.0 } }
  }
}
```

- `weights` is optional; when missing, `score.py` takes them from `roster.json` for the type.
- `vetoes` lists the options a veto seat vetoed in its final card. Only `evidence` and `ethics` may veto; the script ignores vetoes from other seats and warns.

## The veto cap

If the Evidence or Ethics seat holds a veto on an option after Round 2, that option's final score is **capped at 4.0**, however high the other seats scored it. The verdict states that the cap fired, quotes the veto reason, and lists the exact redesign that clears it (the `CLEARS IF` line).

## Verdict labels

For the top-ranked option:

| Final score | Label |
|---|---|
| 7.5 or more, no seat below 5.0 on it | GO |
| 6.0 to 7.4, or 7.5+ with a seat below 5.0 | GO WITH CONDITIONS |
| 4.1 to 5.9 | MAJOR REVISION |
| 4.0 or less, or vetoed | NO-GO: REDESIGN REQUIRED |

The Chair may move the label one band with a written reason in `verdict.md` (for example, one seat's argument went unanswered). The Chair may never move a vetoed option above NO-GO.

## Disagreement flag

If the spread (highest minus lowest seat score) on the top option is 4.0 or more, `score.py` flags it as **SPLIT**. The verdict must then present both sides of that clash before the recommendation.

## Unanimity rule

If every Round 1 stance backs the same option and the spread on it is 2.0 or less, the council agreed too easily. Add this line to every Round 2 prompt, just before the reply format:

```
The council agreed quickly. Before anything else, make the strongest honest case against the
consensus option, then decide whether it changes your scores.
```

## Topic ranking (`topics` mode)

Score each topic as an option. In `verdict.md`, add a FINER grid built from the seat cards, one row per topic, each cell `strong`, `mixed`, or `weak`:

| Criterion | Read from |
|---|---|
| Feasible | Feasibility seat |
| Interesting | Outsider or Editor if seated, else Chair's read of all cards |
| Novel | Evidence seat and `evidence.md` gaps |
| Ethical | Ethics seat |
| Relevant | Patient seat |

Recommend one topic to start, and say what would make the runner-up the better choice.
