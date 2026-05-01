from app.utils import call_etherscan_api


def inspect_token(token_address: str):
    """
    Inspect a token contract and return basic token information.
    """

    source_data = call_etherscan_api(
        module="contract",
        action="getsourcecode",
        params={"address": token_address},
    )

    if source_data["status"] != "1":
        raise ValueError(f"Etherscan error: {source_data['result']}")

    contract_info = source_data["result"][0]

    source_code = contract_info.get("SourceCode", "")
    is_verified = source_code != ""

    risk_notes = []

    if not is_verified:
        risk_notes.append("Contract source code is not verified.")

    if "onlyOwner" in source_code:
        risk_notes.append("Contract contains owner-only functions.")

    if "pause" in source_code.lower():
        risk_notes.append("Contract may include pause/unpause functionality.")

    if "blacklist" in source_code.lower():
        risk_notes.append("Contract may include blacklist functionality.")

    if "mint" in source_code.lower() or "issue" in source_code.lower():
        risk_notes.append("Contract may allow token supply changes.")

    return {
        "address": token_address,
        "name": contract_info.get("ContractName"),
        "symbol": None,
        "decimals": None,
        "total_supply": None,
        "verified_contract": is_verified,
        "risk_notes": risk_notes,
    }