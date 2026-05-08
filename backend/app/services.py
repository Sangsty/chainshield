from web3 import Web3
from app.config import ETH_RPC_URL
from app.utils import call_etherscan_api
from app.analyzers.holder_analyzer import analyze_holders


# Minimal ERC-20 ABI (only what we need)
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
]


def inspect_token(token_address: str):
    """
    Inspect a token contract and return token metadata + holder analysis + risk notes.
    """

    if not Web3.is_address(token_address):
        raise ValueError("Invalid Ethereum token address")

    # Connect to Ethereum RPC
    web3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))

    if not web3.is_connected():
        raise ValueError("Failed to connect to Ethereum RPC")

    checksum_address = Web3.to_checksum_address(token_address)

    # Create ERC-20 contract instance
    contract = web3.eth.contract(
        address=checksum_address,
        abi=ERC20_ABI,
    )

    # --- Fetch token metadata safely ---
    try:
        name = contract.functions.name().call()
    except Exception:
        name = None

    try:
        symbol = contract.functions.symbol().call()
    except Exception:
        symbol = None

    try:
        decimals = contract.functions.decimals().call()
    except Exception:
        decimals = None

    try:
        total_supply = contract.functions.totalSupply().call()
    except Exception:
        total_supply = None

    # --- Etherscan: contract source verification ---
    source_data = call_etherscan_api(
        module="contract",
        action="getsourcecode",
        params={"address": token_address},
    )

    if source_data["status"] != "1":
        raise ValueError(f"Etherscan error: {source_data['result']}")

    contract_info = source_data["result"][0]

    compiler_version = contract_info.get("CompilerVersion", "")
    proxy_status = contract_info.get("Proxy", "0")
    implementation_address = contract_info.get("Implementation", "")
    source_code = contract_info.get("SourceCode", "")
    is_verified = source_code != ""

    # --- Holder analysis default fallback ---
    holder_analysis = {
        "top_10_percentage": 0,
        "largest_wallet_percentage": 0,
        "whale_risk": "Unknown",
        "top_holders_checked": 0,
        "notes": ["Holder data unavailable."]
    }

    # --- Etherscan: top holders ---
    if total_supply is not None:
        try:
            holders_data = call_etherscan_api(
                module="token",
                action="topholders",
                params={
                    "contractaddress": token_address,
                    "offset": 10,
                },
            )

            if holders_data.get("status") == "1":
                raw_holders = holders_data.get("result", [])

                holders = []

                for holder in raw_holders:
                    holders.append({
                        "address": holder.get("TokenHolderAddress") or holder.get("address"),
                        "balance": holder.get("TokenHolderQuantity") or holder.get("balance", 0),
                    })

                holder_analysis = analyze_holders(holders, total_supply)

        except Exception:
            holder_analysis = {
                "top_10_percentage": 0,
                "largest_wallet_percentage": 0,
                "whale_risk": "Unknown",
                "top_holders_checked": 0,
                "notes": ["Holder data unavailable or API access limited."]
            }

    # --- Risk notes + score ---
    risk_notes = []
    risk_score = 0

    if not is_verified:
        risk_notes.append("Contract source code is not verified.")
        risk_score += 25

    if "onlyOwner" in source_code:
        risk_notes.append("Contract contains owner-only functions.")
        risk_score += 15

    if "pause" in source_code.lower():
        risk_notes.append("Contract may include pause/unpause functionality.")
        risk_score += 10

    if "blacklist" in source_code.lower():
        risk_notes.append("Contract may include blacklist functionality.")
        risk_score += 20

    if "mint" in source_code.lower() or "issue" in source_code.lower():
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

    # --- Add holder risk into total score ---
    if holder_analysis["whale_risk"] == "High":
        risk_score += 25
    elif holder_analysis["whale_risk"] == "Medium":
        risk_score += 15

    risk_notes.extend(holder_analysis["notes"])

    # --- Decide final risk level ---
    if risk_score >= 70:
        risk_level = "High"
    elif risk_score >= 40:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    # --- Normalize token supply ---
    normalized_total_supply = None

    if total_supply is not None and decimals is not None:
        normalized_total_supply = total_supply / (10 ** decimals)

    return {
        "token": {
            "address": token_address,
            "name": name,
            "symbol": symbol,
            "decimals": decimals,
            "total_supply_raw": total_supply,
            "total_supply": normalized_total_supply,
        },
        "contract": {
            "verified": is_verified,
            "compiler_version": compiler_version,
            "is_proxy": proxy_status == "1",
            "implementation_address": implementation_address or None,
        },
        "holder_analysis": holder_analysis,
        "risk": {
            "score": risk_score,
            "level": risk_level,
            "notes": risk_notes,
        },
    }