from flask import Flask, jsonify
import time
import json
import os
from datetime import datetime, timezone

app = Flask(__name__)
START_TIME = time.time()


def get_manual_metrics():
    with open('/proc/loadavg', 'r') as f:
        cpu_load = float(f.read().split()[0])

    with open('/proc/meminfo', 'r') as f:
        lines = f.readlines()
        total_mem = int(lines[0].split()[1])
        free_mem = int(lines[1].split()[1])
        mem_usage_percent = ((total_mem - free_mem) / total_mem) * 100

        return cpu_load, round(mem_usage_percent, 2)


@app.route("/")
def hello():
    return "Hello from Cloud Run!! System check complete. You can now proceed with image."


@app.route("/analyze")
def analyze():
    cpu_load, mem_percent = get_manual_metrics()

    uptime = time.time() - START_TIME
    current_time = datetime.now(timezone.utc).isoformat()

    score = 100
    if (mem_percent > 80):
        score -= 20
    if (cpu_load > 2.0):
        score -= 20
    health_score = max(0, score)

    message = ""
    if (health_score < 70):
        message = "Warning: Resource usage is climbing up"
    elif (health_score >= 70 and health_score < 90):
        message = "Healthy: Normal resource usage"
    else:
        message = "Optimal: Resource usage is optimal"

    return jsonify({
        "timestamp": current_time,
        "uptime_seconds": round(uptime, 2),
        "cpu_metric": f"Load: {cpu_load}",
        "memory_metric": f"{mem_percent}%",
        "health_score": health_score,
        "message": message,
        "method": "Linux /proc manual parsing"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
