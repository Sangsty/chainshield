# backend/analyzers/liquidity_analyzer.py


def analyze_liquidity(
    pair_address=None,
    reserve_token=0,
    reserve_weth=0,
    lp_total_supply=0,
    lp_holders=None,
    creator_address=None,
):
    """
    Analyze liquidity safety and rug-pull risk.

    Phase 3 Final Checks:
    1. Liquidity pool existence
    2. Reserve health
    3. Burned liquidity detection
    4. Locked liquidity detection
    5. Creator-controlled liquidity detection
    6. LP ownership concentration analysis
    """

    BURN_ADDRESSES = [
        "0x0000000000000000000000000000000000000000",
        "0x000000000000000000000000000000000000dead",
    ]

    # Common locker addresses
    KNOWN_LOCKER_ADDRESSES = [
        "0x663a5c229c09b049e36dcc11fae4a8eb9e8891b4",  # Team Finance
        "0x71b5759d73262fbb223956913ecf4ecc51057641",  # Unicrypt
        "0x5c5b7f0d6b0f4e3b9f8f4c2b7fbb7d0e2c5f5f7f",  # Example placeholder
    ]

    notes = []

    liquidity_found = False
    liquidity_risk = "Unknown"

    burned_liquidity_percentage = 0
    locked_liquidity_percentage = 0
    creator_liquidity_percentage = 0

    creator_controls_liquidity = False
    liquidity_lock_status = "Unknown"

    top_lp_holder_percentage = 0

    if lp_holders is None:
        lp_holders = []

    # ---------------------------------
    # Step 1: Liquidity pair existence
    # ---------------------------------

    if (
        not pair_address
        or pair_address
        == "0x0000000000000000000000000000000000000000"
    ):
        notes.append("No liquidity pool found.")

        return {
            "liquidity_found": False,
            "pair_address": None,
            "reserve_token": 0,
            "reserve_weth": 0,
            "lp_total_supply": lp_total_supply,
            "burned_liquidity_percentage": 0,
            "locked_liquidity_percentage": 0,
            "creator_liquidity_percentage": 0,
            "top_lp_holder_percentage": 0,
            "creator_controls_liquidity": False,
            "liquidity_lock_status": "No Pool",
            "liquidity_risk": "High",
            "notes": notes,
        }

    liquidity_found = True
    notes.append("Liquidity pair detected.")

    reserve_token = float(reserve_token or 0)
    reserve_weth = float(reserve_weth or 0)
    lp_total_supply = float(lp_total_supply or 0)

    # ---------------------------------
    # Step 2: Reserve-based liquidity quality
    # ---------------------------------

    if reserve_token == 0 or reserve_weth == 0:
        liquidity_risk = "High"
        notes.append("Liquidity pool has zero or incomplete reserves.")

    elif reserve_weth < 1:
        liquidity_risk = "High"
        notes.append("Liquidity appears extremely weak.")

    elif reserve_weth < 10:
        liquidity_risk = "Medium"
        notes.append("Liquidity appears limited.")

    elif reserve_weth < 50:
        liquidity_risk = "Medium"
        notes.append("Liquidity is moderate but not deeply established.")

    else:
        liquidity_risk = "Low"
        notes.append("Liquidity appears healthy.")

    # ---------------------------------
    # Step 3: LP ownership analysis
    # ---------------------------------

    if lp_total_supply <= 0 or not lp_holders:
        notes.append("LP token holder data unavailable.")

        return {
            "liquidity_found": liquidity_found,
            "pair_address": pair_address,
            "reserve_token": reserve_token,
            "reserve_weth": reserve_weth,
            "lp_total_supply": lp_total_supply,
            "burned_liquidity_percentage": 0,
            "locked_liquidity_percentage": 0,
            "creator_liquidity_percentage": 0,
            "top_lp_holder_percentage": 0,
            "creator_controls_liquidity": False,
            "liquidity_lock_status": "Unknown",
            "liquidity_risk": liquidity_risk,
            "notes": notes,
        }

    for holder in lp_holders:
        holder_address = str(holder.get("address", "")).lower()
        holder_balance = float(holder.get("balance", 0) or 0)

        holder_percentage = (
            (holder_balance / lp_total_supply) * 100
            if lp_total_supply > 0
            else 0
        )

        if holder_percentage > top_lp_holder_percentage:
            top_lp_holder_percentage = holder_percentage

        # Burn detection
        if holder_address in BURN_ADDRESSES:
            burned_liquidity_percentage += holder_percentage

        # Known locker detection
        if holder_address in KNOWN_LOCKER_ADDRESSES:
            locked_liquidity_percentage += holder_percentage

        # Creator LP ownership detection
        if creator_address and holder_address == creator_address.lower():
            creator_liquidity_percentage += holder_percentage

    # ---------------------------------
    # Step 4: Decide liquidity lock status
    # ---------------------------------

    if burned_liquidity_percentage >= 50:
        liquidity_lock_status = "Burned"

        notes.append(
            f"{burned_liquidity_percentage:.2f}% of LP tokens appear burned."
        )

    elif locked_liquidity_percentage >= 50:
        liquidity_lock_status = "Locked"

        notes.append(
            f"{locked_liquidity_percentage:.2f}% of LP tokens appear locked."
        )

    elif creator_liquidity_percentage >= 50:
        liquidity_lock_status = "Creator Controlled"

        creator_controls_liquidity = True

        notes.append(
            f"Creator controls {creator_liquidity_percentage:.2f}% of LP tokens."
        )

    else:
        liquidity_lock_status = "Unlocked or Unknown"

        notes.append(
            "LP ownership does not show strong burn or lock protection."
        )

    # ---------------------------------
    # Step 5: LP concentration heuristics
    # ---------------------------------

    if top_lp_holder_percentage >= 80:
        liquidity_risk = "High"

        notes.append(
            f"Single LP holder controls {top_lp_holder_percentage:.2f}% of LP supply."
        )

    elif top_lp_holder_percentage >= 50:
        if liquidity_risk == "Low":
            liquidity_risk = "Medium"

        notes.append(
            f"LP ownership is highly concentrated ({top_lp_holder_percentage:.2f}%)."
        )

    # ---------------------------------
    # Step 6: Creator rug-pull heuristics
    # ---------------------------------

    if creator_controls_liquidity:
        liquidity_risk = "High"

        notes.append(
            "Creator-controlled liquidity significantly increases rug-pull risk."
        )

    elif creator_liquidity_percentage >= 20:
        if liquidity_risk == "Low":
            liquidity_risk = "Medium"

        notes.append(
            f"Creator still controls {creator_liquidity_percentage:.2f}% of LP tokens."
        )

    # ---------------------------------
    # Step 7: Liquidity safety reductions
    # ---------------------------------

    if liquidity_lock_status == "Burned":
        if liquidity_risk == "High":
            liquidity_risk = "Medium"

        elif liquidity_risk == "Medium":
            liquidity_risk = "Low"

        notes.append("Burned liquidity reduces rug-pull risk.")

    elif liquidity_lock_status == "Locked":
        if liquidity_risk == "High":
            liquidity_risk = "Medium"

        elif liquidity_risk == "Medium":
            liquidity_risk = "Low"

        notes.append("Locked liquidity improves liquidity safety.")

    return {
        "liquidity_found": liquidity_found,
        "pair_address": pair_address,
        "reserve_token": reserve_token,
        "reserve_weth": reserve_weth,
        "lp_total_supply": lp_total_supply,
        "burned_liquidity_percentage": round(
            burned_liquidity_percentage,
            2,
        ),
        "locked_liquidity_percentage": round(
            locked_liquidity_percentage,
            2,
        ),
        "creator_liquidity_percentage": round(
            creator_liquidity_percentage,
            2,
        ),
        "top_lp_holder_percentage": round(
            top_lp_holder_percentage,
            2,
        ),
        "creator_controls_liquidity": creator_controls_liquidity,
        "liquidity_lock_status": liquidity_lock_status,
        "liquidity_risk": liquidity_risk,
        "notes": notes,
    }