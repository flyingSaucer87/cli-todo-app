#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import List, Dict, Any

# Default tasks file (next to this script). Can be overridden with TODO_FILE env var.
TASKS_FILE = Path(os.getenv("TODO_FILE", Path(__file__).with_name("tasks.json")))

# Priority levels
PRIORITY_HIGH = "High"
PRIORITY_MEDIUM = "Medium"
PRIORITY_LOW = "Low"
VALID_PRIORITIES = [PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH]
DEFAULT_PRIORITY = PRIORITY_MEDIUM

# Priority order for sorting (higher number = higher priority)
PRIORITY_ORDER = {
    PRIORITY_HIGH: 3,
    PRIORITY_MEDIUM: 2,
    PRIORITY_LOW: 1,
}


def taskload() -> List[Dict[str, str]]:
    """
    Load tasks from the JSON file.

    Returns:
        List of task dictionaries with 'task' and 'priority' keys.
        If file doesn't exist or is corrupted, returns empty list.
    """
    if not TASKS_FILE.exists():
        return []

    try:
        with TASKS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            # Migrate old format (list of strings) to new format (list of dicts)
            tasks = []
            for item in data:
                if isinstance(item, dict) and "task" in item:
                    # New format - ensure it has priority
                    task_dict = {
                        "task": str(item["task"]),
                        "priority": item.get("priority", DEFAULT_PRIORITY)
                    }
                    tasks.append(task_dict)
                elif isinstance(item, str):
                    # Old format - migrate to new format with default priority
                    tasks.append({
                        "task": str(item),
                        "priority": DEFAULT_PRIORITY
                    })
                else:
                    # Skip invalid items
                    continue
            return tasks
        else:
            # unexpected format
            backupcorrupt("not-a-list")
            return []
    except json.JSONDecodeError:
        backupcorrupt("json-decode-error")
        return []
    except Exception as e:
        print(f"Error reading tasks file: {e}", file=sys.stderr)
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
            print(f"Backed up corrupted tasks file to: {backup_name}", file=sys.stderr)
    except Exception as e:
        print(f"Failed to back up corrupted tasks file: {e}", file=sys.stderr)


def tasksave(tasks: List[Dict[str, str]]) -> None:
    """
    Save tasks to the JSON file atomically.

    Uses a temporary file and atomic rename to prevent data corruption.
    Handles permission errors and disk space issues gracefully.

    Args:
        tasks: List of task dictionaries to save.

    Raises:
        SystemExit: If file cannot be saved due to I/O errors.
    """
    try:
        TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError) as e:
        print(f"Error: Cannot create directory {TASKS_FILE.parent}: {e}", file=sys.stderr)
        sys.exit(1)

    data = json.dumps(tasks, ensure_ascii=False, indent=2)

    try:
        fd, tmp_path = tempfile.mkstemp(prefix=".tasks-", dir=str(TASKS_FILE.parent))
    except (PermissionError, OSError) as e:
        print(f"Error: Cannot create temporary file: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmpf:
                tmpf.write(data)
                tmpf.flush()
                os.fsync(tmpf.fileno())
        except (IOError, OSError) as e:
            print(f"Error: Cannot write to temporary file: {e}", file=sys.stderr)
            sys.exit(1)

        try:
            Path(tmp_path).replace(TASKS_FILE)
        except (PermissionError, OSError) as e:
            print(f"Error: Cannot save tasks file: {e}", file=sys.stderr)
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


def cmd_add(description: str, priority: str = DEFAULT_PRIORITY) -> None:
    """
    Add a new task with the given description and priority.

    Args:
        description: The task description.
        priority: Task priority (Low, Medium, or High). Defaults to Medium.
    """
    # Validate task is not empty
    if not validate_task(description):
        print("Error: Task description cannot be empty or whitespace only.", file=sys.stderr)
        sys.exit(1)

    # Validate priority
    if priority not in VALID_PRIORITIES:
        print(f"Error: Invalid priority '{priority}'. Must be one of: {', '.join(VALID_PRIORITIES)}", file=sys.stderr)
        sys.exit(1)

    tasks = taskload()
    new_task = {
        "task": description.strip(),
        "priority": priority
    }
    tasks.append(new_task)
    tasksave(tasks)
    print(f"Added task #{len(tasks)}: {description.strip()} [Priority: {priority}]")


def cmd_list() -> None:
    """
    List all tasks, sorted by priority (High -> Medium -> Low).
    """
    tasks = taskload()
    if not tasks:
        print("No tasks.")
        return

    # Sort tasks by priority (High first, then Medium, then Low)
    sorted_tasks = sorted(tasks, key=lambda t: PRIORITY_ORDER.get(t.get("priority", DEFAULT_PRIORITY), 0), reverse=True)

    for i, task_dict in enumerate(sorted_tasks, start=1):
        task_text = task_dict.get("task", "")
        priority = task_dict.get("priority", DEFAULT_PRIORITY)
        print(f"{i}. [{priority}] {task_text}")


def cmd_remove(index: int) -> None:
    """
    Remove a task by its index (1-based).

    Args:
        index: The 1-based index of the task to remove.
    """
    tasks = taskload()
    if not tasks:
        print("No tasks to remove.")
        sys.exit(0)
    if index < 1 or index > len(tasks):
        print(f"Invalid index: {index}. Must be between 1 and {len(tasks)}.")
        sys.exit(2)
    removed = tasks.pop(index - 1)
    removed_text = removed.get("task", str(removed))
    removed_priority = removed.get("priority", "")
    tasksave(tasks)
    print(f"Removed task #{index}: {removed_text} [Priority: {removed_priority}]")


def cmd_clear() -> None:
    """
    Clear all tasks from the list.
    """
    tasks = taskload()
    if not tasks:
        print("No tasks to clear.")
        return

    tasksave([])
    print(f"Cleared all {len(tasks)} task(s).")


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

    p_list = sub.add_parser("list", help="List all tasks sorted by priority")

    p_remove = sub.add_parser("remove", help="Remove a task by its index (1-based)")
    p_remove.add_argument("index", type=int, help="Enter task index to remove")

    p_clear = sub.add_parser("clear", help="Remove all tasks")

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
        cmd_add(args.description, args.priority)
    elif args.cmd == "list":
        cmd_list()
    elif args.cmd == "remove":
        cmd_remove(args.index)
    elif args.cmd == "clear":
        cmd_clear()


if __name__ == "__main__":
    main()
