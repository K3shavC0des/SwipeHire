import os
import uuid

from flask import Flask, jsonify, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from helpers import loginRequired, parse_pdf, parse_docx, dbe, allowed_file, get_extension

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
        username = request.form.get("username").lower().strip()
        password = request.form.get("password").lower().strip()
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
    
    if request.method == "POST":
        potUsername = request.form.get("username").lower().strip()
        ps1 = request.form.get("ps1").lower().strip()
        ps2 = request.form.get("ps2").lower().strip()
        if not ps1 or not ps2 or not potUsername:
            return render_template("error.html", error="Please fill out the values", pageLink="/register")
        rows = dbe("SELECT username FROM users")
        for row in rows:
            if row["username"] == potUsername:
                return render_template("error.html", error="Username Already Exists :(", pageLink="/register")

        if ps1 != ps2:
            return render_template("error.html", error="Please ensure the two passwords match", pageLink="/register")

        dbe("INSERT INTO users (username, hash) VALUES (?, ?)", (potUsername, generate_password_hash(ps1)))
        session["user_id"] = dbe("SELECT id FROM users WHERE username = ?", (potUsername,))[0]["id"]
        return redirect("/")
        
    else:
        return render_template("register.html")

@app.route("/add_resume", methods=["GET", "POST"])
@loginRequired
def addResume():
    if request.method == "GET": return render_template("resume_upload.html")
    else:
        name = request.form.get("name")
        role = request.form.get("role")
        file = request.files["resume"]
        f = file.filename

        if not name or not role or not f or not allowed_file(f):
            return render_template("error.html", error="Invalid input or file type", pageLink="/add_resume")

        extension = get_extension(f)
        unique_name = str(uuid.uuid4()) + "." + extension
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
        file.save(file_path)

        if extension == "pdf":
            content = parse_pdf(file_path)
        else:
            content = parse_docx(file_path)

        dbe("INSERT INTO resumes (user_id, name, role, content, file_path) VALUES (?, ?, ?, ?, ?)",
            (session["user_id"], name, role, content, file_path))

        return redirect("/")



@app.route("/swipe")
@loginRequired
def swipePage():
    return render_template("swipe.html")

@app.route("/leaderboard")
@loginRequired
def leaderboardPage():
    return render_template("leaderboard.html")

@app.route("/profile", methods=["GET", "POST"])
@loginRequired
def profilePage():
    if request.method == "GET":
        username = dbe("SELECT username FROM users WHERE id = ?", (session["user_id"],))[0]["username"]
        return render_template("profile.html", ProfileName=username)


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
        return jsonify({"id": r["id"], "name": r["name"], "role": r["role"], "file_path": r["file_path"]})
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