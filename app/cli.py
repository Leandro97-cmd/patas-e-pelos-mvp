"""Comandos locais de preparação do banco e criação de colaboradores."""

import click

from app.repositories.database import init_db
from app.services.auth import create_colaborador


def register_commands(app):
    @app.cli.command("init-db")
    def init_db_command():
        """Cria a tabela sem apagar colaboradores existentes."""
        init_db()
        click.echo("Banco de colaboradores preparado.")

    @app.cli.command("create-colaborador")
    @click.option("--nome", prompt="Nome")
    @click.option("--usuario", prompt="Usuário")
    def create_colaborador_command(nome, usuario):
        """Solicita a senha de forma oculta, sem recebê-la na linha de comando."""
        senha = click.prompt("Senha (12 a 128 caracteres)", hide_input=True, confirmation_prompt=True)
        try:
            create_colaborador(nome, usuario, senha)
        except ValueError as error:
            raise click.ClickException(str(error)) from None
        click.echo("Colaborador criado.")
