from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from app.db import get_db
from app.auth.routes import login_required, admin_required

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios", template_folder="templates")

@usuarios_bp.route("/")
@admin_required
def lista_usuarios():
    usuarios = get_db().execute("SELECT id,nombre,username,email,rol,creado_en FROM usuarios ORDER BY id DESC").fetchall()
    return render_template("usuarios/lista.html", usuarios=usuarios)

@usuarios_bp.route("/nuevo", methods=["GET", "POST"])
@admin_required
def nuevo_usuario():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        rol = request.form.get("rol", "usuario")
        if not all([nombre, username, email, password]) or rol not in ("admin", "usuario"):
            flash("Completa todos los campos obligatorios.", "warning")
        else:
            try:
                db = get_db()
                db.execute("INSERT INTO usuarios(nombre,username,email,password_hash,rol) VALUES(?,?,?,?,?)",
                           (nombre, username, email, generate_password_hash(password), rol))
                db.commit()
                flash("Usuario creado correctamente.", "success")
                return redirect(url_for("usuarios.lista_usuarios"))
            except Exception:
                flash("No se pudo crear el usuario. Verifica que el usuario y correo no estén repetidos.", "danger")
    return render_template("usuarios/formulario.html", usuario=None)

@usuarios_bp.route("/<int:user_id>/editar", methods=["GET", "POST"])
@admin_required
def editar_usuario(user_id):
    db = get_db()
    usuario = db.execute("SELECT * FROM usuarios WHERE id=?", (user_id,)).fetchone()
    if not usuario:
        flash("Usuario no encontrado.", "warning")
        return redirect(url_for("usuarios.lista_usuarios"))
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        rol = request.form.get("rol", "usuario")
        password = request.form.get("password", "")
        if not all([nombre, username, email]) or rol not in ("admin", "usuario"):
            flash("Completa los campos obligatorios.", "warning")
        else:
            try:
                if password:
                    db.execute("UPDATE usuarios SET nombre=?,username=?,email=?,rol=?,password_hash=? WHERE id=?",
                               (nombre, username, email, rol, generate_password_hash(password), user_id))
                else:
                    db.execute("UPDATE usuarios SET nombre=?,username=?,email=?,rol=? WHERE id=?",
                               (nombre, username, email, rol, user_id))
                db.commit()
                if user_id == int(__import__("flask").session.get("usuario_id", -1)):
                    __import__("flask").session["usuario"] = username
                    __import__("flask").session["nombre"] = nombre
                    __import__("flask").session["rol"] = rol
                flash("Usuario actualizado.", "success")
                return redirect(url_for("usuarios.lista_usuarios"))
            except Exception:
                flash("No se pudo actualizar: usuario o correo duplicado.", "danger")
    return render_template("usuarios/formulario.html", usuario=usuario)

@usuarios_bp.route("/<int:user_id>/eliminar", methods=["POST"])
@admin_required
def eliminar_usuario(user_id):
    from flask import session
    if user_id == session.get("usuario_id"):
        flash("No puedes eliminar tu propia cuenta mientras estás conectado.", "warning")
    else:
        db = get_db()
        db.execute("DELETE FROM usuarios WHERE id=?", (user_id,))
        db.commit()
        flash("Usuario eliminado.", "success")
    return redirect(url_for("usuarios.lista_usuarios"))

@usuarios_bp.route("/perfil/<nombre>")
@login_required
def perfil(nombre):
    return redirect(url_for("anuncios.lista_anuncios"))
