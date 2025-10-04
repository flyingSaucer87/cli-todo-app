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

# Add a new task with optional priority and tags
def add_todo(task, priority="Medium", tags=None):
    valid_priorities = ["Low", "Medium", "High"]
    if priority not in valid_priorities:
        print("Invalid priority. Use: Low, Medium, or High.")
        return

    if tags is None:
        tags = []

    todos = load_todos()
    todos.append({"task": task, "priority": priority, "tags": tags})
    save_todos(todos)
    print(f"✅ Added: {task} [Priority: {priority}] [Tags: {', '.join(tags)}]")

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

# List all tasks sorted by priority and optionally filtered by tag
def list_todos(filter_tag=None):
    todos = load_todos()
    if not todos:
        print("No tasks yet!")
        return
      
    if filter_tag:
        todos = [t for t in todos if filter_tag in t.get("tags", [])]

    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    todos.sort(key=lambda x: priority_order.get(x.get("priority", "Medium")))

    for i, task in enumerate(todos):
        tags = ", ".join(task.get("tags", []))
        print(f"{i}: {task['task']} [Priority: {task['priority']}] [Tags: {tags}]")

# Remove a task by index
def remove_todo(index):
    todos = load_todos()
    if 0 <= index < len(todos):
        removed = todos.pop(index)
        save_todos(todos)
        print(f"🗑️ Removed: {removed['task']} [Priority: {removed['priority']}]")

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
        print("  python todo.py add \"Task name\" [--priority High|Medium|Low]")
        print("  python todo.py list [--tag work]")

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
        args = sys.argv[2:]
        task = None
        priority = "Medium"
        tags = []

        if "--priority" in args:
            p_index = args.index("--priority")
            if p_index + 1 < len(args):
                priority = args[p_index + 1]
                task = " ".join(args[:p_index])
                args.pop(p_index)
                args.pop(p_index)
            else:
                print("Error: Missing priority value after --priority.")
                return
      
        if "--tags" in args:
            t_index = args.index("--tags")
            tags = []
            i = t_index + 1
            while i < len(args) and not args[i].startswith("--"):
                tags.append(args[i])
                i += 1
            args = args[:t_index] + args[i:]

        task = " ".join(args)
        add_todo(task, priority, tags)

    elif command == "list":
        filter_tag = None
        if "--tag" in sys.argv:
            tag_index = sys.argv.index("--tag")
            if tag_index + 1 < len(sys.argv):
                filter_tag = sys.argv[tag_index + 1]
        list_todos(filter_tag)

    elif command == "remove" and len(sys.argv) == 3:
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
        
if __name__ == "__main__":
    main()
