# DocuMind AI

## Overview
DocuMind AI is a command-line application built using Python. It helps users search, view, summarize, categorize, and upload documents through an easy-to-use CLI.


## Features
- Login (Demo Mode)
- Search Documents
- View Document
- Summarize Documents
- List Categories
- Filter by Category
- Upload Documents
- Version Information

## Technologies Used
- Python
- Typer
- Rich
- UV

## How to Run

```bash
uv run main.py --help
```

### Example Commands

```bash
# Show all available commands
uv run main.py --help

# Show version
uv run main.py version

# Login
uv run main.py login

# Search documents
uv run main.py search "AI"

# View document
uv run main.py view 1

# Generate summary
uv run main.py summarize 1

# List categories
uv run main.py categories

# Search by category
uv run main.py category Linux

# Upload document
uv run main.py upload notes.txt
```
