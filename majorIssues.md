# SwipeHire — Major Issues

## Port 5000 Taken by macOS Control Center
macOS `ControlCe` binds port 5000. Start Flask on port 5001 instead.

## `__pycache__` Corruption From Mixed Python Versions
System Python (3.14) writing `.cpython-314.pyc` into the venv (3.11) breaks imports.
**Fix:** Run `find .venv -name __pycache__ -exec rm -rf {} +` if imports get slow.

## `resumeView` Had No Auth
Route `/resume/<id>` was publicly accessible. Added `@loginRequired`.

## `dbe()` Leaked DB Connections
No `db.close()` on error. Added `try/finally`.

## Orphaned `/profile` Template
`profile.html` existed with no route. Added `/profile` route and nav link.

## `.secret_key` and `flask_session/` Were Tracked in Git
Added to `.gitignore` and removed from tracking.

## Running
```bash
cd /path/to/swipehire
.venv/bin/python -m flask run --port 5001
```
