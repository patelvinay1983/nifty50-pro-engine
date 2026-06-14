from flask import Flask, jsonify
import requests
import time

app = Flask(__name__)

NSE_URL = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}

session = requests.Session()

def get_nse_data():
    try:
        # Step 1: create session cookies
        session.get("https://www.nseindia.com", headers=HEADERS, timeout=5)

        # Step 2: fetch option chain
        response = session.get(NSE_URL, headers=HEADERS, timeout=10)

        return response.json()

    except Exception as e:
        return None


@app.route("/")
def home():
    return "NIFTY50 PRO ENGINE - STABLE MODE"


@app.route("/api/status")
def status():
    return jsonify({
        "engine": "NIFTY50 PRO",
        "status": "STABLE LIVE MODE",
        "version": "3.1"
    })


@app.route("/api/signal")
def signal():

    data = get_nse_data()

    # 🔴 FALLBACK (VERY IMPORTANT)
    if not data:
        return jsonify({
            "error": "Data source unavailable",
            "signal": "NO TRADE",
            "pcr": 0,
            "confidence": 0,
            "support": 0,
            "resistance": 0
        })

    records = data.get("records", {}).get("data", [])

    total_ce = 0
    total_pe = 0

    ce_levels = []
    pe_levels = []

    for item in records:
        if "CE" in item:
            total_ce += item["CE"].get("openInterest", 0)
            ce_levels.append(item["CE"].get("openInterest", 0))

        if "PE" in item:
            total_pe += item["PE"].get("openInterest", 0)
            pe_levels.append(item["PE"].get("openInterest", 0))

    # PCR calculation
    pcr = round(total_pe / total_ce, 2) if total_ce else 0

    # Support / Resistance zones
    support = max(pe_levels) if pe_levels else 0
    resistance = max(ce_levels) if ce_levels else 0

    # Signal logic (cleaned)
    signal = "NO TRADE"
    confidence = 50

    if pcr > 1.25:
        signal = "BUY CALL"
        confidence = min(90, int(60 + (pcr - 1) * 50))

    elif pcr < 0.80:
        signal = "BUY PUT"
        confidence = min(90, int(60 + (1 - pcr) * 50))

    return jsonify({
        "pcr": pcr,
        "signal": signal,
        "confidence": confidence,
        "support": support,
        "resistance": resistance
    })


if __name__ == "__main__":
    app.run()
