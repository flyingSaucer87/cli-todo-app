import { addTodo, listTodos, removeTodo, editTodo, completeTodo, clearTodos } from "./todo.js";
import * as exporter from "./exporter.js";
import process from "process";
import chalk from "chalk";
import { themes } from "./themes.js";
import fs from "fs";

// Load config file if exists
let configTheme = "dark";
try {
  if (fs.existsSync("config.json")) {
    const configData = JSON.parse(fs.readFileSync("config.json", "utf-8"));
    if (configData.theme && themes[configData.theme]) {
      configTheme = configData.theme;
    }
  }
} catch (err) {
  console.error("Failed to read config file:", err);
}

// CLI argument override: e.g. node index.js --theme neon
const args = process.argv.slice(2);
const themeArgIndex = args.indexOf("--theme");
if (themeArgIndex !== -1 && args[themeArgIndex + 1]) {
  const argTheme = args[themeArgIndex + 1];
  if (themes[argTheme]) configTheme = argTheme;
}

const theme = themes[configTheme];
const color = (text) => chalk.hex(theme.primary)(text);
const accent = (text) => chalk.hex(theme.accent)(text);
const command = args[0];

if (command === "help" || args.length === 0) {
  console.log(`
Usage:
  node index.js add "Task description" [--priority High|Medium|Low] [--tags tag1,tag2]
  node index.js list [--completed] [--pending] [--tags tag1,tag2]
  node index.js complete <index> - Mark task as completed
  node index.js remove <index> - Remove task by index
  node index.js edit <index> [--description "New desc"] [--priority High|Medium|Low] [--tags tag1,tag2]
  node index.js clear - Remove all tasks

Examples:
  node index.js add "Buy groceries" --priority High --tags shopping,urgent
  node index.js list --pending
  node index.js list --tags work,urgent
  node index.js complete 0
`);
  process.exit(0);
}

function parseArgs(args) {
  const parsed = { positional: [], flags: {} };
  let i = 0;
  while (i < args.length) {
    if (args[i].startsWith("--")) {
      const flag = args[i].substring(2);
      if (i + 1 < args.length && !args[i + 1].startsWith("--")) {
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
    const description = parsed.positional[0];
    if (!description || !description.trim()) {
      console.log("Error: Please provide a task description.");
      process.exit(1);
    }
    const priority = parsed.flags.priority || "Medium";
    const tags = parsed.flags.tags ? parsed.flags.tags.split(",").map(t => t.trim()) : [];
    addTodo(description, priority, tags);
    console.log(`✓ Added: ${description} (Priority: ${priority}, Tags: [${tags.join(", ")}])`);
    break;

  case "list":
    let filterCompleted = null;
    if (parsed.flags.completed) filterCompleted = true;
    if (parsed.flags.pending) filterCompleted = false;
    const tagsToFilter = parsed.flags.tags ? parsed.flags.tags.split(',').map(t => t.trim()) : null;
    listTodos(filterCompleted, tagsToFilter);
    break;

  case "complete":
    const completeIndex = parseInt(parsed.positional[0], 10);
    if (isNaN(completeIndex)) {
      console.log("Error: Please provide a valid task index.");
      process.exit(1);
    }
    completeTodo(completeIndex);
    break;

  case "remove":
    const removeIndex = parseInt(parsed.positional[0], 10);
    if (isNaN(removeIndex)) {
      console.log("Error: Please provide a valid task index.");
      process.exit(1);
    }
    removeTodo(removeIndex);
    break;

  case "edit":
    const editIndex = parseInt(parsed.positional[0], 10);
    if (isNaN(editIndex)) {
      console.log("Error: Please provide a valid task index.");
      process.exit(1);
    }
    const newTags = parsed.flags.tags ? parsed.flags.tags.split(",").map(t => t.trim()) : undefined;
    editTodo(editIndex, parsed.flags.description, parsed.flags.priority, newTags);
    break;

  case "clear":
    clearTodos();
    console.log("All tasks have been cleared.");
    break;

  case "export":
    const format = process.argv[3] || "csv";
    const out = process.argv[4] || `todos.${format}`;
    exporter.exportTodos(format, out);
    process.exit(0);

  case "import":
    const inFormat = process.argv[3] || "csv";
    const infile = process.argv[4];
    if (!infile) {
      console.error("Usage: node index.js import <csv|md> <file>");
      process.exit(1);
    }
    exporter.importTodos(inFormat, infile);
    process.exit(0);

  default:
    console.log("Unknown command. Use 'help' for usage information.");
}
