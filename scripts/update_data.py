
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

def get_finviz_squeeze_candidates():
    url = "https://finviz.com/screener.ashx?v=111&f=sh_float_u50,sh_short_o15,sh_price_o0.5,sh_price_u100&ft=4"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    data = []
    rows = soup.find_all('tr', class_='table-dark-row-cp')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) > 10:
            ticker = cols[1].text.strip()
            price = float(cols[8].text.strip().replace('$', '').replace(',', ''))
            float_val = cols[10].text.strip()
            short_pct = cols[11].text.strip()
            volume = cols[9].text.strip()
            recommendation = "TFSA" if price < 10 else "Margin"
            data.append({
                "ticker": ticker,
                "price": price,
                "float": float_val,
                "short_percent": short_pct,
                "volume": volume,
                "recommendation": recommendation
            })
    return data

def save_to_json(data, filename):
    os.makedirs("data", exist_ok=True)
    with open(f"data/{filename}", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    squeeze_data = get_finviz_squeeze_candidates()
    save_to_json(squeeze_data, "smart-recommendations.json")
