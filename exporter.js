// exporter.js
// Simple no-deps exporter/importer for the cli-todo-app (CSV / Markdown / ICS)
// Put at project root next to index.js and todos.json

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const TODO_FILE = path.join(__dirname, "todos.json");

// --- low-level IO ---
function loadTodos() {
  if (!fs.existsSync(TODO_FILE)) return [];
  try {
    const raw = fs.readFileSync(TODO_FILE, "utf8").trim();
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    // repo may store either array or object; handle common shapes
    if (Array.isArray(parsed)) return parsed;
    if (parsed && Array.isArray(parsed.todos)) return parsed.todos;
    return [];
  } catch (err) {
    console.error("Failed to read/parse todos.json:", err.message);
    return [];
  }
}

function saveTodos(todos) {
  try {
    fs.writeFileSync(TODO_FILE, JSON.stringify(todos, null, 2), "utf8");
  } catch (err) {
    console.error("Failed to write todos.json:", err.message);
  }
}

// --- normalization for varying todo shapes ---
function normalize(raw) {
  if (typeof raw === "string") {
    return {
      text: raw,
      completed: false,
      priority: null,
      created_at: new Date().toISOString(),
      due: null,
    };
  }
  // try common fields
  return {
    text: raw.text || raw.task || raw.title || "",
    completed: !!raw.completed,
    priority: raw.priority || raw.prio || null,
    created_at: raw.created_at || raw.created || new Date().toISOString(),
    due: raw.due || raw.due_date || raw.dueDate || null,
    // keep any extra fields for round-trip
    __extra: Object.assign({}, raw),
  };
}

// --- CSV helpers ---
function escapeCsvCell(v) {
  if (v === undefined || v === null) return "";
  const s = String(v);
  return `"${s.replace(/"/g, '""')}"`;
}

function parseCSVLine(line) {
  const out = [];
  let cur = "";
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (inQuotes) {
      if (ch === '"') {
        if (line[i + 1] === '"') {
          cur += '"';
          i++;
        } else {
          inQuotes = false;
        }
      } else {
        cur += ch;
      }
    } else {
      if (ch === ",") {
        out.push(cur);
        cur = "";
      } else if (ch === '"') {
        inQuotes = true;
      } else {
        cur += ch;
      }
    }
  }
  out.push(cur);
  return out;
}

// --- Markdown parsing helper ---
const TASK_MD_RE = /^\s*-\s*\[(x|X| )\]\s*(.+)$/;

// --- ICS helpers ---
function pad(n) {
  return String(n).padStart(2, "0");
}

function toICSDate(iso) {
  const d = new Date(iso);
  return `${d.getUTCFullYear()}${pad(d.getUTCMonth() + 1)}${pad(
    d.getUTCDate()
  )}T${pad(d.getUTCHours())}${pad(d.getUTCMinutes())}${pad(
    d.getUTCSeconds()
  )}Z`;
}

function escapeICSText(s) {
  if (s === undefined || s === null) return "";
  return String(s)
    .replace(/\\/g, "\\\\")
    .replace(/;/g, "\\;")
    .replace(/,/g, "\\,")
    .replace(/\r?\n/g, "\\n");
}

// --- export implementations ---
function exportToCSV(outPath) {
  const todos = loadTodos().map(normalize);
  const headers = ["text", "priority", "completed", "created_at", "due"];
  const lines = [headers.join(",")];
  todos.forEach((t) => {
    const row = headers.map((h) => escapeCsvCell(t[h]));
    lines.push(row.join(","));
  });
  fs.writeFileSync(outPath, lines.join("\n"), "utf8");
  console.log(`Exported ${todos.length} tasks → ${outPath}`);
}

function exportToMarkdown(outPath) {
  const todos = loadTodos().map(normalize);
  const out = ["# Tasks", ""];
  todos.forEach((t) => {
    const check = t.completed ? "x" : " ";
    let line = `- [${check}] ${t.text || "(no text)"}`;
    if (t.priority) line += `  _(priority: ${t.priority})_`;
    out.push(line);
    if (t.due) out.push(`  - Due: ${t.due}`);
    out.push("");
  });
  fs.writeFileSync(outPath, out.join("\n"), "utf8");
  console.log(`Exported ${todos.length} tasks → ${outPath}`);
}

function exportToICS(outPath) {
  const todos = loadTodos().map(normalize);
  const header = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//cli-todo-app//EN"];
  const footer = ["END:VCALENDAR"];
  const events = [];
  todos.forEach((t, i) => {
    if (!t.due) return;
    const uid = `todo-${i}-${Date.now()}@cli-todo-app`;
    const dtstamp = toICSDate(new Date().toISOString());
    const dtstart = toICSDate(t.due);
    events.push(
      "BEGIN:VEVENT",
      `UID:${uid}`,
      `DTSTAMP:${dtstamp}`,
      `DTSTART:${dtstart}`,
      `SUMMARY:${escapeICSText(t.text)}`,
      t.text ? `DESCRIPTION:${escapeICSText(t.text)}` : "",
      "END:VEVENT"
    );
  });
  fs.writeFileSync(
    outPath,
    header.concat(events).concat(footer).join("\r\n"),
    "utf8"
  );
  console.log(
    `Exported ${(events.length / 6) | 0} events → ${outPath} (tasks with due dates only)`
  );
}

// --- import implementations ---
function importFromCSV(inPath) {
  if (!fs.existsSync(inPath)) {
    console.error("Import failed: file not found:", inPath);
    return;
  }
  const raw = fs.readFileSync(inPath, "utf8").trim();
  if (!raw) {
    console.error("Import failed: file empty");
    return;
  }
  const lines = raw.split(/\r?\n/);
  const headers = parseCSVLine(lines[0]).map((h) => h.trim());
  const items = [];
  for (let i = 1; i < lines.length; i++) {
    if (!lines[i].trim()) continue;
    const cols = parseCSVLine(lines[i]);
    const obj = {};
    headers.forEach((h, idx) => (obj[h || `col${idx}`] = cols[idx] || ""));
    items.push(
      normalize({
        text: obj.text || obj.task || obj.title || "",
        priority: obj.priority || null,
        completed:
          obj.completed === "true" ||
          obj.completed === "1" ||
          String(obj.completed).toLowerCase() === "x",
        created_at: obj.created_at || new Date().toISOString(),
        due: obj.due || null,
      })
    );
  }
  if (!items.length) {
    console.log("No rows imported.");
    return;
  }
  const todos = loadTodos();
  todos.push(...items);
  saveTodos(todos);
  console.log(`Imported ${items.length} tasks from ${inPath}`);
}

function importFromMarkdown(inPath) {
  if (!fs.existsSync(inPath)) {
    console.error("Import failed: file not found:", inPath);
    return;
  }
  const raw = fs.readFileSync(inPath, "utf8");
  const lines = raw.split(/\r?\n/);
  const items = [];
  for (const L of lines) {
    const m = L.match(TASK_MD_RE);
    if (m) {
      const completed = m[1].toLowerCase() === "x";
      const text = m[2].trim();
      items.push(normalize({ text, completed }));
    }
  }
  if (!items.length) {
    console.log("No tasks found in Markdown file.");
    return;
  }
  const todos = loadTodos();
  todos.push(...items);
  saveTodos(todos);
  console.log(`Imported ${items.length} tasks from ${inPath}`);
}

// --- public API ---
export function exportTodos(format, outPath) {
  format = (format || "csv").toLowerCase();
  outPath = outPath || `todos.${format}`;
  if (format === "csv") return exportToCSV(outPath);
  if (format === "md" || format === "markdown") return exportToMarkdown(outPath);
  if (format === "ics") return exportToICS(outPath);
  console.error("Unknown export format:", format);
}

export function importTodos(format, inPath) {
  format = (format || "csv").toLowerCase();
  if (!inPath) {
    console.error("Usage: node index.js import <format> <file>");
    return;
  }
  if (format === "csv") return importFromCSV(inPath);
  if (format === "md" || format === "markdown") return importFromMarkdown(inPath);
  console.error("Unknown import format:", format);
}
