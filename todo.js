const fs = require("fs");
const filePath = "todos.json";
let todos = [];

// Load tasks from the JSON file
function loadTodos() {
    if (fs.existsSync(filePath)) {
        const data = fs.readFileSync(filePath, "utf-8");
        const parsedData = JSON.parse(data);

        // handle legacy format (array of strings) - BACKWARD COMPATIBILITY
        // this checks if the old format exists and converts it automatically
        if (Array.isArray(parsedData) && parsedData.length > 0 && typeof parsedData[0] === 'string') {
            todos = parsedData.map(task => ({
                description: task, 
                completed: false, 
                priority: 'medium', 
                tags: []
            }));

            // save in new format
            saveTodos();
        } else {
            todos = parsedData || [];
        }
    }

}

// save tasks to JSON file
function saveTodos() {
    fs.writeFileSync(filePath, JSON.stringify(todos, null, 2));
}

// Add a new task with Metadata
function addTodo(description, priority = 'Medium', tags = []) {
    // validate priority is one of the allowed values below
    const validPriorities = ['Low', 'Medium', 'High'];
    if (!validPriorities.includes(priority)) {
        console.log('Invalid priority. Use Low, Medium, or High.');
        return;
    }

    // create task object with all properties mentioned above
    const task = {
        description: description.trim(), 
        completed: false, 
        priority: priority, 
        tags: Array.isArray(tags) ? tags : []
    };

    todos.push(task);
    saveTodos();
}

// List all tasks with enhanced display
function listTodos(filterCompleted = null, filterTag = null) {
    if (todos.length === 0) {
        console.log('No tasks yet!');
        return;
    }

    let filteredTodos = todos;

    // filter by completion status if requested
    if (filterCompleted !== null) {
        filteredTodos = filteredTodos.filter(task => task.completed === filterCompleted);
    }

    // filter by tag if requested
    if (filterTag) {
        filteredTodos = filteredTodos.filter(task => task.tags && task.tags.includes(filterTag));
    }

    // sort by priority: High -> Medium -> Low
    const priorityOrder = { 'High': 0, 'Medium': 1, 'Low': 2 };
    filteredTodos.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);

    // display each task with formatting
    filteredTodos.forEach((task, index) => {
        const status = task.completed ? '✓' : '○';
        const tags = task.tags && task.tags.length > 0 ? ` [${task.tags.join(', ')}]` : '';
        const originalIndex = todos.indexOf(task);
        console.log(`${status} ${originalIndex}: ${task.description} (${task.priority})${tags}`);
    });
}

// Remove a task by index
function removeTodo(index) {
    if (index >= 0 && index < todos.length) {
        const removed = todos.splice(index, 1)[0];
        saveTodos();
        console.log(`Removed: ${removed.description}`);
    } else {
        console.log("Invalid task index.");
    }
}

// Edit a task by index
function editTodo(index, newDescription, newPriority, newTags) {
    if (index >= 0 && index < todos.length) {
        const task = todos[index];

        // only update the fields that are provided
        if (newDescription) task.description = newDescription;
        if (newPriority) task.priority = newPriority;
        if (newTags !== undefined) task.tags = Array.isArray(newTags) ? newTags : [];

        saveTodos();
        console.log(`Updated task ${index}: ${task.description} (${task.priority})`);
    } else {
        console.log("Invalid task index.");
    }
}

// Mark task as completed - NEW FUNCTION
function completeTodo(index) {
    if (index >= 0 && index < todos.length) {
        todos[index].completed = true;
        saveTodos();
        console.log(`✓ Marked as completed: ${todos[index].description}`);
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

module.exports = { addTodo, listTodos, removeTodo, editTodo, completeTodo, clearTodos };
