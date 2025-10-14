# TextEditor-AI

A minimal, fully testable **text editor with Undo/Redo** built in Python.

## Features
- Functional core using **Command Pattern**
- Two-stack **Undo/Redo** manager
- **CLI** (Typer) and **REST API** (FastAPI)
- **TUI** (Textual)
- **Semantic Vector Search** & AI extensions (embeddings, quantization, retrieval)

## Concept
This editor records every action (insert, delete, replace) as a reversible command.
It can undo or redo any change, similar to MS Word, but built from scratch.

modules let it understand text *semantically* using **vector embeddings** — so it can search or summarize by meaning.

## Quickstart
```bash
git clone git@github.com:AdeoluwaAsora/Text-Editor-Ai.git
cd textedit-ai
pip install -r requirements.txt
python -m textedit.api.cli insert "hello"


