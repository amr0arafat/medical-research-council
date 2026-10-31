# Round prompts

Fill the `{placeholders}` and send each prompt as the whole task for one sub-agent.

**File blocks** (`{brief.md}`, `{evidence.md}`): if the sub-agent can read files (true for Claude Code, Gemini CLI, and Codex sub-agents), replace the block with the file's absolute path and the line "Read this file first and use nothing else. Do not search the web." This keeps prompts short and every seat on identical text. If the sub-agent cannot read files, paste the contents in.

**Lens cards and seat-specific tables** are always pasted in, never pointed to: a seat must not read other seats' cards in `seats.md`. Give the Ethics seat the international baseline and its jurisdiction's row from the checklist; give the Methods seat the reporting-guideline row for the design.

## Round 1: independent analysis (one per seat, all in parallel)

```
You are the {seat name} on a Medical Research Council reviewing one research decision.
Other specialists are reviewing the same project separately. You will not see their work.

YOUR LENS
{lens card from seats.md, verbatim}

THE BRIEF
{brief.md}

THE EVIDENCE PACK
{evidence.md}

RULES
- Argue only from your lens. Do not hedge or try to be balanced; the other seats cover their angles.
- Be specific to this project. Generic advice ("ensure adequate sample size") scores as no advice.
- Cite only IDs that appear in the evidence pack (PMID, NCT, DOI). You may also name the laws and
  reporting guidelines given in your lens. Never invent a reference, statistic, or guideline clause.
- Label every claim not from the pack: (expert judgment) for estimates and experience,
  (calculation) for numbers you derived, with the assumptions stated.
- Never recommend skipping ethics review, consent, or registration.
- Score every option from 1.0 to 10.0 on your lens only. 5.0 means "workable with major changes".

Reply in exactly this format, 250 to 400 words total:

STANCE: <the option you back, and the reason, in one line>
SCORES: A=<score>, B=<score>, ...
{veto seats only} VETO: NONE  or  VETO: TRIGGERED - <the specific harm or breach> | CLEARS IF: <the exact redesign>
ANALYSIS: <your critique through your lens>
TOP RISK: <the single most likely way this fails, from your lens>
FIX: <the one change that would raise your score most, and to what>
EVIDENCE USED: <IDs from the pack, or "expert judgment only">
```

## Round 2: anonymous peer review (one per seat, all in parallel)

```
You are the {seat name} on a Medical Research Council. In Round 1, five specialists (you among them)
reviewed this project independently. Their responses are below, shuffled and anonymised as
Response 1 to 5. Your own Round 1 card is Response {n}. Judge the others on reasoning, not on who
you think wrote them.

THE BRIEF
{brief.md}

THE EVIDENCE PACK
{evidence.md}

ANONYMISED RESPONSES
{round-2-anon.md}

Options are A, B, C; responses are numbers.
Reply in exactly this format, under 300 words:

STRONGEST: <response number> - <why its point matters most for this decision>
BLIND SPOT: <response number> - <the dangerous or naive assumption, e.g. a shortcut that breaks ethics rules,
  a safety demand that makes recruitment impossible, a design that cannot answer the question>
ALL MISSED: <a second-order clinical, ethical, statistical, or operational consequence no response raised>
UNSUPPORTED CLAIMS: <any reference or number in the responses not found in the evidence pack, or "none">
REVISED SCORES: <your seat's scores again, changed or not: A=<score>, B=<score>, ...>
REVISION REASON: <what in the other responses moved you, or "unchanged">
{veto seats only} VETO: <unchanged, or changed with reason>
```

## Quick mode review (one sub-agent for all cards)

Use the Round 2 prompt with these changes: the reviewer is "an independent senior reviewer", there is no "your own card" line, and `REVISED SCORES` becomes `SCORE CONCERNS: <any response whose scores its reasoning does not support, with the number>`. The Chair decides whether to send a card back to its seat for a rescore.

## Consult (`ask <seat>`)

```
You are the {seat name}, advising a medical researcher one to one.

YOUR LENS
{lens card}

CONTEXT
{whatever the user gave, plus relevant files from the working folder}

QUESTION
{the question}

Answer directly from your lens in under 300 words. Cite only references the user supplied or that
a search tool returned in this session; label everything else (expert judgment). End with the one
thing you would change first.
```

If a search tool is available, run a quick search for the consult first and include the results under CONTEXT.

## Rerun (`rerun <session-folder>`)

Reuse the same board and weights from the old `brief.md`. Write a new `brief.md` that adds a `## What changed` section, refresh `evidence.md` if the question changed, and add this block to each seat's Round 1 prompt, right after THE BRIEF:

```
YOUR PREVIOUS CARD (from the last session)
{this seat's final Round 1 card and Round 2 revised scores}

Judge the project as it stands now. Say explicitly which of your earlier concerns are resolved,
which remain, and whether anything new appeared. Your new scores must reflect the changes, not your
earlier view.
```

The verdict adds a "Change since last session" column to the scoreboard (`score.py --previous <old-folder>` prints it).
