import requests
from app.config import ETHERSCAN_API_KEY, ETHERSCAN_BASE_URL, CHAIN_ID


def call_etherscan_api(module: str, action: str, params: dict | None = None):
    """
    Generic helper function to call the Etherscan API.
    """

    if params is None:
        params = {}

    request_params = {
        "chainid": CHAIN_ID,
        "module": module,
        "action": action,
        "apikey": ETHERSCAN_API_KEY,
        **params,
    }

    response = requests.get(ETHERSCAN_BASE_URL, params=request_params, timeout=10)
    response.raise_for_status()

    return response.json()