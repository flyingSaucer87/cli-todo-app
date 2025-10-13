def run(args):
    """Display high-priority incomplete tasks from both Node.js and Python versions."""
    import json
    import os

    # Check both Node.js and Python task files
    node_file = "todos.json"
    python_file = "python_ver/tasks.json"

    print("🎯 Focus Mode: High Priority Tasks Only")
    print("=" * 40)

    found_tasks = False

    # Check Node.js tasks
    if os.path.exists(node_file):
        try:
            with open(node_file, "r") as f:
                node_tasks = json.load(f)

            # Filter for high-priority, incomplete tasks
            high_priority_node = [
                task
                for task in node_tasks
                if task.get("priority") == "High" and not task.get("completed", False)
            ]

            if high_priority_node:
                print("\n📋 Node.js Tasks:")
                for i, task in enumerate(high_priority_node):
                    tags = (
                        f" [{', '.join(task.get('tags', []))}]"
                        if task.get("tags")
                        else ""
                    )
                    print(f"  {i + 1}. {task['task']}{tags}")
                found_tasks = True
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Could not read Node.js tasks: {e}")

    # Check Python tasks
    if os.path.exists(python_file):
        try:
            with open(python_file, "r") as f:
                python_tasks = json.load(f)

            # Filter for high-priority, incomplete tasks
            high_priority_python = [
                task
                for task in python_tasks
                if task.get("priority") == "High" and not task.get("completed", False)
            ]

            if high_priority_python:
                print("\n🐍 Python Tasks:")
                for i, task in enumerate(high_priority_python):
                    tags = (
                        f" [{', '.join(task.get('tags', []))}]"
                        if task.get("tags")
                        else ""
                    )
                    print(f"  {i + 1}. {task['task']}{tags}")
                found_tasks = True
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Could not read Python tasks: {e}")

    if not found_tasks:
        print("\n🎉 No high-priority tasks found! Great job!")


if __name__ == "__main__":
    run([])
