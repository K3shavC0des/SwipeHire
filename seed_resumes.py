import os
import random
import sqlite3
from PyPDF2 import PdfReader
from docx import Document
from werkzeug.security import generate_password_hash

UPLOAD_FOLDER = "static/uploads"

FIRST_NAMES = [
    "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry", "Ivy", "Jack",
    "Katherine", "Liam", "Mia", "Noah", "Olivia", "Paul", "Quinn", "Rachel", "Sam", "Tina",
    "Uma", "Victor", "Wendy", "Xander", "Yara", "Zane", "Amelia", "Benjamin", "Chloe", "Daniel",
    "Emily", "Finn", "Georgia", "Harper", "Isaac", "Jasmine", "Kevin", "Luna", "Mason", "Nora",
    "Owen", "Penelope", "Quincy", "Riley", "Savannah", "Theo", "Ursula", "Violet", "Willow", "Xavier"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"
]


def get_db():
    conn = sqlite3.connect("swipehire.db")
    conn.row_factory = sqlite3.Row
    return conn


def dbe(query, params=()):
    db = get_db()
    cursor = db.execute(query, params)
    db.commit()
    rows = cursor.fetchall()
    db.close()
    return rows


def parse_pdf(filepath):
    text = ""
    with open(filepath, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            text += page.extract_text()
    return text


def parse_docx(filepath):
    file = Document(filepath)
    text = "\n".join(p.text for p in file.paragraphs)
    return text


def get_extension(filename):
    return filename.rsplit(".", 1)[1].lower()


def allowed_file(filename):
    if "." not in filename:
        return False
    return get_extension(filename) in {"pdf", "docx"}


def generate_unique_username(base, existing):
    if base not in existing:
        return base
    i = 2
    while f"{base}{i}" in existing:
        i += 1
    return f"{base}{i}"


def main():
    # Collect existing usernames and file paths
    existing_usernames = {row["username"] for row in dbe("SELECT username FROM users")}
    existing_paths = {row["file_path"] for row in dbe("SELECT file_path FROM resumes")}

    # Scan uploads folder
    if not os.path.isdir(UPLOAD_FOLDER):
        print(f"Folder '{UPLOAD_FOLDER}' not found.")
        return

    files = [f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)]

    new_files = [f for f in files if os.path.join(UPLOAD_FOLDER, f) not in existing_paths]

    if not new_files:
        print("No new resume files to import.")
        return

    print(f"Found {len(new_files)} new resume(s) to import.\n")

    password_hash = generate_password_hash("password")
    imported = 0

    for filename in new_files:
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        # Generate random name
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        full_name = f"{first} {last}"
        username_base = f"{first.lower()}.{last.lower()}"
        username = generate_unique_username(username_base, existing_usernames)

        # Create dummy user
        dbe("INSERT INTO users (username, hash) VALUES (?, ?)", (username, password_hash))
        user_id = dbe("SELECT id FROM users WHERE username = ?", (username,))[0]["id"]
        existing_usernames.add(username)

        # Parse resume content
        ext = get_extension(filename)
        if ext == "pdf":
            content = parse_pdf(file_path)
        else:
            content = parse_docx(file_path)

        # Insert resume
        dbe("INSERT INTO resumes (user_id, name, role, content, file_path) VALUES (?, ?, ?, ?, ?)",
            (user_id, full_name, "", content, file_path))

        print(f"  Created '{full_name}' (username: {username}) → {filename}")
        imported += 1

    print(f"\nDone! Imported {imported} resume(s).")
    print(f"You can log in as any dummy user with password 'password'.")


if __name__ == "__main__":
    main()
