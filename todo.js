// todo.js
const fs = require("fs");
const filePath = "todos.json";
let todos = [];

const taskSchema = {
    id: Number,
    name: String,
    due_date: String,
    status: String,
    priority: String,
    created_at: Date,
    updated_at: Date,
    versions: [ // Array of task versions
        {
            version_number: Number,
            name: String,
            due_date: String,
            status: String,
            priority: String,
            modified_at: Date,
            modified_by: String // Track who made the change (optional)
        }
    ]
}


const showTaskHistory = (taskId) => {
    const versions = getTaskVersions(taskId);  // Assume this fetches all versions for the task

    if (versions.length === 0) {
        console.log("No history available for this task.");
    } else {
        console.log("Task History:");
        versions.forEach((version, index) => {
            console.log(`#${index + 1} - Version: ${version.version_number}`);
            console.log(`Name: ${version.name}`);
            console.log(`Due Date: ${version.due_date}`);
            console.log(`Status: ${version.status}`);
            console.log(`Priority: ${version.priority}`);
            console.log(`Modified at: ${new Date(version.modified_at).toLocaleString()}`);
            console.log('------------------------------------');
        });
    }
}

const getTaskVersions = (taskId) => {
    return db.all("SELECT * FROM task_versions WHERE task_id = ? ORDER BY version_number DESC", [taskId]);
}

const rollbackTaskCommand = (taskId, versionNumber) => {
    rollbackTask(taskId, versionNumber);
    console.log(`Task ${taskId} has been rolled back to version ${versionNumber}.`);
}


// Load tasks from the JSON file
function loadTodos() {
  if (fs.existsSync(filePath)) {
    const data = fs.readFileSync(filePath, "utf-8");
    const parsedData = JSON.parse(data);

    // Clear existing todos without breaking reference
    todos.length = 0;

    // handle legacy format (array of strings) - BACKWARD COMPATIBILITY
    if (Array.isArray(parsedData) && parsedData.length > 0 && typeof parsedData[0] === 'string') {
      const migratedTasks = parsedData.map(task => ({
        description: task,
        completed: false,
        priority: 'Medium',
        tags: []
      }));
      todos.push(...migratedTasks);
      saveTodos();
    } else if (Array.isArray(parsedData)) {
      todos.push(...parsedData);
    }
  }
}

// Save tasks to JSON file
function saveTodos() {
  fs.writeFileSync(filePath, JSON.stringify(todos, null, 2));
}

// Helper: get sorted/filtered list for display and operations
function getSortedTodos(filterCompleted = null, filterTag = null) {
  let filtered = todos;
  if (filterCompleted !== null) {
    filtered = filtered.filter(t => t.completed === filterCompleted);
  }
  if (filterTag) {
    filtered = filtered.filter(t => t.tags && t.tags.includes(filterTag));
  }
  const priorityOrder = { High: 0, Medium: 1, Low: 2 };
  return filtered.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
}

// Add a new task with metadata
function addTodo(description, priority = 'Medium', tags = []) {
  const valid = ['Low', 'Medium', 'High'];
  if (!valid.includes(priority)) {
    console.log('Invalid priority. Use Low, Medium, or High.');
    return;
  }
  todos.push({
    description: description.trim(),
    completed: false,
    priority,
    tags: Array.isArray(tags) ? tags : []
  });
  saveTodos();
}

// List tasks in display order
function listTodos(filterCompleted = null, filterTag = null) {
  const sorted = getSortedTodos(filterCompleted, filterTag);
  if (sorted.length === 0) {
    console.log('No tasks yet!');
    return;
  }
  sorted.forEach((task, i) => {
    const status = task.completed ? '✓' : '○';
    const tags = task.tags.length ? ` [${task.tags.join(', ')}]` : '';
    console.log(`${status} ${i}: ${task.description} (${task.priority})${tags}`);
  });
}

// Remove by display index
function removeTodo(idx) {
  const sorted = getSortedTodos();
  if (idx < 0 || idx >= sorted.length) {
    console.log('Invalid task index.');
    return;
  }
  const original = todos.indexOf(sorted[idx]);
  const removed = todos.splice(original, 1)[0];
  saveTodos();
  console.log(`Removed: ${removed.description}`);
}

// Edit by display index
function editTodo(idx, newDesc, newPriority, newTags) {
  const sorted = getSortedTodos();
  if (idx < 0 || idx >= sorted.length) {
    console.log('Invalid task index.');
    return;
  }
  const original = todos.indexOf(sorted[idx]);
  const task = todos[original];
  if (newDesc) task.description = newDesc;
  if (newPriority) task.priority = newPriority;
  if (newTags !== undefined) task.tags = Array.isArray(newTags) ? newTags : [];
  saveTodos();
  console.log(`Updated task ${idx}: ${task.description} (${task.priority})`);
}

// Complete by display index
function completeTodo(idx) {
  const sorted = getSortedTodos();
  if (idx < 0 || idx >= sorted.length) {
    console.log('Invalid task index.');
    return;
  }
  const original = todos.indexOf(sorted[idx]);
  todos[original].completed = true;
  saveTodos();
  console.log(`✓ Marked as completed: ${todos[original].description}`);
}
function markDone(index) {
    const todos = getTodos();
    if (index < 0 || index >= todos.length) {
        console.log("❌ Invalid task index.");
        return;
    }

    todos[index].done = true; // mark the task as done
    saveTodos(todos);
    console.log(`✅ Task "${todos[index].task}" marked as done.`);
}

// Clear all tasks
function clearTodos() {
  todos.length = 0;
  saveTodos();
}

// Initialize on load
loadTodos();

module.exports = {
  addTodo,
  listTodos,
  removeTodo,
  editTodo,
  completeTodo,
  clearTodos,
  loadTodos,
  todos
};

