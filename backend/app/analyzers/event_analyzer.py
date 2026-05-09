# backend/analyzers/event_analyzer.py

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
DEAD_ADDRESS = "0x000000000000000000000000000000000000dead"

def analyze_event_logs(transfer_events=None, ownership_events=None):
    transfer_events = transfer_events or []
    ownership_events = ownership_events or []

    mint_count = 0
    burn_count = 0
    large_mint_detected = False
    ownership_renounced = False

    for event in transfer_events:
        from_address = event.get("from", "").lower()
        to_address = event.get("to", "").lower()
        value = float(event.get("value", 0))

        if from_address == ZERO_ADDRESS:
            mint_count += 1
            if value > 0:
                large_mint_detected = True

        if to_address in [ZERO_ADDRESS, DEAD_ADDRESS]:
            burn_count += 1

    for event in ownership_events:
        new_owner = event.get("new_owner", "").lower()
        if new_owner == ZERO_ADDRESS:
            ownership_renounced = True

    return {
        "mint_count": mint_count,
        "burn_count": burn_count,
        "large_mint_detected": large_mint_detected,
        "ownership_renounced": ownership_renounced
    }