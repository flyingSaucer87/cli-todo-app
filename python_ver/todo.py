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


def taskload() -> List[str]:

    if not TASKS_FILE.exists():
        return []

    try:
        with TASKS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return [str(item) for item in data]
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

    try:
        if TASKS_FILE.exists():
            backup_name = TASKS_FILE.with_suffix(f".backup.{reason}")
            TASKS_FILE.replace(backup_name)
            print(f"Backed up corrupted tasks file to: {backup_name}", file=sys.stderr)
    except Exception as e:
        print(f"Failed to back up corrupted tasks file: {e}", file=sys.stderr)


def tasksave(tasks: List[str]) -> None:

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
    tasks.append(description)
    tasksave(tasks)
    print(f"Added task #{len(tasks)}: {description}")


def cmd_list() -> None:
    tasks = taskload()
    if not tasks:
        print("No tasks.")
        return
    for i, t in enumerate(tasks, start=1):
        print(f"{i}. {t}")


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
    print(f"Removed task #{index}: {removed}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo.py", description="Simple CLI todo app in python")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="Add a task to the list")
    p_add.add_argument("description", help="Task description")

    p_list = sub.add_parser("list", help="List all tasks")

    p_remove = sub.add_parser("remove", help="Remove a task by its index (1-based)")
    p_remove.add_argument("index", type=int, help="Enter task index to remove")

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


if __name__ == "__main__":
    if validate():
        main()
