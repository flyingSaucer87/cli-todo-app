# CLI Todo App

Cross-platform, minimal command-line Todo app with two implementations:

- Node.js (simple and quick)
- Python (feature-rich with prioritization and robust I/O handling)

Use whichever fits your workflow, or contribute to both.

---

## Table of Contents

- Overview
- Features
   - Node.js implementation
   - Python implementation
- Requirements
- Installation
- Usage
   - Node.js
   - Python
- Task Storage
- Project Structure
- Contributing
- License

---

## Overview

This repository contains two independent CLI implementations that manage todos from the terminal. Both store tasks in a local JSON file and provide basic CRUD operations. The Python version also includes task prioritization and robust handling of corrupted/invalid data files.

We keep the Python source under `python_ver/` and the Node.js source at the repository root.

---

## Features

### Node.js implementation

- Add, list, remove, edit, clear tasks
- Stores tasks in a plain JSON file (`todos.json`)
- Zero dependencies; runs with Node.js only

### Python implementation

- Add, list, remove, clear tasks
- Task prioritization (High, Medium, Low) with sorted listing
- Empty task validation (prevents blank/whitespace-only tasks)
- Robust error handling for malformed JSON and I/O errors
- Automatic backup of corrupted task files
- Backward compatibility with older task formats
- Stores tasks in a local JSON file (`tasks.json` next to the script)

---

## Requirements

- Node.js 14+ (for the Node.js CLI)
- Python 3.7+ (for the Python CLI)
   - No external Python dependencies (standard library only)

---

## Installation

Clone the repository:

```bash
git clone https://github.com/flyingSaucer87/cli-todo-app.git
cd cli-todo-app
```

---

## Usage

### Node.js

From the repository root:

```bash
# Add a task
node index.js add "Write tests"

# List tasks
node index.js list

# Remove a task by index
node index.js remove 0

# Edit a task by index
node index.js edit 0 "Write unit tests for todo"

# Clear all tasks
node index.js clear
```

### Python

From the repository root (Windows PowerShell example shown), use the script under `python_ver/`:

```powershell
# Add a task (default priority: Medium)
python python_ver\todo.py add "Review PR"

# Add with explicit priority
python python_ver\todo.py add "Fix critical bug" --priority High

# List tasks sorted by priority (High → Medium → Low)
python python_ver\todo.py list

# Remove by 1-based index
python python_ver\todo.py remove 2

# Clear all tasks
python python_ver\todo.py clear
```

If you prefer using bash/zsh from the `python_ver` directory:

```bash
cd python_ver
python todo.py add "Write docs" -p Low
python todo.py list
```

---

## Task Storage

- Node.js: stores tasks in `todos.json` at the repository root.
- Python: stores tasks in `tasks.json` next to `python_ver/todo.py` by default.

Python also supports overriding the task file path with an environment variable:

```bash
# macOS/Linux
export TODO_FILE=/path/to/custom_tasks.json
```

```powershell
# Windows PowerShell
$env:TODO_FILE = "C:\\path\\to\\custom_tasks.json"
```

---

## Project Structure

```text
cli-todo-app/
├─ index.js                # Node.js CLI entry
├─ todo.js                 # Node.js implementation
├─ package.json            # Node.js metadata/scripts
├─ python_ver/
│  ├─ todo.py              # Python CLI entry and implementation
│  └─ README.md            # Python-specific docs
├─ README.md               # Project-level documentation (this file)
├─ LICENSE
└─ CONTRIBUTING.md
```

Note: We maintain a single Python implementation under `python_ver/`.

---

## Contributing

Contributions are welcome! Please read `CONTRIBUTING.md` for guidelines on setting up your environment, code style, and how to propose changes.

Suggestions, issues, and PRs are encouraged—especially around test coverage and feature parity between the Node and Python versions.

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.
