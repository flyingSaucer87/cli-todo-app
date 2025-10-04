# Python CLI Todo App

Simple command-line todo application written in Python with task prioritization.
Tasks are stored locally in a tasks.json file next to the script.

## Features

- ✅ Add new tasks with priority levels (High, Medium, Low)
- ✅ List all tasks sorted by priority
- ✅ Remove tasks by index
- ✅ Clear all tasks at once
- ✅ Empty task validation (prevents adding blank or whitespace-only tasks)
- ✅ Robust error handling for malformed JSON and I/O errors
- ✅ Automatic backup of corrupted task files
- ✅ Backward compatibility with old task format
- ✅ Stores tasks persistently in a local JSON file

## Requirements

- Python 3.7 or higher
- No external dependencies (uses only the Python standard library)

## Installation

After cloning the repo, navigate to the python_ver directory:
```bash
git clone https://github.com/flyingSaucer87/cli-todo-app.git
cd cli-todo-app/python_ver
```

Alternatively, you can run the script from the repository root by referencing the path:
```powershell
# From repo root (Windows PowerShell)
python python_ver\todo.py list
```

## Usage

### Add a Task
Add a task with default priority (Medium):
```bash
python todo.py add "Task description"
```

Add a task with specific priority:
```bash
python todo.py add "Fix critical bug" --priority High
python todo.py add "Update documentation" --priority Low
python todo.py add "Review PR" -p Medium
```

### List All Tasks
Lists all tasks sorted by priority (High → Medium → Low):
```bash
python todo.py list
```

Example output:
```
1. [High] Fix critical bug
2. [Medium] Review PR
3. [Low] Update documentation
```

### Remove a Task
Remove a task by its index (1-based):
```bash
python todo.py remove 2
```

### Clear All Tasks
Remove all tasks at once:
```bash
python todo.py clear
```

### Get Help
View available commands:
```bash
python todo.py --help
python todo.py add --help
```

## Task Storage

Tasks are saved automatically in a file named `tasks.json` located in the same directory as `todo.py`.

You can change the file location by setting the `TODO_FILE` environment variable:
```bash
export TODO_FILE=/path/to/custom_tasks.json
```

On Windows (PowerShell):
```powershell
$env:TODO_FILE = "C:\\path\\to\\custom_tasks.json"
```

## Error Handling

The app includes robust error handling for:
- **Malformed JSON**: Automatically backs up and resets corrupted files
- **Empty tasks**: Prevents adding blank or whitespace-only tasks
- **File I/O errors**: Graceful handling of permission and disk space issues
- **Invalid priorities**: Validates priority levels before adding tasks

## Improvements from Issue #9

This version addresses all requirements from issue #9:

1. ✅ **Error Handling for Malformed JSON**: Catches `JSONDecodeError` and backs up corrupted files
2. ✅ **Empty Task Validation**: Prevents empty or whitespace-only tasks
3. ✅ **File Permissions and I/O Errors**: Comprehensive error handling for all file operations
4. ✅ **Task Prioritization**: High/Medium/Low priority with automatic sorting
5. ✅ **Code Refactoring**: Added docstrings, type hints, and improved code organization

