const { addTodo, listTodos, removeTodo, editTodo, completeTodo, clearTodos } = require('./todo');
const exporter = require('./exporter');
const args = process.argv.slice(2);
const command = args[0];

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


  if (command === 'export') {
  // node index.js export csv path/to/out.csv
  const format = process.argv[3] || 'csv';
  const out = process.argv[4] || `todos.${format}`;
  exporter.exportTodos(format, out);
  process.exit(0);
}

if (command === 'import') {
  // node index.js import csv path/to/in.csv
  const format = process.argv[3] || 'csv';
  const infile = process.argv[4];
  if (!infile) {
    console.error('Usage: node index.js import <csv|md> <file>');
    process.exit(1);
  }
  exporter.importTodos(format, infile);
  process.exit(0);
}

  default:
    console.log('Unknown command. Use "help" for usage information.');
}

