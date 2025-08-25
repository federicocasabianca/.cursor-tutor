#!/usr/bin/env python3
import argparse, os, re, sys, glob, yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_catalogs():
    bj_path = os.path.join(ROOT, "_shared", "rubrics", "buyer_journey.yaml")
    seg_path = os.path.join(ROOT, "_shared", "rubrics", "buyer_segments.yaml")
    return load_yaml(bj_path), load_yaml(seg_path)

def valid_phase_layer(bj, phase_id, layer_id):
    if not phase_id:
        return True
    for ph in bj.get("phases", []):
        if ph.get("id") == phase_id:
            if not layer_id:
                return True
            for l in ph.get("structural_layers", []):
                if l.get("id") == layer_id:
                    return True
    return False

def valid_segments(seg_catalog, seg_ids):
    if not seg_ids:
        return True
    allowed = {s["id"] for s in seg_catalog.get("segments", []) if "id" in s}
    return all(s in allowed for s in seg_ids)

def parse_nps_dates_and_market(filename):
    m = re.search(r"buyer_experience-sig-nps-(?P<market>[A-Z_]+)-(?P<start>\d{4}-\d{2}-\d{2})_(?P<end>\d{4}-\d{2}-\d{2})\.md$", filename)
    if not m:
        return None, None, None
    return m.group("market"), m.group("start"), m.group("end")

def update_frontmatter(path, updates):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if not content.startswith("---"):
        print(f"Skip (no frontmatter): {path}")
        return
    parts = content.split("---", 2)
    fm = yaml.safe_load(parts[1]) or {}
    for k,v in updates.items():
        if v is not None:
            fm[k] = v
    new = "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---" + parts[2]
    with open(path, "w", encoding="utf-8") as f:
        f.write(new)
    print(f"Tagged: {path}")

def main():
    ap = argparse.ArgumentParser(description="Bulk-tag signal files.")
    ap.add_argument("--glob", default="signals/qualitative/*.md", help="Glob relative to buyer_experience/")
    ap.add_argument("--market", default=None)
    ap.add_argument("--phase", default=None)
    ap.add_argument("--layer", default=None)
    ap.add_argument("--segments", default=None, help="Comma-separated segment ids (see buyer_segments.yaml)")
    ap.add_argument("--observed_at", default=None)
    ap.add_argument("--window_start", default=None)
    ap.add_argument("--window_end", default=None)
    ap.add_argument("--infer_nps", action="store_true")
    args = ap.parse_args()

    bj, segs = load_catalogs()
    if args.phase or args.layer:
        if not valid_phase_layer(bj, args.phase, args.layer):
            print("ERROR: Invalid phase/layer per buyer_journey.yaml")
            sys.exit(1)

    seg_ids = [s.strip() for s in (args.segments.split(",") if args.segments else []) if s.strip()]
    if seg_ids and not valid_segments(segs, seg_ids):
        print("ERROR: One or more segment ids are not in buyer_segments.yaml")
        sys.exit(1)

    files = glob.glob(os.path.join(ROOT, args.__dict__["glob"]))
    if not files:
        print("No files matched.")
        sys.exit(0)

    for fp in files:
        market=args.market
        ws=args.window_start; we=args.window_end
        if args.infer_nps:
            mkt, ws2, we2 = parse_nps_dates_and_market(os.path.basename(fp))
            market = market or mkt
            ws = ws or ws2; we = we or we2
        updates = {
            "market": market,
            "buyer_journey_phase": args.phase,
            "structural_layer": args.layer,
            "segments": seg_ids or None,
            "observed_at": args.observed_at,
            "window_start": ws,
            "window_end": we,
        }
        update_frontmatter(fp, updates)

if __name__ == "__main__":
    main()
