# Report template

## verdict.md

Use these sections in this order. Plain English, no filler. Every reference must be an ID from `evidence.md`.

```markdown
# Medical Research Council Verdict: {short title}

{date} · {project type} · {mode: full | quick | topics | rerun} · Board: {seats}

## 1. The call
**{LABEL}**: {recommended option and one-sentence reason}.
{If the Chair moved the label a band: one line saying why.}

## 2. Scoreboard
| Seat | Weight | A | B | C | Veto | Key point |
|---|---|---|---|---|---|---|
| Evidence | 20% | 6.5 | 7.0 | 3.0 | none | ... |
| ... |
| **Weighted** | 100% | **x.x** | **x.x** | **x.x** | | {cap fired on A / SPLIT on B} |

{rerun only: add a "Change" column, from `score.py --previous`.}

## 3. Veto status
{None, or for each veto: seat, option, the harm or breach, and CLEARS IF: the exact redesign.}

## 4. Where the council agrees
{Points two or more seats reached independently in Round 1. High-confidence signals.}

## 5. Clashes and tradeoffs
{Each real disagreement: the two sides, the seats on each, and how to resolve it
(e.g. rigour vs speed to pilot, data depth vs clinician burden).}

## 6. Caught in peer review
{Blind spots and "all missed" points from Round 2, and any unsupported claims that were removed.}

## 7. Conditions
{Numbered, each checkable: a number, a document, an approval, or a date.
Include every veto-clearing redesign.}

## 8. First step
{One concrete, ethically safe action that tests the riskiest assumption. Not a list.}

## 9. Key evidence
{The 3 to 6 items from evidence.md that mattered, as ID - one line.}

{topics mode only}
## FINER grid
| Topic | Feasible | Interesting | Novel | Ethical | Relevant | Score |

---
Simulated specialist review, not ethics, regulatory, or statistical sign-off. Confirm approvals with
{the bodies the Ethics seat named}.
```

## report.html

One self-contained HTML file with inline CSS and no external requests, so it opens offline and can be emailed. Save it in the session folder and open it.

Contents, top to bottom:
1. Title, date, project type, mode.
2. The call: label as a coloured badge (GO green, GO WITH CONDITIONS amber, MAJOR REVISION orange, NO-GO red) and the one-sentence reason.
3. Option scores as horizontal bars out of 10, with a marker where the veto cap applied.
4. Seat-by-option heatmap: rows are seats, columns are options, cells coloured by score so agreement and splits are visible at a glance.
5. Veto status, conditions, and first step.
6. Collapsible `<details>` per seat with the full Round 1 card, and one for the peer review highlights with the anonymisation map revealed.
7. Key evidence list; PMIDs link to `https://pubmed.ncbi.nlm.nih.gov/<id>/`, NCT IDs to `https://clinicaltrials.gov/study/<id>`, DOIs to `https://doi.org/<doi>`.
8. Footer with the disclaimer line from `verdict.md`.

Style: white background, system font stack, readable at phone width, colour never the only signal (badges and cells also show the text value).
