from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Query
from app.services import inspect_token

app = FastAPI(
    title="ChainShield API",
    description="On-chain fraud and rug pull detection backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.get("/inspect")
def inspect_token_by_query(
    address: str = Query(..., description="Ethereum token contract address")
):
    try:
        return inspect_token(address)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")