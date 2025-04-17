
import json
import os
import sys

FALLBACK_FILE = "data/fallback-watchlist.json"

def load_watchlist():
    if not os.path.exists(FALLBACK_FILE):
        return []
    with open(FALLBACK_FILE, "r") as f:
        return json.load(f)

def save_watchlist(data):
    os.makedirs("data", exist_ok=True)
    with open(FALLBACK_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_ticker(ticker):
    watchlist = load_watchlist()
    ticker = ticker.upper()
    if any(item["ticker"] == ticker for item in watchlist):
        print(f"⚠️ {ticker} is already in the fallback watchlist.")
        return
    watchlist.append({"ticker": ticker, "source": "manual"})
    save_watchlist(watchlist)
    print(f"✅ {ticker} added to fallback-watchlist.json")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python add_ticker.py <TICKER>")
    else:
        add_ticker(sys.argv[1])
