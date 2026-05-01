import os
from dotenv import load_dotenv

load_dotenv()

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
ETHERSCAN_BASE_URL = os.getenv("ETHERSCAN_BASE_URL", "https://api.etherscan.io/v2/api")
CHAIN_ID = os.getenv("CHAIN_ID", "1")
ETH_RPC_URL = os.getenv("ETH_RPC_URL", "https://ethereum.publicnode.com")