from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from google.cloud import storage
from pathlib import Path
from dotenv import load_dotenv
from passlib.context import CryptContext
import logging
import json
import os

# Load environment variables
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)

# Required environment variable
BUCKET_NAME = os.getenv("BUCKET_NAME")
if not BUCKET_NAME:
    raise RuntimeError("BUCKET_NAME not set in .env file")

# FastAPI app
app = FastAPI()

# Password hashing (Argon2)
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

# Google Cloud Storage client
try:
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
except Exception as e:
    logging.error("Failed to initialize Google Cloud Storage")
    raise e


@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    html_path = Path("index.html")
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return html_path.read_text()


@app.post("/submit")
def submit_form(
    username: str = Form(...),
    password: str = Form(...)
):
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username too short")

    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password too short")

    blob_path = f"users/{username}.json"
    blob = bucket.blob(blob_path)

    if blob.exists():
        raise HTTPException(status_code=409, detail="Username already exists")

    password_hash = pwd_context.hash(password)

    data = {
        "username": username,
        "password_hash": password_hash
    }

    try:
        blob.upload_from_string(
            json.dumps(data),
            content_type="application/json"
        )
        logging.info("User %s registered", username)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to store user")

    return {"message": "User registered successfully"}
