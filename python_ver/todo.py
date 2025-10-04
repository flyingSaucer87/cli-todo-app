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


def _normalize_tasks(data: Any) -> List[Dict[str, Any]]:
    """Normalize raw JSON data into a list of task dicts.

    Accepted input formats:
    - legacy: ["task one", "task two", ...]
    - new: [{"description": str, "completed": bool}, ...]
    Any unknown item types are skipped.
    """
    normalized: List[Dict[str, Any]] = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                normalized.append({"description": item, "completed": False})
            elif isinstance(item, dict):
                desc = item.get("description")
                if isinstance(desc, str):
                    normalized.append({
                        "description": desc,
                        "completed": bool(item.get("completed", False)),
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

    try:
        if TASKS_FILE.exists():
            backup_name = TASKS_FILE.with_suffix(f".backup.{reason}")
            TASKS_FILE.replace(backup_name)
            print(f"Backed up corrupted tasks file to: {backup_name}", file=sys.stderr)
    except Exception as e:
        print(f"Failed to back up corrupted tasks file: {e}", file=sys.stderr)


def tasksave(tasks: List[Dict[str, Any]]) -> None:

    TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(tasks, ensure_ascii=False, indent=2)


    fd, tmp_path = tempfile.mkstemp(prefix=".tasks-", dir=str(TASKS_FILE.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmpf:
            tmpf.write(data)
            tmpf.flush()
            os.fsync(tmpf.fileno())
        Path(tmp_path).replace(TASKS_FILE)
    finally:

        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


def cmd_add(description: str) -> None:
    tasks = taskload()
    tasks.append({"description": description, "completed": False})
    tasksave(tasks)
    print(f"Added task #{len(tasks)}: {description}")


def cmd_list() -> None:
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
    tasks = taskload()
    if not tasks:
        print("No tasks to remove.")
        sys.exit(0)
    if index < 1 or index > len(tasks):
        print(f"Invalid index: {index}. Must be between 1 and {len(tasks)}.")
        sys.exit(2)
    removed = tasks.pop(index - 1)
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
    parser = argparse.ArgumentParser(prog="todo.py", description="Simple CLI todo app in python")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="Add a task to the list")
    p_add.add_argument("description", help="Task description")

    p_list = sub.add_parser("list", help="List all tasks")

    p_remove = sub.add_parser("remove", help="Remove a task by its index (1-based)")
    p_remove.add_argument("index", type=int, help="Enter task index to remove")

    p_complete = sub.add_parser("complete", help="Mark a task as completed by its index (1-based)")
    p_complete.add_argument("index", type=int, help="Enter task index to mark complete")

    return parser


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "add":
        cmd_add(args.description)
    elif args.cmd == "list":
        cmd_list()
    elif args.cmd == "remove":
        cmd_remove(args.index)
    elif args.cmd == "complete":
        cmd_complete(args.index)


if __name__ == "__main__":
    main()
