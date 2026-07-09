import os

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = os.urandom(24)
Session(app) 



@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/login")
def loginPage():
    return render_template("login.html")

@app.route("/logout")
def logoutPage():
    session.clear()
    return redirect("logout.html")

@app.route("/register")
def registerPage():
    return render_template("register.html")

@app.route("/swipe")
def swipePage():
    return render_template("swipe.html")

@app.route("/leaderboard")
def leaderboardPage():
    return render_template("leaderboard.html")