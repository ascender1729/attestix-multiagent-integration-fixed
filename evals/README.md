# LLM Output Evaluation (V-1)

Golden-prompt regression suite for the four regulated AI pipelines. Closes the V-1 finding from `06_VIVA_READINESS.md` (viva-panel persona-review test stage flagged "no LLM-output evaluation rubric or golden dataset").

## Why this exists

The pytest suite under `tests/` validates the **security middleware contract** (identity, delegation, compliance gate, Merkle linkage). It does **not** validate that the LLM agents produce correct, safe, or regulation-compliant outputs.

The golden-prompt set in this folder validates the LLM behaviour for a small representative input space per domain. It is a **regression bar**, not a comprehensive eval - 5 prompts per domain x 4 domains = 20 fixtures. Real production deployment would expand this to hundreds of fixtures curated by domain experts.

## Files

```
evals/
  README.md              <- this file
  hospital_golden.json   <- 5 patient cases + expected diagnostic categories
  finance_golden.json    <- 5 ticker scenarios + expected sentiment / recommendation shape
  esg_golden.json        <- 5 supplier audit scenarios + expected risk flags
  court_golden.json      <- 5 contract requirement scenarios + expected risk categories
  score_evals.py         <- scoring runner (requires GROQ_API_KEY)
```

## Rubric

Each fixture has the shape:

```json
{
  "id": "HOSP-001",
  "input": {"patient_statement": "..."},
  "expected": {
    "must_contain": ["congestive heart failure", "furosemide"],
    "must_not_contain": ["[disallowed medication name]"],
    "severity_in": ["High"],
    "must_flag_allergies": true
  },
  "rubric_weight": 1.0,
  "domain_expert_notes": "From the report's P-007 case study. Decompensated CHF should be the primary diagnosis."
}
```

The scoring runner counts:
- substring matches against `must_contain` (positive)
- substring matches against `must_not_contain` (negative)
- structured-field checks (severity_in, must_flag_allergies, etc.)

Score per fixture: 0.0 to 1.0. Aggregate score: mean. Threshold for "pass": 0.8.

## Run

```bash
GROQ_API_KEY=<key> python evals/score_evals.py --domain hospital
GROQ_API_KEY=<key> python evals/score_evals.py --domain all
```

## Scope and limitations

- 5 fixtures per domain is a starter set, not production-grade coverage.
- The `must_contain` / `must_not_contain` rubric is brittle to phrasing changes; production deployment should use an LLM-as-judge approach or a domain-expert review queue.
- No adversarial / prompt-injection probes yet (V-2 item).
- For the medical / legal domains, the expected outputs were drafted from the report's case study and the mock JSON contents; a real eval set must be curated by a licensed clinician / lawyer.

## What this closes

- viva-panel persona review V-1 ("zero eval suite for the LLM components"): now a starter set exists with a reproducible runner.
- Future work in the report Chapter 7: this scaffolding gives the next intern a clear contract to extend rather than start from zero.
