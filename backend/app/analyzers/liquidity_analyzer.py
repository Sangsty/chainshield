def analyze_liquidity(pair_address=None, reserve_token=0, reserve_weth=0):
    """
    Analyze basic liquidity risk for a token.

    For Phase 2, this analyzer only checks:
    1. Whether a liquidity pair exists
    2. Whether reserves are available
    3. Whether liquidity appears weak
    """

    notes = []
    liquidity_found = False
    liquidity_risk = "Unknown"

    if not pair_address or pair_address == "0x0000000000000000000000000000000000000000":
        notes.append("No liquidity pool found.")
        return {
            "liquidity_found": False,
            "pair_address": None,
            "reserve_token": 0,
            "reserve_weth": 0,
            "liquidity_risk": "High",
            "notes": notes,
        }

    liquidity_found = True
    notes.append("Liquidity pair detected.")

    reserve_token = float(reserve_token or 0)
    reserve_weth = float(reserve_weth or 0)

    if reserve_token == 0 or reserve_weth == 0:
        liquidity_risk = "High"
        notes.append("Liquidity pool has zero or incomplete reserves.")

    elif reserve_weth < 1:
        liquidity_risk = "High"
        notes.append("Liquidity appears very weak.")

    elif reserve_weth < 10:
        liquidity_risk = "Medium"
        notes.append("Liquidity appears limited.")

    else:
        liquidity_risk = "Low"
        notes.append("Liquidity appears healthy.")

    return {
        "liquidity_found": liquidity_found,
        "pair_address": pair_address,
        "reserve_token": reserve_token,
        "reserve_weth": reserve_weth,
        "liquidity_risk": liquidity_risk,
        "notes": notes,
    }