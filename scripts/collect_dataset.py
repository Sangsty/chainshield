import json
import time
import requests
from pathlib import Path

# ── Paths ───────────────────────────────────────────────────────────────────
ROOT        = Path(__file__).resolve().parent.parent
TOKEN_LISTS = ROOT / "data" / "token_lists"
RAW_DIR     = ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

BACKEND_URL          = "http://127.0.0.1:8000/inspect"
SLEEP_BETWEEN_CALLS  = 3   # seconds — prevents hammering Etherscan rate limits

# ── Load both token lists ────────────────────────────────────────────────────
def load_tokens():
    with open(TOKEN_LISTS / "safe_tokens.json") as f:
        safe_tokens = json.load(f)
    with open(TOKEN_LISTS / "scam_tokens.json") as f:
        scam_tokens = json.load(f)

    all_tokens = safe_tokens + scam_tokens
    print(f"Loaded {len(safe_tokens)} safe + {len(scam_tokens)} scam = {len(all_tokens)} total tokens\n")
    return all_tokens

# ── Fetch one token from your backend ───────────────────────────────────────
def fetch_token(address, name, label):
    url = f"{BACKEND_URL}/{address}"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data          = response.json()
            data["_label"]   = label     # attach label so build_features can read it
            data["_name"]    = name
            data["_address"] = address
            return data
        else:
            print(f"  [HTTP {response.status_code}] {name}")
            return None
    except requests.exceptions.Timeout:
        print(f"  [TIMEOUT] {name}")
        return None
    except Exception as e:
        print(f"  [ERROR] {name}: {e}")
        return None

# ── Save raw response to data/raw/ ───────────────────────────────────────────
def save_raw(data, address):
    out_path = RAW_DIR / f"{address}.json"
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)

# ── Main loop ────────────────────────────────────────────────────────────────
def main():
    tokens  = load_tokens()
    success = 0
    failed  = 0
    skipped = 0

    for i, token in enumerate(tokens, 1):
        address = token["address"]
        name    = token["name"]
        label   = token["label"]

        out_path = RAW_DIR / f"{address}.json"

        # Skip if already collected — safe to re-run script anytime
        if out_path.exists():
            print(f"[{i:02}/{len(tokens)}] SKIP (already collected): {name}")
            skipped += 1
            continue

        print(f"[{i:02}/{len(tokens)}] Fetching {name} ({label}) ... ", end="", flush=True)

        data = fetch_token(address, name, label)

        if data:
            save_raw(data, address)
            print("✓")
            success += 1
        else:
            print("✗ FAILED")
            failed += 1

        time.sleep(SLEEP_BETWEEN_CALLS)

    print(f"\n{'='*50}")
    print(f"Collection complete.")
    print(f"  Success  : {success}")
    print(f"  Skipped  : {skipped}  (already existed)")
    print(f"  Failed   : {failed}")
    print(f"  Raw files: {RAW_DIR}")

if __name__ == "__main__":
    main()