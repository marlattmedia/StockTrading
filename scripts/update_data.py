
import requests
from bs4 import BeautifulSoup
import json
import os
from time import sleep

def load_fallback_watchlist(path="data/fallback-watchlist.json"):
    with open(path, "r") as f:
        tickers = json.load(f)
    return [entry["ticker"].upper() for entry in tickers]

def scrape_finviz_for_ticker(ticker):
    url = f"https://finviz.com/quote.ashx?t={ticker}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to load {ticker} — status {response.status_code}")
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", class_="snapshot-table2")
        if not table:
            print(f"⚠️ Could not find data table for {ticker}")
            return None
        rows = table.find_all("tr")

        info = {}
        for row in rows:
            cols = row.find_all("td")
            for i in range(0, len(cols) - 1, 2):
                key = cols[i].text.strip()
                val = cols[i + 1].text.strip()
                info[key] = val

        price_str = info.get("Price", "0").replace("$", "").replace(",", "")
        try:
            price = float(price_str)
        except ValueError:
            print(f"⚠️ Could not parse price for {ticker}: {price_str}")
            return None

        if price > 100 or price < 0.5:
            print(f"⏭ Skipping {ticker} — price ${price} outside valid range.")
            return None

        short_float = info.get("Short Float", "0%")
        shares_float = info.get("Shs Float", "N/A")
        volume = info.get("Volume", "0").replace(",", "")

        return {
            "ticker": ticker,
            "price": price,
            "short_percent": short_float,
            "float": shares_float,
            "volume": volume,
            "recommendation": "Margin" if price > 10 else "TFSA"
        }

    except Exception as e:
        print(f"❌ Error with {ticker}: {e}")
        return None

def save_to_json(data, filename):
    os.makedirs("data", exist_ok=True)
    with open(f"data/{filename}", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    tickers = load_fallback_watchlist()
    results = []

    for ticker in tickers:
        result = scrape_finviz_for_ticker(ticker)
        if result:
            results.append(result)
        sleep(1)

    save_to_json(results, "smart-recommendations.json")
    print(f"✅ Saved {len(results)} tickers with valid prices under $100.")
