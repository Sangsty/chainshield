DANGEROUS_FUNCTION_KEYWORDS = [
    "mint",
    "issue",
    "blacklist",
    "pause",
    "settax",
    "setfee",
    "transferownership",
    "excludeFromFees",
    "setMaxTx",
    "setTradingEnabled",
]


def analyze_contract_risks(source_code, compiler_version, proxy_status, implementation_address):
    """
    Analyze verified contract source code for dangerous functions and admin privileges.
    """

    risk_notes = []
    risk_score = 0

    source_code = source_code or ""
    source_code_lower = source_code.lower()
    compiler_version = compiler_version or ""

    if source_code == "":
        risk_notes.append("Contract source code is not verified.")
        risk_score += 25

    if "onlyowner" in source_code_lower:
        risk_notes.append("Contract contains owner-only functions.")
        risk_score += 15

    if "pause" in source_code_lower:
        risk_notes.append("Contract may include pause/unpause functionality.")
        risk_score += 10

    if "blacklist" in source_code_lower:
        risk_notes.append("Contract may include blacklist functionality.")
        risk_score += 20

    if "mint" in source_code_lower or "issue" in source_code_lower:
        risk_notes.append("Contract may allow token supply changes.")
        risk_score += 20

    if proxy_status == "1":
        risk_notes.append("Contract is upgradeable through a proxy.")
        risk_score += 15

    if implementation_address:
        risk_notes.append("Implementation contract detected.")
        risk_score += 10

    if "0.4." in compiler_version or "0.5." in compiler_version:
        risk_notes.append("Contract uses an older Solidity compiler version.")
        risk_score += 10

    dangerous_functions_found = []

    for keyword in DANGEROUS_FUNCTION_KEYWORDS:
        if keyword.lower() in source_code_lower:
            dangerous_functions_found.append(keyword)

    return {
        "score": risk_score,
        "notes": risk_notes,
        "dangerous_functions_found": dangerous_functions_found,
    }