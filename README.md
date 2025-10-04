# 📝 CLI Todo App

[![Hacktoberfest](https://img.shields.io/badge/Hacktoberfest-2025-blueviolet)](https://hacktoberfest.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Node.js](https://img.shields.io/badge/Node.js-14+-339933?logo=node.js&logoColor=white)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.7+-3776AB?logo=python&logoColor=white)](https://www.python.org/)

A lightweight, cross-platform command-line task management tool with dual implementations designed for flexibility and ease of use. Perfect for developers who love staying organized from the terminal!

Choose between our **Node.js** implementation for speed and simplicity, or our **Python** implementation for advanced features like task prioritization and robust error handling.

---

## ✨ Features

### Node.js Implementation
- ✅ **Core Operations** – Add, list, edit, remove, and clear tasks
- 💾 **Lightweight Storage** – Plain JSON file with no external dependencies
- ⚡ **Zero Configuration** – Works out of the box with Node.js installed
- 🚀 **Fast & Simple** – Perfect for quick task management

### Python Implementation
- 🎯 **Priority Management** – Organize tasks by High, Medium, or Low priority
- 🛡️ **Smart Validation** – Prevents empty or whitespace-only task entries
- 🔧 **Robust Error Handling** – Automatic backup and recovery from corrupted data files
- 🔄 **Backward Compatibility** – Seamlessly handles older task formats
- 📊 **Enhanced Sorting** – Automatic priority-based task ordering
- 🐍 **Pure Python** – Standard library only, no external dependencies
  
---

## 🛠️ Project Structure
```
cli-todo-app/
├── index.js # Node.js CLI entry point
├── todo.js # Node.js core implementation
├── package.json # Node.js configuration and metadata
├── todos.json # Node.js task storage
├── python_ver/
│ ├── todo.py # Python CLI entry point and implementation
│ ├── tasks.json # Python task storage
│ └── README.md # Python-specific documentation
├── README.md # Main project documentation (this file)
├── CONTRIBUTING.md # Contribution guidelines
└── LICENSE # MIT License
```

---

## 🚀 Quick Start

### Installation

Clone the repository and start managing your tasks:
```
git clone https://github.com/flyingSaucer87/cli-todo-app.git
cd cli-todo-app
```

You're ready to go! Choose your preferred implementation below.

---

### Node.js Version

#### Prerequisites
- Node.js 14 or higher

#### Usage
```
# Add a new task
node index.js add "Write comprehensive tests"

# View all tasks
node index.js list

# Update an existing task
node index.js edit 0 "Write unit and integration tests"

# Remove a task by index
node index.js remove 0

# Clear all tasks
node index.js clear
```

---

### Python Version

#### Prerequisites
- Python 3.7 or higher

#### Usage
```
# Add a task with default priority (Medium)
python python_ver/todo.py add "Review pull requests"

# Add a task with specific priority
python python_ver/todo.py add "Fix critical security bug" --priority High

# View all tasks (sorted by priority: High → Medium → Low)
python python_ver/todo.py list

# Remove a task by index (1-based)
python python_ver/todo.py remove 2

# Clear all tasks
python python_ver/todo.py clear

```

**If you prefer using bash/zsh from the `python_ver` directory:**
```
cd python_ver
python todo.py add "Update documentation" -p Low
python todo.py list
```

---

## 💾 Task Storage

### Default Storage Locations

- **Node.js**: Tasks are saved in `todos.json` at the repository root
- **Python**: Tasks are saved in `tasks.json` within the `python_ver/` directory

### Custom Storage Path (Python)

Override the default storage location using an environment variable:
```
# macOS/Linux
export TODO_FILE=/path/to/custom_tasks.json
```
```
# Windows PowerShell
$env:TODO_FILE = "C:\path\to\custom_tasks.json"
```

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE). Feel free to use, modify, and distribute as needed.
