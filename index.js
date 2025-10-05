const {
    addTodo,
    listTodos,
    removeTodo,
    editTodo,
    markDone,
    clearTodos,
} = require("./todo");
const args = process.argv.slice(2);

const command = args[0];

if (command === "help" || args.length === 0) {
    console.log(`
    Usage:
      node index.js add "Task description"    - Adds a new task
      node index.js list                       - Lists all tasks
      node index.js remove <task_index>        - Removes a task by index
      node index.js edit <task_index> "New description" - Edits a task by index
      node index.js clear                      - Removes all tasks
  `);
    return;
}

switch (command) {
    case "add":
        const task = args.slice(1).join(" ");
        addTodo(task);
        console.log(`Added new task: ${task}`);
        break;
    case "list":
        listTodos();
        break;
    case "remove":
        const taskIndex = parseInt(args[1], 10);
        removeTodo(taskIndex);
        console.log(`Removed task at index: ${taskIndex}`);
        break;
    case "edit":
        const editIndex = parseInt(args[1], 10);
        const newDescription = args.slice(2).join(" ");
        if (isNaN(editIndex)) {
            console.log("Error: Please provide a valid task index.");
            console.log(
                'Usage: node index.js edit <task_index> "New description"'
            );
        } else if (!newDescription.trim()) {
            console.log("Error: Please provide a new description.");
            console.log(
                'Usage: node index.js edit <task_index> "New description"'
            );
        } else {
            editTodo(editIndex, newDescription);
        }
        break;
    case "clear":
        clearTodos();
        console.log("All tasks have been cleared.");
        break;
    case "done":
        const doneIndex = parseInt(args[1], 10);
        if (isNaN(doneIndex)) {
            console.log("Error: Please provide a valid task index.");
            console.log('Usage: node index.js done <task_index>');
        } else {
            markDone(doneIndex);
        }
        break;
 
    default:
        console.log(
            'Unknown command. Use "add", "list", "remove", "edit", or "clear".'
        );
}
