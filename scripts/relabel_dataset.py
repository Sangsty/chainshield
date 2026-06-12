import json
import csv
from pathlib import Path

ROOT       = Path(__file__).resolve().parent.parent
RAW_DIR    = ROOT / "data" / "raw"
DATASETS   = ROOT / "data" / "datasets"
OUTPUT_CSV = DATASETS / "fraud_dataset.csv"

HONEYPOT_RISK_MAP = {"Low": 0, "Medium": 1, "High": 2, "Unknown": 1}

FEATURE_COLS = [
    "contract_verified", "is_proxy", "dangerous_function_count",
    "ownership_renounced", "large_mint_detected", "mint_count",
    "top_lp_holder_pct", "honeypot_signal_count", "honeypot_risk_encoded"
]

def extract_features(data):
    contract  = data.get("contract", {})
    holder    = data.get("holder_analysis", {})
    liquidity = data.get("liquidity_analysis", {})
    events    = data.get("event_analysis", {})
    honeypot  = data.get("honeypot_analysis", {})

    return {
        "contract_verified"        : int(contract.get("verified", False)),
        "is_proxy"                 : int(contract.get("is_proxy", False)),
        "dangerous_function_count" : len(contract.get("dangerous_functions_found", [])),
        "top_10_holder_pct"        : holder.get("top_10_percentage", 0),
        "largest_wallet_pct"       : holder.get("largest_wallet_percentage", 0),
        "suspicious_wallet_count"  : len(holder.get("suspicious_wallets", [])),
        "burned_liquidity_pct"     : liquidity.get("burned_liquidity_percentage", 0),
        "locked_liquidity_pct"     : liquidity.get("locked_liquidity_percentage", 0),
        "creator_lp_pct"           : liquidity.get("creator_liquidity_percentage", 0),
        "top_lp_holder_pct"        : liquidity.get("top_lp_holder_percentage", 0),
        "creator_controls_liquidity": int(liquidity.get("creator_controls_liquidity", False)),
        "mint_count"               : events.get("mint_count", 0),
        "large_mint_detected"      : int(events.get("large_mint_detected", False)),
        "ownership_renounced"      : int(events.get("ownership_renounced", False)),
        "honeypot_signal_count"    : len(honeypot.get("signals_found", [])),
        "honeypot_risk_encoded"    : HONEYPOT_RISK_MAP.get(
                                        honeypot.get("honeypot_risk", "Unknown"), 1),
    }

def assign_label(data):
    risk = data.get("risk", {})
    score = risk.get("score", 50)

    if score >= 60:
        return "scam"
    elif score <= 40:
        return "safe"
    else:
        return None   # drop ambiguous tokens

def main():
    raw_files = list(RAW_DIR.glob("*.json"))
    print(f"Found {len(raw_files)} raw files\n")

    rows    = []
    safe_c  = 0
    scam_c  = 0
    dropped = 0

    for file_path in sorted(raw_files):
        with open(file_path) as f:
            data = json.load(f)

        name    = data.get("_name",    file_path.stem)
        address = data.get("_address", file_path.stem)

        # Use risk engine score for label
        label = assign_label(data)

        if label is None:
            print(f"  DROP  {name:<20} (ambiguous score)")
            dropped += 1
            continue

        features            = extract_features(data)
        features["address"] = address
        features["name"]    = name
        features["label"]   = label
        rows.append(features)

        if label == "safe":
            safe_c += 1
            print(f"  safe  {name:<20}")
        else:
            scam_c += 1
            print(f"  scam  {name:<20}")

    if not rows:
        print("\nNo rows extracted.")
        return

    fieldnames = list(rows[0].keys())
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n{'='*50}")
    print(f"Dataset re-labeled using risk engine scores.")
    print(f"  Safe    : {safe_c}")
    print(f"  Scam    : {scam_c}")
    print(f"  Dropped : {dropped} (ambiguous 40-60 range)")
    print(f"  Total   : {len(rows)}")
    print(f"  Output  : {OUTPUT_CSV}")

if __name__ == "__main__":
    main()