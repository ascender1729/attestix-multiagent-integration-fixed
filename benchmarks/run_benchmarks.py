"""V-5 / V-6 benchmark runner.

For each of the four domain pipelines, runs the regulated entry point with a
prepared input, times the run, captures terminal output, and approximates
the Groq token spend by counting tokens in the output transcript.

Usage:
    cd benchmarks/
    GROQ_API_KEY=<your_key> python run_benchmarks.py
    # ...generates RESULTS.md in this folder.

Token estimation: this approximates Groq usage by tokenising the captured
stdout text. Real token counts can be read from response_metadata if the
domain agents expose it; this estimator gives an order-of-magnitude figure
sufficient for the report's Results section.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYTHON = sys.executable or "python"

CASES = [
    {
        "domain": "Hospital",
        "entry": "Hospital/c_agents/compliant_medical_board.py",
        "stdin": (
            "Patient P-007 presents with acute decompensated congestive heart "
            "failure: severe shortness of breath, ankle swelling, weight gain 4 kg "
            "in 5 days, fatigue. Severity: High.\n"
        ),
    },
    {
        "domain": "Finance",
        "entry": "Agents/compliant_main_finance.py",
        "stdin": "TSLA\n",
    },
    {
        "domain": "ESG",
        "entry": "ESG/compliant_main_esg.py",
        "stdin": "Vietnam Factory 04\n",
    },
    {
        "domain": "Court",
        "entry": "Court/compliant_main_court.py",
        "stdin": (
            "Draft an Employment Contract for a Senior AI Engineer joining a "
            "stealth startup. Include a 2-year Non-Compete, assignment of all IP, "
            "and an equity grant of 10,000 shares.\n"
        ),
    },
]

TOKEN_PATTERN = re.compile(r"\b\w+\b|[^\s\w]")

def estimate_tokens(text: str) -> int:
    """Order-of-magnitude estimator: 1 token ~= 0.75 words for English text.
    Counts word-tokens and punctuation tokens; multiplies by a calibration
    factor that approximates Groq's tokeniser behaviour on chat output."""
    raw = len(TOKEN_PATTERN.findall(text))
    return int(raw * 1.3)

def run_case(case: dict, timeout_s: int = 600) -> dict:
    started = time.perf_counter()
    started_iso = datetime.utcnow().isoformat() + "Z"
    result = subprocess.run(
        [PYTHON, str(ROOT / case["entry"])],
        input=case["stdin"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        env={**os.environ},
        timeout=timeout_s,
    )
    elapsed = time.perf_counter() - started
    stdout = result.stdout or ""
    stderr = result.stderr or ""
    return {
        "domain": case["domain"],
        "entry": case["entry"],
        "started": started_iso,
        "elapsed_s": round(elapsed, 2),
        "exit_code": result.returncode,
        "tokens_estimated": estimate_tokens(stdout),
        "stdout_lines": stdout.count("\n"),
        "stderr_tail": stderr[-500:] if stderr else "",
    }

def write_results(results: list[dict]) -> None:
    p = Path(__file__).resolve().parent / "RESULTS.md"
    lines = []
    lines.append("# Pipeline Benchmarks (V-5 / V-6)\n")
    lines.append(f"Captured: {datetime.utcnow().isoformat()}Z\n")
    lines.append("Python: " + sys.version.split()[0] + "\n")
    lines.append("Model: llama-3.3-70b-versatile via Groq API\n")
    lines.append("\n")
    lines.append("## Per-domain results\n\n")
    lines.append("| Domain   | Entry script                           | Wall-clock (s) | Tokens (est.) | Lines | Exit |\n")
    lines.append("|----------|----------------------------------------|---------------:|--------------:|------:|-----:|\n")
    for r in results:
        lines.append(
            f"| {r['domain']:<8} | `{r['entry']}` | {r['elapsed_s']:>14} | {r['tokens_estimated']:>13,} | "
            f"{r['stdout_lines']:>5} | {r['exit_code']:>4} |\n"
        )
    lines.append("\n")
    lines.append("## Method\n\n")
    lines.append(
        "Each pipeline run was executed end-to-end via `subprocess` with stdin "
        "piped from a representative input. Wall-clock measured with "
        "`time.perf_counter`. Token counts are estimated by tokenising the "
        "captured stdout transcript with a regex + 1.3x calibration factor; "
        "this is an order-of-magnitude figure suitable for the report's "
        "Results section. For exact Groq token usage, inspect "
        "`response.response_metadata['token_usage']` inside each agent file.\n"
    )
    lines.append("\n## Reproduce\n\n")
    lines.append("```bash\ncd benchmarks/\nGROQ_API_KEY=<your_key> python run_benchmarks.py\n```\n")
    lines.append("\n## Cost ceiling estimate\n\n")
    total_tokens = sum(r["tokens_estimated"] for r in results)
    lines.append(f"Aggregate across all four domains (single run each): ~{total_tokens:,} estimated tokens.\n")
    pct_of_free = total_tokens / 1_000_000 * 100
    lines.append(
        "Groq free tier (May 2026): typically 1M tokens/day on llama-3.3-70b. "
        "At the observed scale, one complete sweep of all four pipelines "
        f"consumes ~{total_tokens/1000:.1f}k tokens, about {pct_of_free:.2f}% "
        "of one day's free-tier budget. Paid tier pricing was approximately "
        "USD 0.59 per 1M input + USD 0.79 per 1M output tokens on this model "
        f"as of capture date; aggregate cost upper-bound ~USD {total_tokens * 0.00000079:.4f} per sweep.\n"
    )
    if any(r["exit_code"] != 0 for r in results):
        lines.append("\n## Failures\n\n")
        for r in results:
            if r["exit_code"] != 0:
                lines.append(f"### {r['domain']} (exit {r['exit_code']})\n\n")
                lines.append("```\n" + r["stderr_tail"] + "\n```\n\n")

    p.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {p}")

if __name__ == "__main__":
    assert os.environ.get("GROQ_API_KEY"), (
        "GROQ_API_KEY missing. Set it in the environment before running."
    )
    results = []
    for case in CASES:
        print(f"\n=== {case['domain']} ===")
        try:
            r = run_case(case, timeout_s=600)
        except subprocess.TimeoutExpired:
            r = {"domain": case["domain"], "entry": case["entry"],
                 "started": datetime.utcnow().isoformat() + "Z",
                 "elapsed_s": 600.0, "exit_code": -1,
                 "tokens_estimated": 0, "stdout_lines": 0,
                 "stderr_tail": "TIMEOUT after 600s"}
        results.append(r)
        print(f"  elapsed: {r['elapsed_s']}s  tokens~{r['tokens_estimated']}  exit={r['exit_code']}")
    write_results(results)
