from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from app.db import get_db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth", template_folder="templates")

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("usuario_id"):
            flash("Inicia sesión para continuar.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("usuario_id"):
            flash("Inicia sesión para continuar.", "warning")
            return redirect(url_for("auth.login"))
        if session.get("rol") != "admin":
            flash("Esta acción requiere permisos de administrador.", "danger")
            return redirect(url_for("anuncios.lista_anuncios"))
        return view(*args, **kwargs)
    return wrapped

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("usuario_id"):
        return redirect(url_for("anuncios.lista_anuncios"))
    if request.method == "POST":
        username = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute("SELECT * FROM usuarios WHERE username = ?", (username,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["usuario_id"] = user["id"]
            session["usuario"] = user["username"]
            session["nombre"] = user["nombre"]
            session["rol"] = user["rol"]
            flash("Sesión iniciada correctamente.", "success")
            return redirect(url_for("anuncios.lista_anuncios"))
        flash("Usuario o contraseña incorrectos.", "danger")
    return render_template("login.html")

@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Has cerrado la sesión.", "info")
    return redirect(url_for("auth.login"))
