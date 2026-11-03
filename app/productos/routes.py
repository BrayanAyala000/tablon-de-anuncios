# Se conserva el blueprint original de la plantilla del docente para no romper
# sus rutas. La gestión principal ahora corresponde al módulo app.anuncios.
from flask import Blueprint, redirect, url_for

productos_bp = Blueprint("productos", __name__, url_prefix="/productos")

@productos_bp.route("/")
def lista_productos():
    return redirect(url_for("anuncios.lista_anuncios"))

@productos_bp.route("/categorias/<categoria>")
def mostrar_categorias(categoria):
    return redirect(url_for("anuncios.lista_anuncios", categoria=categoria))
