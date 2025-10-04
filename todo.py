import json
import os
import sys

FILE_PATH = "todos.json"

# Load tasks from JSON file
def load_todos():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as f:
            return json.load(f)
    return []

# Save tasks to JSON file
def save_todos(todos):
    with open(FILE_PATH, "w") as f:
        json.dump(todos, f, indent=2)

# Add a new task
def add_todo(task):
    todos = load_todos()
    todos.append(task)
    save_todos(todos)
    print(f"✅ Added: {task}")

# List all tasks
def list_todos():
    todos = load_todos()
    if not todos:
        print("No tasks yet!")
        return
    for i, task in enumerate(todos):
        print(f"{i}: {task}")

# Remove a task by index
def remove_todo(index):
    todos = load_todos()
    if 0 <= index < len(todos):
        removed = todos.pop(index)
        save_todos(todos)
        print(f"🗑️ Removed: {removed}")
    else:
        print("Invalid task index.")

# Command-line interface
def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python todo.py add \"Task name\"")
        print("  python todo.py list")
        print("  python todo.py remove <index>")
        return

    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) < 3 or not " ".join(sys.argv[2:]).strip():
            print("Error: Please provide a task description to add.")
            print("Usage: python todo.py add \"Task name\"")
            return
        task = " ".join(sys.argv[2:])
        add_todo(task)
    elif command == "list":
        list_todos()
    elif command == "remove":
        if len(sys.argv) != 3:
            print("Error: Please provide the index of the task to remove.")
            print("Usage: python todo.py remove <index>")
            return
        try:
            index = int(sys.argv[2])
        except ValueError:
            print("Error: Invalid index. Please provide a number.")
            return
        todos = load_todos()
        if not todos:
            print("No tasks to remove.")
            return
        if 0 <= index < len(todos):
            remove_todo(index)
        else:
            print(f"Error: Task index {index} does not exist. Use 'list' to see valid indices.")
    else:
        print(f"Error: Unknown command '{command}'.")
        print("Valid commands are: add, list, remove.")

if __name__ == "__main__":
    main()
