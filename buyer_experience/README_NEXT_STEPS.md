# buyer_experience — prompts & CLI (v3)

Matches your layout:

buyer_experience/
  _shared/
    prompts/
  Insights/
  signals/
    quantitative/
    qualitative/
    raw/
  strategy/
    generic/

## Try first — your four files

### A) Cursor .mdc prompts (no setup)
Copy these into `buyer_experience/_shared/prompts/`:
- 00_ingest_nps_json.mdc
- 00_ingest_goals_text.mdc
- 10_generate_insight.mdc
- 20_generate_strategy_generic.mdc

Run them in this order:

1) **NPS → signal**
   - Open `00_ingest_nps_json.mdc`
   - Inputs: `market: DACH`, your `window_start`/`window_end`, and paste content of `signals/raw/nps_30d.json`
   - Output: `signals/qualitative/buyer_experience-sig-nps-DACH-<start>_<end>.md`

2) **Company docs → signals** (paste text copied from PDFs into `.txt` files under `signals/raw/`)
   - Open `00_ingest_goals_text.mdc`
   - For each file:
     - `2025_Company_Goals.txt` → `period_label: 2025`, `source_title: Company Goals 2025`
     - `2025_Q3_Company_Goals.txt` → `period_label: 2025_Q3`, `source_title: Company Goals Q3 2025`
     - `Company_Mission_Vision.txt` → `period_label: mission_vision`, `source_title: Company Mission & Vision`
   - Each run outputs: `signals/qualitative/buyer_experience-sig-company-<period_label>.md`

3) **Generate an insight**
   - Open `10_generate_insight.mdc`
   - Example inputs:
```
insight_id: be-ic-2025-08-004
type: opportunity
signal_ids:
  - buyer_experience-sig-nps-DACH-2025-07-17_2025-08-16
  - buyer_experience-sig-company-2025
  - buyer_experience-sig-company-2025_Q3
  - buyer_experience-sig-company-mission_vision
owner: federico.casabianca@eduki.com
```

4) **Generate a strategy**
   - Open `20_generate_strategy_generic.mdc`
```
strategy_id_stub: 2025-08
insight_ids:
  - be-ic-2025-08-004
tags: ["buyer_experience","dach"]
owner: federico.casabianca@eduki.com
```

### B) Python CLI (for files in `signals/raw/`)
Copy `buyer_experience/tools/ingest_signals.py` to your repo, then:

Install dependency (once):
```
pip install pyyaml
```

Run from repo root:
```
# NPS
python buyer_experience/tools/ingest_signals.py --type nps_json --file buyer_experience/signals/raw/nps_30d.json --market DACH --window_start 2025-07-17 --window_end 2025-08-16

# Company goals (annual)
python buyer_experience/tools/ingest_signals.py --type company_text --file buyer_experience/signals/raw/2025_Company_Goals.txt --period_label 2025 --source_title "Company Goals 2025"

# Company goals (Q3)
python buyer_experience/tools/ingest_signals.py --type company_text --file buyer_experience/signals/raw/2025_Q3_Company_Goals.txt --period_label 2025_Q3 --source_title "Company Goals Q3 2025"

# Mission & Vision (any text file; .txt recommended)
python buyer_experience/tools/ingest_signals.py --type company_text --file buyer_experience/signals/raw/Company_Mission_Vision.txt --period_label mission_vision --source_title "Company Mission & Vision"
```

Outputs:
- `signals/qualitative/` (NPS, company docs)
Then run the same `10_generate_insight.mdc` → `20_generate_strategy_generic.mdc` to complete the flow.
