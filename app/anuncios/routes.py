from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.db import get_db
from app.auth.routes import login_required

anuncios_bp = Blueprint("anuncios", __name__, url_prefix="/anuncios", template_folder="templates")

def obtener_categorias():
    return get_db().execute("SELECT id,nombre FROM categorias ORDER BY nombre").fetchall()

@anuncios_bp.route("/")
def lista_anuncios():
    db = get_db()
    q = request.args.get("q", "").strip()
    categoria_id = request.args.get("categoria", "").strip()
    sql = """SELECT a.*, u.nombre AS autor, c.nombre AS categoria
             FROM anuncios a JOIN usuarios u ON u.id=a.usuario_id
             JOIN categorias c ON c.id=a.categoria_id WHERE a.estado='publicado'"""
    params = []
    if q:
        sql += " AND (a.titulo LIKE ? OR a.contenido LIKE ? OR a.ubicacion LIKE ?)"
        params.extend([f"%{q}%"] * 3)
    if categoria_id.isdigit():
        sql += " AND a.categoria_id=?"
        params.append(int(categoria_id))
    sql += " ORDER BY a.creado_en DESC"
    anuncios = db.execute(sql, params).fetchall()
    return render_template("anuncios/lista.html", anuncios=anuncios, categorias=obtener_categorias(),
                           q=q, categoria_id=categoria_id)

@anuncios_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_anuncio():
    categorias = obtener_categorias()
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        contenido = request.form.get("contenido", "").strip()
        ubicacion = request.form.get("ubicacion", "").strip()
        estado = request.form.get("estado", "publicado")
        cat = request.form.get("categoria_id", "")
        if not titulo or not contenido or not cat.isdigit() or estado not in ("publicado", "borrador"):
            flash("Completa los campos obligatorios correctamente.", "warning")
        elif not any(int(c["id"]) == int(cat) for c in categorias):
            flash("Selecciona una categoría válida.", "warning")
        else:
            db = get_db()
            db.execute("INSERT INTO anuncios(titulo,contenido,ubicacion,estado,usuario_id,categoria_id) VALUES(?,?,?,?,?,?)",
                       (titulo, contenido, ubicacion, estado, session["usuario_id"], int(cat)))
            db.commit()
            flash("Anuncio guardado.", "success")
            return redirect(url_for("anuncios.lista_anuncios"))
    return render_template("anuncios/formulario.html", anuncio=None, categorias=categorias)

@anuncios_bp.route("/<int:anuncio_id>")
def detalle_anuncio(anuncio_id):
    anuncio = get_db().execute("""SELECT a.*,u.nombre AS autor,c.nombre AS categoria
      FROM anuncios a JOIN usuarios u ON u.id=a.usuario_id JOIN categorias c ON c.id=a.categoria_id
      WHERE a.id=? AND (a.estado='publicado' OR a.usuario_id=?)""",
      (anuncio_id, session.get("usuario_id", -1))).fetchone()
    if not anuncio:
        flash("Anuncio no encontrado.", "warning")
        return redirect(url_for("anuncios.lista_anuncios"))
    return render_template("anuncios/detalle.html", anuncio=anuncio)

@anuncios_bp.route("/<int:anuncio_id>/editar", methods=["GET", "POST"])
@login_required
def editar_anuncio(anuncio_id):
    db = get_db()
    anuncio = db.execute("SELECT * FROM anuncios WHERE id=?", (anuncio_id,)).fetchone()
    if not anuncio:
        flash("Anuncio no encontrado.", "warning")
        return redirect(url_for("anuncios.lista_anuncios"))
    if anuncio["usuario_id"] != session["usuario_id"] and session.get("rol") != "admin":
        flash("Solo el autor o un administrador puede editar este anuncio.", "danger")
        return redirect(url_for("anuncios.lista_anuncios"))
    categorias = obtener_categorias()
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        contenido = request.form.get("contenido", "").strip()
        ubicacion = request.form.get("ubicacion", "").strip()
        estado = request.form.get("estado", "publicado")
        cat = request.form.get("categoria_id", "")
        if not titulo or not contenido or not cat.isdigit() or estado not in ("publicado", "borrador"):
            flash("Completa los campos obligatorios correctamente.", "warning")
        elif not any(int(c["id"]) == int(cat) for c in categorias):
            flash("Selecciona una categoría válida.", "warning")
        else:
            db.execute("""UPDATE anuncios SET titulo=?,contenido=?,ubicacion=?,estado=?,categoria_id=?,
                       actualizado_en=CURRENT_TIMESTAMP WHERE id=?""",
                       (titulo, contenido, ubicacion, estado, int(cat), anuncio_id))
            db.commit()
            flash("Anuncio actualizado.", "success")
            return redirect(url_for("anuncios.detalle_anuncio", anuncio_id=anuncio_id))
    return render_template("anuncios/formulario.html", anuncio=anuncio, categorias=categorias)

@anuncios_bp.route("/<int:anuncio_id>/eliminar", methods=["POST"])
@login_required
def eliminar_anuncio(anuncio_id):
    db = get_db()
    anuncio = db.execute("SELECT * FROM anuncios WHERE id=?", (anuncio_id,)).fetchone()
    if not anuncio:
        flash("Anuncio no encontrado.", "warning")
    elif anuncio["usuario_id"] != session["usuario_id"] and session.get("rol") != "admin":
        flash("No tienes permiso para eliminar este anuncio.", "danger")
    else:
        db.execute("DELETE FROM anuncios WHERE id=?", (anuncio_id,))
        db.commit()
        flash("Anuncio eliminado.", "success")
    return redirect(url_for("anuncios.lista_anuncios"))
