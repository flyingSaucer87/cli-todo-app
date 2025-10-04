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

# Add a new task with optional priority
def add_todo(task, priority="Medium"):
    valid_priorities = ["Low", "Medium", "High"]
    if priority not in valid_priorities:
        print("Invalid priority. Use: Low, Medium, or High.")
        return

    todos = load_todos()
    todos.append({"task": task, "priority": priority})
    save_todos(todos)
    print(f"✅ Added: {task} [Priority: {priority}]")

# List all tasks sorted by priority
def list_todos():
    todos = load_todos()
    if not todos:
        print("No tasks yet!")
        return

    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    todos.sort(key=lambda x: priority_order.get(x.get("priority", "Medium")))

    for i, task in enumerate(todos):
        print(f"{i}: {task['task']} [Priority: {task['priority']}]")

# Remove a task by index
def remove_todo(index):
    todos = load_todos()
    if 0 <= index < len(todos):
        removed = todos.pop(index)
        save_todos(todos)
        print(f"🗑️ Removed: {removed['task']} [Priority: {removed['priority']}]")
    else:
        print("Invalid task index.")

# Clear all tasks
def clear_todos():
    save_todos([])
    print("All tasks have been cleared.")

# Command-line interface
def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python todo.py add \"Task name\" [--priority High|Medium|Low]")
        print("  python todo.py list")
        print("  python todo.py remove <index>")
        print("  python todo.py clear")
        return

    command = sys.argv[1]

    if command == "add":
        args = sys.argv[2:]
        task = None
        priority = "Medium"

        if "--priority" in args:
            p_index = args.index("--priority")
            if p_index + 1 < len(args):
                priority = args[p_index + 1]
                task = " ".join(args[:p_index])
            else:
                print("Error: Missing priority value after --priority.")
                return
        else:
            task = " ".join(args)

        add_todo(task, priority)

    elif command == "list":
        list_todos()

    elif command == "remove" and len(sys.argv) == 3:
        try:
            index = int(sys.argv[2])
            remove_todo(index)
        except ValueError:
            print("Invalid index. Please provide a number.")

    elif command == "clear":
        clear_todos()

    else:
        print("Unknown command.")

if __name__ == "__main__":
    main()

