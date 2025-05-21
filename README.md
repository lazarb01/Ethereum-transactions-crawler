# Ethereum-transactions-crawler

**Ethereum-transactions-crawler** is a web application that allows you to browse Ethereum transactions for a given address starting from a specific block, and to explore the historical balance of ETH and other tokens (USDT, USDC) at a given date.

---

## Features

### Transaction Crawler
- Fetches all Ethereum transactions sent from and received by a specified wallet address starting from a chosen block number.
- Displays transactions in a table with the following columns:
  - `From` (sender)
  - `To` (recipient)
  - `ETH` (amount transferred in Ether)

### Balance Explorer
- Retrieves the balance of a selected token (ETH, USDT, USDC) for a given wallet address on a specified date.
---

## Technologies

- **Backend:** Python, FastAPI
- **Frontend:** HTML, CSS, JavaScript
- **Blockchain Access:** Web3.py, Etherscan & Infura APIs
- **Docker** 

---

## Running the project

In the root directory of the project, run:

```bash
docker compose up
```
The frontend will be available at:
http://localhost:8080



