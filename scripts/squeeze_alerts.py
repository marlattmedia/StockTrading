
import json
import os

def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def check_squeeze_signals(watched, radar_data):
    alerts = []
    radar_lookup = {item["ticker"]: item for item in radar_data}

    for stock in watched:
        ticker = stock["ticker"]
        notes = stock.get("notes", "")

        if ticker in radar_lookup:
            data = radar_lookup[ticker]
            try:
                short_percent = float(data.get("short_percent", "0").replace('%', '').strip())
                volume = int(data.get("volume", "0").replace(',', ''))
                float_val = data.get("float", "N/A")
                price = data.get("price", "N/A")

                if short_percent >= 20 and volume > 100000:
                    alerts.append({
                        "ticker": ticker,
                        "short_percent": short_percent,
                        "volume": volume,
                        "float": float_val,
                        "price": price,
                        "notes": notes,
                        "alert": "⚠️ High Short % and Volume Surge"
                    })
            except:
                continue
    return alerts

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    watched = load_json("data/watched.json")
    radar_data = load_json("data/smart-recommendations.json")
    alerts = check_squeeze_signals(watched, radar_data)

    with open("data/squeeze-alerts.json", "w") as f:
        json.dump(alerts, f, indent=2)

    print(f"✔️ Generated {len(alerts)} squeeze alerts.")
