"""Aplicação isolada e credenciais fictícias geradas a cada teste."""

import re
import secrets

import pytest

from app import create_app
from app.repositories.database import init_db
from app.services.auth import create_colaborador


@pytest.fixture
def credentials():
    return {"nome": "Colaborador Fictício", "usuario": "demo.local", "senha": secrets.token_urlsafe(24)}


@pytest.fixture
def app(tmp_path, credentials):
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": secrets.token_hex(32),
        "DATABASE": str(tmp_path / "test.sqlite3"),
    })
    with app.app_context():
        init_db()
        create_colaborador(**credentials)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def csrf_token():
    def get_token(client, path="/login"):
        response = client.get(path)
        match = re.search(r'name="csrf_token" value="([^"]+)"', response.get_data(as_text=True))
        assert match is not None
        return match.group(1)
    return get_token


@pytest.fixture
def login(client, csrf_token, credentials):
    def do_login(**overrides):
        data = {"usuario": credentials["usuario"], "senha": credentials["senha"],
                "csrf_token": csrf_token(client)}
        data.update(overrides)
        return client.post("/login", data=data)
    return do_login


@pytest.fixture
def authed_client(client, login):
    """Cliente autenticado pelo formulário real, com CSRF habilitado."""
    assert login().status_code == 303
    return client
