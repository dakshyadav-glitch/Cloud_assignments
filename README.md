# Cloud Run System Health Analyzer

A lightweight Flask-based monitoring service deployed on **Google Cloud Run** that exposes real-time system metrics using Linux `/proc` and cgroup data.

This service calculates:

- CPU load & process usage
- Memory usage (host + container-level)
- CPU throttling detection
- Cold start detection
- Dynamic health score

---

## Live URL

```
https://daksh-yadav1-224372059131.us-central1.run.app
```

Health endpoint:

```
GET /analyze
```

---

# Project Overview

This application:

1. Reads system metrics directly from:
    - `/proc/loadavg`
    - `/proc/self/stat`
    - `/proc/meminfo`
    - `/sys/fs/cgroup/*`
2. Computes:
    - CPU usage estimation
    - Memory pressure
    - CPU throttling detection
    - Cold start detection
3. Generates a **dynamic health score (0–100)** based on resource usage.

---

# Sample JSON Output

```json
{
  "cpu_metrics": {
    "cpu_usage_percent_est": null,
    "last_process_id": "0",
    "load_1m": 0,
    "load_5m": 0,
    "process_cpu_seconds": 0.17,
    "runnable_processes": "0/0",
    "throttled_usec": 0,
    "throttling_detected": false
  },
  "health": {
    "cold_start": false,
    "message": "Optimal: Resource usage is optimal",
    "score": 97
  },
  "memory_metrics": {
    "available_kb": 995368,
    "container_limit_kb": 524288,
    "container_used_kb": 53124,
    "memory_pressure": false,
    "process_rss_kb": 33856,
    "total_kb": 1048576,
    "used_kb": 53208,
    "used_percent": 5.07
  },
  "note": "Basic system metrics using Linux /proc and cgroup",
  "timestamp": "2026-02-11 16:39:53",
  "uptime_seconds": 20.26
}

```

---

# JSON Field Explanation

## CPU Metrics

| Field | Description |
| --- | --- |
| `load_1m` | System load average over 1 minute |
| `load_5m` | System load average over 5 minutes |
| `runnable_processes` | Running processes vs total processes |
| `process_cpu_seconds` | Total CPU time consumed by this process |
| `cpu_usage_percent_est` | Estimated CPU % between requests |
| `throttled_usec` | Time CPU was throttled (microseconds) |
| `throttling_detected` | Boolean flag for CPU throttling |

---

## Memory Metrics

| Field | Description |
| --- | --- |
| `total_kb` | Total system memory |
| `available_kb` | Free memory available |
| `used_kb` | Used memory |
| `used_percent` | Percentage memory used |
| `process_rss_kb` | Memory used by this Flask process |
| `container_used_kb` | Memory used by container |
| `container_limit_kb` | Cloud Run memory limit |
| `memory_pressure` | True if usage > 80% of container limit |

---

## Health Object

| Field | Description |
| --- | --- |
| `score` | Calculated health score (0–100) |
| `message` | Health status message |
| `cold_start` | True if container started within last 10 seconds |

---

# Health Score Logic

Initial Score: `100`

Penalties applied:

- Memory usage → `used_percent × 0.4`
- CPU load → `load_1m × 10`
- CPU throttling → `20`
- Cold start → `10`

Score ranges:

| Score | Status |
| --- | --- |
| 81–100 | Optimal |
| 61–80 | Healthy |
| 51–60 | Warning |
| ≤50 | Critical |

---

# Run Locally

## 1️⃣ Clone Repository

```bash
gitclone <your-repo-url>cd <repo-folder>
```

## 2️⃣ Create Virtual Environment

```bash
python3 -m venv venvsource venv/bin/activate
```

## 3️⃣ Install Dependencies

Create `requirements.txt`:

```
flask
```

Then install:

```bash
pip install -r requirements.txt
```

## 4️⃣ Run Application

```bash
python app.py
```

Access locally:

```
http://localhost:8080/analyze
```

---

# Build & Deploy to Cloud Run

## 1️⃣ Set Project

```bash
gcloud configset project YOUR_PROJECT_ID
```

---

## 2️⃣ Build Container Using Cloud Build

```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/system-health-analyzer
```

---

## 3️⃣ Deploy to Cloud Run

```bash
gcloud run deploy system-health-analyzer \
  --image gcr.io/YOUR_PROJECT_ID/system-health-analyzer \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

# Architecture Overview

```
Client → Cloud Run → Flask App
                      ↓
                /proc + cgroup
                      ↓
               JSON Health Output
```

---

# Technical Highlights

- Direct Linux `/proc` parsing
- cgroup v1 memory limit detection
- CPU throttling detection
- Cold start detection
- Custom health scoring algorithm
- IST timestamp handling
- Cloud-native container deployment

---
