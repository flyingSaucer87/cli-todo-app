# Python CLI Todo App

Simple command-line todo application written in Python with task prioritization.
Tasks are stored locally in a tasks.json file next to the script.
Features

    Add new tasks

    List all tasks

    Remove tasks by index

    Mark tasks as completed and view them separately

    Stores tasks persistently in a local JSON file

## Requirements

- Python 3.7 or higher
- No external dependencies (uses only the Python standard library)

Installation
    After cloning the repo, navigate to  
    git clone https://github.com/flyingSaucer87/cli-todo-app.git
    cd cli-todo-app/python_ver

Usage
Add a Task
    python todo.py add "taskname"
List All Tasks
    python todo.py list
    # Shows "Pending tasks" and "Completed tasks" sections.
Remove a Task
    python todo.py remove task_index
Mark a Task as Completed
    python todo.py complete task_index

Task Storage
Tasks are saved automatically in a file named tasks.json located in the same directory as todo.py.
You can change the file location by setting the TODO_FILE environment variable:
    macOS/Linux (bash/zsh):
        export TODO_FILE=/path/to/custom_tasks.json

    Windows (PowerShell):
        $env:TODO_FILE = "C:\\path\\to\\custom_tasks.json"

