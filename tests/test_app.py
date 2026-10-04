import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import os
import pytest

import app as app_module


@pytest.fixture()
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test_aceest_fitness.db"

    monkeypatch.setattr(app_module, "DATABASE", str(test_db))

    app_module.app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key"
    )

    app_module.init_db()

    with app_module.app.test_client() as client:
        yield client


def login(client):
    return client.post(
        "/",
        data={
            "username": "admin",
            "password": "admin"
        },
        follow_redirects=True
    )


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "UP"


def test_login(client):
    response = login(client)

    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_add_client(client):
    login(client)

    response = client.post(
        "/clients/add",
        data={
            "name": "Test Client",
            "age": "30",
            "height": "175",
            "weight": "75",
            "target_weight": "70",
            "target_adherence": "90",
            "calories": "2200",
            "membership_status": "Active",
            "membership_end": "2027-12-31",
            "program": "Beginner"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Test Client" in response.data


def test_generate_ai_program(client):
    login(client)

    client.post(
        "/clients/add",
        data={
            "name": "AI Test Client",
            "age": "28",
            "height": "178",
            "weight": "80",
            "target_weight": "72",
            "target_adherence": "90",
            "calories": "2300",
            "membership_status": "Active",
            "membership_end": "2027-12-31",
            "program": ""
        }
    )

    response = client.post(
        "/clients/1/generate-program",
        data={"goal": "Muscle Gain"},
        follow_redirects=True
    )

    assert response.status_code == 200

    page = client.get("/clients")
    assert page.status_code == 200
    assert any(program in page.data for program in [
        b"Push/Pull/Legs",
        b"Upper/Lower Split",
        b"Full Body Strength"
    ])


def test_add_workout(client):
    login(client)

    client.post(
        "/clients/add",
        data={
            "name": "Workout Client",
            "age": "30",
            "height": "180",
            "weight": "78",
            "target_weight": "72",
            "target_adherence": "90",
            "calories": "2400",
            "membership_status": "Active",
            "membership_end": "2027-12-31",
            "program": "Full Body"
        }
    )

    response = client.post(
        "/workouts/add",
        data={
            "client_id": "1",
            "date": "2026-10-04",
            "type": "Strength",
            "duration": "60",
            "notes": "Test strength workout"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Workout Client" in response.data

    with app_module.get_db() as conn:
        workout = conn.execute(
            "SELECT client_name, workout_type, duration_min, notes FROM workouts WHERE client_name = ?",
            ("Workout Client",)
        ).fetchone()

    assert workout is not None
    assert workout["workout_type"] == "Strength"
    assert workout["duration_min"] == 60
    assert workout["notes"] == "Test strength workout"


def test_add_exercise(client):
    login(client)

    client.post(
        "/clients/add",
        data={
            "name": "Exercise Client",
            "age": "25",
            "height": "175",
            "weight": "70",
            "target_weight": "68",
            "target_adherence": "90",
            "calories": "2200",
            "membership_status": "Active",
            "membership_end": "2027-12-31",
            "program": "Strength"
        }
    )

    client.post(
        "/workouts/add",
        data={
            "client_id": "1",
            "date": "2026-10-04",
            "type": "Strength",
            "duration": "60",
            "notes": "Exercise test"
        }
    )

    with app_module.get_db() as conn:
        workout = conn.execute(
            "SELECT id FROM workouts WHERE client_name = ? ORDER BY id DESC LIMIT 1",
            ("Exercise Client",)
        ).fetchone()

    assert workout is not None
    workout_id = workout["id"]

    response = client.post(
        f"/workouts/{workout_id}/exercises/add",
        data={
            "name": "Bench Press",
            "sets": "3",
            "reps": "10",
            "weight": "60"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Bench Press" in response.data
    assert b"3 sets x 10 reps" in response.data


def test_progress_and_metrics(client):
    login(client)

    client.post(
        "/clients/add",
        data={
            "name": "Progress Client",
            "age": "29",
            "height": "178",
            "weight": "75",
            "target_weight": "70",
            "target_adherence": "95",
            "calories": "2300",
            "membership_status": "Active",
            "membership_end": "2027-12-31",
            "program": "Fitness"
        }
    )

    progress_response = client.post(
        "/clients/1/progress",
        data={
            "week": "1",
            "adherence": "90"
        },
        follow_redirects=True
    )

    assert progress_response.status_code == 200

    metrics_response = client.post(
        "/clients/1/metrics",
        data={
            "date": "2026-10-04",
            "weight": "74",
            "waist": "32",
            "bodyfat": "20"
        },
        follow_redirects=True
    )

    assert metrics_response.status_code == 200

    summary = client.get("/clients/1/summary")

    assert summary.status_code == 200
    assert b"90.0" in summary.data
    assert b"74.0" in summary.data


def test_adherence_chart(client):
    login(client)

    client.post(
        "/clients/add",
        data={
            "name": "Chart Client",
            "age": "30",
            "height": "178",
            "weight": "75",
            "target_weight": "70",
            "target_adherence": "90",
            "calories": "2300",
            "membership_status": "Active",
            "membership_end": "2027-12-31",
            "program": "Fitness"
        }
    )

    client.post(
        "/clients/1/progress",
        data={
            "week": "1",
            "adherence": "90"
        }
    )

    response = client.get("/clients/1/adherence-chart")

    assert response.status_code == 200
    assert response.content_type == "image/png"
    assert response.data.startswith(b"\x89PNG")


def test_pdf_report(client):
    login(client)

    client.post(
        "/clients/add",
        data={
            "name": "PDF Client",
            "age": "30",
            "height": "178",
            "weight": "75",
            "target_weight": "70",
            "target_adherence": "90",
            "calories": "2300",
            "membership_status": "Active",
            "membership_end": "2027-12-31",
            "program": "Fitness"
        }
    )

    response = client.get("/clients/1/report")

    assert response.status_code == 200
    assert response.content_type == "application/pdf"
    assert response.data.startswith(b"%PDF")
