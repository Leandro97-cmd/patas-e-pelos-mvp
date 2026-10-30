"""Validação de colaboradores e autenticação usando Argon2id."""

import re
import secrets
import sqlite3

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.repositories import colaboradores

password_hasher = PasswordHasher()
# Também verifica um hash quando o usuário não existe para reduzir diferenças de tempo.
dummy_hash = password_hasher.hash(secrets.token_urlsafe(32))


def create_colaborador(nome, usuario, senha):
    nome = nome.strip()
    usuario = usuario.strip().lower()
    if not nome or len(nome) > 100:
        raise ValueError("Informe um nome com 1 a 100 caracteres.")
    if not re.fullmatch(r"[a-z0-9_.-]{3,64}", usuario):
        raise ValueError("O usuário deve ter de 3 a 64 caracteres: letras sem acentos, números, ponto, hífen ou sublinhado.")
    if not 12 <= len(senha) <= 128 or not senha.strip():
        raise ValueError("A senha deve ter de 12 a 128 caracteres e não pode conter apenas espaços.")
    try:
        return colaboradores.insert(nome, usuario, password_hasher.hash(senha))
    except sqlite3.IntegrityError:
        raise ValueError("Esse nome de usuário já está cadastrado.") from None


def authenticate(usuario, senha):
    usuario = usuario.strip().lower()
    if not re.fullmatch(r"[a-z0-9_.-]{3,64}", usuario) or not 12 <= len(senha) <= 128:
        return None
    user = colaboradores.find_by_username(usuario)
    try:
        password_hasher.verify(user["senha_hash"] if user else dummy_hash, senha)
    except (VerificationError, InvalidHashError):
        return None
    if user is None:
        return None
    if password_hasher.check_needs_rehash(user["senha_hash"]):
        colaboradores.update_password_hash(user["id"], password_hasher.hash(senha))
    return user


def load_colaborador(user_id):
    if not isinstance(user_id, int):
        return None
    return colaboradores.find_by_id(user_id)
