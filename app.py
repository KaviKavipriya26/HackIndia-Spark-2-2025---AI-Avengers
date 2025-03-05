from flask import Flask, request, jsonify, render_template
from collections import defaultdict
import threading
import time
import datetime

app = Flask(__name__, template_folder="templates", static_folder="static")
tasks = []

# Helper function to assign priority values
def priority_value(priority):
    return {"High": 3, "Medium": 2, "Low": 1}.get(priority, 0)

# Task sorting function
def sort_tasks(tasks):
    graph = defaultdict(list)
    task_dict = {}

    for task in tasks:
        task_dict[task["id"]] = task
        for dep in task["dependencies"]:
            graph[dep].append(task["id"])

    sorted_tasks = []
    visited = set()

    def dfs(task_id):
        if task_id in visited:
            return
        visited.add(task_id)
        for dep in graph[task_id]:
            dfs(dep)
        sorted_tasks.append(task_dict[task_id])

    for task in tasks:
        if task["id"] not in visited:
            dfs(task["id"])

    sorted_tasks.sort(key=lambda t: (t["deadline"], -priority_value(t["priority"])))

    return sorted_tasks

# Background scheduler to check for due tasks
def task_scheduler():
    while True:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        for task in tasks:
            if task["deadline"] == now:
                print(f"ALERT: Task '{task['name']}' is due now!")
        time.sleep(60)  # Check every minute

# Start scheduler in a separate thread
threading.Thread(target=task_scheduler, daemon=True).start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add_task", methods=["POST"])
def add_task():
    data = request.get_json()
    tasks.append(data)
    return jsonify({"message": "Task added successfully!"})

@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify({"tasks": tasks})

@app.route("/schedule", methods=["POST"])
def schedule_tasks():
    global tasks
    optimized_tasks = sort_tasks(tasks)
    return jsonify({"optimizedTasks": optimized_tasks})

if __name__ == "__main__":
    app.run(debug=True)