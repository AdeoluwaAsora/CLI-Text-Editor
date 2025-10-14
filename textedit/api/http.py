from fastapi import FastAPI
from pydantic import BaseModel
import os
from textedit.persist.storage import PersistentUndoRedo, DEFAULT_PATH
from textedit.core.commands import InsertText, DeleteRange, ReplaceRange, MoveCursor

app = FastAPI(title="TextEdit API", version="0.1.0")
STATE_FILE = os.environ.get("TEXTEDIT_STATE_FILE", DEFAULT_PATH)
mgr = PersistentUndoRedo(STATE_FILE)

# --- Request models ---
class InsertReq(BaseModel):
    text: str

class DeleteReq(BaseModel):
    start: int
    end: int

class ReplaceReq(BaseModel):
    start: int
    end: int
    text: str

class MoveReq(BaseModel):
    pos: int

# --- Helpers ---
def snapshot():
    return {"text": mgr.state.text, "cursor": mgr.state.cursor}

# --- Endpoints ---
@app.get("/state")
def state():
    return snapshot()

@app.post("/insert")
def insert(req: InsertReq):
    mgr.apply(InsertText(req.text))
    return snapshot()

@app.post("/delete")
def delete(req: DeleteReq):
    mgr.apply(DeleteRange(req.start, req.end))
    return snapshot()

@app.post("/replace")
def replace(req: ReplaceReq):
    mgr.apply(ReplaceRange(req.start, req.end, req.text))
    return snapshot()

@app.post("/move")
def move(req: MoveReq):
    mgr.apply(MoveCursor(req.pos))
    return snapshot()

@app.post("/undo")
def undo():
    mgr.undo()
    return snapshot()

@app.post("/redo")
def redo():
    mgr.redo()
    return snapshot()
