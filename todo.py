import json
import os
import sys

FILE_PATH = "todos.json"
undo_stack = []
redo_stack = []

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

def snapshot():
    todos = load_todos()
    undo_stack.append(json.dumps(todos))
    redo_stack.clear()

def restore_state(state_json):
    todos = json.loads(state_json)
    save_todos(todos)

# Add a new task with optional priority and tags
def add_todo(task, priority="Medium", tags=None):
    snapshot()
    valid_priorities = ["Low", "Medium", "High"]
    if priority not in valid_priorities:
        print("Invalid priority. Use: Low, Medium, or High.")
        return

    if tags is None:
        tags = []

    todos = load_todos()
    todos.append({"task": task, "priority": priority, "tags": tags, "completed": False})
    save_todos(todos)
    print(f"✅ Added: {task} [Priority: {priority}] [Tags: {', '.join(tags)}]")

# List all tasks sorted by priority and optionally filtered by tag
def list_todos(filter_tag=None, sort_by=None, show_completed=False):
    todos = load_todos()
    if not todos:
        print("No tasks yet!")
        return

    if not show_completed:
        todos = [t for t in todos if not t.get("completed", False)]
    else:
        todos = [t for t in todos if t.get("completed", False)]

    if filter_tag:
        todos = [t for t in todos if filter_tag in t.get("tags", [])]

    if sort_by == "name":
        todos.sort(key=lambda x: x.get("task", "").lower())
    elif sort_by == "due":
        todos.sort(key=lambda x: x.get("due", "")) 
    else:
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        todos.sort(key=lambda x: priority_order.get(x.get("priority", "Medium")))

    for i, task in enumerate(todos):
        tags = ", ".join(task.get("tags", []))
        due = task.get("due", "N/A")
        status = "✅ Done" if task.get("completed") else "⏳ Pending"
        print(f"{i}: {task['task']} [Priority: {task['priority']}] [Tags: {tags}] [Due: {due}] [{status}]")

        # Summary message
    all_tasks = load_todos()
    completed = len([t for t in all_tasks if t.get("completed")])
    pending = len([t for t in all_tasks if not t.get("completed")])
    high_priority = len([t for t in all_tasks if not t.get("completed") and t.get("priority") == "High"])

    print("\n--- Summary ---")
    if pending == 0:
        print("🎉 Nice! All your tasks are completed.")
    else:
        print(f"📝 You have {pending} pending task{'s' if pending > 1 else ''}.")
        if high_priority > 0:
            print(f"🔥 {high_priority} high-priority task{'s' if high_priority > 1 else ''} need your attention today!")
        else:
            print("👍 No high-priority tasks pending.")

# Remove a task by index
def remove_todo(index):
    snapshot()
    todos = load_todos()
    if 0 <= index < len(todos):
        removed = todos.pop(index)
        save_todos(todos)
        print(f"🗑️ Removed: {removed['task']} [Priority: {removed['priority']}]")
    else:
        print("Invalid task index.")

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
                    print(f"⚠️ Failed to load plugin {plugin_name}: {e}")
    return plugins

def complete_todo(index):
    snapshot()
    todos = load_todos()
    if 0 <= index < len(todos):
        todos[index]["completed"] = True
        save_todos(todos)
        print(f"✅ Marked as done: {todos[index]['task']}")
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
    print("↩️ Undo successful.")

def redo():
    if not redo_stack:
        print("Nothing to redo.")
        return
    undo_stack.append(json.dumps(load_todos()))
    next_state = redo_stack.pop()
    restore_state(next_state)
    print("↪️ Redo successful.")       

# Command-line interface
def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python todo.py add \"Task name\" [--priority High|Medium|Low] [--tags work personal]")
        print("  python todo.py list [--tag work] [--sort name|due]")
        print("  python todo.py remove <index>")
        print("  python todo.py clear")
        print("  python todo.py complete <index>")
        print("  python todo.py list --completed")
        print("  python todo.py <plugin_name> [args...]")
        print("  python todo.py undo")
        print("  python todo.py redo")
        return

    command = sys.argv[1]
    plugins = load_plugins()

    if command in plugins:
        plugins[command](sys.argv[2:])
        return

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
        sort_by = None
        show_completed = "--completed" in sys.argv

        if "--tag" in sys.argv:
            tag_index = sys.argv.index("--tag")
            if tag_index + 1 < len(sys.argv):
                filter_tag = sys.argv[tag_index + 1]

        if "--sort" in sys.argv:
            sort_index = sys.argv.index("--sort")
            if sort_index + 1 < len(sys.argv):
                sort_by = sys.argv[sort_index + 1]

        list_todos(filter_tag, sort_by, show_completed)

    elif command == "remove" and len(sys.argv) == 3:
        try:
            index = int(sys.argv[2])
            remove_todo(index)
        except ValueError:
            print("Invalid index. Please provide a number.")

    elif command == "clear":
        clear_todos()

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

    else:
        print("Unknown command.")

if __name__ == "__main__":
    main()

    