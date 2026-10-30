"""Fluxos de tutores e animais, validação, vínculo e proteção das rotas."""

import sqlite3

import pytest

from app.repositories import animais as animal_repository
from app.repositories.colaboradores import find_by_username
from app.repositories.database import get_db, init_db
from app.services.animais import create_animal
from app.services.tutores import create_tutor


@pytest.fixture
def authed_client(client, login):
    assert login().status_code == 303
    return client


@pytest.fixture
def submit(authed_client, csrf_token):
    def post(path, data):
        return authed_client.post(path, data={**data, "csrf_token": csrf_token(authed_client, path)})
    return post


@pytest.fixture
def tutor_data():
    return {"nome": "Ana Exemplo", "telefone": "(11) 99999-0000", "observacoes": "Contato de demonstração."}


@pytest.fixture
def tutor_id(app, tutor_data):
    with app.app_context():
        return create_tutor(**tutor_data)


@pytest.fixture
def animal_data(tutor_id):
    return {"nome": "Bidu", "especie": "Cão", "raca": "Sem raça definida", "porte": "Médio",
            "observacoes": "Animal de demonstração.", "id_tutor": str(tutor_id)}


def test_cadastro_valido_tutor(app, authed_client, submit, tutor_data):
    response = submit("/tutores/novo", tutor_data)
    assert response.status_code == 303
    assert response.location == "/tutores"
    html = authed_client.get(response.location).get_data(as_text=True)
    assert "Tutor cadastrado com sucesso." in html
    assert 'role="status"' in html
    assert "Ana Exemplo" in html
    with app.app_context():
        row = get_db().execute("SELECT * FROM tutores").fetchone()
        assert isinstance(row["id_tutor"], int)
        assert row["nome"] == tutor_data["nome"]
        assert row["telefone"] == "11999990000"
        assert row["observacoes"] == tutor_data["observacoes"]
    # Atualizar a listagem não repete o cadastro.
    assert authed_client.get("/tutores").status_code == 200
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM tutores").fetchone()[0] == 1


@pytest.mark.parametrize("field", ["nome", "telefone"])
@pytest.mark.parametrize("value", [None, "", "   "])
def test_tutor_campos_obrigatorios(app, submit, tutor_data, field, value):
    data = {**tutor_data}
    if value is None:
        data.pop(field)
    else:
        data[field] = value
    response = submit("/tutores/novo", data)
    assert response.status_code == 400
    assert "é obrigatório" in response.get_data(as_text=True)
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM tutores").fetchone()[0] == 0


def test_listagem_tutor(authed_client, tutor_id, tutor_data):
    response = authed_client.get("/tutores")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert tutor_data["nome"] in html
    assert "11999990000" in html
    assert tutor_data["observacoes"] in html


def test_duplicidade_nome_e_telefone_normalizados(app, submit):
    with app.app_context():
        create_tutor("José   Exemplo", "(11) 99999-0000")
    response = submit("/tutores/novo", {"nome": " JOSE exemplo ", "telefone": "11 999990000"})
    assert response.status_code == 400
    html = response.get_data(as_text=True)
    assert "Já existe um tutor com este nome e telefone" in html
    assert "UNIQUE" not in html
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM tutores").fetchone()[0] == 1


@pytest.mark.parametrize("change", [{"nome": "Outro Exemplo"}, {"telefone": "11988880000"}])
def test_tutor_permite_mesmo_telefone_ou_mesmo_nome(app, submit, tutor_id, tutor_data, change):
    assert submit("/tutores/novo", {**tutor_data, **change}).status_code == 303
    with app.app_context():
        ids = [row[0] for row in get_db().execute("SELECT id_tutor FROM tutores")]
        assert len(ids) == len(set(ids)) == 2


@pytest.mark.parametrize("telefone", ["abc", "123", "9" * 16, "11999990000 ramal 2"])
def test_telefone_invalido(submit, tutor_data, telefone):
    response = submit("/tutores/novo", {**tutor_data, "telefone": telefone})
    assert response.status_code == 400
    assert "8 a 15 dígitos" in response.get_data(as_text=True)


@pytest.mark.parametrize("field,value", [("nome", "a" * 101), ("telefone", "1" * 33), ("observacoes", "a" * 2001)])
def test_tutor_limites_no_servidor(submit, tutor_data, field, value):
    assert submit("/tutores/novo", {**tutor_data, field: value}).status_code == 400


def test_tutor_observacoes_opcionais(app, submit, tutor_data):
    data = {**tutor_data}
    data.pop("observacoes")
    assert submit("/tutores/novo", data).status_code == 303
    with app.app_context():
        assert get_db().execute("SELECT observacoes FROM tutores").fetchone()[0] is None


def test_observacoes_unicode_no_limite_sao_aceitas(app, submit, tutor_data):
    observations = "犬" * 2000
    assert submit("/tutores/novo", {**tutor_data, "observacoes": observations}).status_code == 303
    with app.app_context():
        assert get_db().execute("SELECT observacoes FROM tutores").fetchone()[0] == observations


def test_envio_acima_limite_total_tem_mensagem_segura(app, submit, tutor_data):
    response = submit("/tutores/novo", {**tutor_data, "observacoes": "a" * (70 * 1024)})
    assert response.status_code == 413
    assert "O formulário enviado é muito grande" in response.get_data(as_text=True)
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM tutores").fetchone()[0] == 0


def test_formulario_preserva_dados_e_associa_erros(submit, tutor_data):
    html = submit("/tutores/novo", {**tutor_data, "telefone": ""}).get_data(as_text=True)
    assert 'value="Ana Exemplo"' in html
    assert 'id="telefone-error"' in html
    assert 'aria-describedby="telefone-hint telefone-error"' in html
    assert 'aria-invalid="true"' in html
    assert 'role="alert"' in html


def test_cadastro_valido_animal(app, authed_client, submit, animal_data, tutor_id):
    response = submit("/animais/novo", animal_data)
    assert response.status_code == 303
    assert response.location == "/animais"
    assert "Animal cadastrado com sucesso." in authed_client.get(response.location).get_data(as_text=True)
    with app.app_context():
        row = get_db().execute("SELECT * FROM animais").fetchone()
        assert isinstance(row["id_animal"], int)
        for field in ("nome", "especie", "raca", "porte", "observacoes"):
            assert row[field] == animal_data[field]
        assert row["id_tutor"] == tutor_id


def test_animal_sem_tutor(app, submit, animal_data):
    data = {**animal_data}
    data.pop("id_tutor")
    response = submit("/animais/novo", data)
    assert response.status_code == 400
    assert "Selecione um tutor cadastrado." in response.get_data(as_text=True)
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM animais").fetchone()[0] == 0


def test_animal_tutor_inexistente(app, submit, animal_data):
    response = submit("/animais/novo", {**animal_data, "id_tutor": "999999"})
    assert response.status_code == 400
    assert "O tutor selecionado não existe" in response.get_data(as_text=True)
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM animais").fetchone()[0] == 0


@pytest.mark.parametrize("id_tutor", ["", "0", "-1", "abc", "1.5", "9223372036854775808", "1 OR 1=1"])
def test_animal_tutor_invalido(submit, animal_data, id_tutor):
    response = submit("/animais/novo", {**animal_data, "id_tutor": id_tutor})
    assert response.status_code == 400
    assert "Selecione um tutor cadastrado." in response.get_data(as_text=True)


@pytest.mark.parametrize("field", ["nome", "especie", "porte"])
@pytest.mark.parametrize("value", [None, "", "  "])
def test_animal_campos_obrigatorios(app, submit, animal_data, field, value):
    data = {**animal_data}
    if value is None:
        data.pop(field)
    else:
        data[field] = value
    response = submit("/animais/novo", data)
    assert response.status_code == 400
    assert "é obrigatório" in response.get_data(as_text=True)
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM animais").fetchone()[0] == 0


@pytest.mark.parametrize("field,limit", [("nome", 100), ("especie", 60), ("porte", 30), ("raca", 100), ("observacoes", 2000)])
def test_animal_limites_no_servidor(submit, animal_data, field, limit):
    assert submit("/animais/novo", {**animal_data, field: "a" * (limit + 1)}).status_code == 400


def test_animal_campos_opcionais(app, submit, animal_data):
    data = {key: value for key, value in animal_data.items() if key not in ("raca", "observacoes")}
    assert submit("/animais/novo", data).status_code == 303
    with app.app_context():
        row = get_db().execute("SELECT raca, observacoes FROM animais").fetchone()
        assert tuple(row) == (None, None)


def test_listagem_animal_identifica_tutor(app, authed_client, animal_data, tutor_data, tutor_id):
    with app.app_context():
        create_animal(**animal_data)
    response = authed_client.get("/animais")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert animal_data["nome"] in html
    assert animal_data["especie"] in html
    assert animal_data["raca"] in html
    assert animal_data["porte"] in html
    assert tutor_data["nome"] in html
    assert f"#{tutor_id} —" in html


def test_formulario_animal_sem_tutores_orienta_cadastro(authed_client):
    html = authed_client.get("/animais/novo").get_data(as_text=True)
    assert "Nenhum tutor cadastrado" in html
    assert 'href="/tutores/novo"' in html
    assert 'type="submit" disabled>Cadastrar animal' in html


def test_formulario_animal_preserva_tutor_e_dados(submit, animal_data, tutor_id):
    html = submit("/animais/novo", {**animal_data, "porte": ""}).get_data(as_text=True)
    assert f'value="{tutor_id}" selected' in html
    assert 'value="Bidu"' in html
    assert 'id="porte-error"' in html


@pytest.mark.parametrize("path,label", [("/tutores", "tutor"), ("/animais", "animal")])
def test_listas_vazias(authed_client, path, label):
    response = authed_client.get(path)
    assert response.status_code == 200
    assert f"Nenhum {label} cadastrado" in response.get_data(as_text=True)


@pytest.mark.parametrize("path", ["/tutores", "/tutores/novo", "/animais", "/animais/novo"])
def test_rotas_cadastro_exigem_autenticacao(client, path):
    response = client.get(path)
    assert response.status_code == 302
    assert response.location == "/login"


@pytest.mark.parametrize("path", ["/tutores/novo", "/animais/novo"])
def test_post_sem_autenticacao_nao_cria_registros(app, client, path):
    response = client.post(path, data={"nome": "Visitante", "telefone": "11999990000"})
    assert response.status_code == 302
    assert response.location == "/login"
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM tutores").fetchone()[0] == 0
        assert get_db().execute("SELECT COUNT(*) FROM animais").fetchone()[0] == 0


@pytest.mark.parametrize("path", ["/tutores/novo", "/animais/novo"])
def test_cadastros_exigem_csrf(authed_client, path):
    assert authed_client.post(path, data={"nome": "Exemplo"}).status_code == 400


def test_menu_interno_inclui_quatro_opcoes(authed_client):
    html = authed_client.get("/").get_data(as_text=True)
    for path in ("/tutores", "/tutores/novo", "/animais", "/animais/novo"):
        assert f'href="{path}"' in html


def test_cadastros_escapam_html_e_usam_parametros(app, authed_client, submit):
    malicious = "<script>alert(1)</script>"
    sql_text = "'); DROP TABLE tutores; --"
    assert submit("/tutores/novo", {"nome": malicious, "telefone": "11999990000", "observacoes": sql_text}).status_code == 303
    html = authed_client.get("/tutores").get_data(as_text=True)
    assert malicious not in html
    assert "&lt;script&gt;" in html
    with app.app_context():
        row = get_db().execute("SELECT id_tutor, observacoes FROM tutores").fetchone()
        assert row["observacoes"] == sql_text
        id_tutor = row["id_tutor"]
    assert submit("/animais/novo", {"nome": malicious, "especie": sql_text, "porte": "Pequeno", "id_tutor": str(id_tutor)}).status_code == 303
    html = authed_client.get("/animais").get_data(as_text=True)
    assert malicious not in html
    assert "&lt;script&gt;" in html
    with app.app_context():
        assert get_db().execute("SELECT especie FROM animais").fetchone()[0] == sql_text


def test_chave_estrangeira_impede_animal_orfao(app):
    with app.app_context(), pytest.raises(sqlite3.IntegrityError):
        animal_repository.insert("Bidu", "Cão", None, "Pequeno", None, 999999)


def test_init_db_atualiza_etapa2_sem_apagar_colaborador(app):
    with app.app_context():
        before = dict(find_by_username("demo.local"))
        db = get_db()
        db.execute("DROP TABLE animais")
        db.execute("DROP TABLE tutores")
        db.commit()
    result = app.test_cli_runner().invoke(args=["init-db"])
    assert result.exit_code == 0
    with app.app_context():
        assert dict(find_by_username("demo.local")) == before
        id_tutor = create_tutor("Tutor Exemplo", "11999990000")
        assert create_animal("Bidu", "Cão", "Pequeno", id_tutor) > 0


def test_init_db_preserva_tutores_animais_e_colaborador(app, animal_data):
    with app.app_context():
        animal_id = create_animal(**animal_data)
        init_db()
        assert get_db().execute("SELECT id_animal FROM animais").fetchone()[0] == animal_id
        assert get_db().execute("SELECT COUNT(*) FROM tutores").fetchone()[0] == 1
        assert find_by_username("demo.local") is not None


def test_erro_banco_cadastro_nao_expoe_detalhes(app, submit, tutor_data):
    with app.app_context():
        get_db().execute("DROP TABLE tutores")
    response = submit("/tutores/novo", tutor_data)
    html = response.get_data(as_text=True)
    assert response.status_code == 503
    assert "Não foi possível concluir" in html
    assert app.config["DATABASE"] not in html
    assert "INSERT" not in html
    assert "sqlite" not in html.lower()
