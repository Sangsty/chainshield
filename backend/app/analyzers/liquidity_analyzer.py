def analyze_liquidity(
    pair_address=None,
    reserve_token=0,
    reserve_weth=0,
    lp_total_supply=0,
    lp_holders=None,
    creator_address=None,
):
    """
    Analyze liquidity risk for a token.

    Phase 3 checks:
    1. Whether liquidity pair exists
    2. Whether reserves are healthy
    3. Whether LP tokens are burned
    4. Whether LP tokens are locked
    5. Whether creator controls liquidity
    """

    BURN_ADDRESSES = [
        "0x0000000000000000000000000000000000000000",
        "0x000000000000000000000000000000000000dead",
    ]

    # Known locker addresses can be expanded later
    KNOWN_LOCKER_ADDRESSES = [
        # Unicrypt / Team Finance / PinkLock etc. can be added later
    ]

    notes = []
    liquidity_found = False
    liquidity_risk = "Unknown"

    burned_liquidity_percentage = 0
    locked_liquidity_percentage = 0
    creator_liquidity_percentage = 0
    creator_controls_liquidity = False
    liquidity_lock_status = "Unknown"

    if lp_holders is None:
        lp_holders = []

    # Step 1: Check whether pair exists
    if not pair_address or pair_address == "0x0000000000000000000000000000000000000000":
        notes.append("No liquidity pool found.")

        return {
            "liquidity_found": False,
            "pair_address": None,
            "reserve_token": 0,
            "reserve_weth": 0,
            "lp_total_supply": lp_total_supply,
            "burned_liquidity_percentage": burned_liquidity_percentage,
            "locked_liquidity_percentage": locked_liquidity_percentage,
            "creator_liquidity_percentage": creator_liquidity_percentage,
            "creator_controls_liquidity": creator_controls_liquidity,
            "liquidity_lock_status": "No Pool",
            "liquidity_risk": "High",
            "notes": notes,
        }

    liquidity_found = True
    notes.append("Liquidity pair detected.")

    reserve_token = float(reserve_token or 0)
    reserve_weth = float(reserve_weth or 0)
    lp_total_supply = float(lp_total_supply or 0)

    # Step 2: Basic reserve-based liquidity risk
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

    # Step 3: LP holder analysis
    if lp_total_supply <= 0 or not lp_holders:
        notes.append("LP token holder data unavailable.")

        return {
            "liquidity_found": liquidity_found,
            "pair_address": pair_address,
            "reserve_token": reserve_token,
            "reserve_weth": reserve_weth,
            "lp_total_supply": lp_total_supply,
            "burned_liquidity_percentage": burned_liquidity_percentage,
            "locked_liquidity_percentage": locked_liquidity_percentage,
            "creator_liquidity_percentage": creator_liquidity_percentage,
            "creator_controls_liquidity": creator_controls_liquidity,
            "liquidity_lock_status": liquidity_lock_status,
            "liquidity_risk": liquidity_risk,
            "notes": notes,
        }

    for holder in lp_holders:
        holder_address = str(holder.get("address", "")).lower()
        holder_balance = float(holder.get("balance", 0) or 0)

        holder_percentage = (holder_balance / lp_total_supply) * 100

        if holder_address in BURN_ADDRESSES:
            burned_liquidity_percentage += holder_percentage

        if holder_address in KNOWN_LOCKER_ADDRESSES:
            locked_liquidity_percentage += holder_percentage

        if creator_address and holder_address == creator_address.lower():
            creator_liquidity_percentage += holder_percentage

    # Step 4: Decide lock status
    if burned_liquidity_percentage >= 50:
        liquidity_lock_status = "Burned"
        notes.append(
            f"{burned_liquidity_percentage:.2f}% of LP tokens appear to be burned."
        )

    elif locked_liquidity_percentage >= 50:
        liquidity_lock_status = "Locked"
        notes.append(
            f"{locked_liquidity_percentage:.2f}% of LP tokens appear to be locked."
        )

    elif creator_liquidity_percentage >= 50:
        liquidity_lock_status = "Creator Controlled"
        creator_controls_liquidity = True
        notes.append(
            f"Creator appears to control {creator_liquidity_percentage:.2f}% of LP tokens."
        )

    else:
        liquidity_lock_status = "Unlocked or Unknown"
        notes.append("LP token ownership does not show clear burn or lock protection.")

    # Step 5: Upgrade or reduce liquidity risk based on LP ownership
    if creator_controls_liquidity:
        liquidity_risk = "High"
        notes.append("Creator-controlled liquidity increases rug pull risk.")

    elif liquidity_lock_status in ["Burned", "Locked"] and liquidity_risk == "High":
        liquidity_risk = "Medium"
        notes.append("Burned or locked liquidity reduces liquidity risk slightly.")

    elif liquidity_lock_status in ["Burned", "Locked"] and liquidity_risk == "Medium":
        liquidity_risk = "Low"
        notes.append("Burned or locked liquidity improves liquidity safety.")

    return {
        "liquidity_found": liquidity_found,
        "pair_address": pair_address,
        "reserve_token": reserve_token,
        "reserve_weth": reserve_weth,
        "lp_total_supply": lp_total_supply,
        "burned_liquidity_percentage": round(burned_liquidity_percentage, 2),
        "locked_liquidity_percentage": round(locked_liquidity_percentage, 2),
        "creator_liquidity_percentage": round(creator_liquidity_percentage, 2),
        "creator_controls_liquidity": creator_controls_liquidity,
        "liquidity_lock_status": liquidity_lock_status,
        "liquidity_risk": liquidity_risk,
        "notes": notes,
    }