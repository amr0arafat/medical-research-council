---
name: medical-research-council
description: Use when a clinician, researcher, or medical faculty member wants a medical research topic, idea, study protocol, grant proposal, manuscript, or MedTech/digital-health/healthcare-AI project pressure-tested by a panel of specialist reviewers before committing time, money, or patients to it. Triggers - "medical council", "run the medical research council", "council this study", "roast this protocol", "pressure-test this research idea", "which of these research topics should I pursue", "is this grant fundable", "review my manuscript before submission", "ask the methodologist", or a real tradeoff in study design, endpoints, sample size, ethics/IRB, feasibility, funding, or publication strategy. NOT for diagnosing or treating an individual patient, simple factual lookups, or hospital administration decisions (use medical-business-council).
version: 1.0.0
author: Amr Arafat
license: MIT
argument-hint: "[topic or decision] [--type question|protocol|grant|manuscript|medtech] [--quick] [--seats a,b,c] | topics [idea 1; idea 2; ...] | ask <seat> [question] | rerun <session-folder>"
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [council, medical-research, clinical-research, study-design, grant-review, peer-review, digital-health, subagents, llm-council]
    related_skills: [medical-business-council, llm-council]
---

# Medical Research Council

A specialist review board for one medical research decision. Five seats analyse the project **independently** (each is a separate sub-agent), then **review each other anonymously**, then you, the **Chair**, score it and write the verdict. This is Karpathy's LLM Council (independence + anonymous peer review) with Roast Room mechanics (weighted 1-10 scores, a hard Safety & Ethics veto) and an evidence check so no reference in the verdict is invented.

You never argue a side. You frame the question, gather the evidence pack, run the rounds, compute the numbers, and write the verdict.

Read once before the first run: `roster.json`, `references/seats.md`, `references/round-prompts.md`, `references/scoring.md`, `references/report-template.md`.

## Scope

In scope:
- **Topic selection**: is this research question worth doing (FINER), and which of several candidate topics to pursue first.
- **Protocols**: design choice, population, comparator, endpoints, sample size, bias, analysis plan, reporting guideline.
- **Grants**: fundability, aims, feasibility, budget realism, reviewer objections.
- **Manuscripts**: pre-submission review, target journal, the objections reviewers will raise.
- **MedTech, digital health, healthcare AI**: validation pathway, SaMD classification, adoption, payer.

Out of scope: a specific patient's diagnosis or treatment (say so in one line and answer normally without the council), questions with one textbook answer, and hospital business or admin decisions (point to `medical-business-council`).

## Tools by runtime

| Need | Claude Code | Gemini CLI | Codex |
|---|---|---|---|
| Ask the user | AskUserQuestion | `ask_user` | Ask in chat and wait |
| Spawn seats in parallel | Agent tool, `general-purpose`, all seats in one message | `invoke_agent` with `agent_name: "generalist"`, one call per seat in the same response | `spawn_agent` with `fork_turns: "none"`, one per seat, then `wait_agent` (needs `multi_agent = true` in `~/.codex/config.toml`) |
| Literature and trials | PubMed / Consensus / ClinicalTrials.gov / bioRxiv MCP tools, else WebSearch | Same MCP servers if configured, else `google_web_search` / `web_fetch` | Same MCP servers if configured, else web search |
| Read/write files | Read / Write | `read_file` / `write_file` | Shell or apply_patch |
| Run scripts | Bash `python3 ...` | `run_shell_command` | Shell |

Trust the tools you actually have over this table. If the runtime has no sub-agent tool, or it is turned off, follow "Without sub-agents" below and say so in the verdict.

`SKILL_DIR` means this skill's folder (the one holding this file). Sessions go in `./council-sessions/YYYY-MM-DD-<slug>/` under the user's working directory.

## Modes

| Mode | Invocation | What runs |
|---|---|---|
| Full council (default) | `[topic]` | 5 seats, Round 1, Round 2 peer review, verdict |
| Quick | `--quick` | 3 seats, Round 1, one combined peer review, verdict. For reversible or early-stage calls |
| Topic ranking | `topics idea 1; idea 2; ...` | Full council with every idea as an option; ranked table and FINER grid |
| Named seats | `--seats methods,ethics,editor` | Those seats (veto seats still sit if the work involves humans), full protocol |
| Consult | `ask <seat> [question]` | One seat, one answer, no scoring, no session folder |
| Rerun | `rerun <session-folder>` | Same board on the revised project; verdict shows score change per seat |

## Step 1: The brief

1. **Classify** the project type: `question`, `protocol`, `grant`, `manuscript`, or `medtech` (or take `--type`). The type sets the default board and weights in `scoring.md`.
2. **Read context first.** If the working folder holds a protocol draft, manuscript, grant text, `CLAUDE.md`, or earlier `council-sessions/`, read the relevant ones before asking anything.
3. **Fill the brief**, under 400 words, marking every guess `(assumed)`:
   - The decision in one line and the options as A, B, C. For a single idea, add "do not proceed" and the smallest safe version (pilot, retrospective cohort, feasibility study).
   - PICO(T) or the equivalent: population, intervention/exposure, comparator, outcomes, timeframe, setting.
   - Jurisdiction and institution (sets the ethics and regulatory rules), funding source, deadline, team.
   - What success looks like (accepted paper, funded grant, approved protocol, validated tool) and by when.
   - Which way the user is leaning, and why. The council tests the lean; it does not echo it.
4. If the decision, the population, or the jurisdiction is missing and cannot be inferred, ask once, at most three questions in one call. If the user says "just run it", proceed on stated assumptions.

## Step 2: The evidence pack

Before any seat speaks, search for what already exists. A study that duplicates a recent systematic review or an ongoing registered trial is the most common and most expensive miss.

- PubMed (or Consensus): recent systematic reviews and meta-analyses on the question, the key primary studies, and any guideline.
- ClinicalTrials.gov (and WHO ICTRP / PACTR via web search for non-US settings): ongoing or completed trials on the same question.
- For `medtech`: FDA/CE-cleared comparators and published validation studies.

Save `evidence.md`: 5 to 15 items, each with an ID (`PMID:`, `NCT`, or `DOI:`), year, design, n, and a one-line finding, plus a "gaps" line. Only list items a tool actually returned. If no search tool works, write `evidence.md` saying so, and every seat must label claims `(expert judgment, unverified)`.

## Step 3: Set up the room

- Seat the board from `roster.json` for the project type, applying `--seats` or `--quick`. The **Evidence & Safety** and **Ethics & Regulatory** seats always sit when the work involves human participants, human data, or animals.
- Set weights from `scoring.md` and note any change with a one-line reason.
- Create the session folder and save `brief.md` (brief, options, board, weights).
- Tell the user in one line who sits and what mode is running.

## Step 4: Round 1, independent analysis

Spawn every seat **in one message, in parallel**, each with its lens card from `seats.md` inside the Round 1 prompt from `round-prompts.md`, plus `brief.md` and `evidence.md`. Seats never see each other's work in this round.

Save the cards verbatim to `round-1.md` under `## <Seat short name>`. Send a card back once if it lacks a score per option, a stance, or (veto seats) the veto line. Then add `## Chair notes`: the cruxes (one to three real disagreements, seats on each side) and the unanimity check from `scoring.md`.

## Step 5: Round 2, anonymous peer review

Shuffle the cards and relabel them Response A to E. Save the letter-to-seat map in `round-2.md` but never show it to reviewers. Spawn one reviewer per seat, in parallel, with the Round 2 prompt. Each reviewer names the strongest response, the most dangerous blind spot, what every response missed, and may revise its own seat's scores once with a reason.

Quick mode: one reviewer sub-agent covers all three cards.

Save to `round-2.md`, then `## Chair notes`: who revised scores and why, which cruxes resolved, the current veto status.

## Step 6: Score and check

1. Write `scores.json` from the final scores (format in `scoring.md`) and run `python3 SKILL_DIR/scripts/score.py <session-folder>`. It applies the weights and the veto cap, ranks options, and prints the verdict label. Do not do this arithmetic by hand.
2. Write `verdict.md` from `report-template.md`.
3. Run `python3 SKILL_DIR/scripts/check_refs.py <session-folder>`. Every PMID, NCT, and DOI in `verdict.md` and the round files must appear in `evidence.md`. Delete or relabel any that fail, then rerun until it passes. If Python is unavailable, do the same check by reading the files.
4. Build `report.html` per `report-template.md` and open it.

## Step 7: Tell the user

In chat, under 200 words: the verdict label and the call, option scores on one line, veto status, the three arguments that carried it (one line each, naming the seat), the strongest objection, and the one first step. Then the path to `verdict.md` and one line offering `ask <seat>` or `rerun` after revisions.

## Chair rules

- **Weigh arguments, not headcount.** One seat with the strongest reasoning can beat four.
- **A unanimous Round 1 is a warning.** Apply the unanimity rule in `scoring.md`.
- **Never invent evidence.** No PMID, NCT, DOI, statistic, or guideline clause that is not in `evidence.md` or the user's files. Uncited claims are labelled expert judgment.
- **Never recommend skipping ethics review, consent, or registration** to save time. When speed matters, the fast path is a safe one: retrospective data under an exemption or waiver, synthetic data, silent-mode AI deployment, a feasibility study, clinician interviews.
- **Regulatory points are a checklist, not legal clearance.** Say which body must confirm.
- **Quote seats faithfully.** Never rewrite a card to fit the verdict.
- Plain English in the report: no filler, no hedged "it depends" verdicts.
- Cost: a full council is about 11 sub-agent runs; say which mode ran. Use `--quick` for early ideas.

## Without sub-agents

Run the same protocol yourself, one seat at a time. In Round 1 write each card before reading any other. In Round 2 review the shuffled, unlabeled cards. Say in the verdict that independence was simulated.

## Files

- `roster.json`: seats, default boards per project type, veto seats.
- `references/seats.md`: lens cards, jurisdiction checklist, reporting guidelines.
- `references/round-prompts.md`: Round 1, Round 2, quick review, consult, and rerun prompts.
- `references/scoring.md`: weights, veto cap, verdict labels, unanimity rule, `scores.json` format.
- `references/report-template.md`: `verdict.md` and `report.html`.
- `scripts/score.py`: weighted scores, veto cap, ranking. `scripts/check_refs.py`: reference verification. Both need only Python 3.8+, no packages.
