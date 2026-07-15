# SwipeHire

A web application that simulates the recruiter experience — users create accounts, browse resumes in a Tinder-style interface, and swipe to accept or reject candidates. Built as the final project for [CS50](https://cs50.harvard.edu/).

## Features

- **User registration & authentication** — secure password hashing with Werkzeug
- **Resume swiping** — view resumes and make quick hiring decisions
- **Leaderboard** — track which resumes rank highest
- **Session management** — server-side sessions via Flask-Session

## Tech Stack

- **Backend:** Python, Flask, SQLite
- **Frontend:** Jinja2 templates, Bootstrap 5
- **Security:** Werkzeug password hashing

## Setup

1. **Clone the repository**

2. **Create a virtual environment and install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Seed sample resumes**
   Place `.pdf` or `.docx` files in `static/uploads/`, then run:
   ```bash
   python seed_resumes.py
   ```
   This creates dummy user accounts for each resume (password: `password`) and imports their parsed content into the database.

4. **Run the application**
   ```bash
   flask run
   ```

## Database Schema

| Table     | Columns |
|-----------|---------|
| **users** | id, username, hash |
| **resumes** | id, user_id (FK), name, role, content, created_at |
| **swipes** | id, user_id (FK), resume_id (FK), decision, created_at |

## Project Structure

```
├── app.py              # Flask application and routes
├── helpers.py          # Database connection, auth decorator
├── seed_resumes.py     # Import resume files into the database
├── swipehire.db        # SQLite database
├── schema.txt          # Schema reference
├── requirements.txt    # Python dependencies
├── static/
│   └── uploads/        # Place resume files here for seeding
└── templates/          # Jinja2 templates
    ├── layout.html     # Base layout with Bootstrap nav
    ├── index.html      # Homepage
    ├── register.html   # Registration form
    ├── login.html      # Login form
    ├── swipe.html      # Swipe interface
    ├── leaderboard.html# Rankings
    └── error.html      # Error display
```
