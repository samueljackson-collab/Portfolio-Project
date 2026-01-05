from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

app = FastAPI(title="POC API")
API_KEY = None
TODOS: Dict[int, str] = {}


class Todo(BaseModel):
    title: str


def check_api_key(x_api_key: Optional[str]):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="invalid api key")


import os


@app.on_event("startup")
async def load_key():
    global API_KEY
    API_KEY = os.getenv("API_KEY")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/todos", response_model=List[Todo])
async def list_todos(x_api_key: Optional[str] = Header(default=None)):
    check_api_key(x_api_key)
    return [Todo(title=v) for v in TODOS.values()]


@app.post("/todos", status_code=201)
async def create(todo: Todo, x_api_key: Optional[str] = Header(default=None)):
    check_api_key(x_api_key)
    todo_id = len(TODOS) + 1
    TODOS[todo_id] = todo.title
    return {"id": todo_id, "title": todo.title}
