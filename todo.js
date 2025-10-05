const fs = require("fs");
const filePath = "todos.json";

let todos = [];

// Load tasks from the JSON file
function loadTodos() {
    if (fs.existsSync(filePath)) {
        const data = fs.readFileSync(filePath, "utf-8");
        todos = JSON.parse(data);
    }
}

function saveTodos() {
    fs.writeFileSync(filePath, JSON.stringify(todos, null, 2));
}

// Add a new task
function addTodo(taskDescription) {
    const tasks = { task: taskDescription, done: false };
    todos.push(tasks);
    saveTodos();
}

// List all tasks
function listTodos() {
    if (todos.length === 0) {
        console.log("No tasks yet!");
        return;
    }
    todos.forEach((todo, index) => {
        const status = todo.done ? "[✓]" : "[ ]";
        console.log(`${index}: ${status} ${todo.task}`);
    });
}

// Remove a task by index
function removeTodo(index) {
    if (index >= 0 && index < todos.length) {
        todos.splice(index, 1);
        saveTodos();
    } else {
        console.log("Invalid task index.");
    }
}

// Edit a task by index
function editTodo(index, newDescription) {
    if (index >= 0 && index < todos.length) {
        const oldTask = todos[index];
        todos[index] = newDescription;
        saveTodos();
        console.log(` Updated task ${index}:`);
        console.log(`   Old: ${oldTask}`);
        console.log(`   New: ${newDescription}`);
    } else {
        console.log("Invalid task index.");
    }
}
function markDone(index) {
    if (index < 0 || index >= todos.length) {
        console.log("Invalid task index.");
        return;
    }

    todos[index].done = true; // mark the task as done
    saveTodos(todos);
    console.log(`Task "${todos[index].task}" marked as done.`);
}

// Clear all tasks
function clearTodos() {
    todos = [];
    saveTodos();
}

// Initialize tasks on startup
loadTodos();

module.exports = { addTodo, listTodos, removeTodo, editTodo, markDone, clearTodos };
