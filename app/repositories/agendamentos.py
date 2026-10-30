"""Persistência de agendamentos e consulta com animal e tutor."""

from app.repositories.database import get_db


def insert(data, horario, servico, status, id_animal, observacoes):
    db = get_db()
    with db:
        cursor = db.execute("""
            INSERT INTO agendamentos (data, horario, servico, status, id_animal, observacoes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data, horario, servico, status, id_animal, observacoes))
    return cursor.lastrowid


def find_occupied_slot(data, horario):
    return get_db().execute("""
        SELECT id_agendamento FROM agendamentos
        WHERE data = ? AND horario = ? AND status <> 'Cancelado'
    """, (data, horario)).fetchone()


def list_all():
    return get_db().execute("""
        SELECT ag.id_agendamento, ag.data, ag.horario, ag.servico, ag.status,
               ag.observacoes, ag.id_animal, a.nome AS animal_nome,
               t.id_tutor, t.nome AS tutor_nome
        FROM agendamentos AS ag
        JOIN animais AS a ON a.id_animal = ag.id_animal
        JOIN tutores AS t ON t.id_tutor = a.id_tutor
        ORDER BY ag.data, ag.horario, ag.id_agendamento
    """).fetchall()
