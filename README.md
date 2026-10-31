# Medical Research Council

A council of specialist AI reviewers for medical research decisions. Bring it a research idea, a
study protocol, a grant proposal, a manuscript, or a MedTech / digital-health / healthcare-AI
project, and five specialists will tear it apart before a real ethics committee, funder, or
Reviewer 2 does.

Works in **Claude Code**, **Gemini CLI**, and **Codex**.

> Status: private beta. Not yet validated end to end on every runtime.

## How it works

1. **Brief.** The Chair (your agent) frames the decision, the options, PICO, jurisdiction, and what success looks like.
2. **Evidence pack.** It searches PubMed, ClinicalTrials.gov, and other sources for systematic reviews and ongoing trials, so the council knows whether the question is already answered.
3. **Round 1, independent.** Five seats analyse the project in parallel as separate sub-agents. None sees the others' work. Each scores every option from 1 to 10.
4. **Round 2, anonymous peer review.** The cards are shuffled and relabelled A to E. Each seat critiques the others without knowing who wrote what, and may revise its own scores.
5. **Score and check.** A script applies the weights and the veto cap. A second script fails the run if the verdict cites any PMID, NCT, or DOI that the literature search did not return.
6. **Verdict.** `verdict.md` and a one-page `report.html` with a scoreboard, a seat-by-option heatmap, conditions, and one first step.

Method: Andrej Karpathy's LLM Council (independence plus anonymous peer review), with Roast Room
style weighted scoring and a hard veto.

## The council

| Seat | Role | Veto |
|---|---|---|
| Evidence | Clinical Evidence & Safety Officer | Yes |
| Methods | Methodologist & Biostatistician | |
| Ethics | Research Ethics & Regulatory Lead | Yes |
| Patient | Patient & Frontline Clinician Advocate | |
| Feasibility | Feasibility, Funding & Operations Lead | |
| Editor | Journal Editor & Peer Reviewer (on call) | |
| Economist | Health Economist & Payer Strategist (on call) | |
| Informatics | Health Informatics & AI Lead (on call) | |
| Translational | Translational & Basic Scientist (on call) | |
| Outsider | No medical background, reads it cold (on call) | |

A veto from Evidence or Ethics caps that option at 4.0 out of 10, whatever the other seats think,
and the verdict lists the exact redesign that clears it.

Project types (`question`, `protocol`, `grant`, `manuscript`, `medtech`) each seat a different board
with different weights. See `skills/medical-research-council/references/scoring.md`.

## Install

Requirements: Python 3.8+ (standard library only) for the scoring scripts. Sub-agent support in
your runtime for true independence; without it the skill runs the seats one by one and says so.

### Claude Code

As a plugin:

```
/plugin marketplace add amr0arafat/medical-research-council
/plugin install medical-research-council@medical-research-council
```

Or copy the skill into `~/.claude/skills`:

```bash
git clone https://github.com/amr0arafat/medical-research-council.git
cd medical-research-council && bash install.sh --claude
```

### Gemini CLI

As an extension:

```bash
gemini extensions install https://github.com/amr0arafat/medical-research-council
```

Or copy the skill into `~/.agents/skills` (shared by Gemini CLI and Codex):

```bash
bash install.sh --gemini
```

### Codex

```bash
bash install.sh --codex
```

For parallel seats, turn on multi-agent support in `~/.codex/config.toml`:

```toml
[features]
multi_agent = true
```

### Options

`bash install.sh --all` installs for every runtime, `--link` symlinks instead of copying (handy
while editing), and `--uninstall` removes it.

## Use

```
run the medical research council on: <your idea, or point to your protocol file>
medical council --type grant --quick: <grant summary>
topics: SGLT2 inhibitors in HFpEF in Egypt; AI triage for ED chest pain; vitamin D in PCOS
ask methods: is a stepped-wedge design right for this?
rerun council-sessions/2026-10-31-my-trial
```

| Mode | What runs |
|---|---|
| Full (default) | 5 seats, Round 1, anonymous peer review, verdict |
| `--quick` | 3 seats (both veto seats plus one), one combined review |
| `topics` | Ranks several candidate research topics, with a FINER grid |
| `--seats a,b,c` | Choose the board yourself |
| `ask <seat>` | One seat's opinion, no scoring |
| `rerun <folder>` | Re-scores a revised project and shows what changed |

Each session is saved in `./council-sessions/YYYY-MM-DD-<slug>/` in your working folder:
`brief.md`, `evidence.md`, `round-1.md`, `round-2.md`, `scores.json`, `verdict.md`, `report.html`.
That folder is git-ignored here because it may hold unpublished research.

## Limits

- This is a simulated review. It is not ethics, regulatory, legal, or statistical sign-off.
  The Ethics seat names which body must confirm each point.
- It refuses to advise on an individual patient's diagnosis or treatment.
- Regulatory tables (Egypt, Saudi Arabia/GCC, US, EU, UK) are checklists. Laws change; confirm
  with your local committee.
- A full council costs about 11 sub-agent runs. Use `--quick` for early ideas.

## Development

```bash
python3 -m unittest discover -s tests -v
```

The tests check the frontmatter, version numbers across all manifests, the roster, the scoring
and reference-check scripts, and the installer.

## Credits

- Council method: [Andrej Karpathy's LLM Council](https://github.com/karpathy/llm-council).
- Claude adaptation that inspired this skill: [tenfoldmarc/llm-council-skill](https://github.com/tenfoldmarc/llm-council-skill).
- Weighted scoring and veto mechanics: [nateherkai/roast-room](https://github.com/nateherkai/roast-room).
- Packaging layout: [obra/superpowers](https://github.com/obra/superpowers).

## License

MIT. See [LICENSE](LICENSE).
