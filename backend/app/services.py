from web3 import Web3
from app.config import ETH_RPC_URL
from app.utils import call_etherscan_api


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
    Inspect a token contract and return token metadata + risk notes.
    """
    if not Web3.is_address(token_address):
        raise ValueError("Invalid Ethereum token address")
    # Connect to blockchain
    web3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))

    if not web3.is_connected():
        raise ValueError("Failed to connect to Ethereum RPC")

    # Create contract instance
    contract = web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)

    # --- Fetch token data safely ---
    try:
        name = contract.functions.name().call()
    except:
        name = None

    try:
        symbol = contract.functions.symbol().call()
    except:
        symbol = None

    try:
        decimals = contract.functions.decimals().call()
    except:
        decimals = None

    try:
        total_supply = contract.functions.totalSupply().call()
    except:
        total_supply = None

    # --- Etherscan: verification ---
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

    # --- Risk notes ---
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
    normalized_total_supply = None

    if total_supply is not None and decimals is not None:
        normalized_total_supply = total_supply / (10 ** decimals)
    return {
    "address": token_address,
    "name": name,
    "symbol": symbol,
    "decimals": decimals,
    "total_supply_raw": total_supply,
    "total_supply": normalized_total_supply,
    "verified_contract": is_verified,
    "risk_notes": risk_notes,
}