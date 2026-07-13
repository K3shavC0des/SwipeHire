
from flask import redirect, render_template, request, session
from functools import wraps
import sqlite3
from PyPDF2 import PdfReader
from docx import Document



ALLOWED_EXTENSIONS = {"pdf", "docx"}

def get_db():
    conn = sqlite3.connect("swipehire.db")
    conn.row_factory = sqlite3.Row
    return conn

def parse_docx(filepath):   
    file = Document(filepath)
    text = "\n".join(p.text for p in file.paragraphs)
    return text

def parse_pdf(filepath):
    text = ""
    with open(filepath, "rb") as f:
        reader=PdfReader(f)
        for page in reader.pages:
            text += page.extract_text()
    return text

def allowed_file(filename):
    if not "." in filename:
        return False
    extension = get_extension(filename)
    isValid = extension in ALLOWED_EXTENSIONS
    return isValid

def get_extension(f):
    extension = f.rsplit(".", 1)[1].lower()
    return extension

def loginRequired(f):
    @wraps(f)
    def login_required(*args, **kwargs):
        if session.get("user_id") is None:
            return render_template("error.html", error = "Please Login", pageLink = "/")
        return f(*args, **kwargs)
    return login_required

def dbe(query, params=()):
    db = get_db()
    cursor = db.execute(query, params)
    db.commit()
    rows = cursor.fetchall()
    db.close()
    return rows