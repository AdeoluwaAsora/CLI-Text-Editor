import os, tempfile, json
from textedit.core.commands import InsertText, ReplaceRange
from textedit.persist.storage import PersistentUndoRedo, load_snapshot

def test_persistence_roundtrip():
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "state.json")
        mgr = PersistentUndoRedo(p)
        mgr.reset()
        mgr.apply(InsertText("hello"))
        mgr.apply(ReplaceRange(0, 5, "Hi"))

        # Reload from disk
        mgr2 = PersistentUndoRedo(p)
        assert mgr2.state.text == "Hi"
        # Undo still works after reload (stacks persisted)
        mgr2.undo()
        assert mgr2.state.text == "hello"
