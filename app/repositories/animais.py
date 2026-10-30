"""Persistência e consulta dos animais com identificação de seus tutores."""

from app.repositories.database import get_db


def insert(nome, especie, raca, porte, observacoes, id_tutor):
    db = get_db()
    with db:
        cursor = db.execute(
            """INSERT INTO animais (nome, especie, raca, porte, observacoes, id_tutor)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (nome, especie, raca, porte, observacoes, id_tutor),
        )
    return cursor.lastrowid


def list_all():
    return get_db().execute("""
        SELECT a.id_animal, a.nome, a.especie, a.raca, a.porte, a.observacoes,
               a.id_tutor, t.nome AS tutor_nome
        FROM animais AS a
        JOIN tutores AS t ON t.id_tutor = a.id_tutor
        ORDER BY a.id_animal DESC
    """).fetchall()


def find_with_tutor(id_animal):
    return get_db().execute("""
        SELECT a.id_animal, a.nome, t.id_tutor, t.nome AS tutor_nome
        FROM animais AS a
        JOIN tutores AS t ON t.id_tutor = a.id_tutor
        WHERE a.id_animal = ?
    """, (id_animal,)).fetchone()
