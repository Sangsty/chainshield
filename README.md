# chainshield
# ChainShield

ChainShield is an On-Chain Fraud & Rug Pull Detection Platform.

## Phase 1: Token Inspector MVP

The current MVP inspects an Ethereum ERC-20 token contract and returns:

- Token name
- Token symbol
- Decimals
- Total supply
- Contract verification status
- Compiler version
- Proxy status
- Basic risk score
- Risk level
- Risk notes

## Tech Stack

- Python
- FastAPI
- Web3.py
- Etherscan API
- Ethereum RPC

## Run Backend

```bash
cd backend
python -m uvicorn app.main:app --reload



## Phase 2: Risk Signal Engine

Phase 2 expands ChainShield from a basic ERC-20 token inspector into an on-chain risk analysis engine.

### Implemented Features

- Holder Analyzer
  - Added holder concentration analysis framework
  - Added whale-risk classification
  - Handles unavailable holder data safely without breaking the API

- Contract Risk Analyzer
  - Detects owner-only logic
  - Detects dangerous smart contract functions such as mint, blacklist, pause, issue, and transfer ownership
  - Checks proxy status and implementation contracts
  - Flags older Solidity compiler versions

- Liquidity Analyzer
  - Checks Uniswap V2 TOKEN/WETH liquidity pair existence
  - Reads liquidity pool reserves
  - Classifies liquidity risk as Low, Medium, High, or Unknown

- Risk Notes Engine
  - Generates human-readable warnings
  - Combines contract, holder, and liquidity signals into one structured report
  - Supports future expansion for more fraud indicators

### Tested Tokens

- USDT
- UNI
- LINK

### Current Limitations

- Holder data depends on Etherscan API availability.
- Liquidity analysis currently supports Ethereum mainnet Uniswap V2 TOKEN/WETH pairs.
- Liquidity lock/burn detection is not included yet.
- Risk scoring is heuristic and should not be treated as financial advice.
