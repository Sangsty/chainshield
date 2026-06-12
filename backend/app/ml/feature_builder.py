from pathlib import Path

HONEYPOT_RISK_MAP = {"Low": 0, "Medium": 1, "High": 2, "Unknown": 1}

def build_features(inspect_response: dict) -> dict:
    """
    Converts the raw /inspect/ API response into a flat feature dict
    that the ML model can consume.
    """
    contract  = inspect_response.get("contract",           {})
    liquidity = inspect_response.get("liquidity_analysis", {})
    events    = inspect_response.get("event_analysis",     {})
    honeypot  = inspect_response.get("honeypot_analysis",  {})
    risk      = inspect_response.get("risk",               {})
    breakdown = risk.get("category_breakdown",             {})

    return {
        "contract_verified"         : int(contract.get("verified", False)),
        "is_proxy"                  : int(contract.get("is_proxy", False)),
        "dangerous_function_count"  : len(contract.get("dangerous_functions_found", [])),
        "top_lp_holder_pct"         : liquidity.get("top_lp_holder_percentage", 0),
        "creator_controls_liquidity": int(liquidity.get("creator_controls_liquidity", False)),
        "mint_count"                : events.get("mint_count", 0),
        "large_mint_detected"       : int(events.get("large_mint_detected", False)),
        "ownership_renounced"       : int(events.get("ownership_renounced", False)),
        "honeypot_signal_count"     : len(honeypot.get("signals_found", [])),
        "honeypot_risk_encoded"     : HONEYPOT_RISK_MAP.get(
                                         honeypot.get("honeypot_risk", "Unknown"), 1),
        "risk_score"                : risk.get("score", 0),
        "contract_risk_score"       : breakdown.get("contract_risk",  0),
        "honeypot_risk_score"       : breakdown.get("honeypot_risk",  0),
        "event_risk_score"          : breakdown.get("event_risk",     0),
        "liquidity_risk_score"      : breakdown.get("liquidity_risk", 0),
    }