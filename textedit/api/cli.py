import typer
from textedit.core.history import UndoRedoManager
from textedit.core.commands import InsertText, DeleteRange, ReplaceRange, MoveCursor

app = typer.Typer(help="Minimal text editor with Undo/Redo (Command pattern + two stacks)")
mgr = UndoRedoManager()

def _show():
    typer.echo(f"[cursor={mgr.state.cursor}] '{mgr.state.text}'")

@app.command(help="Show current text and cursor")
def show():
    _show()

@app.command(help="Insert text at current cursor")
def insert(s: str):
    mgr.apply(InsertText(s))
    _show()

@app.command(help="Delete characters in [start, end)")
def delete(start: int, end: int):
    mgr.apply(DeleteRange(start, end))
    _show()

@app.command(help="Replace [start, end) with new text")
def replace(start: int, end: int, s: str):
    mgr.apply(ReplaceRange(start, end, s))
    _show()

@app.command(help="Move cursor to absolute position")
def move(pos: int):
    mgr.apply(MoveCursor(pos))
    _show()

@app.command(help="Undo last change")
def undo():
    mgr.undo()
    _show()

@app.command(help="Redo last undone change")
def redo():
    mgr.redo()
    _show()

if __name__ == "__main__":
    app()
