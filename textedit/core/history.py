from dataclasses import dataclass, field
from typing import List
from .editor import EditorState
from .commands import Command

@dataclass
class UndoRedoManager:
    """
    Manages two stacks: one for undo, one for redo.
    Applies commands, stores their inverses, and swaps stacks on undo/redo.
    """
    state: EditorState = field(default_factory=EditorState)
    undo_stack: List[Command] = field(default_factory=list)
    redo_stack: List[Command] = field(default_factory=list)

    def apply(self, cmd: Command) -> EditorState:
        new_state, inverse = cmd.do(self.state)
        self.undo_stack.append(inverse)
        self.redo_stack.clear()
        self.state = new_state
        return self.state

    def undo(self) -> EditorState:
        if not self.undo_stack:
            return self.state
        cmd = self.undo_stack.pop()
        new_state, inverse = cmd.do(self.state)
        self.redo_stack.append(inverse)
        self.state = new_state
        return self.state

    def redo(self) -> EditorState:
        if not self.redo_stack:
            return self.state
        cmd = self.redo_stack.pop()
        new_state, inverse = cmd.do(self.state)
        self.undo_stack.append(inverse)
        self.state = new_state
        return self.state
