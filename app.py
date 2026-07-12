import os

from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import generate_password_hash
from helpers import loginRequired, get_db

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = os.urandom(24)
Session(app) 



@app.route("/")
def homepage():

    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def loginPage():
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def registerPage():
    if request.method == "POST":
        potUsername = request.form.get("username")
        ps1 = request.form.get("ps1")
        ps2 = request.form.get("ps2")
        if not ps1 or not ps2 or not potUsername:
            return render_template("error.html", error="Please fill out the values", pageLink="/register")
        db = get_db()
        rows = db.execute("SELECT username FROM users").fetchall()
        for row in rows:
            if row["username"] == potUsername:
                return render_template("error.html", error="Username Already Exists :(", pageLink="/register")

        if ps1 != ps2:
            return render_template("error.html", error="Please ensure the two passwords match", pageLink="/register")

        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (potUsername, generate_password_hash(ps1)))
        db.commit()
        db.close()

        return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/swipe")
@loginRequired
def swipePage():
    return render_template("swipe.html")

@app.route("/leaderboard")
@loginRequired
def leaderboardPage():
    return render_template("leaderboard.html")