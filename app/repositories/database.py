"""Conexões SQLite por requisição e criação não destrutiva da estrutura."""

import sqlite3
from pathlib import Path

from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"], timeout=5)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    Path(current_app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS colaboradores (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            usuario TEXT NOT NULL UNIQUE COLLATE NOCASE,
            senha_hash TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS tutores (
            id_tutor INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL,
            observacoes TEXT,
            nome_chave TEXT NOT NULL,
            UNIQUE (nome_chave, telefone)
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS animais (
            id_animal INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            especie TEXT NOT NULL,
            raca TEXT,
            porte TEXT NOT NULL,
            observacoes TEXT,
            id_tutor INTEGER NOT NULL,
            FOREIGN KEY (id_tutor) REFERENCES tutores (id_tutor) ON DELETE RESTRICT
        )
    """)
    db.commit()
