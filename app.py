from flask import Flask, jsonify
import random

app = Flask(__name__)

@app.route("/")
def home():
    return "NIFTY50 PRO Engine Running"

@app.route("/api/status")
def status():
    return jsonify({
        "engine": "NIFTY50 PRO",
        "status": "running",
        "version": "2.1"
    })

@app.route("/api/signal")
def signal():

    pcr = round(random.uniform(0.7, 1.4), 2)

    signal = "NO TRADE"
    confidence = 50

    if pcr > 1.2:
        signal = "BUY CALL"
        confidence = 78

    elif pcr < 0.8:
        signal = "BUY PUT"
        confidence = 78

    support = random.randint(24500, 24900)
    resistance = random.randint(24950, 25300)

    return jsonify({
        "pcr": pcr,
        "signal": signal,
        "confidence": confidence,
        "support": support,
        "resistance": resistance
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
