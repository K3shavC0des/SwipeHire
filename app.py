import os
import uuid

from flask import Flask, jsonify, redirect, render_template, request, session, send_file, Response
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from helpers import loginRequired, parse_pdf, dbe, allowed_file, get_extension

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = os.urandom(24)
app.config["UPLOAD_FOLDER"] = "static/uploads"
Session(app)


@app.route("/")
def homepage():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def loginPage():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("username", "").lower().strip()
        password = request.form.get("password", "").strip()
        if not username or not password:
            return render_template("error.html", error="Please enter username and password", pageLink="/login")
        rows = dbe("SELECT * FROM users WHERE username = ?", (username,))
        for row in rows:
            if check_password_hash(row["hash"], password):
                session["user_id"] = row["id"]
                return redirect("/")
        return render_template("error.html", error="Invalid username or password", pageLink="/login")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def registerPage():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username", "").lower().strip()
    ps1 = request.form.get("ps1", "").strip()
    ps2 = request.form.get("ps2", "").strip()

    if not username or not ps1 or not ps2:
        return render_template("error.html", error="Please fill out all fields", pageLink="/register")

    rows = dbe("SELECT id FROM users WHERE username = ?", (username,))
    if rows:
        return render_template("error.html", error="Username already taken", pageLink="/register")

    if ps1 != ps2:
        return render_template("error.html", error="Passwords do not match", pageLink="/register")

    if len(ps1) < 4:
        return render_template("error.html", error="Password must be at least 4 characters", pageLink="/register")

    dbe("INSERT INTO users (username, hash) VALUES (?, ?)", (username, generate_password_hash(ps1)))
    rows = dbe("SELECT id FROM users WHERE username = ?", (username,))
    session["user_id"] = rows[0]["id"]
    return redirect("/")


@app.route("/add_resume", methods=["GET", "POST"])
@loginRequired
def addResume():
    if request.method == "GET":
        return render_template("resume_upload.html")

    name = request.form.get("name", "").strip()
    role = request.form.get("role", "").strip()
    file = request.files.get("resume")

    if not name or not role or not file or not file.filename:
        return render_template("error.html", error="Please fill out all fields and choose a file", pageLink="/add_resume")

    filename = secure_filename(file.filename)
    if not allowed_file(filename):
        return render_template("error.html", error="Only PDF files are supported", pageLink="/add_resume")

    extension = get_extension(filename)
    unique_name = str(uuid.uuid4()) + "." + extension
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
    file.save(file_path)

    content = parse_pdf(file_path)
    dbe("INSERT INTO resumes (user_id, name, role, content, file_path) VALUES (?, ?, ?, ?, ?)",
        (session["user_id"], name, role, content, file_path))
    return redirect("/")


@app.route("/resume/<int:resume_id>")
def resumeView(resume_id):
    rows = dbe("SELECT name, role, content, file_path FROM resumes WHERE id = ?", (resume_id,))
    if not rows:
        return "Resume not found", 404
    r = rows[0]
    resp = send_file(r["file_path"])
    resp.headers.pop("Content-Disposition", None)
    return resp


@app.route("/swipe")
@loginRequired
def swipePage():
    return render_template("swipe.html")

@app.route("/api/next-resume")
@loginRequired
def nextResume():
    swiped = dbe("SELECT resume_id FROM swipes WHERE user_id = ?", (session["user_id"],))
    swiped_ids = [row["resume_id"] for row in swiped]

    if swiped_ids:
        placeholders = ",".join("?" * len(swiped_ids))
        rows = dbe(f"SELECT id, name, role, file_path FROM resumes WHERE id NOT IN ({placeholders})", swiped_ids)
    else:
        rows = dbe("SELECT id, name, role, file_path FROM resumes")

    if rows:
        r = rows[0]
        return jsonify({"id": r["id"], "name": r["name"], "role": r["role"], "file_path": "/" + r["file_path"]})
    return jsonify({"done": True})


@app.route("/api/swipe", methods=["POST"])
@loginRequired
def swipe():
    data = request.get_json()
    resume_id = data["resume_id"]
    decision = data["decision"]
    dbe("INSERT INTO swipes (user_id, resume_id, decision) VALUES (?, ?, ?)",
        (session["user_id"], resume_id, decision))
    return jsonify({"ok": True})


@app.route("/api/reset-swipes", methods=["POST"])
@loginRequired
def resetSwipes():
    dbe("DELETE FROM swipes WHERE user_id = ?", (session["user_id"],))
    return jsonify({"ok": True})
