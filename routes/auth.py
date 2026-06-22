from flask import Blueprint, request, redirect, url_for, session, flash, render_template
from functools import wraps
from models_db.models import AdminUser
from models_db.database import db

auth_bp = Blueprint("auth", __name__)

def login_required(f):
    """Decorator to protect routes and require admin login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Silakan login terlebih dahulu untuk mengakses sistem.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Render login page or process authentication credentials."""
    # If already logged in, redirect to dashboard
    if "user_id" in session:
        return redirect(url_for("dashboard.index"))
        
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        if not username or not password:
            flash("Username dan password harus diisi.", "error")
            return render_template("login.html")
            
        # Retrieve user from DB
        user = AdminUser.query.filter_by(username=username).first()
        if user and user.check_password(password):
            # Store user info in session
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["username"] = user.username
            session["role"] = user.role
            session["region"] = user.region
            
            flash(f"Selamat datang kembali, {user.name}!", "success")
            return redirect(url_for("dashboard.index"))
        else:
            flash("Username atau password salah.", "error")
            
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    """Clear session data and redirect to login."""
    session.clear()
    flash("Anda telah berhasil keluar dari sistem.", "success")
    return redirect(url_for("auth.login"))
