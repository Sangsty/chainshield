def generate_risk_notes(contract_risk, holder_analysis):
    """
    Generate human-readable risk notes from analyzer outputs.
    """

    final_notes = []

    # --- Contract notes ---
    final_notes.extend(contract_risk.get("notes", []))

    # --- Holder notes ---
    final_notes.extend(holder_analysis.get("notes", []))

    # --- Additional human-readable warnings ---
    dangerous_functions = contract_risk.get(
        "dangerous_functions_found",
        []
    )

    for function_name in dangerous_functions:
        final_notes.append(
            f"Contract contains dangerous function: {function_name}"
        )

    whale_risk = holder_analysis.get("whale_risk")

    if whale_risk == "High":
        final_notes.append(
            "High whale concentration detected."
        )

    elif whale_risk == "Medium":
        final_notes.append(
            "Moderate whale concentration detected."
        )

    return list(dict.fromkeys(final_notes))