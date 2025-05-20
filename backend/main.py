from fastapi import FastAPI, HTTPException, Query # type: ignore
from fastapi.responses import HTMLResponse # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
import httpx # type: ignore
import os
from datetime import datetime
from web3 import Web3 # type: ignore

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
ETHERSCAN_API = "YKNW3S9IP8PJRWPYGZCQWPHEKKBIK6ZHAF"
WEB3_PROVIDER ="https://mainnet.infura.io/v3/5a65422129164076992ed4a071b61b57"
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))


@app.get("/", response_class=HTMLResponse)
async def transaction_crawler():
    transaction_crawler_path = os.path.join(FRONTEND_DIR, "transaction_crawler.html")
    with open(transaction_crawler_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/explorer", response_class=HTMLResponse)
async def explorer_page():
    explorer_path = os.path.join(FRONTEND_DIR, "saldo.html")
    with open(explorer_path, "r", encoding="utf-8") as f:
        return f.read()


TOKEN_ADDRESS = {
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606EB48",
}

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
]

async def get_block_by_timestamp(timestamp: int) -> int:
    url = "https://api.etherscan.io/api"
    params = {
        "module": "block",
        "action": "getblocknobytime",
        "timestamp": timestamp,
        "closest": "before",
        "apikey": ETHERSCAN_API,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    if data["status"] == "1":
        return int(data["result"])
    else:
        raise HTTPException(status_code=400, detail="Cannot retrieve the block for the given date.")

@app.get("/crawler")
async def get_transactions(
    wallet: str = Query(...,),
    start_block: int = Query(..., ge=0)
):
    url = "https://api.etherscan.io/api"
    params = {
        "module": "account",
        "action": "txlist",
        "address": wallet,
        "startblock": start_block,
        "endblock": 99999999,
        "sort": "asc",
        "apikey": ETHERSCAN_API
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    if data["status"] != "1":
        raise HTTPException(status_code=404, detail=data.get("message", "Error, data"))

    transactions = []
    for tx in data["result"]:
        transactions.append({
            "blockNumber": tx["blockNumber"],
            "timeStamp": tx["timeStamp"],
            "hash": tx["hash"],
            "from": tx["from"],
            "to": tx["to"],
            "valueETH": int(tx["value"]) / 10**18
        })

    return {"transactions": transactions}

@app.get("/explorer_history")
async def explorer_history(
    wallet: str = Query(...,),
    date: str = Query(...,),
    token: str = Query(),
):
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    if not Web3.is_address(wallet):
        raise HTTPException(status_code=400, detail="Invalid Ethereum address")
    wallet = Web3.to_checksum_address(wallet)

    timestamp = int(dt.timestamp())
    block_number = await get_block_by_timestamp(timestamp)

    if token == "ETH":
        try:
            balance_wei = w3.eth.get_balance(wallet, block_identifier=block_number)
            balance_eth = balance_wei / 10**18
            print(f"ETH balance: {balance_eth}")
            print(f"ETH balance: {block_number}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting ETH balance: {str(e)}")

        return {
            "wallet": wallet,
            "date": date,
            "block": block_number,
            "token": "ETH",
            "balance": float(balance_eth),
        }

    token_address = TOKEN_ADDRESS.get(token)
    token_address = Web3.to_checksum_address(token_address)

    try:
        contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
        balance_raw = contract.functions.balanceOf(wallet).call(block_identifier=block_number)
        decimals = contract.functions.decimals().call()
        balance = balance_raw / (10 ** decimals)
        print(f"ETH balance: {block_number}")
        return {
            "wallet": wallet,
            "date": date,
            "block": block_number,
            "token": token,
            "balance": round(balance, 6),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token balance error:{str(e)}")
