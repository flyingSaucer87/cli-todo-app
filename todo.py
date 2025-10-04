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

    if command == "add" and len(sys.argv) >= 3:
        task = " ".join(sys.argv[2:])
        add_todo(task)
    elif command == "list":
        list_todos()
    elif command == "remove" and len(sys.argv) == 3:
        try:
            index = int(sys.argv[2])
            remove_todo(index)
        except ValueError:
            print("Invalid index. Please provide a number.")
    else:
        print("Unknown command.")

if __name__ == "__main__":
    main()
