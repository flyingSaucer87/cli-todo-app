// todo.js
const fs = require("fs");
const filePath = "todos.json";
let todos = [];

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

