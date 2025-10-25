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
"""
CLI Todo App - Complete Implementation with All Features
Includes: Task management, priorities, tags, voice commands, analytics, and more
"""

import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from collections import Counter
from .i18n import set_language, t

# Try to import optional dependencies
try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, BarColumn, TextColumn
    from rich.panel import Panel
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: 'rich' library not found. Install with: pip install rich")

try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

# Colors for terminal output (fallback when rich not available)
class Colors:
    RESET = '\033[0m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    GRAY = '\033[90m'
    RED = '\033[31m'
    BOLD = '\033[1m'
    STRIKETHROUGH = '\033[9m'

# File paths
BASE_DIR = Path(__file__).parent
TASKS_FILE = Path(os.environ.get('TODO_FILE', BASE_DIR / 'tasks.json'))
CONFIG_FILE = Path(os.environ.get('TODO_CONFIG_FILE', BASE_DIR / 'config.json'))

# Default settings
DEFAULT_SETTINGS = {
    'username': '',
    'require_auth': True,
    'dark_mode': False
}

def load_settings():
    """Load user settings from config file."""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return {**DEFAULT_SETTINGS, **json.load(f)}
        return DEFAULT_SETTINGS.copy()
    except:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Save user settings to config file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"{Colors.RED}Error saving settings: {e}{Colors.RESET}")

def validate_user():
    """Validate username for authentication."""
    settings = load_settings()
    
    if not settings.get('require_auth', True):
        return True
    
    if settings.get('username'):
        print(f"{Colors.CYAN}{t('py_validating')}{Colors.RESET}")
        username = input(f"{t('py_enter_username')}")
        if username == settings['username']:
            return True
        else:
            print(f"{Colors.RED}{t('py_error_invalid_username')}{Colors.RESET}")
            return False
    else:
        # First time setup
        print(f"{Colors.CYAN}============First Time Setup============{Colors.RESET}")
        username = input(f"Create a username: ")
        if username.strip():
            settings['username'] = username.strip()
            save_settings(settings)
            print(f"{Colors.GREEN}✓ Username set successfully!{Colors.RESET}")
            return True
        else:
            print(f"{Colors.RED}Username cannot be empty!{Colors.RESET}")
            return False

def backup_file(filepath):
    """Create a backup of a file."""
    try:
        backup_path = filepath.with_suffix('.json.backup')
        if filepath.exists():
            with open(filepath, 'r') as f:
                content = f.read()
            with open(backup_path, 'w') as f:
                f.write(content)
            print(f"{Colors.YELLOW}Backup created: {backup_path}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}Error creating backup: {e}{Colors.RESET}")

def load_tasks():
    """Load tasks from JSON file with error handling and backward compatibility."""
    try:
        if not TASKS_FILE.exists():
            return []
        
        with open(TASKS_FILE, 'r') as f:
            tasks = json.load(f)
        
        # Ensure backward compatibility
        normalized_tasks = []
        for task in tasks:
            if isinstance(task, str):
                normalized_tasks.append({
                    'id': len(normalized_tasks),
                    'task': task,
                    'priority': 'Medium',
                    'completed': False,
                    'tags': [],
                    'created_at': datetime.now().isoformat()
                })
            else:
                if 'id' not in task:
                    task['id'] = len(normalized_tasks)
                if 'completed' not in task:
                    task['completed'] = False
                if 'priority' not in task:
                    task['priority'] = 'Medium'
                if 'tags' not in task:
                    task['tags'] = []
                if 'created_at' not in task:
                    task['created_at'] = datetime.now().isoformat()
                if 'depends_on' not in task:
                    task['depends-on'] = []
                normalized_tasks.append(task)
        
        return normalized_tasks
    
    except json.JSONDecodeError:
        print(f"{Colors.YELLOW}Warning: Corrupted tasks file detected!{Colors.RESET}")
        backup_file(TASKS_FILE)
        print(f"{Colors.YELLOW}Starting with empty task list.{Colors.RESET}")
        return []
    except Exception as e:
        print(f"{Colors.RED}Error loading tasks: {e}{Colors.RESET}")
        return []

def save_tasks(tasks):
    """Save tasks to JSON file with error handling."""
    try:
        # Reindex tasks
        for i, task in enumerate(tasks):
            task['id'] = i
        
        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks, f, indent=2)
    except PermissionError:
        print(f"{Colors.RED}Error: Permission denied. Cannot write to {TASKS_FILE}{Colors.RESET}")
    except OSError as e:
        print(f"{Colors.RED}Error: Disk I/O error - {e}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}Error saving tasks: {e}{Colors.RESET}")

def check_for_cycle(tasks, start_index, target_index):
    if start_index == target_index:
        return True 
        
    stack = [target_index]
    visited = set()
    
    while stack:
        current_index = stack.pop()
        
        if current_index == start_index:
            return True 
        
        if current_index in visited:
            continue
            
        visited.add(current_index)
        
        prerequisites = tasks[current_index].get('depends_on', [])
        
        for prereq_index in prerequisites:
            # Only push valid indices onto the stack
            if 0 <= prereq_index < len(tasks):
                stack.append(prereq_index)
                
    return False

def add_dependency(task_id: int, prerequisite_id: int):
    """Adds a dependency: task_id depends on prerequisite_id (1-based indices)."""
    tasks = load_tasks()
    
    task_idx = task_id - 1
    prereq_idx = prerequisite_id - 1
    
    # Validation and bounds check
    if not (0 <= task_idx < len(tasks) and 0 <= prereq_idx < len(tasks)):
        print(f"{Colors.YELLOW}Error: One or both task IDs are invalid. Use 'list' to see available IDs.{Colors.RESET}")
        return

    task = tasks[task_idx]
    prereq = tasks[prereq_idx]

    # Cyclic Dependency Check
    if check_for_cycle(tasks, task_idx, prereq_idx):
        print(f"{Colors.RED}🛑 Error: Adding '{task['task']}' dependency on '{prereq['task']}' creates a circular dependency!{Colors.RESET}")
        return

    # Add Dependency
    if prereq_idx not in task.get('depends_on', []):
        task['depends_on'].append(prereq_idx)
        save_tasks(tasks)
        print(f"{Colors.GREEN}✓ Success:{Colors.RESET} Task {task_id} ('{task['task']}') now depends on Task {prerequisite_id} ('{prereq['task']}').")
    else:
        print(f"{Colors.YELLOW}Warning:{Colors.RESET} Dependency already exists.")

def remove_dependency(task_id: int, prerequisite_id: int):
    #Removes a dependency:
    tasks = load_tasks()
    
    task_idx = task_id - 1
    prereq_idx = prerequisite_id - 1
    
    if not (0 <= task_idx < len(tasks) and 0 <= prereq_idx < len(tasks)):
        print(f"{Colors.YELLOW}Error: One or both task IDs are invalid. Use 'list' to see available IDs.{Colors.RESET}")
        return

    task = tasks[task_idx]
    
    if prereq_idx in task.get('depends_on', []):
        task['depends_on'].remove(prereq_idx)
        save_tasks(tasks)
        print(f"{Colors.GREEN}Success:{Colors.RESET} Removed dependency: Task {task_id} no longer depends on Task {prerequisite_id}.")
    else:
        print(f"{Colors.YELLOW}Warning:{Colors.RESET} Task {task_id} does not depend on Task {prerequisite_id}.")

def calculate_progress(tasks):
    """Calculate completion statistics."""
    if not tasks:
        return {'completed': 0, 'total': 0, 'percentage': 0}
    
    completed = sum(1 for task in tasks if task.get('completed', False))
    total = len(tasks)
    percentage = round((completed / total) * 100, 2) if total > 0 else 0
    
    return {
        'completed': completed,
        'total': total,
        'percentage': percentage
    }

def create_progress_bar(percentage, width=30):
    """Create a visual progress bar."""
    filled_length = round((width * percentage) / 100)
    empty_length = width - filled_length
    
    filled = '█' * filled_length
    empty = '░' * empty_length
    
    return f"{Colors.GREEN}{filled}{Colors.GRAY}{empty}{Colors.RESET}"

def display_progress_bar(tasks):
    """Display the progress bar with statistics."""
    stats = calculate_progress(tasks)
    progress_bar = create_progress_bar(stats['percentage'])
    
    print(f"\n{Colors.CYAN}{Colors.BOLD}Progress:{Colors.RESET} {progress_bar} "
          f"{Colors.GREEN}{stats['percentage']}%{Colors.RESET} "
          f"{Colors.GRAY}({stats['completed']}/{stats['total']} completed){Colors.RESET}\n")

def add_task(description, priority='Medium', tags=None, completed=False):
    """Add a new task with priority, tags, and completion status."""
    if not description or description.isspace():
        print(f"{Colors.YELLOW}Error: Task description cannot be empty{Colors.RESET}")
        return
    
    if priority not in ['High', 'Medium', 'Low']:
        print(f"{Colors.YELLOW}Error: Invalid priority. Use High, Medium, or Low{Colors.RESET}")
        return
    
    tasks = load_tasks()
    new_task = {
        'id': len(tasks),
        'task': description.strip(),
        'priority': priority,
        'completed': completed,
        'tags': tags if tags else [],
        'created_at': datetime.now().isoformat()
    }
    tasks.append(new_task)
    
    # Sort by priority and completion status
    priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
    tasks.sort(key=lambda x: (x.get('completed', False), priority_order.get(x.get('priority', 'Medium'), 1)))
    
    save_tasks(tasks)
    
    tags_str = f" {Colors.CYAN}[{', '.join(tags)}]{Colors.RESET}" if tags else ""
    status_str = f" {Colors.GREEN}[✓ Completed]{Colors.RESET}" if completed else ""
    print(f"{Colors.GREEN}✓{Colors.RESET} Added: \"{description.strip()}\" {Colors.BLUE}[{priority}]{Colors.RESET}{tags_str}{status_str}")
    display_progress_bar(tasks)

def list_tasks():
    """List all tasks with rich formatting if available."""
    tasks = load_tasks()
    
    if not tasks:
        print(f"{Colors.YELLOW}No tasks found.{Colors.RESET} Add one with: {Colors.CYAN}python todo.py add \"Your task\"{Colors.RESET}")
        return
    
    display_progress_bar(tasks)
    
    # Separate pending and completed tasks
    pending_tasks = [t for t in tasks if not t.get('completed', False)]
    completed_tasks = [t for t in tasks if t.get('completed', False)]
    
    # Display pending tasks
    if pending_tasks:
        print(f"{Colors.CYAN}{Colors.BOLD}Pending tasks:{Colors.RESET}")
        for task in pending_tasks:
            display_task(task, '○')
        print()
    
    # Display completed tasks
    if completed_tasks:
        print(f"{Colors.GREEN}{Colors.BOLD}Completed tasks:{Colors.RESET}")
        for task in completed_tasks:
            display_task(task, '●')
        print()

def display_task(task, checkbox):
    """Display a single task with formatting."""
    task_id = task.get('id', 0)
    priority = task.get('priority', 'Medium')
    completed = task.get('completed', False)
    tags = task.get('tags', [])
    
    # Priority colors
    priority_colors = {
        'High': Colors.RED,
        'Medium': Colors.BLUE,
        'Low': Colors.GRAY
    }
    priority_color = priority_colors.get(priority, Colors.RESET)
    
    # Task text styling
    task_text = task['task']
    if completed:
        task_text = f"{Colors.GRAY}{Colors.STRIKETHROUGH}{task_text}{Colors.RESET}"
    
    # Tags display
    tags_str = ""
    if tags:
        tags_str = f" {Colors.CYAN}[{', '.join(tags)}]{Colors.RESET}"

    # Dependency Indicator 
    dependency_str = ""
    # Check if this task has incomplete prerequisites
    if not task.get('completed', False):
        incomplete_count = 0
        tasks = load_tasks() #relaod tasks
        for prereq_idx in task.get('depends_on', []):
            if 0 <= prereq_idx < len(tasks) and not tasks[prereq_idx].get('completed', False):
                incomplete_count += 1
        
        if incomplete_count > 0:
            dependency_str = f" {Colors.RED}🔗 ({incomplete_count} blocked){Colors.RESET}"
        elif task.get('depends_on'):
             dependency_str = f" {Colors.GREEN}🔗{Colors.RESET}"
    
    print(f"  {Colors.YELLOW}{checkbox}{Colors.RESET} {Colors.CYAN}{task_id + 1}.{Colors.RESET} {task_text} {priority_color}({priority}){Colors.RESET}{tags_str}")

def remove_task(task_id):
    """Remove a task by ID (1-based index)."""
    tasks = load_tasks()
    
    if not tasks:
        print(f"{Colors.YELLOW}{t('py_no_tasks_to_remove')}{Colors.RESET}")
        return
    
    # Convert to 0-based index
    index = task_id - 1
    
    if 0 <= index < len(tasks):
        task_to_remove = tasks.pop(index)
        save_tasks(tasks)
        print(f"{Colors.GREEN}✓{Colors.RESET}{t('py_removed_success', {'task_name': task_to_remove['task']})}")
        if tasks:
            display_progress_bar(tasks)
    else:
        print(f"{Colors.YELLOW}{t('py_error_task_not_found', {'task_id': task_id})}{Colors.RESET}")

def complete_task(task_id):
    """Toggle task completion status (1-based index)."""
    tasks = load_tasks()
    
    if not tasks:
        print(f"{Colors.YELLOW}No tasks available{Colors.RESET}")
        return
    
    # Convert to 0-based index
    index = task_id - 1
    
    if 0 <= index < len(tasks):
        task = tasks[index]

        #dependency check logic
        if not task.get('completed', False): # Only check dependencies if user is trying to COMPLETE the task
            incomplete_prereqs = []
            
            # Check each prerequisite stored as a 0-based index
            for prereq_idx in task.get('depends_on', []):
                # Ensure the prerequisite index is valid and the task is incomplete
                if 0 <= prereq_idx < len(tasks) and not tasks[prereq_idx].get('completed', False):
                    incomplete_prereqs.append({
                        'id': prereq_idx + 1,
                        'task': tasks[prereq_idx]['task']
                    })

            if incomplete_prereqs:
                print(f"{Colors.RED}{Colors.BOLD}WARNING: Cannot complete Task {task_id}!{Colors.RESET}")
                print(f"{Colors.YELLOW}The following prerequisite tasks are still pending:{Colors.RESET}")
                for prereq in incomplete_prereqs:
                    print(f"  - [{Colors.CYAN}{prereq['id']}{Colors.RESET}] {prereq['task']}")
                return 

        task['completed'] = not task.get('completed', False)
        status = "completed" if task['completed'] else "incomplete"
        icon = "✓" if task['completed'] else "○"
        print(f"{Colors.GREEN}{icon}{Colors.RESET} Marked task {task_id} as {Colors.BOLD}{status}{Colors.RESET}: \"{task['task']}\"")
        save_tasks(tasks)
        display_progress_bar(tasks)
    else:
        print(f"{Colors.YELLOW}Error: Task ID {task_id} not found. Use 'list' to see available tasks.{Colors.RESET}")

def show_stats():
    """Display detailed statistics with rich formatting if available."""
    tasks = load_tasks()
    
    if not tasks:
        print(f"{Colors.YELLOW}No tasks found. Add some tasks to see statistics!{Colors.RESET}")
        return
    
    stats = calculate_progress(tasks)
    pending = stats['total'] - stats['completed']
    
    # Count by priority
    priority_counts = Counter(t.get('priority', 'Medium') for t in tasks if not t.get('completed'))
    
    # Count by tags
    all_tags = []
    for task in tasks:
        all_tags.extend(task.get('tags', []))
    tag_counts = Counter(all_tags)
    
    if RICH_AVAILABLE:
        console = Console()
        console.print("\n[cyan bold]════════════════════ Task Analytics Dashboard ════════════════════[/cyan bold]\n")
        console.print(f"[green]Completion:[/green] {stats['completed']}/{stats['total']} tasks completed ({stats['percentage']}%)\n")
        
        # Priority table
        priority_table = Table(title="Priority Breakdown", show_header=True)
        priority_table.add_column("Priority", style="cyan")
        priority_table.add_column("Count", justify="right")
        
        for priority in ['High', 'Medium', 'Low']:
            count = priority_counts.get(priority, 0)
            priority_table.add_row(priority, str(count))
        
        console.print(priority_table)
        
        # Tags table
        if tag_counts:
            console.print()
            tag_table = Table(title="Tag Statistics", show_header=True)
            tag_table.add_column("Tag", style="cyan")
            tag_table.add_column("Count", justify="right")
            
            for tag, count in tag_counts.most_common(10):
                tag_table.add_row(tag, str(count))
            
            console.print(tag_table)
    else:
        print(f"\n{Colors.CYAN}{Colors.BOLD}📊 Task Analytics Dashboard{Colors.RESET}")
        print('═' * 60)
        
        display_progress_bar(tasks)
        
        print(f"{Colors.CYAN}Total Tasks:{Colors.RESET}        {stats['total']}")
        print(f"{Colors.GREEN}✓ Completed:{Colors.RESET}        {stats['completed']} {Colors.GRAY}({stats['percentage']}%){Colors.RESET}")
        print(f"{Colors.YELLOW}○ Pending:{Colors.RESET}          {pending} {Colors.GRAY}({100 - stats['percentage']}%){Colors.RESET}")
        print()
        print(f"{Colors.BOLD}Pending by Priority:{Colors.RESET}")
        print(f"  {Colors.RED}High:{Colors.RESET}     {priority_counts.get('High', 0)}")
        print(f"  {Colors.BLUE}Medium:{Colors.RESET}   {priority_counts.get('Medium', 0)}")
        print(f"  {Colors.GRAY}Low:{Colors.RESET}      {priority_counts.get('Low', 0)}")
        
        if tag_counts:
            print()
            print(f"{Colors.BOLD}Tag Statistics:{Colors.RESET}")
            for tag, count in tag_counts.most_common(10):
                print(f"  {Colors.CYAN}{tag}:{Colors.RESET} {count}")
    
    if stats['completed'] == stats['total']:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 Congratulations! All tasks completed!{Colors.RESET}")
    elif stats['percentage'] >= 75:
        print(f"\n{Colors.GREEN}Great progress! Keep it up!{Colors.RESET}")
    elif stats['percentage'] >= 50:
        print(f"\n{Colors.BLUE}You're halfway there!{Colors.RESET}")
    elif stats['percentage'] >= 25:
        print(f"\n{Colors.YELLOW}Good start! Keep going!{Colors.RESET}")
    
    print('═' * 60 + '\n')

def manage_settings(dark_mode=None):
    """Manage application settings."""
    settings = load_settings()
    
    if dark_mode is not None:
        settings['dark_mode'] = dark_mode.lower() in ['on', 'true', '1', 'yes']
        save_settings(settings)
        status = "enabled" if settings['dark_mode'] else "disabled"
        print(f"{Colors.GREEN}✓ Dark mode {status}!{Colors.RESET}")
        return
    
    print(f"\n{Colors.CYAN}{Colors.BOLD}⚙️  Settings{Colors.RESET}")
    print('─' * 40)
    print(f"Username: {settings.get('username', 'Not set')}")
    print(f"Authentication: {'Enabled' if settings.get('require_auth') else 'Disabled'}")
    print(f"Dark Mode: {'Enabled' if settings.get('dark_mode') else 'Disabled'}")
    print('─' * 40)
    
    print("\nOptions:")
    print("1. Change username")
    print("2. Toggle authentication")
    print("3. Toggle dark mode")
    print("4. Back")
    
    choice = input(f"\n{Colors.CYAN}Select option:{Colors.RESET} ")
    
    if choice == '1':
        new_username = input("Enter new username: ")
        if new_username.strip():
            settings['username'] = new_username.strip()
            save_settings(settings)
            print(f"{Colors.GREEN}✓ Username updated!{Colors.RESET}")
    elif choice == '2':
        settings['require_auth'] = not settings.get('require_auth', True)
        save_settings(settings)
        status = "enabled" if settings['require_auth'] else "disabled"
        print(f"{Colors.GREEN}✓ Authentication {status}!{Colors.RESET}")
    elif choice == '3':
        settings['dark_mode'] = not settings.get('dark_mode', False)
        save_settings(settings)
        status = "enabled" if settings['dark_mode'] else "disabled"
        print(f"{Colors.GREEN}✓ Dark mode {status}!{Colors.RESET}")

def voice_command():
    """Voice command mode for hands-free interaction."""
    if not VOICE_AVAILABLE:
        print(f"{Colors.RED}Voice commands require SpeechRecognition library.{Colors.RESET}")
        print(f"{Colors.YELLOW}Install with: pip install SpeechRecognition pyaudio{Colors.RESET}")
        return
    
    recognizer = sr.Recognizer()
    
    print(f"\n{Colors.CYAN}{Colors.BOLD}🎤 Voice Command Mode{Colors.RESET}")
    print(f"{Colors.GRAY}Say 'exit' or 'quit' to stop{Colors.RESET}\n")
    
    while True:
        try:
            with sr.Microphone() as source:
                print(f"{Colors.YELLOW}Listening...{Colors.RESET}")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                print(f"{Colors.GRAY}Processing...{Colors.RESET}")
                command = recognizer.recognize_google(audio).lower()
                print(f"{Colors.CYAN}You said: {command}{Colors.RESET}\n")
                
                # Process commands
                if 'exit' in command or 'quit' in command:
                    print(f"{Colors.GREEN}Exiting voice mode...{Colors.RESET}")
                    break
                elif 'add task' in command or 'add' in command:
                    task_desc = command.replace('add task', '').replace('add', '').strip()
                    if task_desc:
                        add_task(task_desc)
                    else:
                        print(f"{Colors.YELLOW}Please specify a task to add{Colors.RESET}")
                elif 'list' in command or 'show' in command:
                    list_tasks()
                elif 'remove' in command:
                    try:
                        words = command.split()
                        task_id = int(words[-1])
                        remove_task(task_id)
                    except:
                        print(f"{Colors.YELLOW}Please specify a task ID to remove{Colors.RESET}")
                elif 'complete' in command:
                    try:
                        words = command.split()
                        task_id = int(words[-1])
                        complete_task(task_id)
                    except:
                        print(f"{Colors.YELLOW}Please specify a task ID to complete{Colors.RESET}")
                elif 'stats' in command or 'statistics' in command:
                    show_stats()
                else:
                    print(f"{Colors.YELLOW}Unknown command. Try: add task, list tasks, remove task #, complete task #{Colors.RESET}")
                
                print()
        
        except sr.WaitTimeoutError:
            print(f"{Colors.YELLOW}No speech detected. Try again...{Colors.RESET}\n")
        except sr.UnknownValueError:
            print(f"{Colors.YELLOW}Could not understand audio. Please speak clearly...{Colors.RESET}\n")
        except sr.RequestError as e:
            print(f"{Colors.RED}Error with speech recognition service: {e}{Colors.RESET}")
            print(f"{Colors.YELLOW}Check your internet connection{Colors.RESET}\n")
        except KeyboardInterrupt:
            print(f"\n{Colors.GREEN}Exiting voice mode...{Colors.RESET}")
            break
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}\n")

def main():
    """Main entry point."""
    # Check authentication
    if not validate_user():
        sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description='CLI Todo App with Progress Tracking, Tags, Voice Commands, and Analytics',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-l', '--lang',
        type=str,
        help='Set language (e.g., "en", "es", "hi")'
    )

    subparsers = parser.add_subparsers(dest='cmd', help='Available commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('description', type=str, nargs='+', help='Task description')
    add_parser.add_argument('-p', '--priority', 
                           choices=['High', 'Medium', 'Low'],
                           default='Medium',
                           help='Task priority (default: Medium)')
    add_parser.add_argument('-t', '--tags', 
                           nargs='*',
                           help='Tags for the task')
    add_parser.add_argument('--completed',
                           action='store_true',
                           help='Mark task as completed when adding')
    
    # List command
    subparsers.add_parser('list', help='List all tasks with progress bar')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove a task')
    remove_parser.add_argument('id', type=int, help='Task ID (1-based)')
    
    # Complete command
    complete_parser = subparsers.add_parser('complete', help='Toggle task completion')
    complete_parser.add_argument('id', type=int, help='Task ID (1-based)')

    #Depends command
    depends_parser = subparsers.add_parser('depends', help='Manage task dependencies')
    depends_subparsers = depends_parser.add_subparsers(dest='depends_cmd', help='Dependency sub-commands')
    
    # Depends Add command
    depends_add_parser = depends_subparsers.add_parser('add', help='Add a dependency: Task A depends on Task B')
    depends_add_parser.add_argument('task_id', type=int, help='ID of the task to receive the dependency (Task A)')
    depends_add_parser.add_argument('prerequisite_id', type=int, help='ID of the task it depends on (Task B)')

    # Depends Remove command 
    depends_remove_parser = depends_subparsers.add_parser('remove', help='Remove a dependency')
    depends_remove_parser.add_argument('task_id', type=int, help='ID of the task to modify')
    depends_remove_parser.add_argument('prerequisite_id', type=int, help='ID of the prerequisite to remove')

    # Stats command
    subparsers.add_parser('stats', help='Show task statistics and analytics')
    
    # Settings command
    settings_parser = subparsers.add_parser('settings', help='Manage settings')
    settings_parser.add_argument('--dark-mode',
                                choices=['on', 'off'],
                                help='Enable or disable dark mode')
    
    # Voice command
    subparsers.add_parser('voice', help='Voice command mode')
    
    args = parser.parse_args()

    lang = args.lang or os.getenv('TODO_LANG')
    set_language(lang)
    
    if args.cmd == 'add':
        description = ' '.join(args.description)
        add_task(description, args.priority, args.tags, args.completed)
    elif args.cmd == 'list':
        list_tasks()
    elif args.cmd == 'remove':
        remove_task(args.id)
    elif args.cmd == 'complete':
        complete_task(args.id)
    elif args.cmd == 'depands': 
        if args.depends_cmd == 'add':
            add_dependency(args.task_id, args.prerequisite_id)
        elif args.depends_cmd == 'remove':
            remove_dependency(args.task_id, args.prerequisite_id)
        else:
            depends_parser.print_help()
    elif args.cmd == 'stats':
        show_stats()
    elif args.cmd == 'settings':
        manage_settings(args.dark_mode)
    elif args.cmd == 'voice':
        voice_command()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()