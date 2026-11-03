import os
from pathlib import Path
from flask import Flask
from .db import init_db

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "cambia-esta-clave-en-produccion"),
        DATABASE=os.environ.get("DATABASE_PATH", str(Path(app.instance_path) / "bd_anuncios.db")),
    )
    if test_config:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    init_db(app)

    from app.auth.routes import auth_bp
    from app.usuarios.routes import usuarios_bp
    from app.categorias.routes import categorias_bp
    from app.anuncios.routes import anuncios_bp
    from app.productos.routes import productos_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(anuncios_bp)
    app.register_blueprint(productos_bp)

    @app.context_processor
    def inject_user():
        from flask import session
        return {"usuario_actual": session.get("usuario")}

    @app.route("/")
    def inicio():
        from flask import redirect, url_for, session

        if "usuario" in session:
            return redirect(url_for("anuncios.listar_anuncios"))

        return redirect(url_for("auth.login"))
    return app
