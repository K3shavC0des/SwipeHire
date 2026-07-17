# SwipeHire

#### Video Demo:  https://www.youtube.com/watch?v=Ak4PLhVCrDc

edX: _KeshavKumar_

#### Description:

SwipeHire is a web application that puts you in the recruiter's seat. people can create accounts, upload PDF resumes, and then review candidates in a full-screen Tinder-style interface. They may reject some and mark others for interview. It was built as the final project for CS50x.

The idea came from watching recruiters at a career fair flip through stacks of paper resumes. Most hiring tools are built for HR departments and enterprise teams; there isnt much that makes the actual act of reviewing resumes quick or even fun. SwipeHire tries to solve that by borrowing the swipe mechanic from dating apps and applying it to hiring. The goal is to let someone burn through a pile of resumes in minutes instead of hours, and allows someone to gamify this experience.

---

### Files

**app.py** — The Flask application. It defines all the routes. The homepage at `/` renders the index template. `/register` and `/login` handle account creation and authentication using Werkzeug's `generate_password_hash` and `check_password_hash`. Passwords are never stored in plain text. The `/logout` route clears the session. `/add_resume` accepts GET and POST — the GET renders an upload form, the POST validates the input, saves the PDF to disk with a UUID filename (so original filenames dont collide or leak info), parses the text out of it with PyPDF2, and stores everything in the database. `/resume/<id>` serves a PDF file directly to the browser without a Content-Disposition header so it renders inline. `/swipe` renders the swipe interface. `/api/next-resume` returns JSON with the next unsWiped resume (or `{"done": true}` if the user has seen everything). `/api/swipe` records a decision. `/api/reset-swipes` deletes all of the current user's swipe history so they can start over.

One design choice worth noting: the resume content is extracted to plain text at upload time and stored in the database. The original PDF is also kept on disk and served for rendering. This dual approach means the app could later support full-text search across resumes without re-parsing files, and the PDF is always available for the user to actually read.

**helpers.py** — Utility functions shared across the app. `get_db()` opens a connection to the SQLite database with `row_factory` set to `sqlite3.Row` so rows behave like dictionaries. `dbe()` is a small wrapper that executes a query, commits, fetches all results, and closes the connection — it cuts down on repetitive boilerplate in app.py. `parse_pdf()` opens a PDF with PyPDF2 and concatenates all page text. `allowed_file()` and `get_extension()` handle filename validation. `loginRequired` is a decorator that checks `session.get("user_id")` and redirects unauthenticated users to an error page rather than letting them hit protected routes.

**seed_resumes.py** — A standalone script for importing batches of PDFs. It scans `static/uploads/` for new PDFs that havent been imported yet, generates a random name for each one from a list of 50 first and last names, creates a dummy user account (password: "password"), parses the PDF text, and inserts it all into the database. This is mainly useful for demoing the app or testing with realistic amounts of data. The username collision logic is simple but works: if "alice.smith" is taken, it tries "alice.smith2", then "alice.smith3", etc.

**schema.txt** — A quick reference for the three database tables and their columns.

**requirements.txt** — Lists the four Python packages the app depends on: Flask, Flask-Session, Werkzeug, and PyPDF2. Pinned to the versions that were installed during development.

**static/styles.css** — All custom styling. The layout is mostly Bootstrap 5, but this file handles the hero section, feature cards, form containers, profile cards, leaderboard tables, and error pages. The color scheme uses a blue primary (`#4361ee`) with neutral grays. The features grid uses flexbox with a max-width so cards dont stretch too wide on large screens.

**static/uploads/** — Where uploaded PDFs are stored. UUID-based filenames prevent overwrites and make it hard to guess other users' files.

**templates/layout.html** — The base template that every other template extends. It includes the Bootstrap 5 CSS and JS from a CDN, the custom stylesheet, a responsive navbar with conditional links (Add Resume and Swipe when logged in, Log In and Register when logged out), a container `<main>` block, and a simple footer. Using a layout template means none of the page-specific templates need to repeat the boilerplate HTML structure.

**templates/index.html** — The landing page. Has a hero section with the tagline, a brief explanation of what the app does, a call-to-action button (Start Swiping or Get Started depending on login state), and two feature cards explaining the upload and swipe workflow. The cards are centered with Bootstrap's grid system using `justify-content-center`.

**templates/register.html** and **templates/login.html** — Simple forms that extend the layout. Both use the `.form-container` class from styles.css for a centered card with rounded corners and shadow. Registration asks for username and password twice (to catch typos). Login asks for username and password. The alt-link at the bottom lets users switch between the two pages.

**templates/resume_upload.html** — A form with fields for the candidate's full name, role/position, and a file picker restricted to PDFs. The server validates everything server-side too, so disabling JavaScript wont bypass the checks.

**templates/swipe.html** — The most complex template. It is a standalone full-screen page (it doesnt extend layout.html because it needs full control over the viewport). It uses pdf.js to render PDFs page-by-page onto canvas elements directly in the browser — no iframe, no image conversion, no server-side rendering. When the page loads, it shows a 3-2-1 countdown animation with a pop effect, then reveals the swipe UI. The user sees the full PDF rendered above two buttons: a red "Reject" and a green "Interview". Each swipe sends a POST to `/api/swipe` and immediately loads the next resume. When all resumes have been seen, a "done" screen appears with the option to reset and start over. All the API calls use fetch with JSON. The decision to render PDFs client-side rather than converting them to images was intentional — it preserves text quality, keeps the file size small, and avoids disk clutter from generated thumbnails.

**templates/error.html** — A minimal error page that displays a message and a "go back" link. Used by the loginRequired decorator and various validation checks throughout app.py.

---

### Design Decisions

Session storage instead of cookies: The app uses Flask-Session with server-side filesystem storage rather than signed client-side cookies. This keeps session data off the client and makes it easier to invalidate sessions server-side if needed.

PDF rendering in the browser with pdf.js rather than converting to images: This avoids generating and storing thumbnail files, preserves text quality at any zoom level, and keeps the code simpler — the server just serves the original file.

Separate API endpoints for the swipe interface: The swipe page is a single HTML file that fetches data from `/api/next-resume` and posts decisions to `/api/swipe`. This separates the frontend from the backend logic and would make it straightforward to build a mobile app or CLI tool against the same API later.

One SQLite database for everything: SQLite is good enough for a personal or small-team tool. No need to run a separate database server. The schema is simple with only three tables with foreign keys and timestamps.

UUIDs for uploaded filenames: Prevents filename collisions and makes it impossible to guess or enumerate other users' uploads. The original filename is thrown away after the extension is extracted.
