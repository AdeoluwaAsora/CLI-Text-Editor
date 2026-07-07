# CLI TextEditor

A minimal, fully testable **text editor with Undo/Redo** built in Python.

## Features
- Functional core using **Command Pattern**
- Two-stack **Undo/Redo** manager
- **CLI** (Typer) 
- **TUI** (Textual)


## Concept
This editor records every action (insert, delete, replace) as a reversible command.
It can undo or redo any change.

modules let it understand text *semantically* using **vector embeddings** — so it can search or summarize by meaning.

## Quickstart
```bash
git clone git@github.com:AdeoluwaAsora/Text-Editor-Ai.git
cd textedit-ai
pip install -r requirements.txt
python -m textedit.api.cli insert "hello"


