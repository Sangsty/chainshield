# backend/analyzers/event_analyzer.py

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

DEAD_ADDRESSES = [
    "0x0000000000000000000000000000000000000000",
    "0x000000000000000000000000000000000000dead",
]


def analyze_event_logs(transfer_events=None, ownership_events=None):
    """
    Analyze blockchain event activity.

    Phase 3 checks:
    1. Mint events
    2. Burn events
    3. Ownership renouncement
    4. Large mint behavior
    5. Basic transfer activity statistics
    """

    transfer_events = transfer_events or []
    ownership_events = ownership_events or []

    mint_count = 0
    burn_count = 0
    total_transfer_volume = 0

    ownership_renounced = False
    large_mint_detected = False

    largest_mint_value = 0
    largest_burn_value = 0

    suspicious_events = []
    notes = []

    # --- Analyze transfer events ---
    for event in transfer_events:
        try:
            from_address = str(event.get("from", "")).lower()
            to_address = str(event.get("to", "")).lower()

            value = float(event.get("value", 0) or 0)

            total_transfer_volume += value

            # --- Mint detection ---
            if from_address == ZERO_ADDRESS:
                mint_count += 1

                if value > largest_mint_value:
                    largest_mint_value = value

                # Large mint heuristic
                if value > 1_000_000:
                    large_mint_detected = True

                    suspicious_events.append(
                        {
                            "type": "Large Mint",
                            "value": value,
                            "reason": "Large token mint detected from zero address.",
                        }
                    )

            # --- Burn detection ---
            if to_address in DEAD_ADDRESSES:
                burn_count += 1

                if value > largest_burn_value:
                    largest_burn_value = value

        except Exception:
            continue

    # --- Analyze ownership events ---
    for event in ownership_events:
        try:
            new_owner = str(
                event.get("new_owner", "")
            ).lower()

            previous_owner = str(
                event.get("previous_owner", "")
            ).lower()

            if new_owner == ZERO_ADDRESS:
                ownership_renounced = True

                suspicious_events.append(
                    {
                        "type": "Ownership Renounced",
                        "previous_owner": previous_owner,
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
        "largest_mint_value": largest_mint_value,
        "largest_burn_value": largest_burn_value,
        "large_mint_detected": large_mint_detected,
        "ownership_renounced": ownership_renounced,
        "total_transfer_volume": total_transfer_volume,
        "suspicious_events": suspicious_events,
        "notes": notes,
    }