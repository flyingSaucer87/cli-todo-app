// todo.test.js
const fs = require('fs');
jest.mock('fs');
const todo = require('./todo');

describe('Unified Task Model - todo.js', () => {
  let fileContent;

  beforeEach(() => {
    todo.clearTodos();
    fs.existsSync.mockClear();
    fs.readFileSync.mockClear();
    fs.writeFileSync.mockClear();
    fileContent = '[]';
    fs.existsSync.mockReturnValue(true);
    fs.readFileSync.mockImplementation(() => fileContent);
    fs.writeFileSync.mockImplementation((_, data) => {
      fileContent = data;
    });
    todo.loadTodos();
  });

  test('migrates legacy string tasks', () => {
    fileContent = JSON.stringify(['a', 'b']);
    todo.loadTodos();
    const parsed = JSON.parse(fileContent);
    expect(parsed[0]).toHaveProperty('description', 'a');
    expect(parsed[0]).toHaveProperty('priority', 'Medium');
  });

  test('adds tasks with metadata', () => {
    todo.addTodo('T1', 'High', ['x']);
    todo.addTodo('T2', 'Medium', []);
    todo.addTodo('T3', 'Low', ['y','z']);
    expect(todo.todos.length).toBe(3);
    expect(todo.todos).toEqual(
      expect.arrayContaining([
        expect.objectContaining({description:'T1',priority:'High',tags:['x']}),
        expect.objectContaining({description:'T2',priority:'Medium'}),
        expect.objectContaining({description:'T3',priority:'Low',tags:['y','z']})
      ])
    );
  });

  test('rejects invalid priority', () => {
    console.log = jest.fn();
    todo.addTodo('X', 'Wrong');
    expect(todo.todos.length).toBe(0);
    expect(console.log).toHaveBeenCalledWith('Invalid priority. Use Low, Medium, or High.');
  });

  test('lists and filters correctly', () => {
    todo.addTodo('A', 'High', []);
    todo.addTodo('B', 'Low', ['t']);
    todo.completeTodo(0);
    let out = [];
    console.log = (l)=>out.push(l);
    todo.listTodos(true,null);
    expect(out[0]).toContain('A');
    out=[];
    todo.listTodos(false,'t');
    expect(out[0]).toContain('B');
  });

  test('edits tasks by display index', () => {
    todo.addTodo('Old','Medium',['i']);
    todo.editTodo(0,'New','High',['u']);
    expect(todo.todos[0]).toMatchObject({description:'New',priority:'High',tags:['u']});
  });

  test('completes by display index', () => {
    todo.addTodo('C','Medium',[]);
    todo.completeTodo(0);
    expect(todo.todos[0].completed).toBe(true);
  });

  test('removes and clears correctly', () => {
    todo.addTodo('R1');
    todo.addTodo('R2');
    todo.removeTodo(0);
    expect(todo.todos.length).toBe(1);
    todo.clearTodos();
    expect(todo.todos.length).toBe(0);
  });

  test('handles invalid indexes gracefully', () => {
    console.log = jest.fn();
    todo.completeTodo(5);
    expect(console.log).toHaveBeenCalledWith('Invalid task index.');
    todo.removeTodo(-1);
    expect(console.log).toHaveBeenCalledWith('Invalid task index.');
    todo.editTodo(3);
    expect(console.log).toHaveBeenCalledWith('Invalid task index.');
  });

  test('sorts by priority in list', () => {
    todo.addTodo('M','Medium',[]);
    todo.addTodo('L','Low',[]);
    todo.addTodo('H','High',[]);
    let out=[]; console.log=(l)=>out.push(l);
    todo.listTodos();
    expect(out[0]).toContain('(High)');
    expect(out[1]).toContain('(Medium)');
    expect(out[2]).toContain('(Low)');
  });
});

