const fs = require('fs');
const filePath = 'todos.json';

let todos = [];

// Load tasks from the JSON file
function loadTodos() {
  if (fs.existsSync(filePath)) {
    const data = fs.readFileSync(filePath, 'utf-8');
    todos = JSON.parse(data);
  }
}

function saveTodos() {
  fs.writeFileSync(filePath, JSON.stringify(todos, null, 2));
}

// Add a new task
function addTodo(task) {
  todos.push(task);
  saveTodos();
}

// Remove all tasks
function clearTodos() {
  todos = [];
  saveTodos();
}

// List all tasks
function listTodos() {
  if (todos.length === 0) {
    console.log('No tasks yet!');
    return;
  }
  todos.forEach((task, index) => {
    console.log(`${index}: ${task}`);
  });
}

// Remove a task by index
function removeTodo(index) {
  if (index >= 0 && index < todos.length) {
    todos.splice(index, 1);
    saveTodos();
  } else {
    console.log('Invalid task index.');
  }
}

// Clear all tasks
function clearTodos() {
  todos = [];
  saveTodos();
}

// Initialize tasks on startup
loadTodos();

module.exports = { addTodo, listTodos, removeTodo , clearTodos };
