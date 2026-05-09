def analyze_holders(holders, total_supply):
    """
    Analyze token holder concentration and suspicious wallets.

    Phase 3 improvements:
    1. Calculates largest wallet percentage
    2. Calculates top 10 holder concentration
    3. Detects whale risk
    4. Reports suspicious wallets
    """

    notes = []
    suspicious_wallets = []

    if not holders or not total_supply:
        return {
            "top_10_percentage": 0,
            "largest_wallet_percentage": 0,
            "whale_risk": "Unknown",
            "top_holders_checked": 0,
            "suspicious_wallets": [],
            "notes": ["Holder data unavailable."],
        }

    total_supply = float(total_supply)

    holder_percentages = []

    for holder in holders:
        address = holder.get("address")
        balance = float(holder.get("balance", 0) or 0)

        percentage = (balance / total_supply) * 100

        holder_percentages.append(
            {
                "address": address,
                "balance": balance,
                "percentage": round(percentage, 2),
            }
        )

        if percentage >= 10:
            suspicious_wallets.append(
                {
                    "address": address,
                    "percentage": round(percentage, 2),
                    "reason": "Wallet holds 10% or more of total token supply.",
                }
            )

    holder_percentages = sorted(
        holder_percentages,
        key=lambda item: item["percentage"],
        reverse=True,
    )

    top_10_holders = holder_percentages[:10]

    top_10_percentage = sum(
        holder["percentage"] for holder in top_10_holders
    )

    largest_wallet_percentage = (
        top_10_holders[0]["percentage"] if top_10_holders else 0
    )

    if largest_wallet_percentage > 20 or top_10_percentage > 60:
        whale_risk = "High"
        notes.append("High holder concentration detected.")

    elif largest_wallet_percentage >= 10 or top_10_percentage >= 40:
        whale_risk = "Medium"
        notes.append("Moderate holder concentration detected.")

    else:
        whale_risk = "Low"
        notes.append("Holder distribution appears reasonably balanced.")

    return {
        "top_10_percentage": round(top_10_percentage, 2),
        "largest_wallet_percentage": round(largest_wallet_percentage, 2),
        "whale_risk": whale_risk,
        "top_holders_checked": len(top_10_holders),
        "suspicious_wallets": suspicious_wallets,
        "top_holders": top_10_holders,
        "notes": notes,
    }