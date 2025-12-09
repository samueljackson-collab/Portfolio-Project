import os
from fastapi import FastAPI

app = FastAPI()
region = os.getenv("REGION", "unknown")

@app.get("/health")
def health():
    return {"region": region, "status": "ok"}

@app.get("/metrics")
def metrics():
    return {"region_active": 1}
