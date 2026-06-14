from flask import Flask, jsonify
import requests
import time

app = Flask(__name__)

URL = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}

session = requests.Session()

# -------- STABLE DATA FETCHER --------
def fetch_option_chain():

    try:
        # Step 1: warm-up session (cookie generation)
        session.get("https://www.nseindia.com", headers=HEADERS, timeout=5)

        # Step 2: fetch data
        response = session.get(URL, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            return None

        return response.json()

    except:
        return None


# -------- API STATUS --------
@app.route("/api/status")
def status():
    return jsonify({
        "engine": "NIFTY50 SMART MONEY ENGINE",
        "status": "STABLE DATA LAYER ACTIVE",
        "version": "4.0"
    })


# -------- MAIN SIGNAL ENGINE --------
@app.route("/api/signal")
def signal():

    data = fetch_option_chain()

    # SAFE FALLBACK (IMPORTANT)
    if not data or "records" not in data:
        return jsonify({
            "signal": "NO TRADE",
            "reason": "DATA_UNAVAILABLE",
            "pcr": 0,
            "confidence": 0,
            "support": 0,
            "resistance": 0,
            "bullish_pressure": 0,
            "bearish_pressure": 0
        })

    records = data["records"]["data"]

    ce_total = 0
    pe_total = 0

    ce_wall = {}
    pe_wall = {}

    # -------- PARSE OI --------
    for item in records:

        if "CE" in item:
            oi = item["CE"].get("openInterest", 0)
            strike = item["CE"].get("strikePrice", 0)
            ce_total += oi
            ce_wall[strike] = ce_wall.get(strike, 0) + oi

        if "PE" in item:
            oi = item["PE"].get("openInterest", 0)
            strike = item["PE"].get("strikePrice", 0)
            pe_total += oi
            pe_wall[strike] = pe_wall.get(strike, 0) + oi

    # -------- CORE METRICS --------
    total = ce_total + pe_total

    pcr = round(pe_total / ce_total, 2) if ce_total else 0

    bullish = round((pe_total / total) * 100, 2) if total else 0
    bearish = round((ce_total / total) * 100, 2) if total else 0

    support = max(pe_wall, key=pe_wall.get) if pe_wall else 0
    resistance = max(ce_wall, key=ce_wall.get) if ce_wall else 0

    # -------- SMART SIGNAL LOGIC --------
    signal = "NO TRADE"
    confidence = 50

    if pcr > 1.25 and bullish > 55:
        signal = "STRONG BUY CALL"
        confidence = 85

    elif pcr > 1.10:
        signal = "WEAK BUY CALL"
        confidence = 70

    elif pcr < 0.80 and bearish > 55:
        signal = "STRONG BUY PUT"
        confidence = 85

    elif pcr < 0.95:
        signal = "WEAK BUY PUT"
        confidence = 70

    return jsonify({
        "pcr": pcr,
        "signal": signal,
        "confidence": confidence,
        "support": support,
        "resistance": resistance,
        "bullish_pressure": bullish,
        "bearish_pressure": bearish
    })


if __name__ == "__main__":
    app.run()
