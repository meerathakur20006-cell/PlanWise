
import pytest
import app as planwise


@pytest.fixture
def client(tmp_path):
    # Use a temporary database so tests do not change real project data.
    planwise.DATABASE = tmp_path / "test_planwise.db"
    planwise.app.config["TESTING"] = True

    planwise.initialize_database()

    with planwise.app.test_client() as test_client:
        yield test_client


def test_dashboard_loads(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"PlanWise" in response.data


def test_create_project(client):
    response = client.post(
        "/projects/new",
        data={
            "name": "Test Project",
            "category": "Development",
            "description": "A project created during testing",
            "due_date": "2026-12-31",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Test Project" in response.data


def test_create_task(client):
    client.post(
        "/projects/new",
        data={
            "name": "Test Project",
            "category": "Development",
            "description": "Testing project",
            "due_date": "2026-12-31",
        },
    )

    with planwise.get_db_connection() as connection:
        project = connection.execute(
            "SELECT id FROM projects WHERE name = ?",
            ("Test Project",),
        ).fetchone()

    response = client.post(
        "/tasks/new",
        data={
            "project_id": str(project["id"]),
            "title": "Write automated tests",
            "description": "Test task creation",
            "priority": "High",
            "due_date": "2026-11-30",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Write automated tests" in response.data


def test_update_task_status(client):
    client.post(
        "/projects/new",
        data={
            "name": "Test Project",
            "category": "Development",
            "due_date": "2026-12-31",
        },
    )

    with planwise.get_db_connection() as connection:
        project = connection.execute(
            "SELECT id FROM projects WHERE name = ?",
            ("Test Project",),
        ).fetchone()

        connection.execute(
            """
            INSERT INTO tasks (project_id, title, priority, due_date)
            VALUES (?, ?, ?, ?)
            """,
            (project["id"], "Test Task", "Medium", "2026-11-30"),
        )

        task = connection.execute(
            "SELECT id FROM tasks WHERE title = ?",
            ("Test Task",),
        ).fetchone()

    response = client.post(
        f"/tasks/{task['id']}/status",
        data={"status": "Completed"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Completed" in response.data
