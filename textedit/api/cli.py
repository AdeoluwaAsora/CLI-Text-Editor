import typer
from typing import Optional
from textedit.core.commands import InsertText, DeleteRange, ReplaceRange, MoveCursor
from textedit.persist.storage import PersistentUndoRedo, DEFAULT_PATH
from textedit.semvec.index import SimpleIndex



app = typer.Typer(help="Minimal text editor with Undo/Redo (Command pattern + two stacks) + file persistence")
state_file_option = typer.Option(DEFAULT_PATH, "--state-file", "-s", help="Path to persistent state JSON")


_sem_index = SimpleIndex()

def _reindex(mgr):
    chunks = [ln for ln in mgr.state.text.splitlines() if ln.strip()]
    _sem_index.__init__()
    if chunks: _sem_index.add(chunks)


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


@app.command(help="Rebuild semantic index from current document")
def reindex(state_file: str = state_file_option):
    mgr = get_mgr(state_file)
    _reindex(mgr)
    typer.echo(f"Indexed {len(_sem_index.texts)} chunks.")

@app.command(help="Semantic find (search by meaning)")
def semfind(query: str, k: int = 5, state_file: str = state_file_option):
    mgr = get_mgr(state_file)
    if not getattr(_sem_index, "texts", []):
        _reindex(mgr)
    hits = _sem_index.search(query, k=k)
    for i, (_, score, text) in enumerate(hits, 1):
        typer.echo(f"{i}. {score:.3f}  {text}")


if __name__ == "__main__":
    app()
