
import requests
from bs4 import BeautifulSoup
import json
import os
from time import sleep

def load_combined_tickers():
    sources = [
        "data/fallback-watchlist.json",
        "data/reddit-sentiment.json",
        "data/squeeze-alerts.json"
    ]
    tickers = set()
    for source in sources:
        if os.path.exists(source):
            with open(source, "r") as f:
                try:
                    data = json.load(f)
                    for entry in data:
                        if isinstance(entry, dict) and "ticker" in entry:
                            tickers.add(entry["ticker"].upper())
                        elif isinstance(entry, str):
                            tickers.add(entry.upper())
                except Exception as e:
                    print(f"⚠️ Failed to read {source}: {e}")
    return sorted(tickers)

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

        price_str = info.get("Price", "").replace("$", "").replace(",", "").strip()
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
    tickers = load_combined_tickers()
    results = []
    print(f"🔍 Found {len(tickers)} unique tickers to scan...")

    for ticker in tickers:
        result = scrape_finviz_for_ticker(ticker)
        if result:
            results.append(result)
        sleep(1)

    save_to_json(results, "data/smart-recommendations.json")
    print(f"✅ Saved {len(results)} validated tickers with Finviz data.")
