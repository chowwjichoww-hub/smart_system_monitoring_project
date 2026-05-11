
from flask import Flask, render_template, jsonify
import psutil
import random

app = Flask(__name__)

def get_system_health():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    health_score = int((100 - ((cpu + ram + disk) / 3)))

    return {
        "cpu": cpu,
        "ram": ram,
        "disk": disk,
        "health_score": health_score,
        "prediction": random.choice([
            "System Stable",
            "Performance Normal",
            "Minor Performance Drop"
        ])
    }

@app.route("/")
def home():
    data = get_system_health()
    return render_template("index.html", data=data)

@app.route("/api/health")
def api_health():
    return jsonify(get_system_health())

if __name__ == "__main__":
    app.run(debug=True)
