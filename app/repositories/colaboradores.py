"""Persistência de colaboradores com consultas parametrizadas."""

from app.repositories.database import get_db


def find_by_username(username):
    return get_db().execute(
        "SELECT id, nome, usuario, senha_hash FROM colaboradores WHERE usuario = ?",
        (username,),
    ).fetchone()


def find_by_id(user_id):
    return get_db().execute(
        "SELECT id, nome, usuario FROM colaboradores WHERE id = ?", (user_id,)
    ).fetchone()


def insert(nome, usuario, senha_hash):
    db = get_db()
    with db:
        cursor = db.execute(
            "INSERT INTO colaboradores (nome, usuario, senha_hash) VALUES (?, ?, ?)",
            (nome, usuario, senha_hash),
        )
    return cursor.lastrowid


def update_password_hash(user_id, senha_hash):
    db = get_db()
    with db:
        db.execute(
            "UPDATE colaboradores SET senha_hash = ? WHERE id = ?", (senha_hash, user_id)
        )
