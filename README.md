# SwipeHire

A web app where you create an account, upload resumes, and swipe through candidates like Tinder to accept or reject them. Final project for CS50.

## Features

- Registration and login with hashed passwords
- Upload PDF resumes
- Swipe left/reject or right/accept on candidates
- Server-side sessions

## Tech Stack

- Python, Flask, SQLite
- Jinja2 templates, Bootstrap 5
- PyPDF2 for PDF parsing
- Werkzeug for password hashing

## Setup

1. Clone the repo.

2. Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Seed sample resumes:
   Place `.pdf` files in `static/uploads/`, then run:
   ```bash
   python seed_resumes.py
   ```
   This creates a dummy user for each resume (password: `password`) and imports them into the database.

4. Run the app:
   ```bash
   flask run
   ```

## Database Schema

| Table     | Columns |
|-----------|---------|
| **users** | id, username, hash |
| **resumes** | id, user_id (FK), name, role, content, file_path, created_at |
| **swipes** | id, user_id (FK), resume_id (FK), decision, created_at |

## Project Structure

```
├── app.py              # Routes and app config
├── helpers.py          # DB helpers, auth decorator, PDF parsing
├── seed_resumes.py     # Import PDFs from static/uploads into the DB
├── swipehire.db        # SQLite database
├── schema.txt          # Schema reference
├── requirements.txt    # Dependencies
├── static/
│   ├── styles.css
│   └── uploads/        # PDFs go here for seeding
└── templates/
    ├── layout.html
    ├── index.html
    ├── register.html
    ├── login.html
    ├── resume_upload.html
    ├── swipe.html
    └── error.html
```
