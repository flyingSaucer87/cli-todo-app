# Python CLI Todo App

A feature-rich command-line todo application written in Python with task prioritization, voice commands, analytics, and beautiful console output.

## ✨ Features

- ✅ **Add, list, remove, and complete tasks** with ease
- 🎯 **Task prioritization** (High, Medium, Low) with automatic sorting
- 🏷️ **Tagging system** to organize tasks by categories
- 🎤 **Voice command mode** for hands-free interaction
- 📊 **Task analytics** showing completion rate, priority breakdown, and tag statistics
- 🎨 **Rich console output** with colors and formatting
- ⚙️ **Configurable settings** (dark mode)
- 💾 **Persistent storage** in local JSON file
- 🛡️ **Robust error handling** with automatic backups

## 📋 Requirements

### Core Requirements
- Python 3.7 or higher
- `rich` - for beautiful console output

### Voice Command Requirements (Optional)
- `SpeechRecognition` - for voice transcription
- `PyAudio` - for microphone access
- Internet connection - for Google Speech Recognition API

Install dependencies:
```bash
pip install rich SpeechRecognition pyaudio
```

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/flyingSaucer87/cli-todo-app.git
cd cli-todo-app/python_ver
```

2. Install required dependencies:
```bash
pip install rich
```

3. **(Optional)** Install voice command dependencies:
```bash
pip install SpeechRecognition pyaudio
```

4. Run the app:
```bash
python todo.py --help
```

## 📖 Usage Guide

### 1️⃣ Add a Task

Add a task with default priority (Medium):
```bash
python todo.py add "Buy groceries"
```

Add a task with specific priority:
```bash
python todo.py add "Fix critical bug" --priority High
python todo.py add "Update documentation" --priority Low
python todo.py add "Review PR" -p Medium
```

Add a task with tags:
```bash
python todo.py add "Implement feature X" -p High -t backend API feature
python todo.py add "Write unit tests" --tags testing python
```

Add a task that's already completed:
```bash
python todo.py add "Completed task" --completed
```

**Full syntax:**
```bash
python todo.py add "<description>" [--priority High|Medium|Low] [--tags tag1 tag2 ...] [--completed]
```

---

### 2️⃣ List All Tasks

List all tasks sorted by priority (High → Medium → Low):
```bash
python todo.py list
```

**Example output:**
```
Pending tasks:
  ○ 1. Fix critical bug (High)
  ○ 3. Review PR (Medium)
  ○ 5. Update documentation (Low)

Completed tasks:
  ● 2. Write tests
  ● 4. Deploy to staging
```

---

### 3️⃣ Complete a Task

Mark a task as completed by its index:
```bash
python todo.py complete 1
```

This moves the task to the "Completed tasks" section when you run `list`.

---

### 4️⃣ Remove a Task

Remove a task by its index (1-based):
```bash
python todo.py remove 2
```

⚠️ **Note:** This permanently deletes the task.

---

### 5️⃣ View Statistics

Display analytics about your tasks:
```bash
python todo.py stats
```

**Example output:**
```
════════════════════ Task Analytics Dashboard ════════════════════

Completion: 5/10 tasks completed (50.00%)

┏━━━━━━━━━━┳━━━━━━━┓
┃ Priority ┃ Count ┃
┡━━━━━━━━━━╇━━━━━━━┩
│ High     │ 3     │
│ Medium   │ 5     │
│ Low      │ 2     │
└──────────┴───────┘

┏━━━━━━━━━━┳━━━━━━━┓
┃ Tag      ┃ Count ┃
┡━━━━━━━━━━╇━━━━━━━┩
│ backend  │ 4     │
│ frontend │ 3     │
│ testing  │ 2     │
└──────────┴───────┘
```

---

### 6️⃣ Configure Settings

View current settings:
```bash
python todo.py settings
```

Enable/disable dark mode:
```bash
python todo.py settings --dark-mode on
python todo.py settings --dark-mode off
```

---

### 7️⃣ Voice Command Mode 🎤

**NEW!** Control your todo list hands-free with voice commands.

Start voice mode:
```bash
python todo.py voice
```

**Supported voice commands:**
- "**add task** buy milk" - Adds a new task
- "**list tasks**" or "**show tasks**" - Lists all tasks
- "**remove task 3**" - Removes task #3
- "**exit**" or "**quit**" - Exits voice mode

**Tips for voice mode:**
- Speak clearly and at a normal pace
- Wait for the "Listening..." prompt before speaking
- You need an active internet connection (uses Google Speech Recognition)
- Press `Ctrl+C` to force quit if needed

**Requirements:**
```bash
pip install SpeechRecognition pyaudio
```

---

### 8️⃣ Get Help

View all available commands:
```bash
python todo.py --help
```

Get help for a specific command:
```bash
python todo.py add --help
python todo.py list --help
python todo.py voice --help
```

## 💾 Data Storage

Tasks are automatically saved in `tasks.json` in the same directory as `todo.py`.

### Custom Storage Location

You can change the file location by setting the `TODO_FILE` environment variable:

**Linux/Mac:**
```bash
export TODO_FILE=/path/to/custom_tasks.json
python todo.py list
```

**Windows PowerShell:**
```powershell
$env:TODO_FILE = "C:\path\to\custom_tasks.json"
python todo.py list
```

**Windows Command Prompt:**
```cmd
set TODO_FILE=C:\path\to\custom_tasks.json
python todo.py list
```

### Configuration File

User settings are stored in `config.json` (same directory as `todo.py`). You can customize the location:

```bash
```bash
export TODO_CONFIG_FILE=/path/to/custom_config.json
```

## 🛡️ Error Handling & Safety

The app includes robust error handling:
- ✅ **Malformed JSON**: Automatically backs up corrupted files with `.backup` extension
- ✅ **Empty tasks**: Prevents adding blank or whitespace-only tasks
- ✅ **File I/O errors**: Graceful handling of permission and disk space issues
- ✅ **Invalid priorities**: Validates priority levels (High, Medium, Low only)
- ✅ **Invalid indices**: Checks task index bounds before operations
- ✅ **Voice errors**: Handles microphone issues, timeout, and network problems

## 🎨 Features in Detail

### Task Priorities
- **High**: Urgent, important tasks (displayed first)
- **Medium**: Regular tasks (default)
- **Low**: Nice-to-have, less urgent tasks

### Tagging System
Organize tasks with custom tags:
```bash
python todo.py add "Deploy app" -t deployment production urgent
python todo.py add "Write blog post" -t content marketing
```

Tags appear in the statistics view to show which categories you work on most.

### Rich Console Output
- Color-coded task priorities
- Strikethrough for completed tasks
- Formatted tables for statistics
- Clear visual feedback for all operations

## 📊 Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `add` | Add a new task | `python todo.py add "Task" -p High -t tag1` |
| `list` | List all tasks | `python todo.py list` |
| `complete` | Mark task as done | `python todo.py complete 1` |
| `remove` | Delete a task | `python todo.py remove 2` |
| `stats` | View analytics | `python todo.py stats` |
| `settings` | Configure preferences | `python todo.py settings --dark-mode on` |
| `voice` | Voice command mode | `python todo.py voice` |

## 🔧 Troubleshooting

### Voice mode not working?
1. Install dependencies: `pip install SpeechRecognition pyaudio`
2. Check microphone permissions in system settings
3. Ensure you have an active internet connection
4. Try speaking more clearly or adjusting microphone volume

### PyAudio installation issues on Windows?
Download the wheel file from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and install:
```bash
pip install PyAudio‑0.2.11‑cp311‑cp311‑win_amd64.whl
```

### Tasks not saving?
- Check write permissions in the directory
- Verify disk space availability
- Look for `.backup` files if JSON was corrupted

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the [MIT License](../LICENSE).

## 🎯 Roadmap

- [ ] Export tasks to CSV/PDF
- [ ] Task reminders and due dates
- [ ] Recurring tasks
- [ ] Multiple todo lists
- [ ] Cloud sync support
- [ ] Natural language processing for smarter voice commands

---

**Made with ❤️ by MohdShayan**
```

## Error Handling

The app includes robust error handling for:
- **Malformed JSON**: Automatically backs up and resets corrupted files
- **Empty tasks**: Prevents adding blank or whitespace-only tasks
- **File I/O errors**: Graceful handling of permission and disk space issues
- **Invalid priorities**: Validates priority levels before adding tasks

## Improvements from Issue #9

This version addresses all requirements from issue #9:

1. ✅ **Error Handling for Malformed JSON**: Catches `JSONDecodeError` and backs up corrupted files
2. ✅ **Empty Task Validation**: Prevents empty or whitespace-only tasks
3. ✅ **File Permissions and I/O Errors**: Comprehensive error handling for all file operations
4. ✅ **Task Prioritization**: High/Medium/Low priority with automatic sorting
5. ✅ **Code Refactoring**: Added docstrings, type hints, and improved code organization

