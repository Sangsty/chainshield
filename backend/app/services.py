from web3 import Web3

from app.config import ETH_RPC_URL
from app.utils import call_etherscan_api

from app.analyzers.holder_analyzer import analyze_holders
from app.analyzers.contract_analyzer import analyze_contract_risks
from app.analyzers.liquidity_analyzer import analyze_liquidity
from app.analyzers.risk_engine import calculate_weighted_risk_score
from app.analyzers.event_analyzer import analyze_event_logs
from app.analyzers.honeypot_analyzer import analyze_honeypot_signals


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


TRANSFER_EVENT_TOPIC = (
    "0x" + Web3.keccak(text="Transfer(address,address,uint256)").hex()
)

OWNERSHIP_TRANSFERRED_TOPIC = (
    "0x" + Web3.keccak(text="OwnershipTransferred(address,address)").hex()
)


UNISWAP_V2_FACTORY_ADDRESS = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
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
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
]


def get_contract_logs(
    token_address: str,
    topic0: str = None,
    from_block: int = 0,
    to_block: str = "latest",
):
    params = {
        "address": token_address,
        "fromBlock": from_block,
        "toBlock": to_block,
        "page": 1,
        "offset": 100,
    }

    if topic0:
        params["topic0"] = topic0

    return call_etherscan_api(
        module="logs",
        action="getLogs",
        params=params,
    )


def extract_address_from_topic(topic: str):
    if not topic:
        return None

    return "0x" + topic[-40:]


def decode_transfer_logs(raw_logs):
    transfer_events = []

    for log in raw_logs:
        try:
            topics = log.get("topics", [])

            if len(topics) < 3:
                continue

            from_address = extract_address_from_topic(topics[1])
            to_address = extract_address_from_topic(topics[2])
            value = int(log.get("data", "0x0"), 16)

            transfer_events.append(
                {
                    "from": from_address,
                    "to": to_address,
                    "value": value,
                    "transaction_hash": log.get("transactionHash"),
                    "block_number": log.get("blockNumber"),
                }
            )

        except Exception:
            continue

    return transfer_events


def decode_ownership_logs(raw_logs):
    ownership_events = []

    for log in raw_logs:
        try:
            topics = log.get("topics", [])

            if len(topics) < 3:
                continue

            previous_owner = extract_address_from_topic(topics[1])
            new_owner = extract_address_from_topic(topics[2])

            ownership_events.append(
                {
                    "previous_owner": previous_owner,
                    "new_owner": new_owner,
                    "transaction_hash": log.get("transactionHash"),
                    "block_number": log.get("blockNumber"),
                }
            )

        except Exception:
            continue

    return ownership_events


def estimate_holders_from_transfer_events(transfer_events, limit=10):
    """
    Estimate token holders from Transfer events.
    Used as fallback when top-holder API is unavailable.
    """

    balances = {}

    for event in transfer_events:
        from_address = event.get("from")
        to_address = event.get("to")
        value = int(event.get("value", 0) or 0)

        if from_address:
            from_address = from_address.lower()
            balances[from_address] = balances.get(from_address, 0) - value

        if to_address:
            to_address = to_address.lower()
            balances[to_address] = balances.get(to_address, 0) + value

    holders = []

    for address, balance in balances.items():
        if balance > 0:
            holders.append(
                {
                    "address": address,
                    "balance": balance,
                }
            )

    holders = sorted(
        holders,
        key=lambda holder: holder["balance"],
        reverse=True,
    )

    return holders[:limit]


def fetch_top_token_holders(contract_address: str, limit: int = 10):
    """
    Fetch top token holders using Etherscan token holder API.
    Used for both token holders and LP token holders.
    """

    holders = []

    try:
        holders_data = call_etherscan_api(
            module="token",
            action="topholders",
            params={
                "contractaddress": contract_address,
                "offset": limit,
            },
        )

        if holders_data.get("status") == "1":
            raw_holders = holders_data.get("result", [])

            for holder in raw_holders:
                holders.append(
                    {
                        "address": holder.get("TokenHolderAddress")
                        or holder.get("address"),
                        "balance": holder.get("TokenHolderQuantity")
                        or holder.get("balance", 0),
                    }
                )

    except Exception:
        return []

    return holders


def get_contract_creator(contract_address: str):
    """
    Fetch contract creator/deployer wallet from Etherscan.
    """

    try:
        creator_data = call_etherscan_api(
            module="contract",
            action="getcontractcreation",
            params={
                "contractaddresses": contract_address,
            },
        )

        if creator_data.get("status") == "1":
            result = creator_data.get("result", [])

            if result:
                return {
                    "creator_address": result[0].get("contractCreator"),
                    "creation_tx_hash": result[0].get("txHash"),
                }

    except Exception:
        pass

    return {
        "creator_address": None,
        "creation_tx_hash": None,
    }


def inspect_token(token_address: str):
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

    source_data = call_etherscan_api(
        module="contract",
        action="getsourcecode",
        params={"address": token_address},
    )

    if source_data.get("status") != "1":
        raise ValueError(f"Etherscan error: {source_data.get('result')}")

    contract_info = source_data["result"][0]

    compiler_version = contract_info.get("CompilerVersion", "")
    proxy_status = contract_info.get("Proxy", "0")
    implementation_address = contract_info.get("Implementation", "")
    source_code = contract_info.get("SourceCode", "")
    is_verified = source_code != ""

    creator_info = get_contract_creator(token_address)
    creator_address = creator_info.get("creator_address")

    holder_analysis = {
        "top_10_percentage": 0,
        "largest_wallet_percentage": 0,
        "whale_risk": "Unknown",
        "top_holders_checked": 0,
        "suspicious_wallets": [],
        "notes": ["Holder data unavailable."],
    }

    if total_supply is not None:
        holders = fetch_top_token_holders(token_address, limit=10)

        if holders:
            holder_analysis = analyze_holders(holders, total_supply)
        else:
            holder_analysis = {
                "top_10_percentage": 0,
                "largest_wallet_percentage": 0,
                "whale_risk": "Unknown",
                "top_holders_checked": 0,
                "suspicious_wallets": [],
                "notes": ["Holder data unavailable or API access limited."],
            }

    liquidity_analysis = {
        "liquidity_found": False,
        "pair_address": None,
        "reserve_token": 0,
        "reserve_weth": 0,
        "lp_total_supply": 0,
        "burned_liquidity_percentage": 0,
        "locked_liquidity_percentage": 0,
        "creator_liquidity_percentage": 0,
        "creator_controls_liquidity": False,
        "liquidity_lock_status": "Unknown",
        "liquidity_risk": "Unknown",
        "notes": ["Liquidity data unavailable."],
    }

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
        lp_total_supply = 0
        lp_holders = []

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

            try:
                lp_total_supply = pair_contract.functions.totalSupply().call()
            except Exception:
                lp_total_supply = 0

            lp_holders = fetch_top_token_holders(pair_address, limit=10)

            if not lp_holders:
                try:
                    lp_transfer_logs_response = get_contract_logs(
                        token_address=pair_address,
                        topic0=TRANSFER_EVENT_TOPIC,
                        from_block=0,
                        to_block="latest",
                    )

                    if lp_transfer_logs_response.get("status") == "1":
                        raw_lp_transfer_logs = lp_transfer_logs_response.get(
                            "result", []
                        )

                        lp_transfer_events = decode_transfer_logs(
                            raw_lp_transfer_logs
                        )

                        lp_holders = estimate_holders_from_transfer_events(
                            lp_transfer_events,
                            limit=10,
                        )

                except Exception:
                    lp_holders = []

        liquidity_analysis = analyze_liquidity(
            pair_address=pair_address,
            reserve_token=reserve_token,
            reserve_weth=reserve_weth,
            lp_total_supply=lp_total_supply,
            lp_holders=lp_holders,
            creator_address=creator_address,
        )

    except Exception:
        liquidity_analysis = {
            "liquidity_found": False,
            "pair_address": None,
            "reserve_token": 0,
            "reserve_weth": 0,
            "lp_total_supply": 0,
            "burned_liquidity_percentage": 0,
            "locked_liquidity_percentage": 0,
            "creator_liquidity_percentage": 0,
            "creator_controls_liquidity": False,
            "liquidity_lock_status": "Unknown",
            "liquidity_risk": "Unknown",
            "notes": ["Liquidity data unavailable or RPC call failed."],
        }

    contract_risk = analyze_contract_risks(
        source_code=source_code,
        compiler_version=compiler_version,
        proxy_status=proxy_status,
        implementation_address=implementation_address,
    )

    contract_analysis = {
        "verified": is_verified,
        "compiler_version": compiler_version,
        "is_proxy": proxy_status == "1",
        "implementation_address": implementation_address or None,
        "dangerous_functions_found": contract_risk[
            "dangerous_functions_found"
        ],
    }

    transfer_events = []
    ownership_events = []

    try:
        transfer_logs_response = get_contract_logs(
            token_address=token_address,
            topic0=TRANSFER_EVENT_TOPIC,
            from_block=0,
            to_block="latest",
        )

        if transfer_logs_response.get("status") == "1":
            raw_transfer_logs = transfer_logs_response.get("result", [])
            transfer_events = decode_transfer_logs(raw_transfer_logs)

    except Exception:
        transfer_events = []

    try:
        ownership_logs_response = get_contract_logs(
            token_address=token_address,
            topic0=OWNERSHIP_TRANSFERRED_TOPIC,
            from_block=0,
            to_block="latest",
        )

        if ownership_logs_response.get("status") == "1":
            raw_ownership_logs = ownership_logs_response.get("result", [])
            ownership_events = decode_ownership_logs(raw_ownership_logs)

    except Exception:
        ownership_events = []

    event_analysis = analyze_event_logs(
        transfer_events=transfer_events,
        ownership_events=ownership_events,
        decimals=decimals,
        total_supply=total_supply,
    )

    honeypot_analysis = analyze_honeypot_signals(source_code)

    final_risk = calculate_weighted_risk_score(
        {
            "contract": contract_analysis,
            "holder_analysis": holder_analysis,
            "liquidity_analysis": liquidity_analysis,
            "event_analysis": event_analysis,
            "honeypot_analysis": honeypot_analysis,
            "creator": creator_info,
        }
    )

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
        "contract": contract_analysis,
        "creator": creator_info,
        "holder_analysis": holder_analysis,
        "liquidity_analysis": liquidity_analysis,
        "event_analysis": event_analysis,
        "honeypot_analysis": honeypot_analysis,
        "risk": final_risk,
    }