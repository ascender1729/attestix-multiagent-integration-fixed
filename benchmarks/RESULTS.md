# Pipeline Benchmarks (V-5 / V-6)
Captured: 2026-05-12T16:38:47.815756Z
Python: 3.13.11
Model: llama-3.3-70b-versatile via Groq API

## Per-domain results

| Domain   | Entry script                           | Wall-clock (s) | Tokens (est.) | Lines | Exit |
|----------|----------------------------------------|---------------:|--------------:|------:|-----:|
| Hospital | `Hospital/c_agents/compliant_medical_board.py` |          43.07 |         3,770 |   202 |    0 |
| Finance  | `Agents/compliant_main_finance.py` |          42.18 |         3,792 |   184 |    0 |
| ESG      | `ESG/compliant_main_esg.py` |          39.51 |         3,227 |   153 |    0 |
| Court    | `Court/compliant_main_court.py` |          47.89 |         4,994 |   242 |    0 |

## Method

Each pipeline run was executed end-to-end via `subprocess` with stdin piped from a representative input. Wall-clock measured with `time.perf_counter`. Token counts are estimated by tokenising the captured stdout transcript with a regex + 1.3x calibration factor; this is an order-of-magnitude figure suitable for the report's Results section. For exact Groq token usage, inspect `response.response_metadata['token_usage']` inside each agent file.

## Reproduce

```bash
cd benchmarks/
GROQ_API_KEY=<your_key> python run_benchmarks.py
```

## Cost ceiling estimate

Aggregate across all four domains (single run each): ~15,783 estimated tokens.
Groq free tier (May 2026): typically 1M tokens/day on llama-3.3-70b. At the observed scale, one complete sweep of all four pipelines consumes ~15.8k tokens, about 1.58% of one day's free-tier budget. Paid tier pricing was approximately USD 0.59 per 1M input + USD 0.79 per 1M output tokens on this model as of capture date; aggregate cost upper-bound ~USD 0.0125 per sweep.
