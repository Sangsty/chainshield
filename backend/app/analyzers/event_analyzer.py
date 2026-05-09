# backend/analyzers/event_analyzer.py

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

DEAD_ADDRESSES = [
    "0x0000000000000000000000000000000000000000",
    "0x000000000000000000000000000000000000dead",
]


def normalize_value(raw_value, decimals):
    """
    Convert raw ERC-20 token value into human-readable token amount.
    """

    try:
        if decimals is None:
            return float(raw_value)

        return float(raw_value) / (10 ** int(decimals))

    except Exception:
        return 0


def calculate_supply_percentage(value, total_supply):
    """
    Calculate how much percentage of total supply a value represents.
    """

    try:
        if not total_supply or total_supply == 0:
            return 0

        return (float(value) / float(total_supply)) * 100

    except Exception:
        return 0


def analyze_event_logs(
    transfer_events=None,
    ownership_events=None,
    decimals=None,
    total_supply=None,
):
    """
    Analyze blockchain event activity.

    Phase 3 improved checks:
    1. Mint events
    2. Burn events
    3. Ownership renouncement
    4. Large mint behavior using total supply percentage
    5. Normalized event values
    6. Basic transfer activity statistics
    """

    transfer_events = transfer_events or []
    ownership_events = ownership_events or []

    mint_count = 0
    burn_count = 0

    total_transfer_volume_raw = 0
    total_transfer_volume = 0

    ownership_renounced = False
    large_mint_detected = False

    largest_mint_raw = 0
    largest_mint_value = 0
    largest_mint_percentage = 0

    largest_burn_raw = 0
    largest_burn_value = 0
    largest_burn_percentage = 0

    suspicious_events = []
    notes = []

    normalized_total_supply = normalize_value(total_supply, decimals)

    # --- Analyze transfer events ---
    for event in transfer_events:
        try:
            from_address = str(event.get("from", "")).lower()
            to_address = str(event.get("to", "")).lower()

            raw_value = float(event.get("value", 0) or 0)
            normalized_value = normalize_value(raw_value, decimals)

            total_transfer_volume_raw += raw_value
            total_transfer_volume += normalized_value

            # --- Mint detection ---
            if from_address == ZERO_ADDRESS:
                mint_count += 1

                mint_percentage = calculate_supply_percentage(
                    normalized_value,
                    normalized_total_supply,
                )

                if normalized_value > largest_mint_value:
                    largest_mint_raw = raw_value
                    largest_mint_value = normalized_value
                    largest_mint_percentage = mint_percentage

                # Smarter large mint heuristic
                if mint_percentage >= 5:
                    large_mint_detected = True

                    suspicious_events.append(
                        {
                            "type": "Large Mint",
                            "value": round(normalized_value, 4),
                            "percentage_of_supply": round(mint_percentage, 2),
                            "transaction_hash": event.get("transaction_hash"),
                            "block_number": event.get("block_number"),
                            "reason": "Mint event represents 5% or more of total supply.",
                        }
                    )

            # --- Burn detection ---
            if to_address in DEAD_ADDRESSES:
                burn_count += 1

                burn_percentage = calculate_supply_percentage(
                    normalized_value,
                    normalized_total_supply,
                )

                if normalized_value > largest_burn_value:
                    largest_burn_raw = raw_value
                    largest_burn_value = normalized_value
                    largest_burn_percentage = burn_percentage

        except Exception:
            continue

    # --- Analyze ownership events ---
    for event in ownership_events:
        try:
            new_owner = str(event.get("new_owner", "")).lower()
            previous_owner = str(event.get("previous_owner", "")).lower()

            if new_owner == ZERO_ADDRESS:
                ownership_renounced = True

                suspicious_events.append(
                    {
                        "type": "Ownership Renounced",
                        "previous_owner": previous_owner,
                        "transaction_hash": event.get("transaction_hash"),
                        "block_number": event.get("block_number"),
                        "reason": "Contract ownership was renounced.",
                    }
                )

        except Exception:
            continue

    # --- Human-readable notes ---
    if mint_count > 0:
        notes.append(f"{mint_count} mint event(s) detected.")

    if burn_count > 0:
        notes.append(f"{burn_count} burn event(s) detected.")

    if largest_mint_percentage >= 5:
        notes.append(
            f"Largest mint equals {largest_mint_percentage:.2f}% of total supply."
        )

    if largest_burn_percentage > 0:
        notes.append(
            f"Largest burn equals {largest_burn_percentage:.2f}% of total supply."
        )

    if ownership_renounced:
        notes.append("Ownership renouncement detected.")

    if large_mint_detected:
        notes.append("Large mint activity detected.")

    if not transfer_events:
        notes.append("No transfer events available.")

    if not ownership_events:
        notes.append("No ownership events available.")

    return {
        "transfer_events_checked": len(transfer_events),
        "ownership_events_checked": len(ownership_events),
        "mint_count": mint_count,
        "burn_count": burn_count,
        "largest_mint_raw": largest_mint_raw,
        "largest_mint_value": round(largest_mint_value, 4),
        "largest_mint_percentage": round(largest_mint_percentage, 2),
        "largest_burn_raw": largest_burn_raw,
        "largest_burn_value": round(largest_burn_value, 4),
        "largest_burn_percentage": round(largest_burn_percentage, 2),
        "large_mint_detected": large_mint_detected,
        "ownership_renounced": ownership_renounced,
        "total_transfer_volume_raw": total_transfer_volume_raw,
        "total_transfer_volume": round(total_transfer_volume, 4),
        "suspicious_events": suspicious_events,
        "notes": notes,
    }