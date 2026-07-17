from flask import redirect, render_template, request, session
from functools import wraps
import sqlite3
from PyPDF2 import PdfReader

ALLOWED_EXTENSIONS = {"pdf"}


def get_db():
    conn = sqlite3.connect("swipehire.db")
    conn.row_factory = sqlite3.Row
    return conn


def dbe(query, params=()):
    db = get_db()
    try:
        cursor = db.execute(query, params)
        db.commit()
        return cursor.fetchall()
    finally:
        db.close()


def parse_pdf(filepath):
    text = ""
    with open(filepath, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text


def allowed_file(filename):
    if "." not in filename:
        return False
    return filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_extension(filename):
    return filename.rsplit(".", 1)[1].lower()


def loginRequired(f):
    @wraps(f)
    def login_required(*args, **kwargs):
        if session.get("user_id") is None:
            return render_template("error.html", error="Please log in first", pageLink="/login")
        return f(*args, **kwargs)
    return login_required
