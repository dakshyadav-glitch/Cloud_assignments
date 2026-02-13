# Cloud Run System Health Monitor (Flask)

A lightweight **Flask-based system health monitoring service** containerized with Docker and deployed on **Google Cloud Run**.

The application exposes REST endpoints to verify service availability and analyze runtime system metrics such as CPU load, memory usage, uptime, and overall health score.

---

## Objective

To demonstrate hands-on proficiency in:

- Linux & shell scripting fundamentals
- Python Flask application development
- Containerization using Docker
- Serverless deployment using **Google Cloud Run**
- Designing custom system health metrics and scoring logic
    
    ---
    

## Project Structure

```jsx

├── sys_check.sh          # Linux automation & system logging script
├── deploy_app/
│   ├── main.py           # Flask application (core logic)
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile        # Container configuration for Cloud Run
└── README.md

```

---

## Application Overview

### 🔹 Root Endpoint

**GET /**

Returns a simple confirmation message indicating the service is running.

```jsx
Hello from Cloud Run!! System check complete. You can now proceed with image.
```

### 🔹 Analyze Endpoint

**GET /analyze**

Returns dynamic system health metrics from inside the running container.

### Sample JSON Response

```
{
  "timestamp": "2026-02-09T10:45:12.345Z",
  "uptime_seconds": 123.45,
  "cpu_metric": "Load: 0.87",
  "memory_metric": "42.18%",
  "health_score": 100,
  "message": "Optimal: Resource usage is optimal",
  "method": "Linux /proc manual parsing"
}

```

---

## Metrics & Logic

- **CPU Metric**
    - Parsed manually from `/proc/loadavg`
- **Memory Metric**
    - Calculated using `/proc/meminfo`
- **Uptime**
    - Measured from application start time
- **Health Score (0–100)**
    - −20 if memory usage > 80%
    - −20 if CPU load > 2.0
- **Health Status Message**
    - `Optimal` → ≥ 90
    - `Healthy` → 70–89
    - `Warning` → < 70

All logic is implemented **inside `main.py`**, as required.

---

## Containerization (Docker)

Cloud Run requires applications to run inside a container.

The provided `Dockerfile`:

- Uses a lightweight Python base image
- Installs dependencies from `requirements.txt`
- Runs the app using **gunicorn** on port `8080`

---

## Deployment to Google Cloud Run

### 1️⃣ Build the Docker Image

```jsx
gcloud builds submit --tag [gcr.io/PROJECT_ID/hello-cloud-run](http://gcr.io/PROJECT_ID/hello-cloud-run)
```

### 2️⃣ Deploy to Cloud Run

```jsx
gcloud run deploy hello-cloud-run \
  --image gcr.io/PROJECT_ID/hello-cloud-run \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

```

After deployment, Cloud Run provides a **public service URL**.

---

## Local Development (Optional)

```jsx
pip install -r requirements.txt
python [main.py](http://main.py/)
```

**Access locally:**

[`http://localhost:8080/`](http://localhost:8080/)

[`http://localhost:8080/analyze`](http://localhost:8080/analyze)

### **Key Learnings**
Manual system metric extraction using Linux /proc

Stateless service design for serverless environments

Optimizing Flask apps for Cloud Run

Designing meaningful health scoring logic

End-to-end containerized deployment on GCP

### Deliverables Checklist
sys_check.sh

`[main.py](http://main.py/)` with / and /analyze

`requirements.txt`

✅ Dockerfile

✅ Deployed Cloud Run Service URL
