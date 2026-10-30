"""Persistência dos tutores, sem regras de negócio."""

from app.repositories.database import get_db


def insert(nome, telefone, observacoes, nome_chave):
    db = get_db()
    with db:
        cursor = db.execute(
            "INSERT INTO tutores (nome, telefone, observacoes, nome_chave) VALUES (?, ?, ?, ?)",
            (nome, telefone, observacoes, nome_chave),
        )
    return cursor.lastrowid


def find_by_id(id_tutor):
    return get_db().execute(
        "SELECT id_tutor, nome, telefone, observacoes FROM tutores WHERE id_tutor = ?",
        (id_tutor,),
    ).fetchone()


def find_by_identity(nome_chave, telefone):
    return get_db().execute(
        "SELECT id_tutor FROM tutores WHERE nome_chave = ? AND telefone = ?",
        (nome_chave, telefone),
    ).fetchone()


def list_all():
    return get_db().execute(
        "SELECT id_tutor, nome, telefone, observacoes FROM tutores ORDER BY id_tutor DESC"
    ).fetchall()
