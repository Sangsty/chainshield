from web3 import Web3
from app.config import ETH_RPC_URL
from app.utils import call_etherscan_api
from app.analyzers.holder_analyzer import analyze_holders
from app.analyzers.contract_analyzer import analyze_contract_risks
from app.analyzers.risk_notes import generate_risk_notes
from app.analyzers.liquidity_analyzer import analyze_liquidity


# Minimal ERC-20 ABI
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


# Uniswap V2 Ethereum mainnet factory
UNISWAP_V2_FACTORY_ADDRESS = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"

# WETH Ethereum mainnet address
WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"


UNISWAP_V2_FACTORY_ABI = [
    {
        "constant": True,
        "inputs": [
            {"name": "tokenA", "type": "address"},
            {"name": "tokenB", "type": "address"},
        ],
        "name": "getPair",
        "outputs": [{"name": "pair", "type": "address"}],
        "type": "function",
    }
]


UNISWAP_V2_PAIR_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"name": "_reserve0", "type": "uint112"},
            {"name": "_reserve1", "type": "uint112"},
            {"name": "_blockTimestampLast", "type": "uint32"},
        ],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token0",
        "outputs": [{"name": "", "type": "address"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token1",
        "outputs": [{"name": "", "type": "address"}],
        "type": "function",
    },
]
def get_contract_logs(
    token_address: str,
    topic0: str = None,
    from_block: int = 0,
    to_block: str = "latest",
):
    """
    Fetch blockchain event logs from Etherscan.

    Parameters:
    - token_address: ERC-20 contract address
    - topic0: Event signature hash
    - from_block: Starting block
    - to_block: Ending block

    Returns:
    - Raw Etherscan log response
    """

    response = call_etherscan_api(
        module="logs",
        action="getLogs",
        params={
            "address": token_address,
            "fromBlock": from_block,
            "toBlock": to_block,
            "topic0": topic0,
        },
    )

    return response
def inspect_token(token_address: str):
    """
    Inspect an ERC-20 token and return metadata, contract risk,
    holder analysis, liquidity analysis, and final risk notes.
    """

    if not Web3.is_address(token_address):
        raise ValueError("Invalid Ethereum token address")

    web3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))

    if not web3.is_connected():
        raise ValueError("Failed to connect to Ethereum RPC")

    checksum_address = Web3.to_checksum_address(token_address)

    contract = web3.eth.contract(
        address=checksum_address,
        abi=ERC20_ABI,
    )

    # --- Fetch token metadata ---
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

    # --- Fetch verified contract source from Etherscan ---
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

    # --- Holder analysis fallback ---
    holder_analysis = {
        "top_10_percentage": 0,
        "largest_wallet_percentage": 0,
        "whale_risk": "Unknown",
        "top_holders_checked": 0,
        "notes": ["Holder data unavailable."],
    }

    # --- Fetch top holders from Etherscan ---
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
                    holders.append(
                        {
                            "address": holder.get("TokenHolderAddress")
                            or holder.get("address"),
                            "balance": holder.get("TokenHolderQuantity")
                            or holder.get("balance", 0),
                        }
                    )

                holder_analysis = analyze_holders(holders, total_supply)

        except Exception:
            holder_analysis = {
                "top_10_percentage": 0,
                "largest_wallet_percentage": 0,
                "whale_risk": "Unknown",
                "top_holders_checked": 0,
                "notes": ["Holder data unavailable or API access limited."],
            }

    # --- Liquidity analysis fallback ---
    liquidity_analysis = {
        "liquidity_found": False,
        "pair_address": None,
        "reserve_token": 0,
        "reserve_weth": 0,
        "liquidity_risk": "Unknown",
        "notes": ["Liquidity data unavailable."],
    }

    # --- Check Uniswap V2 TOKEN/WETH liquidity ---
    try:
        factory_contract = web3.eth.contract(
            address=Web3.to_checksum_address(UNISWAP_V2_FACTORY_ADDRESS),
            abi=UNISWAP_V2_FACTORY_ABI,
        )

        pair_address = factory_contract.functions.getPair(
            checksum_address,
            Web3.to_checksum_address(WETH_ADDRESS),
        ).call()

        reserve_token = 0
        reserve_weth = 0

        if pair_address != "0x0000000000000000000000000000000000000000":
            pair_contract = web3.eth.contract(
                address=Web3.to_checksum_address(pair_address),
                abi=UNISWAP_V2_PAIR_ABI,
            )

            reserves = pair_contract.functions.getReserves().call()

            reserve0 = reserves[0]
            reserve1 = reserves[1]

            token0 = pair_contract.functions.token0().call()

            if token0.lower() == checksum_address.lower():
                reserve_token = reserve0
                reserve_weth = reserve1 / (10 ** 18)
            else:
                reserve_token = reserve1
                reserve_weth = reserve0 / (10 ** 18)

        liquidity_analysis = analyze_liquidity(
            pair_address=pair_address,
            reserve_token=reserve_token,
            reserve_weth=reserve_weth,
        )

    except Exception:
        liquidity_analysis = {
            "liquidity_found": False,
            "pair_address": None,
            "reserve_token": 0,
            "reserve_weth": 0,
            "liquidity_risk": "Unknown",
            "notes": ["Liquidity data unavailable or RPC call failed."],
        }

    # --- Contract risk analysis ---
    contract_risk = analyze_contract_risks(
        source_code=source_code,
        compiler_version=compiler_version,
        proxy_status=proxy_status,
        implementation_address=implementation_address,
    )

    risk_score = contract_risk["score"]

    # --- Add holder risk into total score ---
    if holder_analysis["whale_risk"] == "High":
        risk_score += 25
    elif holder_analysis["whale_risk"] == "Medium":
        risk_score += 15

    # --- Add liquidity risk into total score ---
    if liquidity_analysis["liquidity_risk"] == "High":
        risk_score += 20
    elif liquidity_analysis["liquidity_risk"] == "Medium":
        risk_score += 10

    # --- Generate final human-readable risk notes ---
    risk_notes = generate_risk_notes(
        contract_risk=contract_risk,
        holder_analysis=holder_analysis,
    )

    risk_notes.extend(liquidity_analysis["notes"])
    risk_notes = list(dict.fromkeys(risk_notes))

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
            "dangerous_functions_found": contract_risk[
                "dangerous_functions_found"
            ],
        },
        "holder_analysis": holder_analysis,
        "liquidity_analysis": liquidity_analysis,
        "risk": {
            "score": risk_score,
            "level": risk_level,
            "notes": risk_notes,
        },
    }