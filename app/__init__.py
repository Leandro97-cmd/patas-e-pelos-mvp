"""Criação e configuração da aplicação Flask."""

import os
import sqlite3
from pathlib import Path

from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFError, CSRFProtect

from app.config import Config


def create_app(test_config=None):
    """Cria uma aplicação independente e aceita configurações para testes."""
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("PATAS_SECRET_KEY"),
        SESSION_COOKIE_SECURE=os.environ.get("PATAS_COOKIE_SECURE") == "1",
        DATABASE=str(Path(app.instance_path) / "patas_e_pelos.sqlite3"),
    )

    if test_config is not None:
        app.config.update(test_config)

    if not app.config.get("SECRET_KEY") or len(app.config["SECRET_KEY"]) < 32:
        raise RuntimeError("Configure PATAS_SECRET_KEY com uma chave aleatória de pelo menos 32 caracteres.")

    from app.cli import register_commands
    from app.presentation.auth import auth
    from app.presentation.animais import animais
    from app.presentation.routes import main
    from app.presentation.tutores import tutores
    from app.repositories.database import close_db

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(tutores)
    app.register_blueprint(animais)
    CSRFProtect(app)
    app.teardown_appcontext(close_db)
    register_commands(app)

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return render_template(
            "error.html", message="O formulário expirou ou não pôde ser validado. Recarregue a página e tente novamente."
        ), 400

    @app.errorhandler(sqlite3.Error)
    def database_error(error):
        app.logger.error("Falha de acesso ao banco de dados.")
        return render_template(
            "error.html", message="Não foi possível concluir a solicitação. Tente novamente mais tarde."
        ), 503

    @app.errorhandler(413)
    def request_too_large(error):
        return render_template(
            "error.html", message="O formulário enviado é muito grande. Reduza o conteúdo e tente novamente."
        ), 413

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self' https://cdn.jsdelivr.net; "
            "form-action 'self'; frame-ancestors 'none'; base-uri 'self'"
        )
        if request.endpoint != "static":
            response.headers["Cache-Control"] = "no-store"
        return response

    return app
