from dataclasses import dataclass, replace

@dataclass(frozen=True)
class EditorState:
    """
    Represents the editor's current state — just text and cursor.
    It's immutable (dataclass with frozen=True) for easy undo/redo testing.
    """
    text: str = ""
    cursor: int = 0

    def clamp(self, pos: int) -> int:
        """Clamp cursor position within valid bounds."""
        return max(0, min(len(self.text), pos))

    def with_text(self, new_text: str, new_cursor: int | None = None) -> "EditorState":
        """Return a new state with updated text and optional cursor."""
        c = self.clamp(self.cursor if new_cursor is None else new_cursor)
        return replace(self, text=new_text, cursor=c)

    def insert(self, s: str) -> "EditorState":
        """Insert text at the current cursor."""
        c = self.cursor
        return self.with_text(self.text[:c] + s + self.text[c:], c + len(s))

    def delete_range(self, start: int, end: int) -> "EditorState":
        """Delete characters between [start, end)."""
        start, end = sorted((self.clamp(start), self.clamp(end)))
        new = self.text[:start] + self.text[end:]
        return self.with_text(new, start)

    def replace_range(self, start: int, end: int, s: str) -> "EditorState":
        """Replace range [start, end) with new text s."""
        start, end = sorted((self.clamp(start), self.clamp(end)))
        new = self.text[:start] + s + self.text[end:]
        return self.with_text(new, start + len(s))

    def move_cursor(self, pos: int) -> "EditorState":
        """Move cursor to a specific position."""
        return self.with_text(self.text, self.clamp(pos))
