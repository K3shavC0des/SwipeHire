
from flask import redirect, render_template, request, session
from functools import wraps

def loginRequired(f):
    @wraps(f)
    def login_required(*args, **kwargs):
        if session.get("user_id") is None:
            return render_template("error.html", error = "Please Login")
        return f(*args, **kwargs)
    
    return login_required