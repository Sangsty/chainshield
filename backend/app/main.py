from fastapi import FastAPI, HTTPException
from app.services import inspect_token

app = FastAPI(
    title="ChainShield API",
    description="On-chain fraud and rug pull detection backend",
    version="0.1.0",
)


@app.get("/")
def health_check():
    return {"status": "ChainShield backend is running"}


@app.get("/inspect/{token_address}")
def inspect_token_endpoint(token_address: str):
    try:
        return inspect_token(token_address)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")