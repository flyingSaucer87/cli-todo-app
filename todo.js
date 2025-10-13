import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const TODO_FILE = process.env.TODO_FILE || path.join(__dirname, 'todos.json');

// Colors for terminal output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  gray: '\x1b[90m',
  red: '\x1b[31m',
  strikethrough: '\x1b[9m'
};

const VALID_PRIORITIES = ['High', 'Medium', 'Low'];

function loadTodos() {
  try {
    if (!fs.existsSync(TODO_FILE)) {
      return [];
    }
    const data = fs.readFileSync(TODO_FILE, 'utf8');
    const todos = JSON.parse(data);
    
    // Ensure all todos have required fields (backward compatibility)
    return todos.map(todo => {
      if (typeof todo === 'string') {
        return { 
          task: todo, 
          completed: false,
          priority: 'Medium',
          tags: []
        };
      }
      return { 
        task: todo.task || '',
        completed: todo.completed || false,
        priority: todo.priority || 'Medium',
        tags: todo.tags || []
      };
    });
  } catch (error) {
    console.error('Error loading todos:', error.message);
    return [];
  }
}

function saveTodos(todos) {
  try {
    fs.writeFileSync(TODO_FILE, JSON.stringify(todos, null, 2));
  } catch (error) {
    console.error('Error saving todos:', error.message);
  }
}

function sortTodosByPriority(todos) {
  const priorityOrder = { 'High': 0, 'Medium': 1, 'Low': 2 };
  return [...todos].sort((a, b) => {
    // Completed tasks go to the bottom
    if (a.completed !== b.completed) {
      return a.completed ? 1 : -1;
    }
    // Sort by priority
    return priorityOrder[a.priority] - priorityOrder[b.priority];
  });
}

function calculateProgress(todos) {
  if (todos.length === 0) {
    return { completed: 0, total: 0, percentage: 0 };
  }
  
  const completed = todos.filter(t => t.completed).length;
  const total = todos.length;
  const percentage = Math.round((completed / total) * 100);
  
  return { completed, total, percentage };
}

function createProgressBar(percentage, width = 30) {
  const filledLength = Math.round((width * percentage) / 100);
  const emptyLength = width - filledLength;
  
  const filled = '█'.repeat(filledLength);
  const empty = '░'.repeat(emptyLength);
  
  return `${colors.green}${filled}${colors.gray}${empty}${colors.reset}`;
}

function displayProgressBar(todos) {
  const { completed, total, percentage } = calculateProgress(todos);
  const progressBar = createProgressBar(percentage);
  
  console.log(`\n${colors.cyan}Progress:${colors.reset} ${progressBar} ${colors.green}${percentage}%${colors.reset} (${completed}/${total} tasks completed)\n`);
}

function getPriorityColor(priority) {
  switch (priority) {
    case 'High':
      return colors.red;
    case 'Medium':
      return colors.yellow;
    case 'Low':
      return colors.blue;
    default:
      return colors.reset;
  }
}

export function addTodo(task, priority = 'Medium', tags = []) {
  if (!task || task.trim() === '') {
    console.error('Error: Task description cannot be empty');
    process.exit(1);
  }

  if (!VALID_PRIORITIES.includes(priority)) {
    console.error(`Error: Invalid priority "${priority}". Valid priorities are: ${VALID_PRIORITIES.join(', ')}`);
    process.exit(1);
  }

  const todos = loadTodos();
  todos.push({ 
    task: task.trim(), 
    completed: false,
    priority,
    tags
  });
  saveTodos(todos);
  console.log(`${colors.green}✓${colors.reset} Added: "${task}"`);
  displayProgressBar(todos);
}

export function listTodos(filters = {}) {
  let todos = loadTodos();
  
  if (todos.length === 0) {
    console.log('No todos found. Add one with: node index.js add "Your task"');
    return;
  }

  // Apply filters
  if (filters.completed !== undefined) {
    todos = todos.filter(t => t.completed === filters.completed);
  }

  if (filters.tag) {
    todos = todos.filter(t => t.tags && t.tags.includes(filters.tag));
  }

  // Sort by priority
  todos = sortTodosByPriority(todos);
  
  displayProgressBar(loadTodos()); // Show overall progress
  
  console.log(`${colors.cyan}Your Tasks:${colors.reset}`);
  
  // Get original indices
  const allTodos = loadTodos();
  
  todos.forEach((todo) => {
    const originalIndex = allTodos.findIndex(t => 
      t.task === todo.task && 
      t.completed === todo.completed && 
      t.priority === todo.priority &&
      JSON.stringify(t.tags) === JSON.stringify(todo.tags)
    );
    
    const checkbox = todo.completed ? `${colors.green}[✓]${colors.reset}` : '[ ]';
    const taskText = todo.completed 
      ? `${colors.gray}${colors.strikethrough}${todo.task}${colors.reset}` 
      : todo.task;
    
    const priorityColor = getPriorityColor(todo.priority);
    const priorityLabel = `${priorityColor}[${todo.priority}]${colors.reset}`;
    
    const tagsText = todo.tags && todo.tags.length > 0 
      ? ` ${colors.gray}#${todo.tags.join(' #')}${colors.reset}`
      : '';
    
    console.log(`${originalIndex}. ${checkbox} ${priorityLabel} ${taskText}${tagsText}`);
  });
}

export function editTodo(index, newTask, newPriority, newTags) {
  const todos = loadTodos();
  
  if (index < 0 || index >= todos.length) {
    console.error('Invalid todo index');
    process.exit(1);
  }
  
  const oldTask = todos[index].task;
  const oldPriority = todos[index].priority;
  const oldTags = todos[index].tags;
  
  if (newTask !== undefined) {
    if (newTask.trim() === '') {
      console.error('Error: Task description cannot be empty');
      process.exit(1);
    }
    todos[index].task = newTask.trim();
  }
  
  if (newPriority !== undefined) {
    if (!VALID_PRIORITIES.includes(newPriority)) {
      console.error(`Error: Invalid priority "${newPriority}". Valid priorities are: ${VALID_PRIORITIES.join(', ')}`);
      process.exit(1);
    }
    todos[index].priority = newPriority;
  }
  
  if (newTags !== undefined) {
    todos[index].tags = newTags;
  }
  
  saveTodos(todos);
  
  let changes = [];
  if (newTask !== undefined && newTask !== oldTask) {
    changes.push(`task: "${oldTask}" → "${todos[index].task}"`);
  }
  if (newPriority !== undefined && newPriority !== oldPriority) {
    changes.push(`priority: ${oldPriority} → ${newPriority}`);
  }
  if (newTags !== undefined && JSON.stringify(newTags) !== JSON.stringify(oldTags)) {
    changes.push(`tags: [${oldTags.join(', ')}] → [${newTags.join(', ')}]`);
  }
  
  if (changes.length > 0) {
    console.log(`${colors.green}✓${colors.reset} Updated task ${index}: ${changes.join(', ')}`);
  } else {
    console.log(`${colors.green}✓${colors.reset} Updated task ${index}: "${todos[index].task}"`);
  }
}

export function removeTodo(index) {
  const todos = loadTodos();
  
  if (index < 0 || index >= todos.length) {
    console.error('Invalid todo index');
    process.exit(1);
  }
  
  const removed = todos.splice(index, 1);
  saveTodos(todos);
  console.log(`${colors.green}✓${colors.reset} Removed: "${removed[0].task}"`);
  displayProgressBar(todos);
}

export function toggleTodo(index) {
  const todos = loadTodos();
  
  if (index < 0 || index >= todos.length) {
    console.error('Invalid todo index');
    process.exit(1);
  }
  
  todos[index].completed = !todos[index].completed;
  saveTodos(todos);
  
  const status = todos[index].completed ? 'completed' : 'uncompleted';
  console.log(`${colors.green}✓${colors.reset} Marked task ${index} as ${status}: "${todos[index].task}"`);
  displayProgressBar(todos);
}

export function clearTodos() {
  saveTodos([]);
  console.log(`${colors.green}✓${colors.reset} All todos cleared`);
}