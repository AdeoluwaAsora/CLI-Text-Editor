import typer
from typing import Optional
from textedit.core.commands import InsertText, DeleteRange, ReplaceRange, MoveCursor
from textedit.persist.storage import PersistentUndoRedo, DEFAULT_PATH

app = typer.Typer(help="Minimal text editor with Undo/Redo (Command pattern + two stacks) + file persistence")
state_file_option = typer.Option(DEFAULT_PATH, "--state-file", "-s", help="Path to persistent state JSON")

# We'll create the manager lazily so --state-file works on every command
def get_mgr(path: str) -> PersistentUndoRedo:
    return PersistentUndoRedo(path)

def _show(mgr: PersistentUndoRedo):
    typer.echo(f"[cursor={mgr.state.cursor}] '{mgr.state.text}'")

@app.command(help="Show current text and cursor")
def show(state_file: str = state_file_option):
    mgr = get_mgr(state_file)
    _show(mgr)

@app.command(help="Insert text at current cursor")
def insert(s: str, state_file: str = state_file_option):
    mgr = get_mgr(state_file)
    mgr.apply(InsertText(s))
    _show(mgr)

@app.command(help="Delete characters in [start, end)")
def delete(start: int, end: int, state_file: str = state_file_option):
    mgr = get_mgr(state_file)
    mgr.apply(DeleteRange(start, end))
    _show(mgr)

@app.command(help="Replace [start, end) with new text")
def replace(start: int, end: int, s: str, state_file: str = state_file_option):
    mgr = get_mgr(state_file)
    mgr.apply(ReplaceRange(start, end, s))
    _show(mgr)

@app.command(help="Move cursor to absolute position")
def move(pos: int, state_file: str = state_file_option):
    mgr = get_mgr(state_file)
    mgr.apply(MoveCursor(pos))
    _show(mgr)

@app.command(help="Undo last change")
def undo(state_file: str = state_file_option):
    mgr = get_mgr(state_file)
    mgr.undo()
    _show(mgr)

@app.command(help="Redo last undone change")
def redo(state_file: str = state_file_option):
    mgr = get_mgr(state_file)
    mgr.redo()
    _show(mgr)

@app.command(help="Reset the document (clears history) and save")
def reset(state_file: str = state_file_option):
    mgr = get_mgr(state_file)
    mgr.reset()
    _show(mgr)

if __name__ == "__main__":
    app()
