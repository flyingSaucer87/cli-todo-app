import json
import os
import sys
from datetime import datetime
from datetime import datetime, timedelta

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

def parse_recurrence(recurrence_str):
    if not recurrence_str:
        return None
    
    legacy_map = {
        "daily": {"interval": 1, "unit": "d"},
        "weekly": {"interval": 1, "unit": "w"},
        "monthly": {"interval": 1, "unit": "m"}
    }

    if recurrence_str in legacy_map:
        return legacy_map[recurrence_str]
    
    if len(recurrence_str) >= 2 and recurrence_str[-1] in ['d', 'w', 'm']:
        try:
            interval = int(recurrence_str[:-1])
            unit = recurrence_str[-1]
            if interval > 0:
                return {"interval": interval, "unit": unit}
        except ValueError:
            pass
    
    return None

def format_recurrence(recurrence):
    if not recurrence:
        return "None"
    
    if isinstance(recurrence, str):
        return recurrence
    
    unit_names = {"d": "day", "w": "week", "m": "month"}
    interval = recurrence.get("interval", 1)
    unit = recurrence.get("unit", "d")
    unit_name = unit_names.get(unit, "day")
    
    if interval > 1:
        unit_name += "s"
    
    return f"Every {interval} {unit_name}"

def calculate_next_due(due_date, recurrence):
    if isinstance(due_date, str):
        due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()
    else:
        due_date_obj = due_date

    if not recurrence or not isinstance(recurrence, dict):
        return due_date_obj.strftime("%Y-%m-%d")
    
    interval = recurrence.get("interval", 1)
    unit = recurrence.get("unit", "d")

    if unit == "d":
        next_date = due_date_obj + timedelta(days=interval)
    elif unit == "w":
        next_date = due_date_obj + timedelta(weeks=interval)
    elif unit == "m":
        # Handle month addition
        month = due_date_obj.month - 1 + interval
        year = due_date_obj.year + month // 12
        month = month % 12 + 1
        day = min(due_date_obj.day, [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        next_date = datetime(year, month, day).date()
    else:
        next_date = due_date_obj
    
    return next_date.strftime("%Y-%m-%d")

# Add a new task with optional priority, tags, due_date, recurrence
def add_todo(task, priority="Medium", tags=None, due_date=None, recurrence=None):
    valid_priorities = ["Low", "Medium", "High"]
    if priority not in valid_priorities:
        print("Invalid priority. Use: Low, Medium, or High.")
        return

    if tags is None:
        tags = []

    todos = load_todos()
    due_date_obj = None

    # If due date is provided, ensure it is a string in the format YYYY-MM-DD
    if due_date:
        try:
            due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()  # Convert string to date
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return
        
    recurrence_obj = parse_recurrence(recurrence)
    if recurrence and not recurrence_obj:
        print(f"Invalid recurrence format. Use: daily, weekly, monthly, or custom (e.g., 3d, 2w, 1m)")
        return
    
    # Add task with optional recurrence and due date
    task_obj = {
        "task": task,
        "priority": priority,
        "tags": tags,
        "due_date": due_date_obj.strftime("%Y-%m-%d") if due_date_obj else None,
        "recurrence": recurrence_obj,
        "next_due": due_date_obj.strftime("%Y-%m-%d") if due_date_obj else None
    }
    
    todos.append(task_obj)
    save_todos(todos)

    tags_str = f"[Tags: {', '.join(tags)}]" if tags else ""
    due_str = f"[Due: {due_date_obj.strftime('%Y-%m-%d')}]" if due_date_obj else ""
    rec_str = f"[Recurrence: {format_recurrence(recurrence_obj)}]" if recurrence_obj else ""

    print(f"✅ Added: {task} [Priority: {priority}] {tags_str} {due_str} {rec_str}".strip())

# List all tasks sorted by priority and optionally filtered by tag
def list_todos(filter_tag=None, sort_by=None):
    todos = load_todos()
    if not todos:
        print("No tasks yet!")
        return

    if filter_tag:
        todos = [t for t in todos if filter_tag in t.get("tags", [])]
        if not todos:
            print(f"No tasks found with tag '{filter_tag}'.")
            return

    if sort_by == "name":
        todos.sort(key=lambda x: x.get("task", "").lower())
    elif sort_by == "due":
        todos.sort(key=lambda x: x.get("due", ""))  
    else:
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        todos.sort(key=lambda x: priority_order.get(x.get("priority", "Medium")))

    for i, task in enumerate(todos):
        tags = ", ".join(task.get("tags", []))
        tags_str = f"[Tags: {tags}]" if tags else "[Tags: None]"
        
        due_date = task.get("due_date")
        due_str = f"[Due: {due_date}]" if due_date else "[Due: None]"
        
        recurrence = task.get("recurrence")
        rec_str = f"[Recurrence: {format_recurrence(recurrence)}]"
        
        print(f"{i}: {task['task']} [Priority: {task.get('priority', 'Medium')}] {tags_str} {due_str} {rec_str}")

# Search tasks by text or tag
def search_todos(search_term):
    todos = load_todos()
    if not todos:
        print("No tasks found!")
        return

    # Filter tasks by text or tags matching the search_term
    matching_tasks = [
        task for task in todos
        if search_term.lower() in task['task'].lower() or search_term.lower() in [tag.lower() for tag in task.get("tags", [])]
    ]

    # If no tasks match the search term
    if not matching_tasks:
        print(f"No tasks found matching '{search_term}'.")
        return

    # Display matching tasks
    print(f"Found {len(matching_tasks)} matching task(s) for '{search_term}':")
    for i, task in enumerate(matching_tasks):
        tags = ", ".join(task.get("tags", []))
        print(f"{i}: {task['task']} [Priority: {task.get('priority', 'Medium')}] [Tags: {tags}]")

# Remove a task by index
def remove_todo(index):
    todos = load_todos()
    if 0 <= index < len(todos):
        removed = todos.pop(index)
        save_todos(todos)
        print(f"🗑️ Removed: {removed['task']} [Priority: {removed['priority']}]")
        
        # Check for tasks due today
        check_due_tasks(todos)

        # List the remaining tasks
        for i, task in enumerate(todos):
            due_date_str = task["due_date"] if task["due_date"] else "No due date"
            print(f"{i}: {task['task']} (Due: {due_date_str})")
    else:
        print("Invalid task index.")


# Check and notify if any tasks are due today
def check_due_tasks(todos):
    today = datetime.today().date()  # Get today's date
    due_today = [task for task in todos if task["due_date"] and task["due_date"] == today]
    
    if due_today:
        print("\n🔔 **Reminder**: The following tasks are due today:")
        for task in due_today:
            print(f" - {task['task']}")
            if task['recurrence']:
                task['next_due'] = calculate_next_due(task['due_date'], task['recurrence'])  # Update next_due
        save_todos(todos)
    else:
        print("\n✅ No tasks are due today.")

# Clear all tasks
def clear_todos():
    save_todos([])
    print("All tasks have been cleared.")

# Function to calculate the next due date for recurring tasks
def calculate_next_due(due_date, recurrence):
    due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()
    
    if recurrence == "daily":
        return (due_date_obj + timedelta(days=1)).strftime("%Y-%m-%d")
    elif recurrence == "weekly":
        return (due_date_obj + timedelta(weeks=1)).strftime("%Y-%m-%d")
    elif recurrence == "monthly":
        # Simple approach: add a month (could be improved to handle month length)
        next_month = due_date_obj.replace(month=due_date_obj.month % 12 + 1)
        return next_month.strftime("%Y-%m-%d")
    else:
        return due_date
    
# Edit a task by index
def edit_todo(index, new_description):
    todos = load_todos()
    if 0 <= index < len(todos):
        old_task = todos[index]
        todos[index]['task'] = new_description
        save_todos(todos)
        print(f" Updated task {index}:")
        print(f"   Old: {old_task}")
        print(f"   New: {todos[index]}")
    else:
        print("Invalid task index.")

# Command-line interface
def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python todo.py add \"Task name\" [--priority High|Medium|Low] [--tags tag1 tag2] [--due YYYY-MM-DD] [--recurrence 3d|2w|1m|daily|weekly|monthly]")
        print("  python todo.py list [--tag work] [--sort name|due]")
        print("  python todo.py search \"search_term\"")
        print("  python todo.py remove <index>")
        print("  python todo.py edit <index> --new-description \"New description\"")
        print("  python todo.py clear")
        return

    command = sys.argv[1]

    if command == "add":
        args = sys.argv[2:]
        task = None
        priority = "Medium"
        tags = []
        due_date = None
        recurrence = None

        if "--priority" in args:
            p_index = args.index("--priority")
            if p_index + 1 < len(args):
                priority = args[p_index + 1]
                task = " ".join(args[:p_index])
                args.pop(p_index)
                args.pop(p_index)
        
        if "--tags" in args:
            t_index = args.index("--tags")
            tags = []
            i = t_index + 1
            while i < len(args) and not args[i].startswith("--"):
                tags.append(args[i])
                i += 1
            args = args[:t_index] + args[i:]

        if "--due" in args:
            d_index = args.index("--due")
            if d_index + 1 < len(args):
                due_date = args[d_index + 1]
                args = args[:d_index] + args[d_index + 2:]

        if "--recurrence" in args:
            r_index = args.index("--recurrence")
            if r_index + 1 < len(args):
                recurrence = args[r_index + 1]
                args.pop(r_index)
                args.pop(r_index)

        task = " ".join(args)
        add_todo(task, priority, tags, due_date, recurrence)

    elif command == "list":
        filter_tag = None
        if "--tag" in sys.argv:
            tag_index = sys.argv.index("--tag")
            if tag_index + 1 < len(sys.argv):
                filter_tag = sys.argv[tag_index + 1]
        list_todos(filter_tag)

    elif command == "search":
        if len(sys.argv) < 3:
            print("Error: Please provide a search term.")
            print("Usage: python todo.py search \"search_term\"")
            return
        search_term = " ".join(sys.argv[2:])
        search_todos(search_term)

    elif command == "remove":
        if len(sys.argv) != 3:
            print("Error: Please provide the index of the task to remove.")
            print("Usage: python todo.py remove <index>")
            return
        
        try:
            index = int(sys.argv[2])
        except ValueError:
            print("Invalid index. Please provide a number.")
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
            return
        
        todos = load_todos()
        if not todos:
            print("No tasks to edit.")
            return
        
        if 0 <= index < len(todos):
            edit_todo(index, new_description)
        else:
            print(f"Error: Task index {index} does not exist. Use 'list' to see valid indices.")


    elif command == "clear":
        clear_todos()
        
    else:
        print(f"Error: Unknown command '{command}'.")
        print("Valid commands are: add, list, remove, clear.")



        

if __name__ == "__main__":
    main()
