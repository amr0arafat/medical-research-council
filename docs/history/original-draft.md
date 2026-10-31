---
name: medical-research-council
description: Run any medical, clinical research, digital health, MedTech, healthcare AI, or hospital workflow decision through a 5-seat Medical Research Council. Combines Karpathy's LLM Council methodology (independent analysis + anonymous peer review) with Roast Room mechanics (domain-weighted 1-10 scoring + hard Clinical Safety & Regulatory Veto). Trigger when the user says 'medical council', 'run the medical research council', 'roast this medical project', 'pressure-test this clinical idea', or presents a healthcare, medical research, clinical trial, digital health, or MedTech decision with real tradeoffs.
---

# Medical Research Council

## Summary

Evaluate medical research, digital health, clinical workflow, and MedTech decisions using a 5-seat specialist advisory board. This skill combines **Andrej Karpathy's LLM Council methodology** (independent multi-angle analysis and anonymous peer review) with **Roast Room's anti-sycophancy mechanics** (domain-weighted 1-10 scoring and a hard Clinical Safety & Regulatory Veto).

## When to Use

* The user explicitly triggers the council ("medical council this", "run the medical research council", "pressure-test this clinical study/product", "roast this medical project").
* The user is weighing a high-stakes decision in clinical research, study design, healthcare AI, Software as a Medical Device (SaMD), hospital operations, or digital therapeutics.
* The user asks to validate a medical project proposal, clinical workflow change, or healthcare commercialization strategy.
* Do NOT trigger for simple factual medical lookups or clinical diagnostic questions with a single textbook answer.

## The Five Council Seats

Each advisor operates from an isolated analytical lens with strict heuristics and red flags. They do not hedge or try to be polite.

### 1. Clinical Safety & Evidence Officer
* **Core Lens:** Patient safety, clinical efficacy, study methodology, biostatistics, and "First, do no harm."
* **Heuristics:** Demands peer-reviewed evidence, rigorous validation (sensitivity/specificity, endpoints, bias control), and clear clinical utility over hype.
* **Red Flags (Veto Triggers):** Unmitigated patient harm risk, hallucination/error risk in clinical decision support without human-in-the-loop, or unvalidated diagnostic claims.

### 2. Regulatory, Privacy & Ethics Lead
* **Core Lens:** Regulatory classification (SaMD, clinical trial phases, IRB/ethics), data privacy, and legal liability.
* **Adaptive Region Rule:** Infer the target jurisdiction from context or apply a global standard alongside local specifics (e.g., FDA/HIPAA/IRB in the US; SFDA/PDPL/NPHIES/NCBE in Saudi Arabia & GCC; CE MDR/GDPR in the EU).
* **Red Flags (Veto Triggers):** Illegal PHI/patient data handling, bypassing IRB/ethics approval for human subjects research, or marketing a regulated medical device/diagnostic as a "wellness tool" when its intended use triggers regulatory oversight.

### 3. Patient & Frontline Clinician UX Advocate
* **Core Lens:** Human factors, health literacy, accessibility, and clinician cognitive load.
* **Heuristics:** Assumes doctors and nurses are already burned out and patients are overwhelmed or non-technical. Hunts for "alert fatigue," extra clicks, confusing medical jargon, and drop-off points in patient adherence or trial recruitment.

### 4. Healthcare Economics & Payer Strategist
* **Core Lens:** Unit economics, grant/funding viability, reimbursement pathways, and buyer incentives.
* **Heuristics:** Separates the *user* (patient/clinician) from the *payer* (insurer, hospital CFO, ministry of health, or research grant committee). Asks who actually pays, what budget line it comes from, and whether the ROI justifies switching costs.

### 5. Clinical Operations & IT Integrator
* **Core Lens:** Real-world execution, EHR/HIS interoperability (HL7, FHIR, DICOM), data pipeline readiness, and Monday-morning feasibility.
* **Heuristics:** Ignores theoretical elegance. Focuses on how this survives contact with legacy hospital IT, fragmented clinical data, and slow institutional procurement. Pushes for the smallest, safest, fastest pilot.

## Workflow Steps

### Step 1: Frame the Question & Assign Domain Weights

1. **Check Context:** Identify the core decision, the options being weighed, the target population/clinical setting, and the regulatory region. If critical context is missing (e.g., whether a tool is patient-facing or clinician-facing) and prevents meaningful evaluation, ask **at most 1-2 brief clarifying questions** before running the council. Otherwise, state clear assumptions and proceed immediately.
2. **Frame the Neutral Prompt:** Summarize the decision, constraints, and stakes objectively.
3. **Set Domain Weights (Roast Room Mechanic):** Assign a percentage weight to each of the 5 seats (totaling 100%) based on the nature of the project:
   * *Example (Clinical Research / Trial Design):* Safety & Evidence (35%), Regulatory/IRB (25%), Patient/Clinician UX (15%), Operations/Data (15%), Economics/Funding (10%).
   * *Example (Commercial MedTech / Digital Health App):* Safety & Evidence (20%), Regulatory/Privacy (20%), Patient/Clinician UX (20%), Economics/Payer (25%), Operations/IT (15%).

### Step 2: Independent Advisor Evaluations (Round 1)

Generate an independent, unhedged assessment (150-250 words each) for all 5 advisors. For each seat, include:

* **Core Critique & Analysis:** Direct evaluation strictly through that advisor's lens.
* **Initial Score:** A score from **1.0 to 10.0** for each option being evaluated.
* **Veto / Ruin Risk Flag:** Explicitly state `VETO TRIGGERED: [Reason]` or `NO VETO`. (Only the *Clinical Safety* and *Regulatory/Ethics* seats can trigger a hard veto).

### Step 3: Anonymous Peer Review & Cross-Examination (Round 2)

Map the 5 advisor outputs to anonymized labels (**Response A through Response E** in randomized order) and run an anonymous peer-review pass where the council cross-examines the arguments:

* **Strongest Argument:** Which anonymized response identified the most critical factor, and why?
* **Biggest Blind Spot:** Which response made a dangerous or naive assumption (e.g., an execution shortcut that violates regulatory compliance, or a safety requirement that makes clinician UX unusable)?
* **What All Advisors Missed:** Second-order clinical, ethical, or operational consequences that none of the initial 5 responses addressed.

### Step 4: Scoring & Veto Calculation

Calculate the final quantitative score using Roast Room's anti-sycophancy rules:

1. **Weighted Base Score:** Multiply each advisor's score (1-10) by their assigned domain weight from Step 1 and sum them.
2. **The Clinical Safety & Regulatory Veto Cap:** If *either* the **Clinical Safety & Evidence Officer** or the **Regulatory, Privacy & Ethics Lead** triggered a `VETO` (due to unmitigated patient harm, ethical violation, or severe regulatory breach), **cap the final weighted score at a maximum of 4.0 / 10.0** ("No-Go / Redesign Required"), regardless of how high the commercial or operational scores are. State explicitly if the cap was activated and what exact redesign removes the veto.

### Step 5: Chairman's Final Synthesis

Deliver the final **Medical Research Council Verdict** using this exact structure:

* **1. Scoreboard & Veto Status:** A clean Markdown table showing each seat, its assigned weight, its 1-10 score, key takeaway, Veto status, and the final weighted score (noting any Veto cap).
* **2. Where the Council Agrees:** High-confidence clinical, operational, or strategic signals that multiple seats converged on independently.
* **3. Key Clashes & Tradeoffs:** The core tensions (e.g., *Clinical Rigor vs. Speed to Pilot*, or *Data Collection Depth vs. Clinician Burnout*) and how to resolve them.
* **4. Blind Spots Caught in Peer Review:** Crucial insights that emerged during Round 2 cross-examination.
* **5. Final Verdict & De-Risking Conditions:** A clear, decisive recommendation (not "it depends"). If a Veto was triggered, list the exact modifications required to clear the safety/regulatory bar.
* **6. The Monday-Morning Pilot Step:** One concrete, minimum-viable, ethically safe action the user should take first to validate the decision.

## Gotchas

* **Avoid Silicon Valley Hustle Clichés:** Never advise a medical or clinical research project to "move fast and break things" or bypass IRB/regulatory review. When speed is needed, the *Clinical Operations & IT Integrator* should propose safe, non-interventional validation methods (e.g., retrospective chart reviews, synthetic datasets, silent-mode shadow deployments, or clinician workflow interviews).
* **Prevent Premature Consensus:** If all 5 seats agree too easily, force the *Clinical Safety* and *Patient/Clinician UX* seats to challenge the operational assumptions during Peer Review.
* **Keep Output Scannable:** Present the full Council session clearly in Markdown using tables and structured sections so the user can scan the verdict in seconds or read the deep-dive debates.