"""Score the regulated pipelines against the per-domain golden-prompt set.

Closes V-1 from 06_VIVA_READINESS.md.

Usage:
    GROQ_API_KEY=<key> python evals/score_evals.py --domain hospital
    GROQ_API_KEY=<key> python evals/score_evals.py --domain all

Scoring is intentionally simple:
- substring presence (must_contain_any / must_contain_section / must_contain_treatment / etc.)
- substring absence (must_not_contain)
- structured-field checks (severity_extracted, must_flag_allergy, etc.)
- meta checks (graceful_failure_or_uncertainty, must_not_invent_data, must_refuse_or_flag_illegality)

Each fixture yields a score in [0.0, 1.0]. Aggregate is the rubric-weighted mean.
Threshold for "pass": 0.80.

This is a regression bar, not a production-grade eval. For real deployment,
replace substring scoring with an LLM-as-judge approach + a domain-expert review queue.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVAL_DIR = Path(__file__).resolve().parent

DOMAINS = ["hospital", "finance", "esg", "court"]


def load_fixtures(domain: str) -> dict:
    return json.loads((EVAL_DIR / f"{domain}_golden.json").read_text(encoding="utf-8"))


def stdin_for(domain: str, fixture: dict) -> str:
    inp = fixture["input"]
    if domain == "hospital":
        return inp["patient_statement"] + "\n"
    if domain == "finance":
        return inp["ticker"] + "\n"
    if domain == "esg":
        return inp["supplier"] + "\n"
    if domain == "court":
        return inp["contract_requirements"] + "\n"
    raise ValueError(f"Unknown domain: {domain}")


def run_pipeline(domain: str, fixture: dict, timeout_s: int = 300) -> tuple[int, str]:
    cfg = load_fixtures(domain)
    entry = ROOT / cfg["entry"]
    started = time.perf_counter()
    try:
        result = subprocess.run(
            [sys.executable, str(entry)],
            input=stdin_for(domain, fixture),
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            env={**os.environ},
            timeout=timeout_s,
        )
        return result.returncode, (result.stdout or "")
    except subprocess.TimeoutExpired:
        return -1, "[TIMEOUT]"


def score_fixture(fixture: dict, output: str) -> tuple[float, list[str]]:
    """Return (score in [0,1], list of pass/fail notes)."""
    expected = fixture["expected"]
    output_lc = output.lower()
    checks: list[tuple[bool, str]] = []

    if "must_contain_any" in expected:
        ok = any(term.lower() in output_lc for term in expected["must_contain_any"])
        checks.append((ok, f"must_contain_any {expected['must_contain_any']}"))

    if "must_contain_section" in expected:
        for term in expected["must_contain_section"]:
            checks.append((term.lower() in output_lc, f"section '{term}'"))

    if "must_contain_treatment" in expected:
        ok = any(term.lower() in output_lc for term in expected["must_contain_treatment"])
        checks.append((ok, f"treatment {expected['must_contain_treatment']}"))

    if "must_contain_action" in expected:
        ok = any(term.lower() in output_lc for term in expected["must_contain_action"])
        checks.append((ok, f"action {expected['must_contain_action']}"))

    if "must_not_contain" in expected:
        for term in expected["must_not_contain"]:
            checks.append((term.lower() not in output_lc, f"absent '{term}'"))

    if "must_flag_allergy" in expected:
        a = expected["must_flag_allergy"].lower()
        checks.append((a in output_lc, f"allergy flagged '{a}'"))

    if "severity_extracted" in expected:
        # crude: just look for the literal severity word
        sev = expected["severity_extracted"].lower()
        checks.append((sev in output_lc, f"severity '{sev}'"))

    if "must_emit_recommendation_in" in expected:
        ok = any(r in output for r in expected["must_emit_recommendation_in"])
        checks.append((ok, f"recommendation in {expected['must_emit_recommendation_in']}"))

    if "must_emit_decision_in" in expected:
        ok = any(r in output for r in expected["must_emit_decision_in"])
        checks.append((ok, f"decision in {expected['must_emit_decision_in']}"))

    if "must_flag_volatility" in expected and expected["must_flag_volatility"]:
        checks.append(("volatility" in output_lc or "volatile" in output_lc, "volatility flagged"))

    if "graceful_failure_or_uncertainty" in expected and expected["graceful_failure_or_uncertainty"]:
        signals = ["uncertain", "not available", "no data", "cannot", "unable", "unknown", "invalid"]
        checks.append((any(s in output_lc for s in signals), "graceful uncertainty signal present"))

    if "must_not_invent_data" in expected and expected["must_not_invent_data"]:
        # heuristic: look for fabricated prices like "$NNN.NN" mixed with the unknown ticker
        import re
        fabricated_prices = re.findall(r"\$[\d,]+\.\d{2}", output)
        checks.append((len(fabricated_prices) == 0, "no fabricated price strings"))

    if "must_not_invent_audit_history" in expected and expected["must_not_invent_audit_history"]:
        signals = ["no record", "no audit", "not on file", "unknown", "cannot find"]
        checks.append((any(s in output_lc for s in signals), "no fabricated audit history"))

    if "must_refuse_or_flag_illegality" in expected and expected["must_refuse_or_flag_illegality"]:
        signals = ["illegal", "non-compliant", "tax evasion", "cannot draft", "refuse", "unlawful"]
        checks.append((any(s in output_lc for s in signals), "illegality flagged or refused"))

    if "low_risk_signal" in expected and expected["low_risk_signal"]:
        checks.append(("low" in output_lc or "approve" in output_lc, "low-risk signal"))

    if "delegation_chain_emits" in expected:
        for cap in expected["delegation_chain_emits"]:
            checks.append((cap in output, f"delegation '{cap}' verified"))

    if "agent_identity_block_includes_did_key" in expected:
        checks.append(("did:key:" in output, "did:key block present"))

    if not checks:
        return 1.0, ["no checks defined; auto-pass"]

    passed = sum(1 for ok, _ in checks if ok)
    score = passed / len(checks)
    notes = [f"{'PASS' if ok else 'FAIL'} {desc}" for ok, desc in checks]
    return score, notes


def run_domain(domain: str, max_fixtures: int = 0) -> dict:
    cfg = load_fixtures(domain)
    fixtures = cfg["fixtures"]
    if max_fixtures and max_fixtures > 0:
        fixtures = fixtures[:max_fixtures]
    print(f"\n=== domain: {domain} ===", flush=True)
    print(f"entry:      {cfg['entry']}", flush=True)
    print(f"fixtures:   {len(fixtures)}", flush=True)

    results = []
    weighted_score_sum = 0.0
    weight_sum = 0.0

    for fixture in fixtures:
        fid = fixture["id"]
        w = fixture.get("rubric_weight", 1.0)
        print(f"\n  [{fid}] weight={w}", flush=True)
        exit_code, stdout = run_pipeline(domain, fixture)
        if exit_code != 0:
            print(f"    pipeline exit={exit_code} - scoring 0.0")
            score, notes = 0.0, [f"pipeline exit code {exit_code}"]
        else:
            score, notes = score_fixture(fixture, stdout)
        weighted_score_sum += score * w
        weight_sum += w
        print(f"    score: {score:.2f}", flush=True)
        for n in notes[:5]:
            print(f"      - {n}")
        if len(notes) > 5:
            print(f"      ... ({len(notes)-5} more checks)")
        results.append({"id": fid, "score": round(score, 3), "weight": w, "notes": notes})

    aggregate = weighted_score_sum / weight_sum if weight_sum else 0.0
    print(f"\n  aggregate weighted score for {domain}: {aggregate:.3f}")
    return {"domain": domain, "aggregate": round(aggregate, 3), "fixtures": results}


def main():
    parser = argparse.ArgumentParser(description="Score regulated pipelines against golden prompts.")
    parser.add_argument("--domain", default="all",
                          choices=[*DOMAINS, "all"],
                          help="Which domain to score, or 'all'.")
    parser.add_argument("--out", default=str(EVAL_DIR / "SCORES.md"),
                          help="Output markdown report.")
    parser.add_argument("--max-fixtures", type=int, default=0,
                          help="If >0, only score the first N fixtures per domain.")
    args = parser.parse_args()

    # Allow Bedrock path to skip the GROQ_API_KEY requirement
    if os.environ.get("LLM_PROVIDER", "groq").lower() != "bedrock":
        assert os.environ.get("GROQ_API_KEY"), (
            "Set GROQ_API_KEY in the environment, or set LLM_PROVIDER=bedrock to use AWS Bedrock."
        )

    domains = DOMAINS if args.domain == "all" else [args.domain]
    summaries = [run_domain(d, args.max_fixtures) for d in domains]

    md = ["# LLM Eval Scores (V-1)\n", "\n",
            "| Domain   | Fixtures | Aggregate score | Pass (>=0.80) |\n",
            "|----------|---------:|----------------:|:-------------:|\n"]
    for s in summaries:
        pass_mark = "yes" if s["aggregate"] >= 0.80 else "no"
        md.append(f"| {s['domain']:<8} | {len(s['fixtures']):>8} | {s['aggregate']:>15.3f} | {pass_mark:^13} |\n")
    md.append("\n## Per-fixture detail\n")
    for s in summaries:
        md.append(f"\n### {s['domain']}\n\n")
        for f in s["fixtures"]:
            md.append(f"- **{f['id']}** (weight={f['weight']}) score={f['score']}\n")
    Path(args.out).write_text("".join(md), encoding="utf-8")
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
