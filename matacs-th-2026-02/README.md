# MATACS Technical Assessment: AI Proposal Triage Design

- **Name:** Talha Muhammad Saleem
- **Reference:** MATACS-TH-2026-02
- **Role:** Associate Software Developer
- **Time actually spent:** TOOK 35 Minutes

## Files

| File | What it is |
|---|---|
| [WRITEUP.md](WRITEUP.md) | Answers to the five questions, plus assumptions and how the five samples are handled |
| [diagram/process-flow.png](diagram/process-flow.png) | Flow diagram from upload to ranked output, with AI steps, rule steps and human checkpoints |
| [PROMPTS.md](PROMPTS.md) | The extraction prompt and the reason-writing prompt, as I would send them |
| [ranking.json](ranking.json) | Expected ranking of proposals A to E |
| [prototype/](prototype/) | Optional: the rule-based half of the design (mandatory checks, scoring, ranking) as a small Python script |

## Short summary of the design

AI reads messy proposal text and returns structured facts with quoted evidence, and later writes a one-line reason. Everything that must be exact (pass/fail checks, scoring, ranking) is plain code driven by the admin's versioned criteria. Proposals that look manipulated or that miss key information are held for a person instead of being auto-ranked, and a person makes the final decision.

## Running the prototype (optional)

```
cd prototype
python score.py
```

It reads `criteria.json` and `extracted_facts.json` (the facts the AI extraction step would return, after validation) and rewrites `../ranking.json`. It needs only Python 3 and makes no AI calls, so no API key or `.env.example` is needed. The extraction step itself is not included, because the sample proposal text must not be copied into this repository.

## How I used AI tools

I used Claude to help draft the design, the prompts, the scoring script, and the diagram, and then I reviewed and edited everything myself[cite: 5]. One place where I disagreed with and corrected the AI was on how Proposal C's injection attempt (the hidden procurement note) was handled. Initially, the AI suggested letting the model evaluate the text naturally and flag it using sentiment analysis. I corrected this because relying on sentiment or general AI judgment for security risks is unreliable; instead, I enforced a strict rule-based pattern matching layer to catch prompt injections before the data ever hits the scoring logic.
