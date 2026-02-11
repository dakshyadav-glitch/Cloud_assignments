from flask import Flask, jsonify
import time
import os
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

# Time when container/app started
START_TIME = time.time()

# Used to calculate CPU usage between requests
LAST_CPU_TIME = None
LAST_TIME = None


def get_system_metrics():
    global LAST_CPU_TIME, LAST_TIME

    # CPU LOAD
    with open("/proc/loadavg", "r") as f:
        parts = f.read().split()
        load_1m = float(parts[0])
        load_5m = float(parts[1])
        runnable_processes = parts[3]
        p_id = parts[4]

    # PROCESS CPU & MEMORY
    with open("/proc/self/stat", "r") as f:
        stat = f.read().split()
        utime = int(stat[13])                                # user mode time
        stime = int(stat[14])                                # kernal mode time
        rss_pages = int(stat[23])

    # Convert CPU ticks to seconds
    process_cpu_seconds = (utime + stime) / 100

    # Convert memory pages to KB
    page_size_kb = os.sysconf("SC_PAGE_SIZE") // 1024
    process_rss_kb = rss_pages * page_size_kb

    #  CPU USAGE (ESTIMATED)
    cpu_usage_percent = None
    now = time.time()

    if LAST_CPU_TIME is not None:
        cpu_diff = process_cpu_seconds - LAST_CPU_TIME
        time_diff = now - LAST_TIME
        if time_diff > 0:
            cpu_usage_percent = round((cpu_diff / time_diff) * 100, 2)

    LAST_CPU_TIME = process_cpu_seconds
    LAST_TIME = now

    # ____CPU THROTTLING
    throttled_usec = 0
    throttling_detected = False

    if os.path.exists("/sys/fs/cgroup/cpu.stat"):
        with open("/sys/fs/cgroup/cpu.stat", "r") as f:
            for line in f:
                if line.startswith("throttled_usec"):
                    throttled_usec = int(line.split()[1])
                    throttling_detected = throttled_usec > 0

    # ____MEMORY INFO (cgroup v1 version)
    meminfo = {}
    with open("/proc/meminfo", "r") as f:
        for line in f:
            key, value = line.split(":")
            meminfo[key] = int(value.strip().split()[0])

    total_kb = meminfo.get("MemTotal", 0)
    available_kb = meminfo.get("MemAvailable", 0)
    used_kb = total_kb - available_kb
    used_percent = round((used_kb / total_kb) * 100, 2) if total_kb else 0

    # CONTAINER MEMORY LIMIT (v1 specific)
    container_used_kb = None
    container_limit_kb = None
    memory_pressure = False

    try:
        # Read usage in v1
        usage_path = "/sys/fs/cgroup/memory/memory.usage_in_bytes"
        if os.path.exists(usage_path):
            with open(usage_path, "r") as f:
                container_used_kb = int(f.read().strip()) // 1024

        # Read limit in v1
        limit_path = "/sys/fs/cgroup/memory/memory.limit_in_bytes"
        if os.path.exists(limit_path):
            with open(limit_path, "r") as f:
                limit_val = int(f.read().strip())
                # cgroup v1 reports a massive number if no limit is set
                if limit_val < 9223372036854771712:
                    container_limit_kb = limit_val // 1024

        if container_limit_kb and container_used_kb:
            memory_pressure = (container_used_kb / container_limit_kb) > 0.8

    except Exception as e:
        print(f"Cgroup v1 read error: {e}")

    return {
        "cpu": {
            "load_1m": load_1m,
            "load_5m": load_5m,
            "runnable_processes": runnable_processes,
            "last_process_id": p_id,
            "process_cpu_seconds": round(process_cpu_seconds, 2),
            "cpu_usage_percent_est": cpu_usage_percent,
            "throttled_usec": throttled_usec,
            "throttling_detected": throttling_detected
        },
        "memory": {
            "total_kb": total_kb,
            "available_kb": available_kb,
            "used_kb": used_kb,
            "used_percent": used_percent,
            "process_rss_kb": process_rss_kb,
            "container_used_kb": container_used_kb,
            "container_limit_kb": container_limit_kb,
            "memory_pressure": memory_pressure
        }
    }


@app.route("/")
def home():
    return "Hello from Cloud Run! System check complete."


@app.route("/analyze")
def analyze():
    metrics = get_system_metrics()
    uptime = time.time() - START_TIME

    # Detect cold start
    cold_start = uptime < 10

    # ---------------- HEALTH SCORE ----------------
    score = 100

    # Memory usage impact
    score -= min(metrics["memory"]["used_percent"], 100) * 0.4

    # CPU load impact
    score -= min(metrics["cpu"]["load_1m"] * 10, 20)

    # CPU throttling impact
    if metrics["cpu"]["throttling_detected"]:
        score -= 20

    # Cold start penalty
    if cold_start:
        score -= 10

    health_score = max(0, int(score))

    if health_score > 80:
        message = "Optimal: Resource usage is optimal"
    elif health_score > 60 and health_score <= 80:
        message = "Healthy: Normal resource usage"
    elif health_score > 50 and health_score <= 60:
        message = "Warning:System usage is high"
    else:
        message = "CRITICAL"

    # IST time
    current_time = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)

    return jsonify({
        "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "uptime_seconds": round(uptime, 2),
        "cpu_metrics": metrics["cpu"],
        "memory_metrics": metrics["memory"],
        "health": {
            "score": health_score,
            "message": message,
            "cold_start": cold_start
        },

        "note": "Basic system metrics using Linux /proc and cgroup"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
