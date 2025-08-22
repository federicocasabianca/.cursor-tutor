#!/usr/bin/env python3
# (shortened header, full content kept from prior cell)
import argparse, os, sys, json, datetime as dt, re
from typing import List, Dict, Any, Optional, Tuple

OUT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

MARKET_COUNTRIES = {"DACH":{"DE","AT","CH"},"ES":{"ES"},"ITA":{"IT"},"FR":{"FR"},"NL":{"NL"},"PL":{"PL"},"SE":{"SE"},"WORLD":set()}
MARKET_LANGS = {"DACH":{"de","fr","it"},"ES":{"es"},"ITA":{"it"},"FR":{"fr"},"NL":{"nl"},"PL":{"pl"},"SE":{"sv"},"WORLD":set()}
COUNTRY_SYNONYMS = {"de":"DE","ger":"DE","germany":"DE","deutschland":"DE","at":"AT","austria":"AT","österreich":"AT","ch":"CH","switzerland":"CH","schweiz":"CH","suisse":"CH","svizzera":"CH","es":"ES","spain":"ES","españa":"ES","it":"IT","italy":"IT","italia":"IT","fr":"FR","france":"FR","français":"FR","nl":"NL","netherlands":"NL","holland":"NL","nederland":"NL","pl":"PL","poland":"PL","polska":"PL","se":"SE","sweden":"SE","sverige":"SE","dach":"DACH"}
STOPWORDS = {"de":{"und","nicht","ich","die","der","das","ist","mit","für","bei","aber","wie","auch","ein","eine","man","zu"},"es":{"el","la","los","las","de","que","y","en","no","muy","pero","para","con","por","si","como"},"it":{"il","lo","la","i","gli","le","di","che","e","non","ma","per","con"},"fr":{"le","la","les","de","des","et","un","une","est","pas","mais","pour","avec"},"nl":{"de","het","een","en","niet","maar","voor","met"},"pl":{"i","nie","ale","dla","jest","to","że","jak"},"sv":{"och","det","att","inte","men","för","är","som"},"en":{"the","and","is","not","with","for","but","as","also"},"el":{"και","να","στο","στην","είναι","που"}}

def tokenize(text: str): 
    return re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]+", (text or "").lower())

def detect_lang_from_tokens(tokens):
    if not tokens: return None
    scores = {lang: sum(1 for t in tokens if t in words) for lang, words in STOPWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None

def country_code_from_value(val):
    if not val: return None
    s = str(val).strip().lower()
    if not s: return None
    s = s.replace("(", " ").replace(")", " ").replace(".", " ")
    s = re.sub(r"\s+", " ", s)
    if s in COUNTRY_SYNONYMS:
        cc = COUNTRY_SYNONYMS[s]; 
        return cc if cc != "DACH" else None
    if len(s)==2 and s.isalpha(): return s.upper()
    return None

def belongs_to_market(market, cc, lang, lang_infer, min_hits, lang_hits):
    if market=="WORLD": return True
    if cc and cc in MARKET_COUNTRIES.get(market,set()): return True
    if lang_infer=="off": return False
    allowed = {"de"} if (market=="DACH" and lang_infer=="de_only") else MARKET_LANGS.get(market,set())
    if not lang: return False
    if lang_hits.get(lang,0) < min_hits: return False
    return lang in allowed

def ensure_dir(p): os.makedirs(os.path.dirname(p), exist_ok=True)
def write_file(p,c): ensure_dir(p); open(p,"w",encoding="utf-8").write(c); print(f"Wrote: {p}")
def today(): import datetime as dt; return dt.date.today().isoformat()

def yaml_dump(d):
    try:
        import yaml
    except Exception:
        sys.exit("Missing dependency 'pyyaml'. Install with: pip install pyyaml")
    return yaml.safe_dump(d, sort_keys=False, allow_unicode=True)

def fm_block(d): return "---\n"+yaml_dump(d)+"---\n"
def classify(score): return "promoter" if score>=9 else ("passive" if score>=7 else "detractor")
def normalize_comment(c):
    c=(c or "").replace("\r"," ").replace("\n"," ").strip()
    return re.sub(r"\s+"," ",c)
def truncate(c,limit=240): return (c[:limit-1]+"…") if len(c)>limit else c

def pick_examples(items, group, k=5, lang=None):
    filtered=[]
    for x in items:
        if classify(x["score"])!=group: continue
        c=normalize_comment(x["comment"])
        if not c: continue
        if lang and x.get("lang")!=lang: continue
        filtered.append(c)
    seen=set(); unique=[]
    for c in filtered:
        key=c.lower()
        if key in seen: continue
        seen.add(key); unique.append(c)
    if not unique: return []
    mid=[c for c in unique if 40<=len(c)<=240]
    rest=[c for c in unique if c not in mid]
    chosen=sorted(mid,key=lambda s:abs(len(s)-120))+sorted(rest,key=lambda s:-len(s))
    return [truncate(c) for c in chosen[:k]]

def ingest_nps_json(path, market, start, end, lang_infer, min_lang_hits, country_field, examples_language, examples_per_group):
    import json
    data=json.load(open(path,encoding="utf-8"))
    responses = data.get("responses") if isinstance(data, dict) else data
    used,excluded=[],[]; lang_counts={}; country_counts={}
    for r in responses:
        try: score=int(float(str(r.get("grade")).strip()))
        except Exception: excluded.append(r); continue
        comment=(r.get("comment") or "").strip()
        cc=country_code_from_value(r.get(country_field))
        tokens=tokenize(comment); hits={lang: sum(1 for t in tokens if t in words) for lang,words in STOPWORDS.items()}
        lang=max(hits,key=hits.get) if hits else None
        if hits.get(lang,0)==0: lang=None
        if belongs_to_market(market, cc, lang, lang_infer, min_lang_hits, hits):
            used.append({"score":score,"comment":comment,"cc":cc,"lang":lang,"lang_hits":hits})
            if cc: country_counts[cc]=country_counts.get(cc,0)+1
            if lang: lang_counts[lang]=lang_counts.get(lang,0)+1
        else:
            excluded.append(r)
    total_used=len(used); promoters=sum(1 for x in used if x["score"]>=9); passives=sum(1 for x in used if 7<=x["score"]<=8); detractors=total_used-promoters-passives
    nps=round(((promoters/total_used)-(detractors/total_used))*100,1) if total_used else 0.0

    lang_pref=None if (not examples_language or examples_language=="any") else examples_language
    ex_promoters=pick_examples(used,"promoter",k=examples_per_group,lang=lang_pref)
    ex_passives= pick_examples(used,"passive", k=examples_per_group,lang=lang_pref)
    ex_detracts= pick_examples(used,"detractor",k=examples_per_group,lang=lang_pref)

    ex_promoters_non=ex_passives_non=ex_detracts_non=[]
    if lang_pref=="en":
        def any_lang(g): return pick_examples(used,g,k=min(3,examples_per_group),lang=None)
        if len(ex_promoters)<2: ex_promoters_non=any_lang("promoter")
        if len(ex_passives) <2: ex_passives_non =any_lang("passive")
        if len(ex_detracts) <2: ex_detracts_non =any_lang("detractor")

    fm={
        "artifact":"signal",
        "scope":"project",
        "project":"buyer_experience",
        "nature":"qualitative",
        "id":f"buyer_experience-sig-nps-{market}-{start}_{end}",
        "date":today(),
        "source":"nps_survey",
        "summary":f"NPS feedback for {market} over {start} → {end} (multilingual).",
        "coverage":f"{market}, all platforms",
        "tags":["nps","buyer_journey",market],
        "confidence":"medium",
        "limitations":[
            "Rolling window only; not seasonally adjusted.",
            f"Some rows included by language inference ({lang_infer})." if lang_infer!="off" else "Country-only selection."
        ],
        "pii":False,
        "metrics":[
            {"name":"NPS","value":nps,"unit":"index","window":f"{start} to {end}"},
            {"name":"Responses_used","value":total_used,"unit":"responses","window":f"{start} to {end}"},
            {"name":"Responses_excluded","value":len(excluded),"unit":"responses","window":f"{start} to {end}"},
            {"name":"Promoters","value":promoters,"unit":"responses","window":f"{start} to {end}"},
            {"name":"Passives","value":passives,"unit":"responses","window":f"{start} to {end}"},
            {"name":"Detractors","value":detractors,"unit":"responses","window":f"{start} to {end}"},
        ],
        "feedback_examples":{
            "language": examples_language or "any",
            "promoters": ex_promoters,
            "passives":  ex_passives,
            "detractors": ex_detracts
        },
        "links":{"from":[], "to":[]}
    }
    if ex_promoters_non or ex_passives_non or ex_detracts_non:
        fm["feedback_examples_non_en"]={"promoters":ex_promoters_non,"passives":ex_passives_non,"detractors":ex_detracts_non}

    breakdown=[]
    if country_counts: breakdown.append("**By country (explicit):** "+", ".join(f"{k}:{v}" for k,v in sorted(country_counts.items())))
    if lang_counts: breakdown.append("**By inferred language:** "+", ".join(f"{k}:{v}" for k,v in sorted(lang_counts.items())))

    def yaml_dump(d):
        try:
            import yaml
        except Exception:
            sys.exit("Missing dependency 'pyyaml'. Install with: pip install pyyaml")
        return yaml.safe_dump(d, sort_keys=False, allow_unicode=True)

    content="---\n"+yaml_dump(fm)+"---\n"
    content += f"### Summary\n- NPS **{nps}** from **{total_used}** used responses ({len(excluded)} excluded).\n\n"
    if breakdown:
        content += "### Breakdown\n" + "\n".join(f"- {ln}" for ln in breakdown) + "\n\n"
    content += "### Notes\n- Language inference applied as configured.\n"

    out_path=os.path.join(OUT_ROOT,"signals","qualitative",f"buyer_experience-sig-nps-{market}-{start}_{end}.md")
    ensure_dir(out_path); open(out_path,"w",encoding="utf-8").write(content); print(f"Wrote: {out_path}")

# ---- Company text ----
KPI_PATTERNS=[r"\b(?:GMV|AOV|NPS|CTR|CR|CVR|Revenue|Sessions?|Retention|Churn|ARPU|MAU|DAU|LTV)\b", r"\b\d{1,3}(?:\.\d+)?\s?%", r"\b\d+(?:\.\d+)?\s?(?:k|K|M|B)\b", r"\bOKR\b", r"\btarget\b", r"\bgoal\b"]
GUARDRAIL_HINTS=["must not","should not","no ","without ","cannot","avoid ","do not ","privacy","security","gdpr","sla","uptime","latency","budget","capex","opex","brand","quality bar","regulatory","compliance","risk"]
GOAL_VERBS=["increase","improve","reduce","grow","expand","launch","migrate","decrease","optimize","raise","accelerate","stabilize","localize","personalize"]

def extract_candidates(lines):
    kpi_lines, guard_lines, goal_lines=[],[],[]
    for ln in lines:
        s=ln.strip(" -•*").strip(); sl=s.lower()
        if any(re.search(p,s,flags=re.I) for p in KPI_PATTERNS): kpi_lines.append(s)
        if any(h in sl for h in GUARDRAIL_HINTS): guard_lines.append(s)
        if any(sl.startswith(v+" ") for v in GOAL_VERBS) or re.match(r"^\d+[\).\s-]", s): goal_lines.append(s)
    def dedup(seq):
        seen=set(); out=[]
        for x in seq:
            k=x.lower()
            if k in seen: continue
            seen.add(k); out.append(x)
        return out
    return dedup(goal_lines)[:8], dedup(guard_lines)[:8], dedup(kpi_lines)[:12]

def ingest_company_text(file_path, period_label, source_title):
    text=open(file_path,encoding="utf-8").read().strip()
    raw_lines=[ln for ln in (ln.strip() for ln in text.splitlines()) if ln]
    bullet_lines=[ln for ln in raw_lines if ln.startswith(("- ","* ","• ")) or re.match(r"^\d+[\).\s-]", ln)]
    themes=[ln.lstrip("-*• ").strip() for ln in bullet_lines[:8]] if bullet_lines else raw_lines[:8]

    goals, guardrails, kpis = extract_candidates(raw_lines)

    fm={
        "artifact":"signal","scope":"company","project":"buyer_experience","nature":"qualitative",
        "id":f"buyer_experience-sig-company-{period_label}","date":today(),"source":"company_doc",
        "summary":f"{source_title} — extracted themes, goals, guardrails, and KPIs.","coverage":"Company-wide",
        "tags":["company","goals",period_label],"confidence":"medium",
        "limitations":["Text extracted manually; may be incomplete."],"pii":False,
        "themes":themes[:8],"goals":goals or themes[:5],"guardrails":guardrails or ["TBD"],"kpis":kpis or ["TBD"],
        "links":{"from":[],"to":[]}
    }

    try:
        import yaml
    except Exception:
        sys.exit("Missing dependency 'pyyaml'. Install with: pip install pyyaml")
    content="---\n"+yaml.safe_dump(fm, sort_keys=False, allow_unicode=True)+"---\n"
    if bullet_lines:
        content += "### Raw Excerpts\n" + "\n".join(f"- {ln}" for ln in bullet_lines[:12]) + "\n"
    else:
        content += "### Raw Excerpts\n- (No bullet lines detected; pasted text preserved.)\n"
    content += "\n### Notes\n- Source text parsed heuristically for goals/guardrails/KPIs.\n"

    out_path=os.path.join(OUT_ROOT,"signals","qualitative",f"buyer_experience-sig-company-{period_label}.md")
    ensure_dir(out_path); open(out_path,"w",encoding="utf-8").write(content); print(f"Wrote: {out_path}")

def main():
    ap=argparse.ArgumentParser(description="Convert raw files in signals/raw into Markdown signals. (v7)")
    ap.add_argument("--type", choices=["nps_json","company_text"], required=True)
    ap.add_argument("--file", required=True, help="Path to raw file under buyer_experience/signals/raw/")
    ap.add_argument("--market", default="DACH")
    ap.add_argument("--window_start")
    ap.add_argument("--window_end")
    ap.add_argument("--lang_infer", choices=["off","broad","de_only"], default="broad")
    ap.add_argument("--min_lang_hits", type=int, default=2)
    ap.add_argument("--country_field", default="country")
    ap.add_argument("--examples_language", default="en")
    ap.add_argument("--examples_per_group", type=int, default=5)
    ap.add_argument("--period_label", default="2025")
    ap.add_argument("--source_title", default="Company Document")
    args=ap.parse_args()

    if args.type=="nps_json":
        if not (args.window_start and args.window_end):
            sys.exit("--window_start and --window_end are required for nps_json")
        ingest_nps_json(args.file, args.market, args.window_start, args.window_end, args.lang_infer, args.min_lang_hits, args.country_field, args.examples_language, args.examples_per_group)
    else:
        ingest_company_text(args.file, args.period_label, args.source_title)

if __name__=="__main__":
    main()
