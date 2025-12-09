from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Payload(BaseModel):
    id: str
    name: str
    value: int

@app.post("/items")
def create_item(payload: Payload):
    if payload.value < 0:
        raise HTTPException(status_code=422, detail="value must be positive")
    return {"status": "ok", "id": payload.id}

@app.get("/health")
def health():
    return {"status": "up"}
