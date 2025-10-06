# ✅ Manual Testing Guide for Issue #53 - Priority and Tags Support

This document provides a **comprehensive suite of terminal commands** for manually testing all functionality added or updated as part of **Issue #53** in the CLI Todo App. These manual tests validate:

- 🏷️ Tag support
- 🚦 Priority levels (High, Medium, Low)
- 🔄 Backward compatibility with old formats
- 🎯 Filtering support via flags
- ✅ Completion and editing
- 🧪 Robust error handling
- 🧠 Focus mode (plugin)
- 📄 Proper JSON structure in `todos.json`

> ⚙️ **How to use:**
> Simply copy and paste each block of commands into your terminal from top to bottom (after checking out the feature branch).
> Make sure to run: `rm -f todos.json` at the beginning for a clean slate.

---

## 📝 Test Backward Compatibility

```bash
echo '["Old task 1", "Old task 2", "Legacy string task"]' > todos.json
cat todos.json
node index.js list
cat todos.json
```

---

## ➕ Test Adding Tasks (Various Scenarios)

```bash
# Basic add with defaults
node index.js add "Basic task with no flags"

# High priority tasks
node index.js add "Fix critical security vulnerability" --priority High --tags security,urgent,backend
node index.js add "Server is down - immediate fix needed" --priority High --tags infrastructure,urgent
node index.js add "Memory leak in production" --priority High --tags performance,urgent,debugging
node index.js add "Database corruption detected" --priority High --tags database,critical,urgent

# Medium priority tasks
node index.js add "Implement user authentication" --priority Medium --tags feature,backend,auth
node index.js add "Write unit tests for API" --priority Medium --tags testing,backend,qa
node index.js add "Update documentation" --priority Medium --tags docs,maintenance
node index.js add "Code review for PR #123" --priority Medium --tags review,collaboration
node index.js add "Refactor legacy code" --priority Medium --tags refactor,technical-debt

# Low priority tasks
node index.js add "Buy groceries for the week" --priority Low --tags personal,shopping,weekend
node index.js add "Clean up development environment" --priority Low --tags maintenance,dev-tools
node index.js add "Organize digital photos" --priority Low --tags personal,organization
node index.js add "Learn new JavaScript framework" --priority Low --tags learning,javascript,skill-development
node index.js add "Update resume" --priority Low --tags personal,career

# Tasks with multiple tags
node index.js add "Deploy new feature to staging" --priority Medium --tags deployment,staging,devops,testing
node index.js add "Performance optimization research" --priority Low --tags research,performance,optimization,learning
node index.js add "Team meeting preparation" --priority Medium --tags meeting,planning,team,collaboration

# Tasks with single tags
node index.js add "Exercise - go for a run" --priority Low --tags exercise
node index.js add "Call mom" --priority Low --tags family
node index.js add "Backup important files" --priority Medium --tags backup

# Edge cases
node index.js add "Task with special characters @#$%^&*()" --priority Medium --tags special,test
node index.js add "Very long task description that goes on and on and should still work properly even with lots of text" --priority Low --tags verbose,test
```

---

## 📋 Test Listing (All Variations)

```bash
node index.js list
node index.js help
node index.js
```

---

## ✅ Test Completing Tasks

```bash
node index.js complete 0
node index.js complete 1
node index.js complete 3
node index.js complete 5
node index.js complete 7
node index.js complete 10
node index.js complete 12
```

---

## 🔍 Test Filtering

```bash
# By status
node index.js list --completed
node index.js list --pending

# By tag
node index.js list --tag urgent
node index.js list --tag backend
node index.js list --tag personal
node index.js list --tag testing
node index.js list --tag security
node index.js list --tag maintenance
node index.js list --tag learning
node index.js list --tag performance
node index.js list --tag deployment

# Combined filters
node index.js list --pending --tag urgent
node index.js list --completed --tag backend
```

---

## ✏️ Test Editing Tasks

```bash
node index.js edit 2 --description "Updated critical vulnerability fix - in progress"
node index.js edit 4 --description "Enhanced user authentication with OAuth2"
node index.js edit 8 --priority High
node index.js edit 15 --priority Medium
node index.js edit 6 --priority Low
node index.js edit 9 --tags weekend,shopping,healthy-eating
node index.js edit 11 --tags development,tools,automation,productivity
node index.js edit 13 --description "Comprehensive photo organization project" --priority Medium --tags personal,organization,productivity
node index.js edit 14 --tags ""
```

---

## 🗑️ Test Removing Tasks

```bash
node index.js remove 0
node index.js remove 1
node index.js remove 3
node index.js remove 5
```

---

## 🎯 Test Focus Mode

```bash
python plugins/focus-mode.py
```

---

## ❌ Test Error Handling

```bash
# Invalid priority
node index.js add "Invalid priority task" --priority Urgent
node index.js add "Another invalid" --priority Critical
node index.js add "Wrong priority" --priority Super-High

# Invalid indexes
node index.js complete 999
node index.js remove 888
node index.js edit 777 --description "Should fail"
node index.js complete -1
node index.js remove -5

# Empty description
node index.js add ""
node index.js add "   "

# Invalid commands
node index.js invalidcommand
node index.js xyz
```

---

## 🔄 Test More Complex Scenarios

```bash
# Add more tasks
node index.js add "Another high priority" --priority High --tags urgent,test
node index.js add "Another medium priority" --priority Medium --tags test
node index.js add "Another low priority" --priority Low --tags test

# Complete a few
node index.js complete 0
node index.js complete 2

# Re-sort test
node index.js edit 1 --priority Low
node index.js edit 3 --priority High

# Tag filters again
node index.js list --tag test
node index.js list --tag urgent
```

---

## 🧪 Edge Cases

```bash
node index.js add "No tags task" --priority Medium
node index.js add "Task with, comma in description" --priority Low --tags punctuation,test
node index.js add 'Task with "quotes" in description' --priority Low --tags quotes,test
```

---

## 🗂️ Check File State

```bash
cat todos.json
python -m json.tool todos.json
```

---

## 🧹 Final Cleanup

```bash
node index.js clear
node index.js list
cat todos.json
```

---

## 🔄 Backward Compatibility (Final Check)

```bash
echo '["Final test task", "Another final task"]' > todos.json
node index.js list
cat todos.json
```

---
