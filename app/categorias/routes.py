from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db import get_db
from app.auth.routes import admin_required

categorias_bp = Blueprint("categorias", __name__, url_prefix="/categorias", template_folder="templates")

@categorias_bp.route("/")
@admin_required
def lista_categorias():
    categorias = get_db().execute("""
      SELECT c.*, COUNT(a.id) AS total_anuncios
      FROM categorias c LEFT JOIN anuncios a ON a.categoria_id=c.id
      GROUP BY c.id ORDER BY c.nombre
    """).fetchall()
    return render_template("categorias/lista.html", categorias=categorias)

@categorias_bp.route("/nueva", methods=["GET", "POST"])
@admin_required
def nueva_categoria():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        if not nombre:
            flash("El nombre es obligatorio.", "warning")
        else:
            try:
                db = get_db()
                db.execute("INSERT INTO categorias(nombre,descripcion) VALUES(?,?)", (nombre, descripcion))
                db.commit()
                flash("Categoría creada.", "success")
                return redirect(url_for("categorias.lista_categorias"))
            except Exception:
                flash("Ya existe una categoría con ese nombre.", "danger")
    return render_template("categorias/formulario.html", categoria=None)

@categorias_bp.route("/<int:categoria_id>/editar", methods=["GET", "POST"])
@admin_required
def editar_categoria(categoria_id):
    db = get_db()
    categoria = db.execute("SELECT * FROM categorias WHERE id=?", (categoria_id,)).fetchone()
    if not categoria:
        flash("Categoría no encontrada.", "warning")
        return redirect(url_for("categorias.lista_categorias"))
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        if not nombre:
            flash("El nombre es obligatorio.", "warning")
        else:
            try:
                db.execute("UPDATE categorias SET nombre=?,descripcion=? WHERE id=?",
                           (nombre, descripcion, categoria_id))
                db.commit()
                flash("Categoría actualizada.", "success")
                return redirect(url_for("categorias.lista_categorias"))
            except Exception:
                flash("No se pudo actualizar: el nombre ya existe.", "danger")
    return render_template("categorias/formulario.html", categoria=categoria)

@categorias_bp.route("/<int:categoria_id>/eliminar", methods=["POST"])
@admin_required
def eliminar_categoria(categoria_id):
    db = get_db()
    try:
        db.execute("DELETE FROM categorias WHERE id=?", (categoria_id,))
        db.commit()
        flash("Categoría eliminada.", "success")
    except Exception:
        db.rollback()
        flash("No se puede eliminar: primero cambia o elimina los anuncios asociados.", "danger")
    return redirect(url_for("categorias.lista_categorias"))
