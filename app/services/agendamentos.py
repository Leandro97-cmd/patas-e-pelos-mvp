"""Regras de criação de agendamentos e consulta da agenda."""

import re
import sqlite3
from datetime import date, time

from app.repositories import agendamentos, animais
from app.services.validation import ValidationError, clean_text

SERVICOS = ("Banho", "Tosa", "Banho + Tosa")
STATUS_PERMITIDOS = ("Agendado", "Concluído", "Cancelado")
STATUS_INICIAL = STATUS_PERMITIDOS[0]


def create_agendamento(id_animal, servico, data, horario, observacoes=""):
    errors = {}
    servico = clean_text(servico, "servico", "Serviço", 30, errors, required=True)
    data = clean_text(data, "data", "Data", 10, errors, required=True)
    horario = clean_text(horario, "horario", "Horário", 5, errors, required=True)
    observacoes = clean_text(observacoes, "observacoes", "Observações", 2000, errors)
    if servico and servico not in SERVICOS:
        errors["servico"] = "Selecione um serviço permitido: Banho, Tosa ou Banho + Tosa."
    if data and "data" not in errors:
        try:
            if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", data):
                raise ValueError
            date.fromisoformat(data)
        except ValueError:
            errors["data"] = "Informe uma data válida no formato ano-mês-dia."
    if horario and "horario" not in errors:
        try:
            if not re.fullmatch(r"[0-9]{2}:[0-9]{2}", horario):
                raise ValueError
            time.fromisoformat(horario)
        except ValueError:
            errors["horario"] = "Informe um horário válido entre 00:00 e 23:59."
    try:
        if isinstance(id_animal, bool) or not isinstance(id_animal, (str, int)):
            raise ValueError
        id_animal = int(id_animal)
        if not 1 <= id_animal <= 9223372036854775807:
            raise ValueError
    except (ValueError, TypeError):
        errors["id_animal"] = "Selecione um animal cadastrado."
    if errors:
        raise ValidationError(errors)
    if animais.find_with_tutor(id_animal) is None:
        raise ValidationError({"id_animal": "Animal não encontrado ou sem tutor válido. Selecione um animal cadastrado."})
    try:
        return agendamentos.insert(data, horario, servico, STATUS_INICIAL, id_animal, observacoes or None)
    except sqlite3.IntegrityError:
        if agendamentos.find_occupied_slot(data, horario):
            raise ValidationError({"horario": "Já existe um agendamento nesta data e horário. Escolha outro horário."}) from None
        if animais.find_with_tutor(id_animal) is None:
            raise ValidationError({"id_animal": "Animal não encontrado ou sem tutor válido. Selecione um animal cadastrado."}) from None
        raise


def list_agendamentos():
    records = []
    for row in agendamentos.list_all():
        record = dict(row)
        record["data_formatada"] = date.fromisoformat(record["data"]).strftime("%d/%m/%Y")
        records.append(record)
    return records
