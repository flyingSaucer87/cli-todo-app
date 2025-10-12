import time

tasks = []
def add_task():
    task = input("Enter new task: ")
    tasks.append({'name': task, 'completed': False})

def select_task():
    for idx, task in enumerate(tasks):
        status = "Done" if task['completed'] else "Pending"
        print(f"{idx+1}. {task['name']} [{status}]")
    choice = int(input("Select a task number to focus on: ")) - 1
    return choice

def start_pomodoro(task_index, work_duration=25, break_duration=5):
    print(f"Starting Pomodoro for: {tasks[task_index]['name']}")
    print(f"Work interval: {work_duration} minutes.")
    for i in range(work_duration*60, 0, -1):
        mins, secs = divmod(i, 60)
        print(f"{mins:02d}:{secs:02d}", end='\r')
        time.sleep(1)
    print("\nPomodoro complete! Time for a break.")
    tasks[task_index]['completed'] = True
    time.sleep(break_duration*60)
    print("Break over!")

def main():
    while True:
        print("\n1. Add Task\n2. Start Pomodoro\n3. View Tasks\n4. Exit")
        choice = input("Choose an option: ")
        if choice == '1':
            add_task()
        elif choice == '2':
            if not tasks:
                print("No tasks available!")
                continue
            idx = select_task()
            start_pomodoro(idx)
        elif choice == '3':
            select_task()
        elif choice == '4':
            break

if __name__ == "__main__":
    main()
