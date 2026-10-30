"""Criação e configuração da aplicação Flask."""

from flask import Flask

from app.config import Config


def create_app(test_config=None):
    """Cria uma aplicação independente e aceita configurações para testes."""
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config is not None:
        app.config.update(test_config)

    from app.presentation.routes import main

    app.register_blueprint(main)
    return app
