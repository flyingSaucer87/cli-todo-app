#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import List
from auth import validate

# Default tasks file (next to this script). Can be overridden with TODO_FILE env var.
TASKS_FILE = Path(os.getenv("TODO_FILE", Path(__file__).with_name("tasks.json")))


def _normalize_tasks(data: Any) -> List[Dict[str, Any]]:
    """Normalize raw JSON data into a list of task dicts."""
    normalized: List[Dict[str, Any]] = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):  # Legacy task format: simple string
                normalized.append({"description": item, "completed": False, "priority": "Medium", "tags": []})
            elif isinstance(item, dict):  # New task format
                desc = item.get("description")
                if isinstance(desc, str):
                    normalized.append({
                        "description": desc,
                        "completed": bool(item.get("completed", False)),
                        "priority": item.get("priority", "Medium"),
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


def tasksave(tasks: List[Dict[str, Any]]) -> None:
    """
    Save tasks to the JSON file.
    """
    TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
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

def build_parser() -> argparse.ArgumentParser:
    """
    Build and configure the argument parser for CLI commands.
    """
    parser = argparse.ArgumentParser(prog="todo.py", description="Simple CLI todo app in python")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="Add a task to the list")
    p_add.add_argument("description", help="Task description")
    p_add.add_argument(
        "--priority",
        "-p",
        choices=["Low", "Medium", "High"],
        default="Medium",
        help="Task priority (default: Medium)"
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

    return parser


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
    tasks.append({"description": description, "completed": False})
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

    pending = [(i, t) for i, t in enumerate(tasks, start=1) if not t.get("completed", False)]
    completed = [(i, t) for i, t in enumerate(tasks, start=1) if t.get("completed", False)]

    if pending:
        print("Pending tasks:")
        for i, t in pending:
            print(f"  {i}. {t['description']}")
    else:
        print("No pending tasks.")

    if completed:
        print("\nCompleted tasks:")
        for i, t in completed:
            print(f"  {i}. {t['description']} (completed)")


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
    desc = removed["description"] if isinstance(removed, dict) else str(removed)
    print(f"Removed task #{index}: {desc}")


def cmd_complete(index: int) -> None:
    tasks = taskload()
    if not tasks:
        print("No tasks to complete.")
        sys.exit(0)
    if index < 1 or index > len(tasks):
        print(f"Invalid index: {index}. Must be between 1 and {len(tasks)}.")
        sys.exit(2)
    task = tasks[index - 1]
    if task.get("completed", False):
        print(f"Task #{index} is already completed: {task['description']}")
        return
    task["completed"] = True
    tasksave(tasks)
    print(f"Marked task #{index} as completed: {task['description']}")


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

    p_complete = sub.add_parser("complete", help="Mark a task as completed by its index (1-based)")
    p_complete.add_argument("index", type=int, help="Enter task index to mark complete")

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
    elif args.cmd == "complete":
        cmd_complete(args.index)
    elif command == "stats":
        show_stats()


if __name__ == "__main__":
    if validate():
        main()
