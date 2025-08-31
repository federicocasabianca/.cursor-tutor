#!/usr/bin/env python3
import argparse, glob, os, re, sys
from typing import Dict, Any, Tuple

try:
    import yaml
except Exception:
    sys.exit("Missing dependency 'pyyaml'. Install with: pip install pyyaml")

def read_md_frontmatter(path: str) -> Tuple[Dict[str, Any], str]:
    txt = open(path, encoding="utf-8").read()
    if not txt.startswith("---"):
        return {}, txt
    parts = txt.split("---", 2)
    fm = yaml.safe_load(parts[1]) or {}
    body = parts[2]
    return fm, body

def core_gate(fm: Dict[str, Any]) -> Tuple[bool, list]:
    missing = []
    claim_ok = bool(fm.get("claim"))
    if not claim_ok: missing.append("claim")
    sigs = (fm.get("evidence") or {}).get("signals") or []
    evidence_ok = len([s for s in sigs if isinstance(s, str)]) >= 2
    if not evidence_ok: missing.append("evidence.signals (>=2)")
    okrs = ((fm.get("business_relevance") or {}).get("related_okrs")) or []
    if not okrs: missing.append("business_relevance.related_okrs (>=1)")
    rc = fm.get("root_cause_analysis") or {}
    why = rc.get("why_analysis") or []
    if not rc.get("primary_cause"): missing.append("root_cause_analysis.primary_cause")
    if len([w for w in why if isinstance(w, str)]) < 3:
        missing.append("root_cause_analysis.why_analysis (>=3 entries)")
    return (len(missing) == 0), missing

def score_quality(fm: Dict[str, Any], body: str):
    scores = {}

    # 1 Depth
    why = ((fm.get("root_cause_analysis") or {}).get("why_analysis")) or []
    contrib = ((fm.get("root_cause_analysis") or {}).get("contributing_factors")) or []
    depth = 2 if len(why) >= 3 and len(contrib) >= 2 else (1 if len(why) >= 2 else 0)
    scores["Depth"] = (depth, f"why={len(why)}, contributing_factors={len(contrib)}")

    # 2 Novelty
    nf = (fm.get("novelty_factor") or "incremental").lower()
    novelty = 2 if nf in ("significant","disruptive") else (1 if nf=="incremental" else 0)
    scores["Novelty"] = (novelty, f"novelty_factor={nf}")

    # 3 Customer Impact
    ci = fm.get("customer_impact") or {}
    segs = ci.get("affected_segments") or []
    sev  = (ci.get("pain_severity") or "").lower()
    opp  = (ci.get("opportunity_size") or "").lower()
    impact = 2 if (segs and sev in ("high","critical") and opp in ("large","massive")) else (1 if segs or sev else 0)
    scores["Customer Impact"] = (impact, f"segments={len(segs)}, severity={sev}, opp={opp}")

    # 4 Actionability
    ra = fm.get("recommended_actions") or {}
    immediate = ra.get("immediate") or []
    short = ra.get("short_term") or []
    sm = ra.get("success_metrics") or []
    action = 2 if (immediate and short and sm) else (1 if (immediate or short) else 0)
    scores["Actionability"] = (action, f"immediate={len(immediate)}, short_term={len(short)}, success_metrics={len(sm)}")

    # 5 Measurability
    base = fm.get("baseline") or {}
    targ = fm.get("target") or {}
    has_plan = bool(re.search(r"(?i)measurement plan", body))
    meas = 2 if (base.get("metric") and base.get("unit") and targ.get("value")) else (1 if has_plan else 0)
    scores["Measurability"] = (meas, f"baseline={'set' if base else 'no'}, target={'set' if targ else 'no'}, plan={'yes' if has_plan else 'no'}")

    # 6 Clarity
    claim = (fm.get("claim") or "").strip()
    clarity = 2 if (claim and len(claim) <= 200) else (1 if claim else 0)
    scores["Clarity"] = (clarity, f"len(claim)={len(claim)}")

    # 7 Evidence Quality
    ev = fm.get("evidence") or {}
    sigs = ev.get("signals") or []
    recency = (fm.get("behavior") or {}).get("recency")
    eq = 2 if (len(sigs) >= 2 and recency) else (1 if len(sigs) >= 2 else 0)
    scores["Evidence Quality"] = (eq, f"signals={len(sigs)}, recency={'yes' if recency else 'no'}")

    # 8 Strategic Priority
    br = fm.get("business_relevance") or {}
    sp = (br.get("strategic_priority") or "low").lower()
    strat = 2 if sp in ("high","critical") else (1 if sp=="medium" else 0)
    scores["Strategic Priority"] = (strat, f"strategic_priority={sp}")

    return scores

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default="Insights/*.md", help="Glob of insight files to lint (relative to repo root)")
    args = ap.parse_args()

    files = glob.glob(args.glob)
    if not files:
        print("No files found for pattern:", args.glob)
        sys.exit(0)

    overall_ok = True
    for fp in files:
        fm, body = read_md_frontmatter(fp)
        ok, missing = core_gate(fm)
        scores = score_quality(fm, body) if ok else {}
        total = sum(v for v,_ in scores.values()) if ok else 0

        print(f"\n=== {fp} ===")
        if not ok:
            overall_ok = False
            print("Core gate: NOT READY")
            print("Missing:", ", ".join(missing))
            continue

        print("Core gate: PASS")
        for name, (val, why) in scores.items():
            print(f"- {name}: {val}/2  ({why})")
        print(f"Total: {total}/16")

        if total < 12:
            overall_ok = False
            print("Result: BELOW publish bar (<12). Refine and re-run.")
        else:
            print("Result: OK to publish (>=12).")


    sys.exit(0 if overall_ok else 2)

if __name__ == "__main__":
    main()
