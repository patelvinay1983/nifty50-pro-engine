from flask import Flask, jsonify
import requests

app = Flask(__name__)

URL = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}

session = requests.Session()


def fetch():
    try:
        session.get("https://www.nseindia.com", headers=HEADERS, timeout=5)
        r = session.get(URL, headers=HEADERS, timeout=10)
        return r.json()
    except:
        return None


@app.route("/api/signal")
def signal():

    data = fetch()

    if not data:
        return jsonify({"signal": "NO TRADE", "error": "data unavailable"})

    records = data["records"]["data"]

    ce_total = 0
    pe_total = 0
    ce_walls = {}
    pe_walls = {}

    for i in records:

        if "CE" in i:
            oi = i["CE"]["openInterest"]
            strike = i["CE"]["strikePrice"]
            ce_total += oi
            ce_walls[strike] = ce_walls.get(strike, 0) + oi

        if "PE" in i:
            oi = i["PE"]["openInterest"]
            strike = i["PE"]["strikePrice"]
            pe_total += oi
            pe_walls[strike] = pe_walls.get(strike, 0) + oi

    # PCR
    pcr = pe_total / ce_total if ce_total else 0

    # Strong walls
    resistance = max(ce_walls, key=ce_walls.get) if ce_walls else 0
    support = max(pe_walls, key=pe_walls.get) if pe_walls else 0

    # Pressure score
    total = ce_total + pe_total
    bull = pe_total / total * 100 if total else 0
    bear = ce_total / total * 100 if total else 0

    # Signal logic (SMART VERSION)
    signal = "NO TRADE"
    confidence = 50

    if pcr > 1.25 and bull > 55:
        signal = "STRONG BUY CALL"
        confidence = 80

    elif pcr > 1.1:
        signal = "WEAK BUY CALL"
        confidence = 65

    elif pcr < 0.8 and bear > 55:
        signal = "STRONG BUY PUT"
        confidence = 80

    elif pcr < 0.95:
        signal = "WEAK BUY PUT"
        confidence = 65

    return jsonify({
        "pcr": round(pcr, 2),
        "signal": signal,
        "confidence": confidence,
        "support": support,
        "resistance": resistance,
        "bullish_pressure": round(bull, 2),
        "bearish_pressure": round(bear, 2)
    })


if __name__ == "__main__":
    app.run()
