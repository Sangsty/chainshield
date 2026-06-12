import json
import csv
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).resolve().parent.parent
RAW_DIR    = ROOT / "data" / "raw"
DATASETS   = ROOT / "data" / "datasets"
DATASETS.mkdir(parents=True, exist_ok=True)
OUTPUT_CSV = DATASETS / "fraud_dataset.csv"

# honeypot_risk is a string — convert to number for ML
HONEYPOT_RISK_MAP = {
    "Low"     : 0,
    "Medium"  : 1,
    "High"    : 2,
    "Unknown" : 1   # treat unknown as medium risk
}

# ── Extract 16 features from one token's raw JSON ────────────────────────────
def extract_features(data):
    contract  = data.get("contract", {})
    holder    = data.get("holder_analysis", {})
    liquidity = data.get("liquidity_analysis", {})
    events    = data.get("event_analysis", {})
    honeypot  = data.get("honeypot_analysis", {})

    return {
        # Contract
        "contract_verified"        : int(contract.get("verified", False)),
        "is_proxy"                 : int(contract.get("is_proxy", False)),
        "dangerous_function_count" : len(contract.get("dangerous_functions_found", [])),

        # Holders
        "top_10_holder_pct"        : holder.get("top_10_percentage", 0),
        "largest_wallet_pct"       : holder.get("largest_wallet_percentage", 0),
        "suspicious_wallet_count"  : len(holder.get("suspicious_wallets", [])),

        # Liquidity
        "burned_liquidity_pct"     : liquidity.get("burned_liquidity_percentage", 0),
        "locked_liquidity_pct"     : liquidity.get("locked_liquidity_percentage", 0),
        "creator_lp_pct"           : liquidity.get("creator_liquidity_percentage", 0),
        "top_lp_holder_pct"        : liquidity.get("top_lp_holder_percentage", 0),
        "creator_controls_liquidity": int(liquidity.get("creator_controls_liquidity", False)),

        # Events
        "mint_count"               : events.get("mint_count", 0),
        "large_mint_detected"      : int(events.get("large_mint_detected", False)),
        "ownership_renounced"      : int(events.get("ownership_renounced", False)),

        # Honeypot
        "honeypot_signal_count"    : len(honeypot.get("signals_found", [])),
        "honeypot_risk_encoded"    : HONEYPOT_RISK_MAP.get(
                                        honeypot.get("honeypot_risk", "Unknown"), 1
                                     ),
    }

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    raw_files = list(RAW_DIR.glob("*.json"))

    if not raw_files:
        print("No raw JSON files found in data/raw/")
        print("Run collect_dataset.py first.")
        return

    print(f"Found {len(raw_files)} raw token files\n")

    rows   = []
    failed = 0

    for file_path in sorted(raw_files):
        with open(file_path) as f:
            data = json.load(f)

        label   = data.get("_label",   "unknown")
        name    = data.get("_name",    "unknown")
        address = data.get("_address", file_path.stem)

        if label == "unknown":
            print(f"  [SKIP] No label in {file_path.name}")
            failed += 1
            continue

        try:
            features            = extract_features(data)
            features["address"] = address
            features["name"]    = name
            features["label"]   = label
            rows.append(features)
            print(f"  ✓  {name:<20} label={label}")
        except Exception as e:
            print(f"  ✗  {name}: {e}")
            failed += 1

    if not rows:
        print("\nNo rows extracted. Something went wrong.")
        return

    # Write CSV
    fieldnames = list(rows[0].keys())
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    safe_count = sum(1 for r in rows if r["label"] == "safe")
    scam_count = sum(1 for r in rows if r["label"] == "scam")

    print(f"\n{'='*50}")
    print(f"fraud_dataset.csv built successfully.")
    print(f"  Total rows : {len(rows)}")
    print(f"  Safe       : {safe_count}")
    print(f"  Scam       : {scam_count}")
    print(f"  Failed     : {failed}")
    print(f"  Output     : {OUTPUT_CSV}")

if __name__ == "__main__":
    main()