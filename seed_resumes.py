import os
import random
import sqlite3
from PyPDF2 import PdfReader
from werkzeug.security import generate_password_hash
from helpers import dbe

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


def init_db():
    conn = sqlite3.connect("swipehire.db")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hash TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            role TEXT,
            content TEXT,
            file_path TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS swipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resume_id INTEGER NOT NULL,
            decision TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (resume_id) REFERENCES resumes(id)
        );
    """)
    conn.commit()
    conn.close()


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
    return filename.rsplit(".", 1)[1].lower() == "pdf"


def generate_unique_username(base, existing):
    if base not in existing:
        return base
    i = 2
    while f"{base}{i}" in existing:
        i += 1
    return f"{base}{i}"


def main():
    init_db()

    existing_usernames = {row["username"] for row in dbe("SELECT username FROM users")}
    existing_paths = {row["file_path"] for row in dbe("SELECT file_path FROM resumes")}

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

        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        full_name = f"{first} {last}"
        username_base = f"{first.lower()}.{last.lower()}"
        username = generate_unique_username(username_base, existing_usernames)

        dbe("INSERT INTO users (username, hash) VALUES (?, ?)", (username, password_hash))
        user_id = dbe("SELECT id FROM users WHERE username = ?", (username,))[0]["id"]
        existing_usernames.add(username)

        content = parse_pdf(file_path)

        dbe("INSERT INTO resumes (user_id, name, role, content, file_path) VALUES (?, ?, ?, ?, ?)",
            (user_id, full_name, "", content, file_path))

        print(f"  Created '{full_name}' (username: {username}) \u2192 {filename}")
        imported += 1

    print(f"\nDone! Imported {imported} resume(s).")
    print("You can log in as any dummy user with password 'password'.")


if __name__ == "__main__":
    main()
