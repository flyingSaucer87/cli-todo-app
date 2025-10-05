# #!/usr/bin/env python3
# from __future__ import annotations
# import argparse
# import json
# import os
# import sys
# import tempfile
# from pathlib import Path
# from typing import List, Dict, Any
# from typing import List, Dict, Any
# from collections import Counter
# from rich.console import Console
# from rich.table import Table
# from rich.progress import Progress
# from auth import validate

# console = Console()

# def show_stats():
#     tasks = taskload()
#     if not tasks:
#         print("No tasks to analyze.")
#         return

#     # Completion Rate
#     completed = sum(1 for task in tasks if task.get("completed", False))
#     total = len(tasks)
#     completion_percent = (completed / total) * 100 if total else 0

#     # Priority Breakdown
#     priority_counts = Counter(task.get("priority", "Medium") for task in tasks)

#     # Tags Breakdown
#     tag_counts = Counter(tag for task in tasks for tag in task.get("tags", []))

#     # Display
#     console.rule("[bold green]📊 Task Analytics Dashboard")
#     console.print(f"\n✅ [bold]Completion:[/bold] {completed}/{total} tasks completed ({completion_percent:.2f}%)")

#     # Priority Table
#     table = Table(title="Priority Breakdown")
#     table.add_column("Priority", justify="left", style="cyan")
#     table.add_column("Count", justify="right", style="magenta")
#     for priority, count in priority_counts.items():
#         table.add_row(priority, str(count))
#     console.print(table)

#     # Tag Table
#     if tag_counts:
#         tag_table = Table(title="Most Used Tags")
#         tag_table.add_column("Tag", style="green")
#         tag_table.add_column("Count", justify="right", style="yellow")
#         for tag, count in tag_counts.most_common(10):
#             tag_table.add_row(tag, str(count))
#         console.print(tag_table)
#     else:
#         console.print("🔖 No tags found.")

#     console.rule()


# def cmd_add(description: str, priority: str = "Medium", tags: List[str] = [], completed: bool = False) -> None:

#     # Validate task is not empty
#     if not validate_task(description):
#         print("Error: Task description cannot be empty or whitespace only.", file=sys.stderr)
#         sys.exit(1)

#     # Validate priority
#     if priority not in "VALID_PRIORITIES":
#         print(f"Error: Invalid priority '{priority}'. Must be one of: {', '.join('VALID_PRIORITIES')}", file=sys.stderr)
#         sys.exit(1)

#     # Create a new task with additional attributes
#     tasks = taskload()
#     tasks.append({
#         "description": description,
#         "priority": priority,
#         "tags": tags,
#         "completed": completed,
#     })
#     tasksave(tasks)
#     print(f"Added task #{len(tasks)}: {description.strip()} [Priority: {priority}] [Tags: {', '.join(tags)}] [Completed: {completed}]")



# # Default tasks file (next to this script). Can be overridden with TODO_FILE env var.
# TASKS_FILE = Path(os.getenv("TODO_FILE", Path(__file__).with_name("tasks.json")))

# # File for user settings
# CONFIG_FILE = Path(os.getenv("TODO_CONFIG_FILE", Path(__file__).with_name("config.json")))

# # --- Settings Management ---
# def load_config() -> Dict[str, Any]:
#     """Load user settings from the config file."""
#     if not CONFIG_FILE.exists():
#         return {"dark_mode": False}  # Default settings
#     try:
#         with CONFIG_FILE.open("r", encoding="utf-8") as f:
#             return json.load(f)
#     except (json.JSONDecodeError, IOError):
#         # If config is corrupt or unreadable, return defaults
#         return {"dark_mode": False}


# def save_config(config: Dict[str, Any]) -> None:
#     """Save user settings to the config file."""
#     try:
#         CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
#         with CONFIG_FILE.open("w", encoding="utf-8") as f:
#             json.dump(config, f, indent=2)
#     except IOError as e:
#         print(f"Error: Could not save settings to {CONFIG_FILE}: {e}", file=sys.stderr)
#         sys.exit(1)

# def _normalize_tasks(data: Any) -> List[Dict[str, Any]]:
#     """Normalize raw JSON data into a list of task dicts."""
#     normalized: List[Dict[str, Any]] = []
#     if isinstance(data, list):
#         for item in data:
#             if isinstance(item, str):  # Legacy task format: simple string
#                 normalized.append({"description": item, "completed": False, "priority": "Medium", "tags": []})
#             elif isinstance(item, dict):  # New task format
#                 desc = item.get("description")
#                 if isinstance(desc, str):
#                     normalized.append({
#                         "description": desc,
#                         "completed": bool(item.get("completed", False)),
#                         "priority": item.get("priority", "Medium"),
#                         "tags": item.get("tags", []),
#                     })
#             # ignore other types silently
#     return normalized


# def taskload() -> List[Dict[str, Any]]:

#     if not TASKS_FILE.exists():
#         return []

#     try:
#         with TASKS_FILE.open("r", encoding="utf-8") as f:
#             data = json.load(f)
#         tasks = _normalize_tasks(data)
#         # If file was legacy format, persist normalized structure
#         if isinstance(data, list) and tasks and not isinstance(data[0], dict):
#             tasksave(tasks)
#         return tasks
#     except json.JSONDecodeError:
#         backupcorrupt("json-decode-error")
#         return []
#     except Exception as e:
#         print(f"Error reading tasks file: {e}", file=sys.stderr)
#         return []


# def backupcorrupt(reason: str) -> None:
#     """
#     Backup a corrupted tasks file before resetting.

#     Args:
#         reason: Description of why the file is being backed up.
#     """
#     try:
#         if TASKS_FILE.exists():
#             backup_name = TASKS_FILE.with_suffix(f".backup.{reason}")
#             TASKS_FILE.replace(backup_name)
#             print(f"Backed up corrupted tasks file to: {backup_name}", file=sys.stderr)
#     except Exception as e:
#         print(f"Failed to back up corrupted tasks file: {e}", file=sys.stderr)


# def tasksave(tasks: List[Dict[str, Any]]) -> None:
#     """
#     Save tasks to the JSON file.
#     """
#     TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
#     data = json.dumps(tasks, ensure_ascii=False, indent=2)

#     try:
#         fd, tmp_path = tempfile.mkstemp(prefix=".tasks-", dir=str(TASKS_FILE.parent))
#     except (PermissionError, OSError) as e:
#         print(f"Error: Cannot create temporary file: {e}", file=sys.stderr)
#         sys.exit(1)

#     try:
#         try:
#             with os.fdopen(fd, "w", encoding="utf-8") as tmpf:
#                 tmpf.write(data)
#                 tmpf.flush()
#                 os.fsync(tmpf.fileno())
#         except (IOError, OSError) as e:
#             print(f"Error: Cannot write to temporary file: {e}", file=sys.stderr)
#             sys.exit(1)

#         try:
#             Path(tmp_path).replace(TASKS_FILE)
#         except (PermissionError, OSError) as e:
#             print(f"Error: Cannot save tasks file: {e}", file=sys.stderr)
#             sys.exit(1)
#     finally:
#         # Clean up temporary file if it still exists
#         if os.path.exists(tmp_path):
#             try:
#                 os.remove(tmp_path)
#             except Exception:
#                 pass

# def build_parser() -> argparse.ArgumentParser:
#     """
#     Build and configure the argument parser for CLI commands.
#     """
#     parser = argparse.ArgumentParser(prog="todo.py", description="Simple CLI todo app in python")
#     sub = parser.add_subparsers(dest="cmd", required=True)

#     p_add = sub.add_parser("add", help="Add a task to the list")
#     p_add.add_argument("description", help="Task description")
#     p_add.add_argument(
#         "--priority",
#         "-p",
#         choices=["Low", "Medium", "High"],
#         default="Medium",
#         help="Task priority (default: Medium)"
#     )
#     p_add.add_argument(
#         "--tags",
#         "-t",
#         nargs="*",
#         default=[],
#         help="Tags associated with the task"
#     )
#     p_add.add_argument(
#         "--completed",
#         "-c",
#         action="store_true",
#         help="Mark task as completed"
#     )

#     p_list = sub.add_parser("list", help="List all tasks sorted by priority")

#     p_remove = sub.add_parser("remove", help="Remove a task by its index (1-based)")
#     p_remove.add_argument("index", type=int, help="Enter task index to remove")

#     p_complete = sub.add_parser("complete", help="Mark a task as completed by its index (1-based)")
#     p_complete.add_argument("index", type=int, help="Enter task index to mark complete")

#     p_stats = sub.add_parser("stats", help="Display task analytics (completion rate, priority, tags)")

#     return parser


# def validate_task(description: str) -> bool:
#     """
#     Validate that a task description is not empty or whitespace-only.

#     Args:
#         description: The task description to validate.

#     Returns:
#         True if valid, False otherwise.
#     """
#     return description and description.strip()


# def cmd_add(description: str, priority: str = "DEFAULT_PRIORITY") -> None:
#     """
#     Add a new task with the given description and priority.

#     Args:
#         description: The task description.
#         priority: Task priority (Low, Medium, or High). Defaults to Medium.
#     """
#     # Validate task is not empty
#     if not validate_task(description):
#         print("Error: Task description cannot be empty or whitespace only.", file=sys.stderr)
#         sys.exit(1)

#     # Validate priority
#     if priority not in "VALID_PRIORITIES":
#         print(f"Error: Invalid priority '{priority}'. Must be one of: {', '.join('VALID_PRIORITIES')}", file=sys.stderr)
#         sys.exit(1)

#     tasks = taskload()
#     tasks.append({"description": description, "completed": False})
#     tasksave(tasks)
#     print(f"Added task #{len(tasks)}: {description.strip()} [Priority: {priority}]")


# def cmd_list() -> None:
#     """
#     List all tasks, using a dark-mode friendly format if enabled.
#     """
#     config = load_config()
#     dark_mode = config.get("dark_mode", False)
#     tasks = taskload()

#     if not tasks:
#         print("No tasks.")
#         return

#     # Define display characters based on the mode
#     pending_char = "○" if dark_mode else "[ ]"
#     completed_char = "●" if dark_mode else "[x]"

#     pending = [(i, t) for i, t in enumerate(tasks, start=1) if not t.get("completed", False)]
#     completed = [(i, t) for i, t in enumerate(tasks, start=1) if t.get("completed", False)]

#     if pending:
#         print("Pending tasks:")
#         for i, t in pending:
#             print(f"  {pending_char} {i}. {t['description']}")
#     else:
#         print("No pending tasks.")

#     if completed:
#         print("\nCompleted tasks:")
#         for i, t in completed:
#             print(f"  {completed_char} {i}. {t['description']} (completed)")


# def cmd_remove(index: int) -> None:
#     """
#     Remove a task by its index (1-based).

#     Args:
#         index: The 1-based index of the task to remove.
#     """
#     tasks = taskload()
#     if not tasks:
#         print("No tasks to remove.")
#         sys.exit(0)
#     if index < 1 or index > len(tasks):
#         print(f"Invalid index: {index}. Must be between 1 and {len(tasks)}.")
#         sys.exit(2)
#     removed = tasks.pop(index - 1)
#     removed_text = removed.get("task", str(removed))
#     removed_priority = removed.get("priority", "")
#     tasksave(tasks)
#     desc = removed["description"] if isinstance(removed, dict) else str(removed)
#     print(f"Removed task #{index}: {desc}")


# def cmd_complete(index: int) -> None:
#     tasks = taskload()
#     if not tasks:
#         print("No tasks to complete.")
#         sys.exit(0)
#     if index < 1 or index > len(tasks):
#         print(f"Invalid index: {index}. Must be between 1 and {len(tasks)}.")
#         sys.exit(2)
#     task = tasks[index - 1]
#     if task.get("completed", False):
#         print(f"Task #{index} is already completed: {task['description']}")
#         return
#     task["completed"] = True
#     tasksave(tasks)
#     print(f"Marked task #{index} as completed: {task['description']}")

# def cmd_settings(dark_mode: str | None) -> None:
#     """Update user preferences."""
#     if dark_mode is None:
#         # Show current settings if no flag is provided
#         config = load_config()
#         status = "on" if config.get("dark_mode", False) else "off"
#         print(f"Current settings:\n- Dark Mode: {status}")
#         return

#     config = load_config()
#     new_status = dark_mode.lower() == 'on'
#     config['dark_mode'] = new_status
#     save_config(config)
#     status_text = "enabled" if new_status else "disabled"
#     print(f"Dark mode has been {status_text}.")

# def build_parser() -> argparse.ArgumentParser:
#     """
#     Build and configure the argument parser for CLI commands.

#     Returns:
#         Configured ArgumentParser instance.
#     """
#     parser = argparse.ArgumentParser(prog="todo.py", description="Simple CLI todo app in python")
#     sub = parser.add_subparsers(dest="cmd", required=True)

#     p_add = sub.add_parser("add", help="Add a task to the list")
#     p_add.add_argument("description", help="Task description")
#     p_add.add_argument(
#         "--priority",
#         "-p",
#         choices="VALID_PRIORITIES",
#         default="DEFAULT_PRIORITY",
#         help=f"Task priority (default: {'DEFAULT_PRIORITY'})"
#     )

#     p_list = sub.add_parser("list", help="List all tasks sorted by priority")

#     p_remove = sub.add_parser("remove", help="Remove a task by its index (1-based)")
#     p_remove.add_argument("index", type=int, help="Enter task index to remove")

#     p_complete = sub.add_parser("complete", help="Mark a task as completed by its index (1-based)")
#     p_complete.add_argument("index", type=int, help="Enter task index to mark complete")

#     p_settings = sub.add_parser("settings", help="Configure user preferences")
#     p_settings.add_argument(
#         "--dark-mode",
#         choices=['on', 'off'],
#         help="Enable or disable dark mode ('on' or 'off')"
#     )

#     return parser


# def main(argv: List[str] | None = None) -> None:
#     """
#     Main entry point for the CLI application.

#     Args:
#         argv: Command-line arguments (uses sys.argv if None).
#     """
#     parser = build_parser()
#     args = parser.parse_args(argv)

#     if args.cmd == "add":
#         cmd_add(args.description, args.priority)
#     elif args.cmd == "list":
#         cmd_list()
#     elif args.cmd == "remove":
#         cmd_remove(args.index)
#     elif args.cmd == "complete":
#         cmd_complete(args.index)
#     elif args.cmd == "stats":
#         show_stats()
#     elif args.cmd == "settings":
#         cmd_settings(args.dark_mode)


# if __name__ == "__main__":
#     if validate():
#         main()







#!/usr/bin/env python3
#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
import sys
import tempfile
import re
from pathlib import Path
from typing import List, Dict, Any
from collections import Counter
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
import speech_recognition as sr
from auth import validate

console = Console()

VALID_PRIORITIES = ["Low", "Medium", "High"]
DEFAULT_PRIORITY = "Medium"

# Default tasks file (next to this script). Can be overridden with TODO_FILE env var.
TASKS_FILE = Path(os.getenv("TODO_FILE", Path(__file__).with_name("tasks.json")))

# File for user settings
CONFIG_FILE = Path(os.getenv("TODO_CONFIG_FILE", Path(__file__).with_name("config.json")))

# --- Settings Management ---
def load_config() -> Dict[str, Any]:
    """Load user settings from the config file."""
    if not CONFIG_FILE.exists():
        return {"dark_mode": False}  # Default settings
    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # If config is corrupt or unreadable, return defaults
        return {"dark_mode": False}


def save_config(config: Dict[str, Any]) -> None:
    """Save user settings to the config file."""
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with CONFIG_FILE.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except IOError as e:
        console.print(f"Error: Could not save settings to {CONFIG_FILE}: {e}", style="red")
        sys.exit(1)

def _normalize_tasks(data: Any) -> List[Dict[str, Any]]:
    """Normalize raw JSON data into a list of task dicts."""
    normalized: List[Dict[str, Any]] = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):  # Legacy task format: simple string
                normalized.append({"description": item, "completed": False, "priority": DEFAULT_PRIORITY, "tags": []})
            elif isinstance(item, dict):  # New task format
                desc = item.get("description")
                if isinstance(desc, str):
                    normalized.append({
                        "description": desc,
                        "completed": bool(item.get("completed", False)),
                        "priority": item.get("priority", DEFAULT_PRIORITY),
                        "tags": item.get("tags", []),
                    })
            # ignore other types silently
    return normalized


def taskload() -> List[Dict[str, Any]]:
    if not TASKS_FILE.exists():
        return []

    try:
        with TASKS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        tasks = _normalize_tasks(data)
        # If file was legacy format, persist normalized structure
        if isinstance(data, list) and tasks and not isinstance(data[0], dict):
            tasksave(tasks)
        return tasks
    except json.JSONDecodeError:
        backupcorrupt("json-decode-error")
        return []
    except Exception as e:
        console.print(f"Error reading tasks file: {e}", style="red")
        return []


def backupcorrupt(reason: str) -> None:
    """
    Backup a corrupted tasks file before resetting.

    Args:
        reason: Description of why the file is being backed up.
    """
    try:
        if TASKS_FILE.exists():
            backup_name = TASKS_FILE.with_suffix(f".backup.{reason}")
            TASKS_FILE.replace(backup_name)
            console.print(f"Backed up corrupted tasks file to: {backup_name}", style="yellow")
    except Exception as e:
        console.print(f"Failed to back up corrupted tasks file: {e}", style="red")


def tasksave(tasks: List[Dict[str, Any]]) -> None:
    """
    Save tasks to the JSON file.
    """
    TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(tasks, ensure_ascii=False, indent=2)

    try:
        fd, tmp_path = tempfile.mkstemp(prefix=".tasks-", dir=str(TASKS_FILE.parent))
    except (PermissionError, OSError) as e:
        console.print(f"Error: Cannot create temporary file: {e}", style="red")
        sys.exit(1)

    try:
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmpf:
                tmpf.write(data)
                tmpf.flush()
                os.fsync(tmpf.fileno())
        except (IOError, OSError) as e:
            console.print(f"Error: Cannot write to temporary file: {e}", style="red")
            sys.exit(1)

        try:
            Path(tmp_path).replace(TASKS_FILE)
        except (PermissionError, OSError) as e:
            console.print(f"Error: Cannot save tasks file: {e}", style="red")
            sys.exit(1)
    finally:
        # Clean up temporary file if it still exists
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

def validate_task(description: str) -> bool:
    """
    Validate that a task description is not empty or whitespace-only.

    Args:
        description: The task description to validate.

    Returns:
        True if valid, False otherwise.
    """
    return description and description.strip()

def cmd_add(description: str, priority: str = DEFAULT_PRIORITY, tags: List[str] = None, completed: bool = False) -> None:
    if tags is None:
        tags = []

    # Validate task is not empty
    if not validate_task(description):
        console.print("Error: Task description cannot be empty or whitespace only.", style="red")
        return

    # Validate priority
    if priority not in VALID_PRIORITIES:
        console.print(f"Error: Invalid priority '{priority}'. Must be one of: {', '.join(VALID_PRIORITIES)}", style="red")
        return

    tasks = taskload()
    new_task = {
        "description": description.strip(),
        "priority": priority,
        "tags": tags,
        "completed": completed,
    }
    tasks.append(new_task)
    tasksave(tasks)
    tag_str = ', '.join(tags) if tags else 'None'
    console.print(f"Added task #{len(tasks)}: [bold cyan]{description.strip()}[/bold cyan] [Priority: {priority}] [Tags: {tag_str}]")

def cmd_list() -> None:
    tasks = taskload()

    if not tasks:
        console.print("No tasks.", style="italic")
        return

    priority_order = {"High": 0, "Medium": 1, "Low": 2}

    pending = [(i+1, t) for i, t in enumerate(tasks) if not t.get("completed", False)]
    completed = [(i+1, t) for i, t in enumerate(tasks) if t.get("completed", False)]

    # Sort pending by priority
    pending.sort(key=lambda x: priority_order.get(x[1].get("priority", DEFAULT_PRIORITY), 1))

    if pending:
        console.print("\nPending tasks:", style="bold blue")
        for idx, t in pending:
            pri = t.get("priority", DEFAULT_PRIORITY)
            console.print(f"  ○ {idx}. [bold cyan]{t['description']}[/bold cyan] [dim]({pri})[/dim]")
    else:
        console.print("No pending tasks.", style="green")

    if completed:
        console.print("\nCompleted tasks:", style="bold green")
        for idx, t in completed:
            console.print(f"  ● {idx}. [strikethrough dim]{t['description']}[/strikethrough dim]")

def cmd_remove(index: int) -> None:
    tasks = taskload()
    if not tasks:
        console.print("No tasks to remove.")
        return
    if index < 1 or index > len(tasks):
        console.print(f"Invalid index: {index}. Must be between 1 and {len(tasks)}.", style="red")
        return
    removed = tasks.pop(index - 1)
    tasksave(tasks)
    console.print(f"Removed task #{index}: [bold red]{removed['description']}[/bold red]")

def cmd_complete(index: int) -> None:
    tasks = taskload()
    if not tasks:
        console.print("No tasks to complete.")
        return
    if index < 1 or index > len(tasks):
        console.print(f"Invalid index: {index}. Must be between 1 and {len(tasks)}.", style="red")
        return
    task = tasks[index - 1]
    if task.get("completed", False):
        console.print(f"Task #{index} is already completed: [yellow]{task['description']}[/yellow]")
        return
    task["completed"] = True
    tasksave(tasks)
    console.print(f"Marked task #{index} as completed: [bold green]{task['description']}[/bold green]")

def cmd_settings(dark_mode: str | None) -> None:
    """Update user preferences."""
    if dark_mode is None:
        # Show current settings if no flag is provided
        config = load_config()
        status = "on" if config.get("dark_mode", False) else "off"
        console.print(f"Current settings:\n- Dark Mode: {status}")
        return

    config = load_config()
    new_status = dark_mode.lower() == 'on'
    config['dark_mode'] = new_status
    save_config(config)
    status_text = "enabled" if new_status else "disabled"
    console.print(f"Dark mode has been {status_text}.")

def show_stats():
    tasks = taskload()
    if not tasks:
        console.print("No tasks to analyze.")
        return

    # Completion Rate
    completed = sum(1 for task in tasks if task.get("completed", False))
    total = len(tasks)
    completion_percent = (completed / total) * 100 if total else 0

    # Priority Breakdown
    priority_counts = Counter(task.get("priority", DEFAULT_PRIORITY) for task in tasks)

    # Tags Breakdown
    tag_counts = Counter(tag for task in tasks for tag in task.get("tags", []))

    # Display
    console.rule("[bold green]Task Analytics Dashboard")
    console.print(f"\n[bold]Completion:[/bold] {completed}/{total} tasks completed ({completion_percent:.2f}%)")

    # Priority Table
    table = Table(title="Priority Breakdown")
    table.add_column("Priority", justify="left", style="cyan")
    table.add_column("Count", justify="right", style="magenta")
    for priority, count in priority_counts.items():
        table.add_row(priority, str(count))
    console.print(table)

    # Tag Table
    if tag_counts:
        tag_table = Table(title="Most Used Tags")
        tag_table.add_column("Tag", style="green")
        tag_table.add_column("Count", justify="right", style="yellow")
        for tag, count in tag_counts.most_common(10):
            tag_table.add_row(tag, str(count))
        console.print(tag_table)
    else:
        console.print("No tags found.")

    console.rule()

def cmd_voice() -> None:
    """Voice command mode for hands-free interaction."""
    r = sr.Recognizer()
    try:
        m = sr.Microphone()
    except Exception as e:
        console.print(f"No microphone found: {e}", style="red")
        return

    try:
        with m as source:
            r.adjust_for_ambient_noise(source, duration=1)
    except Exception as e:
        pass  # Continue anyway

    console.print("Voice mode activated. Speak your commands clearly. Say 'exit' to quit.")
    console.print("Supported: 'add task <description>', 'list tasks', 'remove task <number>'")
    console.print("Tip: Press Ctrl+C to force quit if needed.", style="italic")

    while True:
        try:
            with m as source:
                console.print("Listening... (5s timeout)", style="dim")
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
            console.print("Processing speech...", style="dim")

        except sr.WaitTimeoutError:
            console.print("No speech detected within 5 seconds. Listening again...", style="yellow")
            continue
        except Exception as e:
            console.print(f"Error during listening: {e}", style="red")
            console.print("Retrying in a moment...", style="dim")
            continue

        if audio is None:
            continue

        try:
            text = r.recognize_google(audio).lower()
            console.print(f"You said: [italic]{text}[/italic]")

            if "exit" in text or "quit" in text:
                console.print("Exiting voice mode.", style="bold")
                break

            elif "add task" in text:
                desc_start = text.find("add task") + len("add task")
                desc = text[desc_start:].strip()
                if not desc:
                    console.print("Please provide a task description after 'add task'.", style="yellow")
                    continue
                cmd_add(desc, priority=DEFAULT_PRIORITY, tags=[], completed=False)

            elif "list tasks" in text or "show tasks" in text:
                cmd_list()

            elif "remove task" in text:
                num_start = text.find("remove task") + len("remove task")
                num_str = text[num_start:].strip()
                num_match = re.search(r'\d+', num_str)
                if num_match:
                    index = int(num_match.group())
                    cmd_remove(index)
                else:
                    console.print("Please specify a valid task number after 'remove task'.", style="yellow")

            else:
                console.print("Command not recognized. Try 'add task <description>', 'list tasks', 'remove task <number>', or 'exit'.", style="yellow")

        except sr.UnknownValueError:
            console.print("Sorry, could not understand the audio. Please speak clearly and try again.", style="yellow")
            continue
        except sr.RequestError as e:
            console.print(f"Speech recognition service error: {e}", style="red")
            console.print("Check your internet connection and try again.", style="yellow")
            continue
        except KeyboardInterrupt:
            console.print("\nInterrupted by user (Ctrl+C). Exiting voice mode.", style="bold yellow")
            break
        except Exception as e:
            console.print(f"Unexpected error in voice processing: {e}", style="red")
            continue

    console.print("Voice mode ended.", style="bold")

def build_parser() -> argparse.ArgumentParser:
    """
    Build and configure the argument parser for CLI commands.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(prog="todo.py", description="Simple CLI todo app in python")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="Add a task to the list")
    p_add.add_argument("description", help="Task description")
    p_add.add_argument(
        "--priority",
        "-p",
        choices=VALID_PRIORITIES,
        default=DEFAULT_PRIORITY,
        help=f"Task priority (default: {DEFAULT_PRIORITY})"
    )
    p_add.add_argument(
        "--tags",
        "-t",
        nargs="*",
        default=[],
        help="Tags associated with the task"
    )
    p_add.add_argument(
        "--completed",
        "-c",
        action="store_true",
        help="Mark task as completed"
    )

    p_list = sub.add_parser("list", help="List all tasks sorted by priority")

    p_remove = sub.add_parser("remove", help="Remove a task by its index (1-based)")
    p_remove.add_argument("index", type=int, help="Enter task index to remove")

    p_complete = sub.add_parser("complete", help="Mark a task as completed by its index (1-based)")
    p_complete.add_argument("index", type=int, help="Enter task index to mark complete")

    p_stats = sub.add_parser("stats", help="Display task analytics (completion rate, priority, tags)")

    p_settings = sub.add_parser("settings", help="Configure user preferences")
    p_settings.add_argument(
        "--dark-mode",
        choices=['on', 'off'],
        help="Enable or disable dark mode ('on' or 'off')"
    )

    p_voice = sub.add_parser("voice", help="Activate voice command mode for hands-free interaction")

    return parser


def main(argv: List[str] | None = None) -> None:
    """
    Main entry point for the CLI application.

    Args:
        argv: Command-line arguments (uses sys.argv if None).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "add":
        cmd_add(args.description, args.priority, args.tags, args.completed)
    elif args.cmd == "list":
        cmd_list()
    elif args.cmd == "remove":
        cmd_remove(args.index)
    elif args.cmd == "complete":
        cmd_complete(args.index)
    elif args.cmd == "stats":
        show_stats()
    elif args.cmd == "settings":
        cmd_settings(args.dark_mode)
    elif args.cmd == "voice":
        cmd_voice()


if __name__ == "__main__":
    if validate():
        main()