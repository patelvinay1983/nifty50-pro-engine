```python
from flask import Flask, jsonify
import requests
import time

app = Flask(__name__)

NSE_URL = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9"
}

session = requests.Session()

# Cache (60 seconds)
cache_data = None
cache_timestamp = 0
CACHE_TIME = 60


def get_nse_data():
    global cache_data, cache_timestamp

    now = time.time()

    # Use cached data if available
    if cache_data and (now - cache_timestamp < CACHE_TIME):
        return cache_data

    try:
        # Generate cookies
        session.get("https://www.nseindia.com", headers=HEADERS, timeout=5)

        # Fetch option chain
        response = session.get(NSE_URL, headers=HEADERS, timeout=10)
        data = response.json()

        cache_data = data
        cache_timestamp = now

        return data

    except Exception:
        return cache_data


@app.route("/")
def home():
    return "NIFTY50 PRO ENGINE - STAGE 2"


@app.route("/api/status")
def status():
    return jsonify({
        "engine": "NIFTY50 PRO",
        "status": "RUNNING",
        "version": "Stage 2"
    })


@app.route("/api/signal")
def signal():

    data = get_nse_data()

    if not data:
        return jsonify({
            "signal": "NO TRADE",
            "confidence": 0,
            "pcr": 0,
            "support": 0,
            "resistance": 0
        })

    records = data.get("records", {}).get("data", [])

    total_ce = 0
    total_pe = 0

    ce_dict = {}
    pe_dict = {}

    for item in records:

        strike = item.get("strikePrice")

        if "CE" in item:
            ce_oi = item["CE"].get("openInterest", 0)
            total_ce += ce_oi
            ce_dict[strike] = ce_oi

        if "PE" in item:
            pe_oi = item["PE"].get("openInterest", 0)
            total_pe += pe_oi
            pe_dict[strike] = pe_oi

    pcr = round(total_pe / total_ce, 2) if total_ce else 0

    support = max(pe_dict, key=pe_dict.get) if pe_dict else 0
    resistance = max(ce_dict, key=ce_dict.get) if ce_dict else 0

    signal = "NO TRADE"
    confidence = 50

    if pcr > 1.25:
        signal = "BUY CALL"
        confidence = min(90, int(60 + (pcr - 1) * 50))

    elif pcr < 0.80:
        signal = "BUY PUT"
        confidence = min(90, int(60 + (1 - pcr) * 50))

    return jsonify({
        "signal": signal,
        "confidence": confidence,
        "pcr": pcr,
        "support": support,
        "resistance": resistance
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

