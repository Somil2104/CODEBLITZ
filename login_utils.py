from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    """
    Decorate routes to require login.

    Redirects to the login page if the user is not logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash("You must log in to access this page.", "warning")
            return redirect(url_for("home"))
        return f(*args, **kwargs)

    return decorated_function
