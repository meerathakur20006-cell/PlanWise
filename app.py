
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path

app = Flask(__name__)
APP_VERSION = "1.0.2"
DATABASE = Path(__file__).with_name("planwise.db")

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_db_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT DEFAULT '',
                due_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Planned',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                priority TEXT NOT NULL DEFAULT 'Medium',
                due_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'To Do',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        """)


@app.route("/")
def dashboard():
    with get_db_connection() as connection:
        projects = connection.execute("""
            SELECT * FROM projects ORDER BY id DESC
        """).fetchall()

        tasks = connection.execute("""
            SELECT tasks.*, projects.name AS project_name
            FROM tasks
            JOIN projects ON tasks.project_id = projects.id
            ORDER BY tasks.id DESC
        """).fetchall()

    stats = {
        "total_projects": len(projects),
        "active_projects": sum(
            project["status"] == "In Progress" for project in projects
        ),
        "completed_tasks": sum(
            project["status"] == "Completed" for project in projects
        ),
        "overdue_tasks": 0,
    }

    return render_template(
        "index.html",
        stats=stats,
        projects=projects,
        tasks=tasks,
    )


@app.route("/projects/new", methods=["POST"])
def create_project():
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()
    due_date = request.form.get("due_date", "").strip()

    if not name or not category or not due_date:
        return "Project name, category, and due date are required.", 400

    with get_db_connection() as connection:
        connection.execute("""
            INSERT INTO projects (name, category, description, due_date)
            VALUES (?, ?, ?, ?)
        """, (name, category, description, due_date))

    return redirect(url_for("dashboard"))


@app.route("/tasks/new", methods=["POST"])
def create_task():
    project_id = request.form.get("project_id", type=int)
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    priority = request.form.get("priority", "Medium")
    due_date = request.form.get("due_date", "").strip()

    if not project_id or not title or not due_date:
        return "Project, task title, and deadline are required.", 400

    if priority not in ("Low", "Medium", "High"):
        return "Invalid priority.", 400

    with get_db_connection() as connection:
        project = connection.execute(
            "SELECT id FROM projects WHERE id = ?", (project_id,)
        ).fetchone()

        if project is None:
            return "Selected project does not exist.", 400

        connection.execute("""
            INSERT INTO tasks
                (project_id, title, description, priority, due_date)
            VALUES (?, ?, ?, ?, ?)
        """, (project_id, title, description, priority, due_date))

    return redirect(url_for("dashboard"))


@app.route("/tasks/<int:task_id>/status", methods=["POST"])
def update_task_status(task_id):
    status = request.form.get("status", "")

    if status not in ("To Do", "In Progress", "Completed"):
        return "Invalid task status.", 400

    with get_db_connection() as connection:
        connection.execute("""
            UPDATE tasks SET status = ? WHERE id = ?
        """, (status, task_id))

    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
