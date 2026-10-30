"""Cadastro e consulta de tutores, incluindo prevenção simples de duplicidade."""

import re
import sqlite3
import unicodedata

from app.repositories import tutores
from app.services.validation import ValidationError, clean_text


def create_tutor(nome, telefone, observacoes=""):
    errors = {}
    nome = clean_text(nome, "nome", "Nome", 100, errors, required=True)
    telefone = clean_text(telefone, "telefone", "Telefone", 32, errors, required=True)
    observacoes = clean_text(observacoes, "observacoes", "Observações", 2000, errors)
    digits = re.sub(r"[^0-9]", "", telefone)
    if telefone and (not re.fullmatch(r"\+?[0-9 ()-]+", telefone) or not 8 <= len(digits) <= 15):
        errors["telefone"] = "Informe um telefone com 8 a 15 dígitos. Use apenas números, espaços, parênteses, hífen e + inicial."
    if errors:
        raise ValidationError(errors)
    nome = " ".join(nome.split())
    nome_chave = "".join(
        char for char in unicodedata.normalize("NFKD", nome.casefold())
        if not unicodedata.combining(char)
    )
    try:
        return tutores.insert(nome, digits, observacoes or None, nome_chave)
    except sqlite3.IntegrityError:
        if tutores.find_by_identity(nome_chave, digits):
            raise ValidationError({"telefone": "Já existe um tutor com este nome e telefone. Consulte a lista de tutores."}) from None
        raise


def list_tutores():
    return tutores.list_all()
