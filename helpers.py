
from flask import redirect, render_template, request, session
from functools import wraps
import sqlite3

def get_db():
    conn = sqlite3.connect("swipehire.db")
    conn.row_factory = sqlite3.Row
    return conn

def loginRequired(f):
    @wraps(f)
    def login_required(*args, **kwargs):
        if session.get("user_id") is None:
            return render_template("error.html", error = "Please Login", pageLink = "/")
        return f(*args, **kwargs)
    
    return login_required