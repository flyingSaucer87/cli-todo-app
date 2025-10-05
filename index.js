const { addTodo, listTodos, removeTodo, editTodo, completeTodo, clearTodos } = require('./todo');

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
      node index.js done <task_index>          - Marks a task as done by index
// Show help if no command or help is requested
if (command === 'help' || args.length === 0) {
  console.log(`
Usage:
  node index.js add "Task description" [--priority High|Medium|Low] [--tags tag1,tag2]
  node index.js list [--completed] [--pending] [--tag tagname]
  node index.js complete <index> - Mark task as completed
  node index.js remove <index> - Remove task by index  
  node index.js edit <index> [--description "New desc"] [--priority High|Medium|Low] [--tags tag1,tag2]
  node index.js clear - Remove all tasks

Examples:
  node index.js add "Buy groceries" --priority High --tags shopping,urgent
  node index.js list --pending
  node index.js list --tag work
  node index.js complete 0
  `);
  return;
}

// Parse command-line arguments to separate flags from positional args
function parseArgs(args) {
  const parsed = { positional: [], flags: {} };
  let i = 0;
  
  while (i < args.length) {
    if (args[i].startsWith('--')) {
      const flag = args[i].substring(2);
      if (i + 1 < args.length && !args[i + 1].startsWith('--')) {
        parsed.flags[flag] = args[i + 1];
        i += 2;
      } else {
        parsed.flags[flag] = true;
        i++;
      }
    } else {
      parsed.positional.push(args[i]);
      i++;
    }
  }
  
  return parsed;
}

const parsed = parseArgs(args.slice(1));

switch (command) {
    case "add":
        const task = args.slice(1).join(" ");
        if (!task.trim()) {
            console.log("Error: Please provide a task description.");
        } else {
            addTodo(task);
            console.log(`Added new task: "${task}"`);
        }
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
            'Unknown command. Use "add", "list", "remove", "edit", "clear" , or "done".'
        );
  case 'add':
    const description = parsed.positional[0];
    if (!description || !description.trim()) {
      console.log('Error: Please provide a task description.');
      console.log('Usage: node index.js add "Task description" [--priority High|Medium|Low] [--tags tag1,tag2]');
      return;
    }
    const priority = parsed.flags.priority || 'Medium';
    const tags = parsed.flags.tags ? parsed.flags.tags.split(',').map(t => t.trim()) : [];
    addTodo(description, priority, tags);
    console.log(`✓ Added: ${description} (Priority: ${priority}, Tags: [${tags.join(', ')}])`);
    break;

  case 'list':
    let filterCompleted = null;
    if (parsed.flags.completed) filterCompleted = true;
    if (parsed.flags.pending) filterCompleted = false;
    listTodos(filterCompleted, parsed.flags.tag);
    break;

  case 'complete':
    const completeIndex = parseInt(parsed.positional[0], 10);
    if (isNaN(completeIndex)) {
      console.log('Error: Please provide a valid task index.');
      console.log('Usage: node index.js complete <index>');
      return;
    }
    completeTodo(completeIndex);
    break;

  case 'remove':
    const removeIndex = parseInt(parsed.positional[0], 10);
    if (isNaN(removeIndex)) {
      console.log('Error: Please provide a valid task index.');
      console.log('Usage: node index.js remove <index>');
      return;
    }
    removeTodo(removeIndex);
    break;

  case 'edit':
    const editIndex = parseInt(parsed.positional[0], 10);
    if (isNaN(editIndex)) {
      console.log('Error: Please provide a valid task index.');
      console.log('Usage: node index.js edit <index> [--description "New"] [--priority High|Medium|Low] [--tags tag1,tag2]');
      return;
    }
    const newTags = parsed.flags.tags ? parsed.flags.tags.split(',').map(t => t.trim()) : undefined;
    editTodo(editIndex, parsed.flags.description, parsed.flags.priority, newTags);
    break;

  case 'clear':
    clearTodos();
    console.log('All tasks have been cleared.');
    break;

  default:
    console.log('Unknown command. Use "help" for usage information.');
}

