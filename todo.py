import json
import os
import sys
from datetime import datetime, timedelta
# Import both functions from your calendar plugin
from plugins.google_calendar import add_to_calendar, fetch_upcoming_events

FILE_PATH = "todos.json"

# Load tasks
def load_todos():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as f:
            return json.load(f)
    return []

# Save tasks
def save_todos(todos):
    with open(FILE_PATH, "w") as f:
        json.dump(todos, f, indent=2)

# Parse recurrence formats
def parse_recurrence(recurrence_str):
    if not recurrence_str:
        return None
    legacy_map = {"daily": {"interval": 1, "unit": "d"},
                  "weekly": {"interval": 1, "unit": "w"},
                  "monthly": {"interval": 1, "unit": "m"}}
    if recurrence_str in legacy_map:
        return legacy_map[recurrence_str]
    if len(recurrence_str) >= 2 and recurrence_str[-1] in ['d', 'w', 'm']:
        try:
            interval = int(recurrence_str[:-1])
            unit = recurrence_str[-1]
            return {"interval": interval, "unit": unit}
        except ValueError:
            pass
    return None

def format_recurrence(recurrence):
    if not recurrence:
        return "None"
    unit_names = {"d": "day", "w": "week", "m": "month"}
    interval = recurrence.get("interval", 1)
    unit = recurrence.get("unit", "d")
    unit_name = unit_names.get(unit, "day")
    if interval > 1:
        unit_name += "s"
    return f"Every {interval} {unit_name}"

# Calculate next due date
def calculate_next_due(due_date, recurrence):
    due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()
    interval = recurrence.get("interval", 1)
    unit = recurrence.get("unit", "d")

    if unit == "d":
        next_date = due_date_obj + timedelta(days=interval)
    elif unit == "w":
        next_date = due_date_obj + timedelta(weeks=interval)
    elif unit == "m":
        month = due_date_obj.month - 1 + interval
        year = due_date_obj.year + month // 12
        month = month % 12 + 1
        day = min(due_date_obj.day, [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        next_date = datetime(year, month, day).date()
    else:
        next_date = due_date_obj
    return next_date.strftime("%Y-%m-%d")

# Add new task
def add_todo(task, priority="Medium", tags=None, due_date=None, recurrence=None, auto_sync=True):
    valid_priorities = ["Low", "Medium", "High"]
    if priority not in valid_priorities:
        print("Invalid priority. Use: Low, Medium, or High.")
        return

    if tags is None:
        tags = []

    due_date_obj = None
    if due_date:
        try:
            due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return

    recurrence_obj = parse_recurrence(recurrence)
    if recurrence and not recurrence_obj:
        print("Invalid recurrence format. Use daily, weekly, monthly, or 3d/2w/1m.")
        return

    todos = load_todos()
    task_obj = {
        "task": task,
        "priority": priority,
        "tags": tags,
        "due_date": due_date_obj.strftime("%Y-%m-%d") if due_date_obj else None,
        "recurrence": recurrence_obj,
        "next_due": due_date_obj.strftime("%Y-%m-%d") if due_date_obj else None,
        "completed": False,
        "synced": False # Initialize as not synced
    }
    
    # Google Calendar Sync (if due date is present and auto_sync is on)
    if due_date_obj and auto_sync:
        print(f"Syncing '{task}' to Google Calendar...")
        try:
            add_to_calendar(task, due_date_obj)
            task_obj['synced'] = True # Mark as synced
            print("📅 Task synced to Google Calendar successfully!")
        except Exception as e:
            print(f"❌ Failed to sync with Google Calendar: {e}")
            
    todos.append(task_obj)
    save_todos(todos)

    print(f"✅ Added: {task} [Priority: {priority}]")

# List tasks
def list_todos(filter_tag=None):
    todos = load_todos()
    if not todos:
        print("No tasks yet!")
        return

    if filter_tag:
        todos = [t for t in todos if filter_tag in t.get("tags", [])]
        if not todos:
            print(f"No tasks found with tag '{filter_tag}'.")
            return

    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    todos.sort(key=lambda x: priority_order.get(x.get("priority", "Medium")))

    for i, task in enumerate(todos):
        tags = ", ".join(task.get("tags", [])) or "None"
        due = task.get("due_date", "N/A")
        rec = format_recurrence(task.get("recurrence"))
        status = "✅ Done" if task.get("completed") else "⏳ Pending"
        print(f"{i}: {task['task']} [Priority: {task['priority']}] [Tags: {tags}] [Due: {due}] [Recurrence: {rec}] [{status}]")

# Remove task
def remove_todo(index):
    todos = load_todos()
    if 0 <= index < len(todos):
        removed = todos.pop(index)
        save_todos(todos)
        print(f"🗑️ Removed: {removed['task']}")
    else:
        print("Invalid task index.")

# Clear all
def clear_todos():
    save_todos([])
    print("All tasks cleared.")

# Mark complete
def complete_todo(index):
    todos = load_todos()
    if 0 <= index < len(todos):
        todos[index]["completed"] = True
        save_todos(todos)
        print(f"✅ Marked as done: {todos[index]['task']}")
    else:
        print("Invalid task index.")

# Function to sync all due tasks to Google Calendar
def sync_all_tasks_to_calendar():
    todos = load_todos()
    tasks_to_sync = [
        task for task in todos 
        if task.get("due_date") and not task.get("completed") and not task.get("synced")
    ]
    
    if not tasks_to_sync:
        print("✅ All tasks are already synced.")
        return

    print(f"Found {len(tasks_to_sync)} tasks to sync.")
    
    for task in tasks_to_sync:
        try:
            print(f"Syncing '{task['task']}'...")
            due_date_obj = datetime.strptime(task['due_date'], "%Y-%m-%d").date()
            add_to_calendar(task['task'], due_date_obj)
            task['synced'] = True # Mark the task as synced to prevent duplicates
        except Exception as e:
            print(f"❌ Failed to sync '{task['task']}': {e}")
            
    save_todos(todos)
    print("Sync complete.")

# Function to pull tasks from Google Calendar
def pull_tasks_from_calendar():
    print("Fetching upcoming events from Google Calendar...")
    events = fetch_upcoming_events()
    
    if events is None:
        print("❌ Could not fetch events.")
        return

    if not events:
        print("✅ No upcoming events found.")
        return

    todos = load_todos()
    existing_tasks = {t['task'].lower() for t in todos} # Use .lower() for case-insensitive check
    new_tasks_added = 0

    for event in events:
        task_name = event['summary']
        if task_name.lower() not in existing_tasks:
            # The start object can contain 'dateTime' (for timed events) or 'date' (for all-day events)
            start = event['start'].get('dateTime', event['start'].get('date'))
            due_date = start.split('T')[0] # Get just the YYYY-MM-DD part

            # Add the task without auto-syncing it back to the calendar
            add_todo(task=task_name, due_date=due_date, auto_sync=False)
            new_tasks_added += 1
            print(f"➕ Imported task: {task_name} [Due: {due_date}]")
    
    if new_tasks_added == 0:
        print("No new tasks to import.")
    else:
        print(f"Import complete. Added {new_tasks_added} new tasks.")


# CLI
def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python todo.py add \"Task name\" --priority High --tags work --due 2025-10-07")
        print("  python todo.py list [--tag work]")
        print("  python todo.py remove <index>")
        print("  python todo.py complete <index>")
        print("  python todo.py clear")
        print("  python todo.py sync calendar")
        print("  python todo.py pull calendar")
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
            idx = args.index("--priority")
            priority = args[idx + 1]
            args = args[:idx] + args[idx + 2:]
        if "--tags" in args:
            idx = args.index("--tags")
            i = idx + 1
            while i < len(args) and not args[i].startswith("--"):
                tags.append(args[i])
                i += 1
            args = args[:idx] + args[i:]
        if "--due" in args:
            idx = args.index("--due")
            due_date = args[idx + 1]
            args = args[:idx] + args[idx + 2:]
        if "--recurrence" in args:
            idx = args.index("--recurrence")
            recurrence = args[idx + 1]
            args = args[:idx] + args[idx + 2:]

        task = " ".join(args)
        add_todo(task, priority, tags, due_date, recurrence)

    elif command == "list":
        tag = None
        if "--tag" in sys.argv:
            tag_idx = sys.argv.index("--tag")
            tag = sys.argv[tag_idx + 1]
        list_todos(tag)

    elif command == "remove":
        remove_todo(int(sys.argv[2]))

    elif command == "complete":
        complete_todo(int(sys.argv[2]))

    elif command == "clear":
        clear_todos()

    elif command == "sync":
        if len(sys.argv) > 2 and sys.argv[2] == "calendar":
            sync_all_tasks_to_calendar()
        else:
            print("Unknown sync command. Did you mean 'sync calendar'?")

    elif command == "pull":
        if len(sys.argv) > 2 and sys.argv[2] == "calendar":
            pull_tasks_from_calendar()
        else:
            print("Unknown pull command. Did you mean 'pull calendar'?")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()