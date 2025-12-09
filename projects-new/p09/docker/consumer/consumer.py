from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI()

class Event(BaseModel):
    id: str
    payload: str


def get_db():
    conn = sqlite3.connect("/tmp/events.db")
    conn.execute("create table if not exists events(id text primary key, payload text)")
    return conn

@app.post("/events")
def ingest(event: Event):
    conn = get_db()
    conn.execute("insert or ignore into events(id, payload) values (?, ?)", (event.id, event.payload))
    conn.commit()
    conn.close()
    return {"status": "stored"}

@app.get("/metrics")
def metrics():
    conn = get_db()
    cur = conn.execute("select count(*) from events")
    count = cur.fetchone()[0]
    conn.close()
    return {"poc_events_processed_total": count}
