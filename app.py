from flask import Flask, jsonify
import requests

app = Flask(__name__)

NSE_URL = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9"
}

def fetch_data():
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers, timeout=5)
    response = session.get(NSE_URL, headers=headers, timeout=10)
    return response.json()

@app.route("/")
def home():
    return "NIFTY50 PRO ENGINE - LIVE MODE"

@app.route("/api/status")
def status():
    return jsonify({
        "engine": "NIFTY50 PRO",
        "status": "LIVE MARKET MODE",
        "version": "3.0"
    })

@app.route("/api/signal")
def signal():

    data = fetch_data()

    records = data["records"]["data"]

    total_ce_oi = 0
    total_pe_oi = 0

    ce_levels = []
    pe_levels = []

    for item in records:
        if "CE" in item:
            ce_oi = item["CE"]["openInterest"]
            total_ce_oi += ce_oi
            ce_levels.append(ce_oi)

        if "PE" in item:
            pe_oi = item["PE"]["openInterest"]
            total_pe_oi += pe_oi
            pe_levels.append(pe_oi)

    # PCR
    pcr = total_pe_oi / total_ce_oi if total_ce_oi != 0 else 0

    # Support / Resistance (OI walls)
    support = max(pe_levels) if pe_levels else 0
    resistance = max(ce_levels) if ce_levels else 0

    signal = "NO TRADE"
    confidence = 50

    if pcr > 1.2:
        signal = "BUY CALL"
        confidence = min(90, 60 + int(pcr * 10))

    elif pcr < 0.8:
        signal = "BUY PUT"
        confidence = min(90, 60 + int((1 - pcr) * 100))

    return jsonify({
        "pcr": round(pcr, 2),
        "signal": signal,
        "confidence": confidence,
        "support": support,
        "resistance": resistance
    })

if __name__ == "__main__":
    app.run()
