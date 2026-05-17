# backend/analyzers/risk_engine.py


def calculate_weighted_risk_score(analysis_data):
    """
    Calculate final weighted fraud/rug-pull risk score.

    Phase 3 improved scoring:
    1. Contract risk
    2. Holder concentration risk
    3. Liquidity risk
    4. Creator/deployer liquidity control
    5. Event-based mint/burn behavior
    6. Honeypot-style transfer restrictions
    7. Liquidity safety reductions
    """

    score = 0
    reasons = []
    category_breakdown = {
        "contract_risk": 0,
        "holder_risk": 0,
        "liquidity_risk": 0,
        "event_risk": 0,
        "honeypot_risk": 0,
        "creator_risk": 0,
        "safety_adjustments": 0,
    }

    contract = analysis_data.get("contract", {})
    holder = analysis_data.get("holder_analysis", {})
    liquidity = analysis_data.get("liquidity_analysis", {})
    events = analysis_data.get("event_analysis", {})
    honeypot = analysis_data.get("honeypot_analysis", {})
    creator = analysis_data.get("creator", {})

    dangerous_functions = [
        function.lower()
        for function in contract.get("dangerous_functions_found", [])
    ]

    # -----------------------------
    # Contract risk signals
    # -----------------------------

    if not contract.get("verified"):
        score += 20
        category_breakdown["contract_risk"] += 20
        reasons.append("Contract source code is not verified.")

    if contract.get("is_proxy"):
        score += 15
        category_breakdown["contract_risk"] += 15
        reasons.append("Proxy contract detected.")

    if "blacklist" in dangerous_functions:
        score += 20
        category_breakdown["contract_risk"] += 20
        reasons.append("Blacklist-related function detected.")

    if "pause" in dangerous_functions or "pausable" in dangerous_functions:
        score += 10
        category_breakdown["contract_risk"] += 10
        reasons.append("Pause functionality detected.")

    if "mint" in dangerous_functions or "issue" in dangerous_functions:
        score += 15
        category_breakdown["contract_risk"] += 15
        reasons.append("Minting capability detected.")

    if "transferownership" in dangerous_functions:
        score += 8
        category_breakdown["contract_risk"] += 8
        reasons.append("Ownership transfer capability detected.")

    # -----------------------------
    # Holder concentration risk
    # -----------------------------

    if holder.get("whale_risk") == "High":
        score += 20
        category_breakdown["holder_risk"] += 20
        reasons.append("High holder concentration detected.")

    elif holder.get("whale_risk") == "Medium":
        score += 10
        category_breakdown["holder_risk"] += 10
        reasons.append("Moderate holder concentration detected.")

    largest_wallet_percentage = holder.get("largest_wallet_percentage", 0)

    if largest_wallet_percentage and largest_wallet_percentage >= 25:
        score += 10
        category_breakdown["holder_risk"] += 10
        reasons.append(
            f"Largest wallet holds {largest_wallet_percentage}% of supply."
        )

    # -----------------------------
    # Liquidity risk signals
    # -----------------------------

    if liquidity.get("liquidity_risk") == "High":
        score += 20
        category_breakdown["liquidity_risk"] += 20
        reasons.append("High liquidity risk detected.")

    elif liquidity.get("liquidity_risk") == "Medium":
        score += 10
        category_breakdown["liquidity_risk"] += 10
        reasons.append("Medium liquidity risk detected.")

    if liquidity.get("creator_controls_liquidity"):
        score += 30
        category_breakdown["creator_risk"] += 30
        reasons.append("Creator appears to control liquidity.")

    creator_liquidity_percentage = liquidity.get(
        "creator_liquidity_percentage", 0
    )

    if creator_liquidity_percentage >= 20:
        score += 15
        category_breakdown["creator_risk"] += 15
        reasons.append(
            f"Creator controls {creator_liquidity_percentage}% of LP tokens."
        )

    # -----------------------------
    # Deployer / creator intelligence
    # -----------------------------

    creator_address = creator.get("creator_address")

    if creator_address:
        category_breakdown["creator_risk"] += 0
        reasons.append("Creator wallet identified for deployer tracking.")
    else:
        score += 5
        category_breakdown["creator_risk"] += 5
        reasons.append("Creator wallet could not be identified.")

    # -----------------------------
    # Event-based risk signals
    # -----------------------------

    if events.get("large_mint_detected"):
        score += 20
        category_breakdown["event_risk"] += 20
        reasons.append("Large mint event detected.")

    if events.get("mint_count", 0) >= 3:
        score += 10
        category_breakdown["event_risk"] += 10
        reasons.append("Multiple mint events detected.")

    if events.get("ownership_renounced"):
        score -= 5
        category_breakdown["safety_adjustments"] -= 5
        reasons.append("Ownership renouncement reduces admin-control risk.")

    # -----------------------------
    # Honeypot risk signals
    # -----------------------------

    if honeypot.get("honeypot_risk") == "High":
        score += 25
        category_breakdown["honeypot_risk"] += 25
        reasons.append("High honeypot-style transfer restriction risk detected.")

    elif honeypot.get("honeypot_risk") == "Medium":
        score += 12
        category_breakdown["honeypot_risk"] += 12
        reasons.append("Moderate honeypot-style transfer restriction risk detected.")

    signals_found = honeypot.get("signals_found", [])

    if len(signals_found) >= 5:
        score += 10
        category_breakdown["honeypot_risk"] += 10
        reasons.append("Multiple honeypot-related source-code signals detected.")

    # -----------------------------
    # Liquidity safety adjustments
    # -----------------------------

    liquidity_lock_status = liquidity.get("liquidity_lock_status")

    if liquidity_lock_status == "Burned":
        score -= 15
        category_breakdown["safety_adjustments"] -= 15
        reasons.append("Burned liquidity reduces rug-pull risk.")

    elif liquidity_lock_status == "Locked":
        score -= 10
        category_breakdown["safety_adjustments"] -= 10
        reasons.append("Locked liquidity reduces rug-pull risk.")

    burned_percentage = liquidity.get("burned_liquidity_percentage", 0)

    if burned_percentage >= 50:
        score -= 10
        category_breakdown["safety_adjustments"] -= 10
        reasons.append(
            f"{burned_percentage}% of LP tokens appear to be burned."
        )

    # -----------------------------
    # Final score normalization
    # -----------------------------

    score = max(score, 0)
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
        "reasons": reasons,
        "category_breakdown": category_breakdown,
    }