from dataclasses import dataclass
from .editor import EditorState

class Command:
    """Base command interface — each command can perform and undo itself."""
    def do(self, st: EditorState) -> tuple[EditorState, "Command"]:
        raise NotImplementedError

@dataclass(frozen=True)
class InsertText(Command):
    text: str

    def do(self, st: EditorState):
        before = st.cursor
        new_st = st.insert(self.text)
        # inverse: delete what was inserted
        return new_st, DeleteRange(before, before + len(self.text))

@dataclass(frozen=True)
class DeleteRange(Command):
    start: int
    end: int

    def do(self, st: EditorState):
        start, end = sorted((st.clamp(self.start), st.clamp(self.end)))
        deleted = st.text[start:end]
        new_st = st.delete_range(start, end)
        # inverse: re-insert deleted text
        return new_st, ReplaceRange(start, start, deleted)

@dataclass(frozen=True)
class ReplaceRange(Command):
    start: int
    end: int
    text: str

    def do(self, st: EditorState):
        start, end = sorted((st.clamp(self.start), st.clamp(self.end)))
        old = st.text[start:end]
        new_st = st.replace_range(start, end, self.text)
        # inverse: put the old text back
        return new_st, ReplaceRange(start, start + len(self.text), old)

@dataclass(frozen=True)
class MoveCursor(Command):
    pos: int

    def do(self, st: EditorState):
        old = st.cursor
        new_st = st.move_cursor(self.pos)
        return new_st, MoveCursor(old)
