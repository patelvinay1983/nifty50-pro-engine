from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "NIFTY50 PRO Engine Running"

@app.route("/api/status")
def status():
    return jsonify({
        "status": "running",
        "engine": "NIFTY50 PRO",
        "version": "2.0"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
