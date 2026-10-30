"""Fluxo de autenticação e casos de segurança, com CSRF habilitado."""

import time

import pytest
from argon2 import PasswordHasher

from app import create_app
from app.repositories.colaboradores import find_by_username
from app.repositories.database import get_db
from app.services.auth import create_colaborador


def test_login_valido(client, login, credentials):
    response = login()
    assert response.status_code == 303
    assert response.location == "/"
    with client.session_transaction() as session:
        assert session["user_id"] == 1
        assert session.permanent
        assert set(session) == {"user_id", "_permanent"}
    assert credentials["senha"] not in response.get_data(as_text=True)


def test_login_normaliza_usuario(login):
    assert login(usuario="  DEMO.LOCAL  ").status_code == 303


@pytest.mark.parametrize("overrides", [
    {"usuario": "inexistente"},
    {"senha": "senha-incorreta-local"},
    {"usuario": "' OR 1=1 --"},
    {"usuario": ""},
    {"senha": ""},
    {"usuario": "a" * 65},
    {"senha": "a" * 129},
])
def test_login_invalido_generico(client, login, overrides):
    response = login(**overrides)
    assert response.status_code == 401
    assert "Usuário ou senha inválidos." in response.get_data(as_text=True)
    with client.session_transaction() as session:
        assert "user_id" not in session


def test_rota_protegida_sem_autenticacao(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response.location == "/login"
    assert "Colaborador Fictício" not in response.get_data(as_text=True)


def test_rota_protegida_apos_autenticacao(client, login):
    login()
    response = client.get("/")
    assert response.status_code == 200
    assert "Colaborador Fictício" in response.get_data(as_text=True)
    assert response.headers["Cache-Control"] == "no-store"


def test_logout(client, login, csrf_token):
    login()
    response = client.post("/logout", data={"csrf_token": csrf_token(client, "/")})
    assert response.status_code == 303
    assert response.location == "/login"
    with client.session_transaction() as session:
        assert "user_id" not in session
    assert client.get("/").location == "/login"


def test_logout_nao_aceita_get(client, login):
    login()
    assert client.get("/logout").status_code == 405
    assert client.get("/").status_code == 200


def test_logout_exige_csrf(client, login):
    login()
    assert client.post("/logout").status_code == 400
    assert client.get("/").status_code == 200


def test_login_exige_csrf(client, credentials):
    response = client.post("/login", data=credentials)
    assert response.status_code == 400
    assert "Recarregue a página" in response.get_data(as_text=True)
    assert client.get("/").location == "/login"


def test_token_csrf_invalido(login):
    assert login(csrf_token="token-adulterado").status_code == 400


def test_login_redireciona_colaborador_autenticado(client, login):
    login()
    response = client.get("/login")
    assert response.status_code == 302
    assert response.location == "/"


def test_login_labels_e_senha_nao_reexibida(client, login, credentials):
    response = login(usuario="inexistente")
    html = response.get_data(as_text=True)
    assert 'for="usuario"' in html
    assert 'for="senha"' in html
    assert 'type="password"' in html
    assert credentials["senha"] not in html


def test_senha_armazenada_com_argon2id(app, credentials):
    with app.app_context():
        user = find_by_username(credentials["usuario"])
        assert user["senha_hash"].startswith("$argon2id$")
        assert user["senha_hash"] != credentials["senha"]
        assert PasswordHasher().verify(user["senha_hash"], credentials["senha"])
        assert [row[1] for row in get_db().execute("PRAGMA table_info(colaboradores)")] == [
            "id", "nome", "usuario", "senha_hash"
        ]


def test_hashes_tem_salt_independente(app, credentials):
    with app.app_context():
        create_colaborador("Outro Fictício", "outro.local", credentials["senha"])
        assert find_by_username("outro.local")["senha_hash"] != find_by_username("demo.local")["senha_hash"]


def test_usuario_duplicado(app, credentials):
    with app.app_context(), pytest.raises(ValueError, match="já está cadastrado"):
        create_colaborador(credentials["nome"], "DEMO.LOCAL", credentials["senha"])


@pytest.mark.parametrize("overrides", [
    {"nome": " "}, {"nome": "a" * 101}, {"usuario": "ab"},
    {"usuario": "usuario com espaço"}, {"senha": "curta"}, {"senha": " " * 12},
])
def test_criacao_valida_campos_no_servidor(app, credentials, overrides):
    data = {**credentials, "usuario": "novo.local", **overrides}
    with app.app_context(), pytest.raises(ValueError):
        create_colaborador(**data)


def test_consulta_parametrizada(app):
    with app.app_context():
        assert find_by_username("' OR 1=1 --") is None


def test_nome_escapado_contra_xss(app, client, login):
    with app.app_context():
        db = get_db()
        db.execute("UPDATE colaboradores SET nome = ? WHERE id = ?", ("<script>alert(1)</script>", 1))
        db.commit()
    login()
    html = client.get("/").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_cookie_configurado(client, login):
    response = login()
    cookie = response.headers["Set-Cookie"]
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie


def test_cookie_secure_em_https(app, client, login):
    app.config["SESSION_COOKIE_SECURE"] = True
    assert "Secure;" in login().headers["Set-Cookie"]


def test_cookie_adulterado_nao_autentica(client):
    client.set_cookie("session", "cookie-forjado")
    assert client.get("/").location == "/login"


def test_sessao_expirada_nao_autentica(app, client, monkeypatch):
    with monkeypatch.context() as patch:
        expired_timestamp = int(time.time()) - 9 * 60 * 60
        patch.setattr("itsdangerous.timed.TimestampSigner.get_timestamp", lambda self: expired_timestamp)
        serializer = app.session_interface.get_signing_serializer(app)
        old_cookie = serializer.dumps({"user_id": 1, "_permanent": True})
    client.set_cookie("session", old_cookie)
    assert client.get("/").location == "/login"


def test_colaborador_removido_perde_acesso(app, client, login):
    login()
    with app.app_context():
        db = get_db()
        db.execute("DELETE FROM colaboradores WHERE id = ?", (1,))
        db.commit()
    assert client.get("/").location == "/login"
    with client.session_transaction() as session:
        assert "user_id" not in session


@pytest.mark.parametrize("key", [None, "chave-curta"])
def test_chave_secreta_obrigatoria(monkeypatch, key):
    monkeypatch.delenv("PATAS_SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="PATAS_SECRET_KEY"):
        create_app({"SECRET_KEY": key})


def test_erro_banco_nao_expoe_detalhes(app, client, login):
    with app.app_context():
        get_db().execute("DROP TABLE colaboradores")
    response = login()
    assert response.status_code == 503
    html = response.get_data(as_text=True)
    assert app.config["DATABASE"] not in html
    assert "sqlite" not in html.lower()
    assert "SELECT" not in html


def test_init_db_preserva_colaboradores(app):
    result = app.test_cli_runner().invoke(args=["init-db"])
    assert result.exit_code == 0
    with app.app_context():
        assert find_by_username("demo.local") is not None


def test_cli_cria_ficticio_sem_exibir_senha(app, credentials):
    result = app.test_cli_runner().invoke(
        args=["create-colaborador", "--nome", "Demo CLI", "--usuario", "demo.cli"],
        input=f"{credentials['senha']}\n{credentials['senha']}\n",
    )
    assert result.exit_code == 0
    assert credentials["senha"] not in result.output
    with app.app_context():
        assert find_by_username("demo.cli")["senha_hash"].startswith("$argon2id$")


def test_arquivos_estaticos_publicos(client):
    assert client.get("/static/css/style.css").status_code == 200
