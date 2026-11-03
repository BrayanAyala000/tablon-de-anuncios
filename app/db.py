import sqlite3
from flask import current_app, g
from werkzeug.security import generate_password_hash

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS usuarios (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 nombre TEXT NOT NULL,
 username TEXT NOT NULL UNIQUE,
 email TEXT NOT NULL UNIQUE,
 password_hash TEXT NOT NULL,
 rol TEXT NOT NULL DEFAULT 'usuario' CHECK (rol IN ('admin','usuario')),
 creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS categorias (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 nombre TEXT NOT NULL UNIQUE,
 descripcion TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS anuncios (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 titulo TEXT NOT NULL,
 contenido TEXT NOT NULL,
 ubicacion TEXT DEFAULT '',
 estado TEXT NOT NULL DEFAULT 'publicado' CHECK (estado IN ('publicado','borrador')),
 usuario_id INTEGER NOT NULL,
 categoria_id INTEGER NOT NULL,
 creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 actualizado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
 FOREIGN KEY(categoria_id) REFERENCES categorias(id) ON DELETE RESTRICT
);
"""

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db(app):
    with app.app_context():
        db = sqlite3.connect(app.config["DATABASE"])
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        db.executescript(SCHEMA)
        count = db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
        if count == 0:
            db.execute(
                "INSERT INTO usuarios(nombre, username, email, password_hash, rol) VALUES(?,?,?,?,?)",
                ("Administrador", "admin", "admin@tablondeanuncios.local",
                 generate_password_hash("Admin123!"), "admin")
            )
        if db.execute("SELECT COUNT(*) FROM categorias").fetchone()[0] == 0:
            db.executemany("INSERT INTO categorias(nombre, descripcion) VALUES(?,?)", [
                ("Académicos", "Avisos y actividades académicas"),
                ("Institucionales", "Comunicados institucionales"),
                ("Comunidad", "Anuncios de interés general"),
            ])
        db.commit()
        db.close()
    app.teardown_appcontext(close_db)
