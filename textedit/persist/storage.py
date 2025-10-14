from __future__ import annotations
import json, os
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Tuple, Type

from textedit.core.editor import EditorState
from textedit.core.history import UndoRedoManager
from textedit.core import commands as cmds

# ---------- Serialization helpers ----------

def state_to_dict(st: EditorState) -> Dict[str, Any]:
    return {"text": st.text, "cursor": st.cursor}

def state_from_dict(d: Dict[str, Any]) -> EditorState:
    return EditorState(text=d.get("text", ""), cursor=int(d.get("cursor", 0)))

# Map command class -> type name and back (explicit = safe for versioning)
_COMMAND_REGISTRY: Dict[str, Type[cmds.Command]] = {
    "InsertText": cmds.InsertText,
    "DeleteRange": cmds.DeleteRange,
    "ReplaceRange": cmds.ReplaceRange,
    "MoveCursor": cmds.MoveCursor,
}

def command_to_dict(c: cmds.Command) -> Dict[str, Any]:
    if isinstance(c, cmds.InsertText):
        return {"type": "InsertText", "text": c.text}
    if isinstance(c, cmds.DeleteRange):
        return {"type": "DeleteRange", "start": c.start, "end": c.end}
    if isinstance(c, cmds.ReplaceRange):
        return {"type": "ReplaceRange", "start": c.start, "end": c.end, "text": c.text}
    if isinstance(c, cmds.MoveCursor):
        return {"type": "MoveCursor", "pos": c.pos}
    raise ValueError(f"Unknown command class: {type(c).__name__}")

def command_from_dict(d: Dict[str, Any]) -> cmds.Command:
    t = d.get("type")
    if t == "InsertText":
        return cmds.InsertText(text=d["text"])
    if t == "DeleteRange":
        return cmds.DeleteRange(start=int(d["start"]), end=int(d["end"]))
    if t == "ReplaceRange":
        return cmds.ReplaceRange(start=int(d["start"]), end=int(d["end"]), text=d["text"])
    if t == "MoveCursor":
        return cmds.MoveCursor(pos=int(d["pos"]))
    raise ValueError(f"Unknown command type in JSON: {t}")

# ---------- Snapshot dataclass ----------

@dataclass
class Snapshot:
    state: EditorState
    undo_stack: List[cmds.Command]
    redo_stack: List[cmds.Command]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": state_to_dict(self.state),
            "undo_stack": [command_to_dict(c) for c in self.undo_stack],
            "redo_stack": [command_to_dict(c) for c in self.redo_stack],
            "version": 1,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Snapshot":
        return Snapshot(
            state=state_from_dict(d.get("state", {})),
            undo_stack=[command_from_dict(x) for x in d.get("undo_stack", [])],
            redo_stack=[command_from_dict(x) for x in d.get("redo_stack", [])],
        )

# ---------- File I/O ----------

DEFAULT_PATH = os.path.expanduser("~/.textedit_state.json")

def load_snapshot(path: str = DEFAULT_PATH) -> Snapshot | None:
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Snapshot.from_dict(data)
    except Exception:
        # Leave a breadcrumb for debugging; start fresh if corrupted
        try:
            os.replace(path, path + ".corrupt")
        except Exception:
            pass
        return None

def save_snapshot(snap: Snapshot, path: str = DEFAULT_PATH) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(snap.to_dict(), f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

# ---------- Persistent wrapper ----------

class PersistentUndoRedo:
    """
    Wraps UndoRedoManager and persists state/stacks to a JSON file
    after every apply/undo/redo. Safe to use from CLI or API; survives
    process restarts.
    """
    def __init__(self, path: str = DEFAULT_PATH):
        self.path = path
        snap = load_snapshot(path)
        if snap:
            self.mgr = UndoRedoManager(
                state=snap.state,
                undo_stack=snap.undo_stack,
                redo_stack=snap.redo_stack,
            )
        else:
            self.mgr = UndoRedoManager()
            self._save()

    # convenience passthroughs
    @property
    def state(self) -> EditorState:
        return self.mgr.state

    def _save(self) -> None:
        save_snapshot(
            Snapshot(self.mgr.state, self.mgr.undo_stack, self.mgr.redo_stack),
            self.path,
        )

    def apply(self, command: cmds.Command) -> EditorState:
        st = self.mgr.apply(command)
        self._save()
        return st

    def undo(self) -> EditorState:
        st = self.mgr.undo()
        self._save()
        return st

    def redo(self) -> EditorState:
        st = self.mgr.redo()
        self._save()
        return st

    # utilities
    def reset(self) -> EditorState:
        """Clear everything and save."""
        self.mgr = UndoRedoManager()
        self._save()
        return self.mgr.state
