import json
import csv
from pathlib import Path

ROOT       = Path(__file__).resolve().parent.parent
RAW_DIR    = ROOT / "data" / "raw"
DATASETS   = ROOT / "data" / "datasets"
OUTPUT_CSV = DATASETS / "fraud_dataset.csv"

HONEYPOT_RISK_MAP = {"Low": 0, "Medium": 1, "High": 2, "Unknown": 1}

def extract_features(data):
    contract  = data.get("contract",          {})
    liquidity = data.get("liquidity_analysis",{})
    events    = data.get("event_analysis",    {})
    honeypot  = data.get("honeypot_analysis", {})
    risk      = data.get("risk",              {})
    breakdown = risk.get("category_breakdown",{})

    return {
        # Contract features
        "contract_verified"        : int(contract.get("verified", False)),
        "is_proxy"                 : int(contract.get("is_proxy", False)),
        "dangerous_function_count" : len(contract.get("dangerous_functions_found", [])),

        # Liquidity features
        "top_lp_holder_pct"        : liquidity.get("top_lp_holder_percentage", 0),
        "creator_controls_liquidity": int(liquidity.get("creator_controls_liquidity", False)),

        # Event features
        "mint_count"               : events.get("mint_count", 0),
        "large_mint_detected"      : int(events.get("large_mint_detected", False)),
        "ownership_renounced"      : int(events.get("ownership_renounced", False)),

        # Honeypot features
        "honeypot_signal_count"    : len(honeypot.get("signals_found", [])),
        "honeypot_risk_encoded"    : HONEYPOT_RISK_MAP.get(
                                        honeypot.get("honeypot_risk", "Unknown"), 1),

        # Risk engine scores — strong ML signal
        "risk_score"               : risk.get("score", 0),
        "contract_risk_score"      : breakdown.get("contract_risk",  0),
        "honeypot_risk_score"      : breakdown.get("honeypot_risk",  0),
        "event_risk_score"         : breakdown.get("event_risk",     0),
        "liquidity_risk_score"     : breakdown.get("liquidity_risk", 0),
    }

def main():
    raw_files = list(RAW_DIR.glob("*.json"))

    if not raw_files:
        print("No raw files found. Run collect_dataset.py first.")
        return

    print(f"Found {len(raw_files)} raw token files\n")

    rows   = []
    failed = 0

    for file_path in sorted(raw_files):
        with open(file_path) as f:
            data = json.load(f)

        # Use ORIGINAL labels from token lists — ground truth
        label   = data.get("_label",   "unknown")
        name    = data.get("_name",    "unknown")
        address = data.get("_address", file_path.stem)

        if label == "unknown":
            print(f"  [SKIP] No label: {file_path.name}")
            failed += 1
            continue

        try:
            features            = extract_features(data)
            features["address"] = address
            features["name"]    = name
            features["label"]   = label
            rows.append(features)
            score = data.get("risk", {}).get("score", "?")
            print(f"  ✓  {name:<22} label={label:<5}  risk_score={score}")
        except Exception as e:
            print(f"  ✗  {name}: {e}")
            failed += 1

    if not rows:
        print("\nNo rows extracted.")
        return

    fieldnames = list(rows[0].keys())
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    safe_count = sum(1 for r in rows if r["label"] == "safe")
    scam_count = sum(1 for r in rows if r["label"] == "scam")

    print(f"\n{'='*50}")
    print(f"fraud_dataset.csv rebuilt.")
    print(f"  Safe    : {safe_count}")
    print(f"  Scam    : {scam_count}")
    print(f"  Failed  : {failed}")
    print(f"  Total   : {len(rows)}")
    print(f"  Output  : {OUTPUT_CSV}")

if __name__ == "__main__":
    main()