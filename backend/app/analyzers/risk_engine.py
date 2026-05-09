# backend/analyzers/risk_engine.py

def calculate_weighted_risk_score(analysis_data):
    score = 0
    reasons = []

    contract = analysis_data.get("contract", {})
    holder = analysis_data.get("holder_analysis", {})
    liquidity = analysis_data.get("liquidity_analysis", {})
    events = analysis_data.get("event_analysis", {})
    honeypot = analysis_data.get("honeypot_analysis", {})

    if not contract.get("verified"):
        score += 20
        reasons.append("Contract source code is not verified.")

    if contract.get("is_proxy"):
        score += 15
        reasons.append("Proxy contract detected.")

    dangerous_functions = contract.get("dangerous_functions_found", [])

    if "blacklist" in dangerous_functions:
        score += 20
        reasons.append("Blacklist-related function detected.")

    if "mint" in dangerous_functions or "issue" in dangerous_functions:
        score += 15
        reasons.append("Minting capability detected.")

    if holder.get("whale_risk") == "High":
        score += 20
        reasons.append("High holder concentration detected.")

    if liquidity.get("liquidity_risk") == "High":
        score += 20
        reasons.append("High liquidity risk detected.")

    if liquidity.get("creator_controls_liquidity"):
        score += 25
        reasons.append("Creator appears to control liquidity.")

    if events.get("large_mint_detected"):
        score += 20
        reasons.append("Large mint event detected.")

    if honeypot.get("honeypot_risk") == "High":
        score += 25
        reasons.append("Possible honeypot transfer restriction detected.")

    score = min(score, 100)

    if score <= 30:
        level = "Low"
    elif score <= 60:
        level = "Medium"
    elif score <= 80:
        level = "High"
    else:
        level = "Critical"

    return {
        "score": score,
        "level": level,
        "reasons": reasons
    }