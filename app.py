from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime, date
import random
import os

app = Flask(__name__)
app.secret_key = "aceest-dev-secret-key"

DATABASE = os.path.join(os.path.dirname(__file__), "aceest_fitness.db")


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            height REAL,
            weight REAL,
            program TEXT,
            calories INTEGER,
            target_weight REAL,
            target_adherence REAL,
            membership_status TEXT,
            membership_end TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            week INTEGER,
            adherence REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            date TEXT,
            workout_type TEXT,
            duration_min INTEGER,
            notes TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER,
            name TEXT,
            sets INTEGER,
            reps INTEGER,
            weight REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            date TEXT,
            weight REAL,
            waist REAL,
            bodyfat REAL
        )
    """)

    cursor.execute(
        "SELECT username FROM users WHERE username = ?",
        ("admin",)
    )

    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", "admin", "Admin")
        )

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# AI PROGRAM GENERATION
# ---------------------------------------------------------

PROGRAM_TEMPLATES = {
    "Fat Loss": [
        "Full Body HIIT",
        "Circuit Training",
        "Cardio + Weights"
    ],
    "Muscle Gain": [
        "Push/Pull/Legs",
        "Upper/Lower Split",
        "Full Body Strength"
    ],
    "Beginner": [
        "Full Body 3x/week",
        "Light Strength + Mobility"
    ]
}


def generate_ai_program(goal):
    programs = PROGRAM_TEMPLATES.get(goal, PROGRAM_TEMPLATES["Beginner"])
    return random.choice(programs)


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()

        user = conn.execute(
            """
            SELECT username, role
            FROM users
            WHERE username = ? AND password = ?
            """,
            (username, password)
        ).fetchone()

        conn.close()

        if user:
            session["username"] = user["username"]
            session["role"] = user["role"]

            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    client_count = conn.execute(
        "SELECT COUNT(*) AS count FROM clients"
    ).fetchone()["count"]

    workout_count = conn.execute(
        "SELECT COUNT(*) AS count FROM workouts"
    ).fetchone()["count"]

    conn.close()

    return render_template(
        "dashboard.html",
        client_count=client_count,
        workout_count=workout_count
    )


# ---------------------------------------------------------
# CLIENTS
# ---------------------------------------------------------

@app.route("/clients")
def clients():

    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    clients = conn.execute(
        "SELECT * FROM clients ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "clients.html",
        clients=clients
    )


@app.route("/clients/add", methods=["POST"])
def add_client():

    if "username" not in session:
        return redirect(url_for("login"))

    name = request.form.get("name", "").strip()

    if not name:
        flash("Client name is required.", "danger")
        return redirect(url_for("clients"))

    age = request.form.get("age") or None
    height = request.form.get("height") or None
    weight = request.form.get("weight") or None
    target_weight = request.form.get("target_weight") or None
    target_adherence = request.form.get("target_adherence") or None
    membership_status = request.form.get("membership_status", "")
    membership_end = request.form.get("membership_end", "")
    program = request.form.get("program", "")
    calories = request.form.get("calories") or None

    conn = get_db()

    conn.execute(
        """
        INSERT INTO clients
        (
            name,
            age,
            height,
            weight,
            program,
            calories,
            target_weight,
            target_adherence,
            membership_status,
            membership_end
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            age,
            height,
            weight,
            program,
            calories,
            target_weight,
            target_adherence,
            membership_status,
            membership_end
        )
    )

    conn.commit()
    conn.close()

    flash("Client added successfully.", "success")

    return redirect(url_for("clients"))


# ---------------------------------------------------------
# AI PROGRAM
# ---------------------------------------------------------

@app.route("/clients/<int:client_id>/generate-program", methods=["POST"])
def generate_program(client_id):

    if "username" not in session:
        return redirect(url_for("login"))

    goal = request.form.get("goal", "Beginner")

    program = generate_ai_program(goal)

    conn = get_db()

    conn.execute(
        """
        UPDATE clients
        SET program = ?
        WHERE id = ?
        """,
        (program, client_id)
    )

    conn.commit()
    conn.close()

    flash(
        f"AI program generated: {program}",
        "success"
    )

    return redirect(url_for("clients"))


# ---------------------------------------------------------
# MEMBERSHIP
# ---------------------------------------------------------

@app.route("/clients/<int:client_id>/membership")
def check_membership(client_id):

    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    client = conn.execute(
        "SELECT * FROM clients WHERE id = ?",
        (client_id,)
    ).fetchone()

    conn.close()

    if client is None:
        flash("Client not found.", "danger")
        return redirect(url_for("clients"))

    membership_end = client["membership_end"]

    if membership_end:

        try:
            end_date = datetime.strptime(
                membership_end,
                "%Y-%m-%d"
            ).date()

            if end_date >= date.today():
                status = "Active"
            else:
                status = "Expired"

        except ValueError:
            status = "Invalid membership date"

    else:
        status = "No membership end date"

    flash(
        f"{client['name']} membership: {status}",
        "info"
    )

    return redirect(url_for("clients"))


# ---------------------------------------------------------
# WORKOUTS
# ---------------------------------------------------------

@app.route("/workouts")
def workouts():

    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    workouts = conn.execute(
        """
        SELECT
            id,
            client_name,
            date,
            workout_type,
            duration_min,
            notes
        FROM workouts
        ORDER BY date DESC, id DESC
        """
    ).fetchall()

    clients = conn.execute(
        """
        SELECT id, name
        FROM clients
        ORDER BY name
        """
    ).fetchall()

    workout_list = []

    for workout in workouts:
        workout_data = dict(workout)
        workout_data["exercises"] = conn.execute(
            """
            SELECT id, name, sets, reps, weight
            FROM exercises
            WHERE workout_id = ?
            ORDER BY id
            """,
            (workout["id"],)
        ).fetchall()
        workout_list.append(workout_data)

    conn.close()

    return render_template(
        "workouts.html",
        workouts=workout_list,
        clients=clients
    )


@app.route("/workouts/add", methods=["POST"])
def add_workout():

    if "username" not in session:
        return redirect(url_for("login"))

    client_id = request.form.get("client_id")
    date = request.form.get("date")
    workout_type = request.form.get("type")
    duration = request.form.get("duration")
    notes = request.form.get("notes", "")

    conn = get_db()

    client = conn.execute(
        "SELECT name FROM clients WHERE id = ?",
        (client_id,)
    ).fetchone()

    if client is None:
        conn.close()
        flash("Client not found.")
        return redirect(url_for("workouts"))

    conn.execute(
        """
        INSERT INTO workouts
        (client_name, date, workout_type, duration_min, notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            client["name"],
            date,
            workout_type,
            duration,
            notes
        )
    )

    conn.commit()
    conn.close()

    flash("Workout added successfully.")
    return redirect(url_for("workouts"))


# ---------------------------------------------------------
# CLIENT SUMMARY
# ---------------------------------------------------------

@app.route("/clients/<int:client_id>/summary")
def client_summary(client_id):

    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    client = conn.execute(
        "SELECT * FROM clients WHERE id = ?",
        (client_id,)
    ).fetchone()

    if client is None:
        conn.close()
        flash("Client not found.", "danger")
        return redirect(url_for("clients"))

    progress = conn.execute(
        """
        SELECT *
        FROM progress
        WHERE client_name = ?
        ORDER BY week
        """,
        (client["name"],)
    ).fetchall()

    workouts = conn.execute(
        """
        SELECT *
        FROM workouts
        WHERE client_name = ?
        ORDER BY date DESC
        """,
        (client["name"],)
    ).fetchall()

    metrics = conn.execute(
        """
        SELECT *
        FROM metrics
        WHERE client_name = ?
        ORDER BY date DESC
        """,
        (client["name"],)
    ).fetchall()

    conn.close()

    return render_template(
        "client_summary.html",
        client=client,
        progress=progress,
        workouts=workouts,
        metrics=metrics
    )


# ---------------------------------------------------------
# ADHERENCE CHART
# ---------------------------------------------------------

@app.route("/clients/<int:client_id>/adherence-chart")
def adherence_chart(client_id):

    if "username" not in session:
        return redirect(url_for("login"))

    import io
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    conn = get_db()

    client = conn.execute(
        "SELECT name FROM clients WHERE id = ?",
        (client_id,)
    ).fetchone()

    if client is None:
        conn.close()
        return "Client not found", 404

    progress = conn.execute(
        """
        SELECT week, adherence
        FROM progress
        WHERE client_name = ?
        ORDER BY week
        """,
        (client["name"],)
    ).fetchall()

    conn.close()

    weeks = [row["week"] for row in progress]
    adherence = [row["adherence"] for row in progress]

    plt.figure(figsize=(8, 4))
    plt.plot(weeks, adherence, marker="o")
    plt.title(f"Weekly Adherence - {client['name']}")
    plt.xlabel("Week")
    plt.ylabel("Adherence (%)")
    plt.ylim(0, 100)
    plt.grid(True)

    image = io.BytesIO()
    plt.savefig(image, format="png", bbox_inches="tight")
    plt.close()

    image.seek(0)

    from flask import send_file
    return send_file(image, mimetype="image/png")


# ---------------------------------------------------------
# PROGRESS AND METRICS
# ---------------------------------------------------------

@app.route("/clients/<int:client_id>/progress", methods=["POST"])
def add_progress(client_id):

    if "username" not in session:
        return redirect(url_for("login"))

    week = request.form.get("week")
    adherence = request.form.get("adherence")

    conn = get_db()

    client = conn.execute(
        "SELECT name FROM clients WHERE id = ?",
        (client_id,)
    ).fetchone()

    if client is None:
        conn.close()
        flash("Client not found.", "danger")
        return redirect(url_for("clients"))

    conn.execute(
        """
        INSERT INTO progress
        (client_name, week, adherence)
        VALUES (?, ?, ?)
        """,
        (client["name"], week, adherence)
    )

    conn.commit()
    conn.close()

    flash("Progress added successfully.")
    return redirect(url_for("client_summary", client_id=client_id))


@app.route("/clients/<int:client_id>/metrics", methods=["POST"])
def add_metrics(client_id):

    if "username" not in session:
        return redirect(url_for("login"))

    date = request.form.get("date")
    weight = request.form.get("weight")
    waist = request.form.get("waist")
    bodyfat = request.form.get("bodyfat")

    conn = get_db()

    client = conn.execute(
        "SELECT name FROM clients WHERE id = ?",
        (client_id,)
    ).fetchone()

    if client is None:
        conn.close()
        flash("Client not found.", "danger")
        return redirect(url_for("clients"))

    conn.execute(
        """
        INSERT INTO metrics
        (client_name, date, weight, waist, bodyfat)
        VALUES (?, ?, ?, ?, ?)
        """,
        (client["name"], date, weight, waist, bodyfat)
    )

    conn.commit()
    conn.close()

    flash("Body metrics added successfully.")
    return redirect(url_for("client_summary", client_id=client_id))


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------



@app.route("/clients/<int:client_id>/report")
def client_report(client_id):
    if "username" not in session:
        return redirect(url_for("login"))

    import io
    from fpdf import FPDF
    from flask import send_file

    conn = get_db()

    client = conn.execute(
        "SELECT * FROM clients WHERE id = ?",
        (client_id,)
    ).fetchone()

    if client is None:
        conn.close()
        return "Client not found", 404

    progress = conn.execute(
        "SELECT week, adherence FROM progress WHERE client_name = ? ORDER BY week",
        (client["name"],)
    ).fetchall()

    metrics = conn.execute(
        "SELECT date, weight, waist, bodyfat FROM metrics WHERE client_name = ? ORDER BY date DESC",
        (client["name"],)
    ).fetchall()

    workouts = conn.execute(
        "SELECT date, workout_type, duration_min, notes FROM workouts WHERE client_name = ? ORDER BY date DESC",
        (client["name"],)
    ).fetchall()

    conn.close()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "ACEest Fitness & Gym", ln=True, align="C")

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Client Fitness Report", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Client Details", ln=True)

    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 7, f"Name: {client['name']}", ln=True)
    pdf.cell(0, 7, f"Age: {client['age']}", ln=True)
    pdf.cell(0, 7, f"Height: {client['height']} cm", ln=True)
    pdf.cell(0, 7, f"Current Weight: {client['weight']} kg", ln=True)
    pdf.cell(0, 7, f"Target Weight: {client['target_weight']} kg", ln=True)
    pdf.cell(0, 7, f"Membership: {client['membership_status']}", ln=True)
    pdf.cell(0, 7, f"Program: {client['program'] or 'Not assigned'}", ln=True)
    pdf.cell(0, 7, f"Daily Calories: {client['calories']}", ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Weekly Adherence", ln=True)

    pdf.set_font("Helvetica", size=10)
    if progress:
        for row in progress:
            pdf.cell(0, 7, f"Week {row['week']}: {row['adherence']}%", ln=True)
    else:
        pdf.cell(0, 7, "No adherence data available.", ln=True)

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Body Metrics", ln=True)

    pdf.set_font("Helvetica", size=10)
    if metrics:
        for row in metrics:
            pdf.cell(
                0,
                7,
                f"{row['date']} - Weight: {row['weight']} kg, Waist: {row['waist']} in, Body Fat: {row['bodyfat']}%",
                ln=True
            )
    else:
        pdf.cell(0, 7, "No body metrics available.", ln=True)

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Workout History", ln=True)

    pdf.set_font("Helvetica", size=10)
    if workouts:
        for row in workouts:
            notes = row["notes"] or ""
            pdf.multi_cell(
                0,
                7,
                f"{row['date']} - {row['workout_type']} - {row['duration_min']} min - {notes}"
            )
    else:
        pdf.cell(0, 7, "No workout history available.", ln=True)

    output = io.BytesIO()
    pdf.output(output)
    output.seek(0)

    return send_file(
        output,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{client['name'].replace(' ', '_')}_fitness_report.pdf"
    )


@app.route("/workouts/<int:workout_id>/exercises/add", methods=["POST"])
def add_exercise(workout_id):
    if "username" not in session:
        return redirect(url_for("login"))

    name = request.form.get("name", "").strip()
    sets = request.form.get("sets", "").strip()
    reps = request.form.get("reps", "").strip()
    weight = request.form.get("weight", "").strip()

    if not name or not sets or not reps:
        return "Exercise name, sets and reps are required", 400

    conn = get_db()

    workout = conn.execute(
        "SELECT id FROM workouts WHERE id = ?",
        (workout_id,)
    ).fetchone()

    if workout is None:
        conn.close()
        return "Workout not found", 404

    conn.execute(
        """
        INSERT INTO exercises (workout_id, name, sets, reps, weight)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            workout_id,
            name,
            int(sets),
            int(reps),
            float(weight) if weight else None
        )
    )

    conn.commit()
    conn.close()

    return redirect(url_for("workouts"))


@app.route("/health")
def health():

    return {
        "status": "UP",
        "application": "ACEest Fitness & Gym"
    }


# ---------------------------------------------------------
# APPLICATION START
# ---------------------------------------------------------

init_db()


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
