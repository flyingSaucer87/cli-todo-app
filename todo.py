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

# Edit a task by index
def edit_todo(index, new_description):
    todos = load_todos()
    if 0 <= index < len(todos):
        old_task = todos[index]
        todos[index] = new_description
        save_todos(todos)
        print(f" Updated task {index}:")
        print(f"   Old: {old_task}")
        print(f"   New: {new_description}")
    else:
        print("Invalid task index.")

# Command-line interface
def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python todo.py add \"Task name\"")
        print("  python todo.py list")
        print("  python todo.py remove <index>")
        print("  python todo.py edit <index> --new-description \"Updated task\"")
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
    elif command == "edit":
        if len(sys.argv) < 5 or "--new-description" not in sys.argv:
            print("Error: Please provide the index and new description.")
            print("Usage: python todo.py edit <index> --new-description \"New task description\"")
            return
        
        try:
            index = int(sys.argv[2])
        except ValueError:
            print("Error: Invalid index. Please provide a number.")
            return
            
        # Find the --new-description flag and get the description after it
        try:
            flag_index = sys.argv.index("--new-description")
            if flag_index + 1 >= len(sys.argv):
                print("Error: Please provide a description after --new-description.")
                return
            new_description = " ".join(sys.argv[flag_index + 1:])
            if not new_description.strip():
                print("Error: New description cannot be empty.")
                return
        except ValueError:
            print("Error: --new-description flag not found.")
            print("Usage: python todo.py edit <index> --new-description \"New task description\"")
            return
            
        todos = load_todos()
        if not todos:
            print("No tasks to edit.")
            return
        if 0 <= index < len(todos):
            edit_todo(index, new_description)
        else:
            print(f"Error: Task index {index} does not exist. Use 'list' to see valid indices.")
    else:
        print(f"Error: Unknown command '{command}'.")
        print("Valid commands are: add, list, remove, edit.")

if __name__ == "__main__":
    main()
