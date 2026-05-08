BURN_ADDRESSES = {
    "0x0000000000000000000000000000000000000000",
    "0x000000000000000000000000000000000000dead",
}


def analyze_holders(holders, total_supply):
    """
    Analyze token holder concentration and whale risk.

    holders format expected:
    [
        {"address": "0x...", "balance": 12345},
        {"address": "0x...", "balance": 67890}
    ]
    """

    if not holders or not total_supply or total_supply == 0:
        return {
            "top_10_percentage": 0,
            "largest_wallet_percentage": 0,
            "whale_risk": "Unknown",
            "notes": ["Holder data unavailable."]
        }

    valid_holders = []

    for holder in holders:
        address = holder.get("address", "").lower()
        balance = float(holder.get("balance", 0))

        if address not in BURN_ADDRESSES:
            valid_holders.append({
                "address": address,
                "balance": balance
            })

    sorted_holders = sorted(
        valid_holders,
        key=lambda h: h["balance"],
        reverse=True
    )

    top_10_holders = sorted_holders[:10]
    top_10_total = sum(holder["balance"] for holder in top_10_holders)

    largest_wallet_balance = sorted_holders[0]["balance"] if sorted_holders else 0

    top_10_percentage = (top_10_total / float(total_supply)) * 100
    largest_wallet_percentage = (largest_wallet_balance / float(total_supply)) * 100

    if largest_wallet_percentage >= 20 or top_10_percentage >= 80:
        whale_risk = "High"
    elif largest_wallet_percentage >= 10 or top_10_percentage >= 50:
        whale_risk = "Medium"
    else:
        whale_risk = "Low"

    notes = [
        f"Top 10 holders own {top_10_percentage:.2f}% of supply.",
        f"Largest holder owns {largest_wallet_percentage:.2f}% of supply.",
        f"Whale risk is {whale_risk}."
    ]

    return {
        "top_10_percentage": round(top_10_percentage, 2),
        "largest_wallet_percentage": round(largest_wallet_percentage, 2),
        "whale_risk": whale_risk,
        "top_holders_checked": len(top_10_holders),
        "notes": notes
    }