const { addTodo, listTodos, removeTodo, clearTodos } = require("./todo");
const args = process.argv.slice(2);

const command = args[0];

if (command === 'help' || args.length === 0) {
  console.log(`
    Usage:
      node index.js add "Task description"    - Adds a new task
      node index.js list                       - Lists all tasks
      node index.js remove <task_index>        - Removes a task by index
      node index.js clear                      - Removes all tasks
  `);
  return;
}

switch (command) {
  case 'add':
    const task = args.slice(1).join(' ');
    addTodo(task);
    console.log(`Added new task: ${task}`);
    break;
  case 'list':
    listTodos();
    break;
  case 'remove':
    const taskIndex = parseInt(args[1], 10);
    removeTodo(taskIndex);
    console.log(`Removed task at index: ${taskIndex}`);
    break;
  case 'clear':
    clearTodos();
    console.log('All tasks have been removed.');
    break;
  default:
    console.log('Unknown command. Use "add", "list", or "remove".');
}
