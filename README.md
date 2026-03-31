# FileBot

> Desktop automation tool for file processing and organization — built with Python + PyQt6.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.x-purple)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **Batch rename** files using rules or AI-generated names
- **Organize** files into folders by extension, date, or custom rules
- **Data cleanup** for CSV / JSON files
- **AI summarization** of documents (local via Ollama, or online via OpenAI)
- **Undo / rollback** — every operation is reversible
- **Dry-run preview** before executing anything
- Works fully **offline** — AI is optional

## Architecture

```
filebot/
├── main.py               # entry point
├── core/
│   ├── file_scanner.py   # scan directories → FileEntry objects
│   └── rule_engine.py    # apply rename/organize rules (coming in v0.2)
├── ui/
│   └── main_window.py    # PyQt6 MainWindow
├── ai/
│   └── providers.py      # AIProvider interface + Ollama + OpenAI
└── actions/
    └── rename.py         # Rename action (coming in v0.2)
```

## Installation

```bash
pip install PyQt6
python main.py
```

## Roadmap

| Version | Features |
|---------|----------|
| v0.1 | Folder scan, file table, UI shell |
| v0.2 | Batch rename with rules, undo system |
| v0.5 | Ollama integration, summarize action |
| v1.0 | OpenAI support, CSV cleanup, PyInstaller builds |
