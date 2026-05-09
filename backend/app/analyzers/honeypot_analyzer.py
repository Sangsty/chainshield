# backend/analyzers/honeypot_analyzer.py

HONEYPOT_KEYWORDS = [
    "blacklist",
    "isBlacklisted",
    "setBlacklist",
    "tradingEnabled",
    "enableTrading",
    "maxTxAmount",
    "maxWallet",
    "cooldown",
    "antiBot",
    "excludeFromFee",
    "setTax",
    "sellTax",
    "buyTax",
    "transferDelay",
    "canTransfer"
]

def analyze_honeypot_signals(source_code):
    if not source_code:
        return {
            "honeypot_risk": "Unknown",
            "signals_found": [],
            "notes": ["Source code unavailable for honeypot analysis."]
        }

    found = []

    lower_source = source_code.lower()

    for keyword in HONEYPOT_KEYWORDS:
        if keyword.lower() in lower_source:
            found.append(keyword)

    if len(found) >= 5:
        risk = "High"
    elif len(found) >= 2:
        risk = "Medium"
    elif len(found) == 1:
        risk = "Low"
    else:
        risk = "Low"

    return {
        "honeypot_risk": risk,
        "signals_found": found,
        "notes": [
            "Honeypot analysis is based on static source-code signals, not live sell simulation."
        ]
    }