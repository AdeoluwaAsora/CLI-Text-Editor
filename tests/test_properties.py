# tests/test_properties.py
from hypothesis import given, settings, strategies as st, note
from textedit.core.history import UndoRedoManager
from textedit.core.commands import InsertText, DeleteRange, ReplaceRange, MoveCursor

# --- Helpers ---
def clamp(i, n):
    return max(0, min(n, i))

# 1) Inserting any text then undo must restore the exact prior state
@given(st.text())
@settings(deadline=None)
def test_insert_then_undo_restores(s):
    m = UndoRedoManager()
    before = m.state
    m.apply(InsertText(s))
    m.undo()
    assert m.state == before

# 2) Delete a valid slice; undo must restore deleted substring; redo must re-delete it
@given(
    base=st.text(min_size=1),
    pad=st.integers(min_value=0, max_value=5),
)
@settings(deadline=None)
def test_delete_roundtrip(base, pad):
    m = UndoRedoManager()
    m.apply(InsertText(" " * pad + base + " " * pad))
    start = pad
    end = pad + len(base)
    # delete middle region
    m.apply(DeleteRange(start, end))
    after_delete = m.state
    m.undo()
    assert m.state.text[start:end] == base  # restored
    m.redo()
    assert m.state == after_delete

# 3) Replace keeps length deltas consistent and is reversible
@given(
    base=st.text(),
    pos=st.integers(min_value=0, max_value=50),
    ins=st.text(),
)
@settings(deadline=None)
def test_replace_length_and_reversibility(base, pos, ins):
    m = UndoRedoManager()
    m.apply(InsertText(base))
    start = clamp(pos, len(base))
    end = clamp(start + len(base) // 2, len(base))
    old_len = len(m.state.text)
    m.apply(ReplaceRange(start, end, ins))
    delta = len(ins) - (end - start)
    assert len(m.state.text) == old_len + delta
    m.undo()
    assert m.state.text == base
    m.redo()
    assert len(m.state.text) == old_len + delta

# 4) Cursor moves are safe (never out of bounds) and undoable
@given(
    base=st.text(),
    moves=st.lists(st.integers(min_value=-10, max_value=100), min_size=1, max_size=20),
)
@settings(deadline=None)
def test_cursor_moves_safe_and_undoable(base, moves):
    m = UndoRedoManager()
    m.apply(InsertText(base))
    for p in moves:
        m.apply(MoveCursor(p))
        assert 0 <= m.state.cursor <= len(m.state.text)
        m.undo()
        # after undo, cursor should be whatever it was before the move
        # We reapply same move and check it clamps
        m.redo()
        assert 0 <= m.state.cursor <= len(m.state.text)

# 5) Random mixed script of operations keeps invariants (no OOB cursor)
@given(
    base=st.text(),
    ops=st.lists(
        st.one_of(
            st.tuples(st.just("ins"), st.text()),
            st.tuples(st.just("del"), st.integers(0, 50), st.integers(0, 50)),
            st.tuples(st.just("rep"), st.integers(0, 50), st.integers(0, 50), st.text()),
            st.tuples(st.just("mov"), st.integers(-10, 200)),
            st.tuples(st.just("und"), st.none()),
            st.tuples(st.just("red"), st.none()),
        ),
        min_size=1, max_size=100
    )
)
@settings(deadline=None, max_examples=200)
def test_mixed_script_invariants(base, ops):
    m = UndoRedoManager()
    m.apply(InsertText(base))

    for op in ops:
        kind = op[0]
        try:
            if kind == "ins":
                m.apply(InsertText(op[1]))
            elif kind == "del":
                a, b = op[1], op[2]
                if len(m.state.text) == 0:  # skip when empty
                    continue
                start = clamp(min(a, b), len(m.state.text))
                end = clamp(max(a, b), len(m.state.text))
                m.apply(DeleteRange(start, end))
            elif kind == "rep":
                a, b, s = op[1], op[2], op[3]
                start = clamp(min(a, b), len(m.state.text))
                end = clamp(max(a, b), len(m.state.text))
                m.apply(ReplaceRange(start, end, s))
            elif kind == "mov":
                m.apply(MoveCursor(op[1]))
            elif kind == "und":
                m.undo()
            elif kind == "red":
                m.redo()
        except Exception as e:
            # Editor should be robust; if an error occurred, the property fails
            note(f"Operation {op} raised {e}")
            raise

        # Invariants after every step
        assert 0 <= m.state.cursor <= len(m.state.text)
