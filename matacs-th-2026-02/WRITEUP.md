# Write-up: AI Proposal Triage Design (MATACS-TH-2026-02)

Diagram: `diagram/process-flow.png`. Prompts: `PROMPTS.md`. Ranking: `ranking.json`.

**Assumptions** (stated rather than waiting for a reply):
- "Held by the bidder" means the bidder itself holds the licence. A promise to hire a licensed subcontractor later does not count.
- Price, timeline, experience and warranty points are relative: the best bid among those passing the mandatory checks gets full marks, others a proportional share.
- Team and approach is a fixed checklist: named lead 4, crew stated 3, safety plan 3, monitoring plan 3, extra assurance (roof assessment, progress reports) 2.

## 1. AI vs. rules

**AI does two things only:**
- **Extraction (step 5):** read messy proposal text and return structured facts, each with a quoted piece of evidence. Proposals word the same facts many ways, so rules would break here.
- **Reason writing (step 11):** turn finished numbers into one readable sentence.

**Everything else is plain code:** loading criteria, PDF text, safety scan, validation, mandatory pass/fail, scoring formulas, flagging, ranking, audit log.

**Why there:** anything that must be exact or repeatable is safer as code, because a model can be inconsistent or be talked into a different answer. The AI never decides eligibility, sets a score or sets a rank.

## 2. Consistency and explainability

- **Repeatable:** temperature 0, a fixed versioned prompt, and a strict JSON schema. Extracted facts are saved with the run. Scoring is code, so the same facts and criteria version always give the same scores and order.
- **Residual variation:** a fresh AI extraction could occasionally read a value differently. So re-ranking uses the saved facts, not a new AI call, and a deliberate re-extraction shows any differences to the reviewer.
- **Visible reasons:** each row shows the per-criterion score breakdown, a one-line reason, the evidence quote behind each fact, and flags.
- **No drift between reason and numbers:** code checks every number in the AI-written reason against the score sheet, and falls back to a template sentence if one differs.

## 3. Human in the loop

- **Checkpoint 1 (review):** the reviewer sees ranked, held and ineligible proposals. They can correct an extracted value (re-scoring runs in code), release or exclude a held proposal, or re-order, each with a required typed reason.
- **Checkpoint 2 (award):** a person decides. The tool never awards anything.
- **Audit log (every step):** user and time, criteria version, file hashes, prompt version, model name, raw AI output, extracted facts with evidence, scores, flags, and every human change with its reason.

## 4. Changing criteria

- Criteria are **versioned**. An edit creates version N+1; version N never changes.
- Each run stores the version it used, so old results stay explainable.
- Facts are stored separately from scores. After an edit the tool shows "criteria changed since this run" and offers a **re-score**. This runs in code on saved facts: instant and free. New AI extraction is needed only if a new criterion needs a fact never extracted.
- A re-score creates a new run beside the old one with a rank comparison. Nothing is overwritten.
- If an award is already logged, the tool warns instead of silently changing the order.
- The admin screen validates on save: weights total 100, and each criterion uses a supported scoring method.

## 5. Risks and safeguards

| Risk | Safeguard |
|---|---|
| **Wrong extraction** | Strict schema; each value needs an exact quote that code checks against the PDF text; reviewer sees the quote; scanned or empty PDFs are flagged. |
| **Made-up facts** | "Not stated means null" rule; unsupported quotes drop the value and flag the proposal. |
| **Manipulation (prompt injection)** | Proposal text is wrapped as data; a rule scan and the AI's `suspicious_instructions` field catch text aimed at AI reviewers; the AI cannot set scores or rank, so an injected order has nothing to change; a hit holds the proposal for a person. |
| **Promises counted as facts** | Mandatory checks need the fact stated as held, not promised. |
| **Bias** | AI sees no scores or other bids; scoring uses only the admin's criteria, never company size, name or location; humans can override with a logged reason; periodic accuracy spot-checks. |
| **Missing data** | Scores zero on that criterion and holds the proposal, so a person decides whether to ask the bidder. |
| **Cost** | One extraction call per proposal plus one reason call per run; re-scoring is free; upload size limits. |
| **Over-trust** | Output is labelled a triage aid; flagged bids are never silently dropped. |

## The five samples

- **A, E:** pass all checks, no flags: ranked 1 and 2.
- **B:** ineligible. Electrical work goes to an unnamed subcontractor, so the licence check fails despite the lowest price.
- **C:** contains an instruction aimed at automated reviewers. It is ignored, not obeyed, and the proposal is held for a person. Its honest score is shown for reference.
- **D:** no completion time, so the 16-week limit cannot be confirmed. Held for review so the reviewer can ask the bidder.
