import json
import os
import sys
from datetime import datetime

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
def add_todo(task, due_date=None):
    todos = load_todos()
    
    # If due date is provided, ensure it is a string in the format YYYY-MM-DD
    if due_date:
        try:
            due_date = datetime.strptime(due_date, "%Y-%m-%d").date()  # Convert string to date
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return
    
    todos.append({"task": task, "due_date": due_date})  # Add task with due date
    save_todos(todos)
    print(f"✅ Added: {task}, Due: {due_date if due_date else 'No due date'}")

# List all tasks
def list_todos():
    todos = load_todos()
    if not todos:
        print("No tasks yet!")
        return

    # Check for tasks due today
    check_due_tasks(todos)
    
    for i, task in enumerate(todos):
        due_date_str = task["due_date"].strftime("%Y-%m-%d") if task["due_date"] else "No due date"
        print(f"{i}: {task['task']} (Due: {due_date_str})")

# Check and notify if any tasks are due today
def check_due_tasks(todos):
    today = datetime.today().date()  # Get today's date
    due_today = [task for task in todos if task["due_date"] and task["due_date"] == today]
    
    if due_today:
        print("\n🔔 **Reminder**: The following tasks are due today:")
        for task in due_today:
            print(f" - {task['task']}")
    else:
        print("\n✅ No tasks are due today.")

# Clear all tasks
def clear_todos():
    save_todos([])
    print("All tasks have been cleared.")

# Command-line interface
def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python todo.py add \"Task name\" [due_date (YYYY-MM-DD)]")
        print("  python todo.py list")
        print("  python todo.py remove <index>")
        print("  python todo.py clear")
        return

    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) < 3 or not " ".join(sys.argv[2:]).strip():
            print("Error: Please provide a task description to add.")
            print("Usage: python todo.py add \"Task name\" [due_date (YYYY-MM-DD)]")
            return
        
        task = " ".join(sys.argv[2:])
        due_date = None

        # Check if due date is provided as an argument
        if len(sys.argv) == 4:
            due_date = sys.argv[3]

        add_todo(task, due_date)
    
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
            print("Invalid index. Please provide a number.")
    elif command == "clear":
        clear_todos()
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

