import json
import os
import sys
import time
import uuid

FILE_PATH = "todos.json"
OFFLINE_QUEUE = "offline_queue.json"
undo_stack = []
redo_stack = []
import sqlite3

from datetime import datetime
from datetime import datetime, timedelta

# Import both functions from your calendar plugin
from plugins.google_calendar import add_to_calendar, fetch_upcoming_events

FILE_PATH = "todos.json"
OFFLINE_QUEUE = "offline_queue.json"
undo_stack = []
redo_stack = []
tags = []
due_date_obj = None
recurrence_obj = None
task = {}
priority = 1
show_completed = False

# Load tasks from JSON file


# Load tasks
def load_todos():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as f:
            todos = json.load(f)
            # Remove tasks missing 'task' or with empty descriptions
            valid_todos = [t for t in todos if "task" in t and t["task"].strip()]
            if len(valid_todos) != len(todos):
                save_todos(valid_todos)  # save cleaned list
            return valid_todos
    return []


# Save tasks to JSON file
def save_todos(todos):
    with open(FILE_PATH, "w") as f:
        json.dump(todos, f, indent=2)
def snapshot():
    todos = load_todos()
    undo_stack.append(json.dumps(todos))
    redo_stack.clear()

def restore_state(state_json):
    todos = json.loads(state_json)
    save_todos(todos)
    
def snapshot():
    todos = load_todos()
    undo_stack.append(json.dumps(todos))
    redo_stack.clear()

def restore_state(state_json):
    todos = json.loads(state_json)
    save_todos(todos)

def load_offline_queue():
    if os.path.exists(OFFLINE_QUEUE):
        with open(OFFLINE_QUEUE, "r") as f:
            return json.load(f)
    return []

def save_offline_queue(queue):
    with open(OFFLINE_QUEUE, "w") as f:
        json.dump(queue, f, indent=2)


 # Log offline actions
def log_offline_action(operation, task_data):
    queue = load_offline_queue()
    queue.append({
        "timestamp": time.time(),
        "operation": operation,
        "task_id": task_data.get("id"),
        "task_data": task_data
    })
    save_offline_queue(queue)

 # Sync offline actions with server
def sync_with_server(server_tasks):
    local_queue = load_offline_queue()
    for action in local_queue:
     pass  
    save_offline_queue([])
    print("Sync complete.")

def load_server_tasks():
    return load_todos()

# Add a new task with optional priority and tags
def add_todo(task, priority="Medium", tags=None):
    snapshot()

def load_offline_queue():
    if os.path.exists(OFFLINE_QUEUE):
        with open(OFFLINE_QUEUE, "r") as f:
            return json.load(f)
    return []

def save_offline_queue(queue):
    with open(OFFLINE_QUEUE, "w") as f:
        json.dump(queue, f, indent=2)


 # Log offline actions
def log_offline_action(operation, task_data):
    queue = load_offline_queue()
    queue.append({
        "timestamp": time.time(),
        "operation": operation,
        "task_id": task_data.get("id"),
        "task_data": task_data
    })
    save_offline_queue(queue)

def log_task_change(task, change_type, new_data):
    if "history" not in task:
        task["history"] = []
    task["history"].append({
        "timestamp": time.time(),
        "change": change_type,
        "data": new_data
    })

 # Sync offline actions with server
def sync_with_server(server_tasks):
    local_queue = load_offline_queue()
    for action in local_queue:
     pass  
    save_offline_queue([])
    print("Sync complete.")

def load_server_tasks():
    return load_todos()

# Add a new task with optional priority and tags
def add_todo(task, priority="Medium", tags=None):
    snapshot()
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

# --- Functions from the 'main' branch for database interaction ---
def create_task(task_name, due_date, status='pending'):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (name, due_date, status, timestamp) VALUES (?, ?, ?, ?)",
                   (task_name, due_date, status, datetime.now().timestamp()))
    conn.commit()
    conn.close()

def get_all_tasks():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    conn.close()
    return tasks

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

# Add a new task with combined features
def add_todo(task, priority="Medium", tags=None, due_date=None, recurrence=None, auto_sync=True):
    # Validate non-empty task description
    if not task or not task.strip():
        print("Error: Task description cannot be empty.")
        return

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
    new_task = {
        "id": str(uuid.uuid4()),
        "task": task,
        "priority": priority,
        "tags": tags,
        "completed": False,
        "history": [
            {
                "timestamp": time.time(),
                "change": "created",
                "data": {
                    "task": task,
                    "priority": priority,
                    "tags": tags,
                    "completed": False
                }
            }
        ]
    }

    todos.append(new_task)
    save_todos(todos)
    log_offline_action("add", new_task)
    print(f" Added: {task} [Priority: {priority}] [Tags: {', '.join(tags)}]")   

    todos = load_todos()
    todos.append({"task": task, "priority": priority, "tags": tags, "completed": False})
    save_todos(todos)
    log_offline_action("add", todos[-1])
    print(f"Added: {task} [Priority: {priority}] [Tags: {', '.join(tags)}]")
    task_obj = {
        "task": task,
        "priority": priority,
        "tags": tags,
        "due_date": due_date_obj.strftime("%Y-%m-%d") if due_date_obj else None,
        "recurrence": recurrence_obj,
        "next_due": due_date_obj.strftime("%Y-%m-%d") if due_date_obj else None,
        "completed": False,
        "synced": False  # Initialize as not synced (from your branch)
    }
    
    # Google Calendar Sync (from your branch)
    if due_date_obj and auto_sync:
        print(f"Syncing '{task}' to Google Calendar...")
        try:
            add_to_calendar(task, due_date_obj)
            task_obj['synced'] = True  # Mark as synced
            print("📅 Task synced to Google Calendar successfully!")
        except Exception as e:
            print(f"❌ Failed to sync with Google Calendar: {e}")
            
    todos.append(task_obj)
    save_todos(todos)
    log_offline_action("add", todos[-1])
    print(f"Added: {task} [Priority: {priority}] [Tags: {', '.join(tags)}]")
    print(f"✅ Added: {task} [Priority: {priority}]")

# --- Functions from the 'main' branch for advanced listing ---
def adjust_priority_by_due_date(task):
    due = task.get("due") or task.get("due_date")
    if not due:
        return task.get("priority", "Medium")
    try:
        due_dt = datetime.strptime(due, "%Y-%m-%d")
    except (ValueError, TypeError):
        return task.get("priority", "Medium")
    delta = due_dt - datetime.now()
    if delta <= timedelta(days=1):
        return "High"
    elif delta <= timedelta(days=3):
        return "Medium"
    else:
        return task.get("priority", "Medium")

# List tasks (using the more advanced version from 'main')

from datetime import datetime, timedelta

def adjust_priority_by_due_date(task):
    """
    Returns auto-adjusted priority if the task has a due date:
      - Due within 1 day: High
      - Due within 3 days: Medium
      - Otherwise: original priority (default: Medium)
    """
    due = task.get("due") or task.get("due_date")
    if not due:
        return task.get("priority", "Medium")
    try:
        due_dt = datetime.strptime(due, "%Y-%m-%d")
    except (ValueError, TypeError):
        return task.get("priority", "Medium")
    delta = due_dt - datetime.now()
    if delta <= timedelta(days=1):
        return "High"
    elif delta <= timedelta(days=3):
        return "Medium"
    else:
        return task.get("priority", "Medium")

# List all tasks sorted by priority and optionally filtered by tag
def list_todos(filter_tag=None, sort_by=None, show_completed=False):
    tags_str = f"[Tags: {', '.join(tags)}]" if tags else ""
    due_str = f"[Due: {due_date_obj.strftime('%Y-%m-%d')}]" if due_date_obj else ""
    rec_str = f"[Recurrence: {format_recurrence(recurrence_obj)}]" if recurrence_obj else ""

    print(f" Added: {task} [Priority: {priority}] {tags_str} {due_str} {rec_str}".strip())

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

    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    todos.sort(key=lambda x: priority_order.get(x.get("priority", "Medium")))

    for i, task in enumerate(todos):
     
        tags = ", ".join(task.get("tags", []))
        due = task.get("due", "N/A")
        status = " Done" if task.get("completed") else "⏳ Pending"
        print(f"{i}: {task['task']} [Priority: {task['priority']}] [Tags: {tags}] [Due: {due}] [{status}]")
        tags = ", ".join(task.get("tags", [])) if task.get("tags") else ""
        tags_str = f"[Tags: {tags}]" if tags else "[Tags: None]"

        due_date = task.get("due_date")
        due_str = f"[Due: {due_date}]" if due_date else "[Due: None]"

        rec_str = f"[Recurrence: {format_recurrence(task.get('recurrence'))}]"
        status = "✅ Done" if task.get("completed") else "⏳ Pending"
        print(f"{i}: {task.get('task', '<No task description>')} [Priority: {task.get('priority', 'Medium')}] {tags_str} {due_str} {rec_str}")

# Search tasks by text or tag
        print(f"{i}: {task.get('task', '<No task description>')} "
          f"[Priority: {task.get('priority', 'Medium')}] {tags_str} {due_str} {rec_str} [{status}]")

def search_todos(search_term):
    todos = load_todos()
    if not todos:
        print("No tasks found!")
        return

    matching_tasks = [
        task for task in todos
        if search_term.lower() in task['task'].lower() or search_term.lower() in [tag.lower() for tag in task.get("tags", [])]
    ]

    if not matching_tasks:
        print(f"No tasks found matching '{search_term}'.")
        return

    print(f"Found {len(matching_tasks)} matching task(s) for '{search_term}':")
    for i, task in enumerate(matching_tasks):
        tags = ", ".join(task.get("tags", []))
        due = task.get("due", "N/A")
        status = " Done" if task.get("completed") else "⏳ Pending"
        print(f"{i}: {task['task']} [Priority: {task['priority']}] [Tags: {tags}] [Due: {due}] [{status}]")
        print(f"{i}: {task['task']} [Priority: {task.get('priority', 'Medium')}] [Tags: {tags}]")

        # Summary message
    all_tasks = load_todos()
    completed = len([t for t in all_tasks if t.get("completed")])
    pending = len([t for t in all_tasks if not t.get("completed")])
    high_priority = len([t for t in all_tasks if not t.get("completed") and t.get("priority") == "High"])

    print("\n--- Summary ---")
    if pending == 0:
        print("Nice! All your tasks are completed.")
    else:
        print(f"You have {pending} pending task{'s' if pending > 1 else ''}.")
        if high_priority > 0:
            print(f"{high_priority} high-priority task{'s' if high_priority > 1 else ''} need your attention today!")
        else:
            print(" No high-priority tasks pending.")

# Remove a task by index
def remove_todo(index):
    snapshot()
    todos = load_todos()
    if 0 <= index < len(todos):
        log_offline_action("remove", todos[index])
        removed = todos.pop(index)
        save_todos(todos)
        print(f"Removed: {removed['task']} [Priority: {removed['priority']}]")
        print(f"Removed: {removed['task']} [Priority: {removed['priority']}]")
        print(f" Removed: {removed['task']} [Priority: {removed['priority']}]")
        
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
        print("\n **Reminder**: The following tasks are due today:")
        for task in due_today:
            print(f" - {task['task']}")
            if task['recurrence']:
                task['next_due'] = calculate_next_due(task['due_date'], task['recurrence'])  # Update next_due
        save_todos(todos)
    else:
        print("\n No tasks are due today.")

# Clear all tasks
def clear_todos():
    snapshot()
    save_todos([])
    print("All tasks have been cleared.")

# Load plugins from plugins/ folder
def load_plugins():
    plugins = {}
    plugin_dir = "plugins"
    if os.path.isdir(plugin_dir):
        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py"):
                plugin_name = filename[:-3]
                try:
                    module = __import__(f"{plugin_dir}.{plugin_name}", fromlist=["run"])
                    if hasattr(module, "run"):
                        plugins[plugin_name] = module.run
                except Exception as e:
                    print(f"Failed to load plugin {plugin_name}: {e}")
    return plugins
  
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
        print(f"🗑️ Removed: {removed['task']}")
    else:
        print("Invalid task index.")

# Clear all
def clear_todos():
    snapshot()
    save_todos([])
    print("All tasks have been cleared.")

# Load plugins from plugins/ folder
def load_plugins():
    plugins = {}
    plugin_dir = "plugins"
    if os.path.isdir(plugin_dir):
        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py"):
                plugin_name = filename[:-3]
                try:
                    module = __import__(f"{plugin_dir}.{plugin_name}", fromlist=["run"])
                    if hasattr(module, "run"):
                        plugins[plugin_name] = module.run
                except Exception as e:
                    print(f"Failed to load plugin {plugin_name}: {e}")
    return plugins
    print("All tasks cleared.")

# Mark complete
def complete_todo(index):
    snapshot()
    todos = load_todos()
    if 0 <= index < len(todos):
        todos[index]["completed"] = True
        log_task_change(todos[index], "completed", {"completed": True})
        log_offline_action("complete", todos[index])
        save_todos(todos)
        print(f"Marked as done: {todos[index]['task']}")
    else:
        print("Invalid task index.")

def undo():
    if not undo_stack:
        print("Nothing to undo.")
        return
    current = json.dumps(load_todos())
    redo_stack.append(current)
    previous = undo_stack.pop()
    restore_state(previous)
    print("Undo successful.")
    print("↩️ Undo successful.")

def redo():
    if not redo_stack:
        print("Nothing to redo.")
        return
    undo_stack.append(json.dumps(load_todos()))
    next_state = redo_stack.pop()
    restore_state(next_state)
    print("Redo successful.")
           
def rollback_task(index):
    todos = load_todos()
    if 0 <= index < len(todos):
        history = todos[index].get("history", [])
        if len(history) < 2:
            print("No previous version to roll back to.")
            return
        last = history[-2]["data"]
        todos[index].update(last)
        log_task_change(todos[index], "rolled back", last)
        save_todos(todos)
        print(f"Rolled back task: {todos[index]['task']}")
    else:
        print("Invalid task index.")        
    print("Redo successful.")       
    print("↪️ Redo successful.")       

# Command-line interface

# --- Calendar Sync functions from your branch ---
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
            task['synced'] = True  # Mark the task as synced to prevent duplicates
        except Exception as e:
            print(f"❌ Failed to sync '{task['task']}': {e}")
            
    save_todos(todos)
    print("Sync complete.")

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
    existing_tasks = {t['task'].lower() for t in todos}
    new_tasks_added = 0

    for event in events:
        task_name = event['summary']
        if task_name.lower() not in existing_tasks:
            start = event['start'].get('dateTime', event['start'].get('date'))
            due_date = start.split('T')[0]

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
        print("  python todo.py list --completed")
        print("  python todo.py remove <index>")
        print("  python todo.py complete <index>")
        print("  python todo.py clear")
        print("  python todo.py sync calendar")
        print("  python todo.py pull calendar")
        print("  python todo.py list --completed")
        print("  python todo.py <plugin_name> [args...]")
        print("  python todo.py undo")
        print("  python todo.py redo")
        print("  python todo.py sync")

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
        # Using the improved version from 'main' with error handling
        if len(sys.argv) == 3:
            try:
                index = int(sys.argv[2])
                complete_todo(index)
            except ValueError:
                print("Invalid index. Please provide a number.")
        else:
            print("Usage: python todo.py complete <index>")


    elif command == "clear":
        clear_todos()

    # Commands from your branch
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

    elif command == "complete" and len(sys.argv) == 3:
        try:
            index = int(sys.argv[2])
            complete_todo(index)
        except ValueError:
            print("Invalid index. Please provide a number.")

    elif command == "undo":
        undo()

    elif command == "redo":
        redo()       

    elif command == "sync":
     server_tasks = load_server_tasks()
     sync_with_server(server_tasks)    

    elif command == "rollback" and len(sys.argv) == 3:
        try:
           index = int(sys.argv[2])
           rollback_task(index)
        except ValueError:
           print("Invalid index.")
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
