import { addTodo, listTodos, editTodo, removeTodo, toggleTodo, clearTodos } from './todo.js';

const args = process.argv.slice(2);
const command = args[0];

function parseFlags(args) {
  const flags = {};
  const positional = [];
  
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const flag = args[i].substring(2);
      
      // Check if next arg exists and is not a flag
      if (i + 1 < args.length && !args[i + 1].startsWith('--')) {
        flags[flag] = args[i + 1];
        i++; // Skip next arg since we consumed it
      } else {
        flags[flag] = true;
      }
    } else {
      positional.push(args[i]);
    }
  }
  
  return { flags, positional };
}

function parseTags(tagString) {
  // Handle cases where tagString might be boolean true or other non-string
  if (tagString === true || tagString === undefined || tagString === null) {
    return [];
  }
  
  // Convert to string if needed
  const str = String(tagString);
  
  if (str.trim() === '') {
    return [];
  }
  
  return str.split(',').map(t => t.trim()).filter(t => t.length > 0);
}

function showHelp() {
  console.log(`
Usage: node index.js <command> [arguments] [flags]

Commands:
  add <task>           Add a new task
  list                 List all tasks with progress bar
  edit <index>         Edit a task at the given index
  remove <index>       Remove a task at the given index
  complete <index>     Toggle task completion status
  clear                Clear all tasks
  help                 Show this help message

Flags for 'add':
  --priority <level>   Set priority (High, Medium, Low)
  --tags <tags>        Comma-separated tags

Flags for 'list':
  --completed          Show only completed tasks
  --pending            Show only pending tasks
  --tag <tag>          Filter by tag

Flags for 'edit':
  --description <text> Update task description
  --priority <level>   Update priority
  --tags <tags>        Update tags (comma-separated, or empty string to clear)

Examples:
  node index.js add "Buy groceries" --priority High --tags shopping,urgent
  node index.js list --pending --tag urgent
  node index.js complete 0
  node index.js edit 0 --description "New description" --priority Low
  node index.js edit 1 --tags dev,testing
  node index.js remove 0
  node index.js clear
  `);
}

if (command === "help" || args.length === 0 || command === undefined) {
  showHelp();
  process.exit(0);
}

const { flags, positional } = parseFlags(args.slice(1));

switch (command) {
  case "add": {
    if (positional.length === 0) {
      console.error('Error: Please provide a task description');
      console.log('Usage: node index.js add "Your task" [--priority <level>] [--tags <tags>]');
      process.exit(1);
    }
    
    const description = positional.join(' ');
    const priority = flags.priority || 'Medium';
    const tags = flags.tags ? parseTags(flags.tags) : [];
    
    addTodo(description, priority, tags);
    break;
  }

  case "list": {
    const filters = {};
    
    if (flags.completed) {
      filters.completed = true;
    } else if (flags.pending) {
      filters.completed = false;
    }
    
    if (flags.tag) {
      filters.tag = flags.tag;
    }
    
    listTodos(filters);
    break;
  }

  case "complete": {
    if (positional.length === 0) {
      console.error('Error: Please provide an index');
      console.log('Usage: node index.js complete <index>');
      process.exit(1);
    }
    
    const index = parseInt(positional[0], 10);
    if (isNaN(index)) {
      console.error('Error: Please provide a valid task index.');
      process.exit(1);
    }
    
    toggleTodo(index);
    break;
  }

  case "remove": {
    if (positional.length === 0) {
      console.error('Error: Please provide an index');
      console.log('Usage: node index.js remove <index>');
      process.exit(1);
    }
    
    const index = parseInt(positional[0], 10);
    if (isNaN(index)) {
      console.error('Error: Please provide a valid task index.');
      process.exit(1);
    }
    
    removeTodo(index);
    break;
  }

  case "edit": {
    if (positional.length === 0) {
      console.error('Error: Please provide an index');
      console.log('Usage: node index.js edit <index> [--description <text>] [--priority <level>] [--tags <tags>]');
      process.exit(1);
    }
    
    const index = parseInt(positional[0], 10);
    if (isNaN(index)) {
      console.error('Error: Please provide a valid task index.');
      process.exit(1);
    }
    
    const newDescription = flags.description;
    const newPriority = flags.priority;
    const newTags = flags.tags !== undefined ? parseTags(flags.tags) : undefined;
    
    if (newDescription === undefined && newPriority === undefined && newTags === undefined) {
      console.error('Error: Please provide at least one flag to edit (--description, --priority, or --tags)');
      process.exit(1);
    }
    
    editTodo(index, newDescription, newPriority, newTags);
    break;
  }

  case "clear": {
    clearTodos();
    break;
  }

  default:
    console.error(`Unknown command: ${command}`);
    showHelp();
    process.exit(1);
}