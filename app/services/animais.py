"""Cadastro de animais com vínculo obrigatório a um tutor existente."""

import sqlite3

from app.repositories import animais, tutores
from app.services.validation import ValidationError, clean_id, clean_text


def create_animal(nome, especie, porte, id_tutor, raca="", observacoes=""):
    errors = {}
    nome = clean_text(nome, "nome", "Nome", 100, errors, required=True)
    especie = clean_text(especie, "especie", "Espécie", 60, errors, required=True)
    porte = clean_text(porte, "porte", "Porte", 30, errors, required=True)
    raca = clean_text(raca, "raca", "Raça", 100, errors)
    observacoes = clean_text(observacoes, "observacoes", "Observações", 2000, errors)
    id_tutor = clean_id(id_tutor, "id_tutor", errors, "Selecione um tutor cadastrado.")
    if errors:
        raise ValidationError(errors)
    if tutores.find_by_id(id_tutor) is None:
        raise ValidationError({"id_tutor": "O tutor selecionado não existe. Escolha um tutor cadastrado."})
    try:
        return animais.insert(nome, especie, raca or None, porte, observacoes or None, id_tutor)
    except sqlite3.IntegrityError:
        if tutores.find_by_id(id_tutor) is None:
            raise ValidationError({"id_tutor": "O tutor selecionado não existe. Escolha um tutor cadastrado."}) from None
        raise


def list_animais():
    return animais.list_all()
