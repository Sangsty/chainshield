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
