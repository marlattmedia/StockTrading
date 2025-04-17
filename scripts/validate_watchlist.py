
import requests
from bs4 import BeautifulSoup
import json
import os

def scrape_valid_ticker(ticker):
    url = f"https://finviz.com/quote.ashx?t={ticker}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return False
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", class_="snapshot-table2")
        if not table:
            return False
        price_cell = soup.find(text="Price")
        return bool(price_cell)
    except:
        return False

def load_all_sources():
    sources = [
        "data/fallback-watchlist.json",
        "data/reddit-sentiment.json",
        "data/squeeze-alerts.json"
    ]
    tickers = set()
    for source in sources:
        if os.path.exists(source):
            try:
                with open(source, "r") as f:
                    data = json.load(f)
                    for entry in data:
                        if isinstance(entry, dict) and "ticker" in entry:
                            tickers.add(entry["ticker"].upper())
                        elif isinstance(entry, str):
                            tickers.add(entry.upper())
            except Exception as e:
                print(f"⚠️ Failed to load {source}: {e}")
    return sorted(tickers)

if __name__ == "__main__":
    tickers = load_all_sources()
    valid = []

    print(f"🔍 Checking {len(tickers)} tickers...")
    for t in tickers:
        if scrape_valid_ticker(t):
            valid.append({ "ticker": t })
            print(f"✅ Valid: {t}")
        else:
            print(f"❌ Invalid or unsupported: {t}")

    os.makedirs("data", exist_ok=True)
    with open("data/validated-watchlist.json", "w") as f:
        json.dump(valid, f, indent=2)

    print(f"✅ Saved {len(valid)} validated tickers to data/validated-watchlist.json")
