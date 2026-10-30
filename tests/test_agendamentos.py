"""Agendamentos: fluxo completo, validação, relacionamentos e segurança."""

import sqlite3

import pytest

from app.repositories import agendamentos as repository
from app.repositories.database import get_db
from app.services.agendamentos import create_agendamento, list_agendamentos
from app.services.animais import create_animal
from app.services.tutores import create_tutor


@pytest.fixture
def authed_client(client, login):
    assert login().status_code == 303
    return client


@pytest.fixture
def submit(authed_client, csrf_token):
    def post(data):
        return authed_client.post("/agendamentos/novo", data={
            **data, "csrf_token": csrf_token(authed_client, "/agendamentos/novo")
        })
    return post


@pytest.fixture
def animal_id(app):
    with app.app_context():
        id_tutor = create_tutor("Ana Exemplo", "11999990000")
        return create_animal("Bidu", "Cão", "Pequeno", id_tutor)


@pytest.fixture
def appointment_data(animal_id):
    return {"id_animal": str(animal_id), "servico": "Banho", "data": "2030-11-20",
            "horario": "09:30", "observacoes": "Atendimento de demonstração."}


@pytest.mark.parametrize("servico", ["Banho", "Tosa", "Banho + Tosa"])
def test_criacao_valida_e_status_inicial(app, authed_client, submit, appointment_data, animal_id, servico):
    data = {**appointment_data, "servico": servico}
    response = submit(data)
    assert response.status_code == 303
    assert response.location == "/agendamentos"
    html = authed_client.get(response.location).get_data(as_text=True)
    assert "Agendamento criado com sucesso." in html
    assert 'role="status"' in html
    assert "Agendado" in html
    with app.app_context():
        row = get_db().execute("SELECT * FROM agendamentos").fetchone()
        assert isinstance(row["id_agendamento"], int)
        assert row["id_animal"] == animal_id
        assert row["status"] == "Agendado"
        for field in ("data", "horario", "servico", "observacoes"):
            assert row[field] == data[field]
    authed_client.get("/agendamentos")
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM agendamentos").fetchone()[0] == 1


@pytest.mark.parametrize("field", ["id_animal", "servico", "data", "horario"])
@pytest.mark.parametrize("value", [None, "", "   "])
def test_campos_obrigatorios(app, submit, appointment_data, field, value):
    data = {**appointment_data}
    if value is None:
        data.pop(field)
    else:
        data[field] = value
    response = submit(data)
    assert response.status_code == 400
    assert f'href="#{field}"' in response.get_data(as_text=True)
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM agendamentos").fetchone()[0] == 0


@pytest.mark.parametrize("id_animal", ["999999", "0", "-1", "abc", "1.5", "9223372036854775808", "1 OR 1=1"])
def test_animal_invalido_ou_inexistente(submit, appointment_data, id_animal):
    response = submit({**appointment_data, "id_animal": id_animal})
    assert response.status_code == 400
    assert 'id="id_animal-error"' in response.get_data(as_text=True)


@pytest.mark.parametrize("servico", ["banho", "Consulta", "' OR 1=1 --", "a" * 31])
def test_servico_fora_conjunto_permitido(submit, appointment_data, servico):
    response = submit({**appointment_data, "servico": servico})
    assert response.status_code == 400
    assert "Selecione um serviço permitido" in response.get_data(as_text=True)


@pytest.mark.parametrize("data", ["2030-02-30", "2030-02-29", "2030-13-01", "0000-01-01", "20/11/2030", "2030-1-01", "20301120"])
def test_data_invalida(submit, appointment_data, data):
    response = submit({**appointment_data, "data": data})
    assert response.status_code == 400
    assert 'id="data-error"' in response.get_data(as_text=True)


@pytest.mark.parametrize("horario", ["24:00", "12:60", "9:30", "09:30:00", "09h30", "-1:00"])
def test_horario_invalido(submit, appointment_data, horario):
    response = submit({**appointment_data, "horario": horario})
    assert response.status_code == 400
    assert 'id="horario-error"' in response.get_data(as_text=True)


@pytest.mark.parametrize("data,horario", [("2032-02-29", "00:00"), ("2020-01-01", "23:59")])
def test_datas_calendario_e_limites_horario_validos(submit, appointment_data, data, horario):
    assert submit({**appointment_data, "data": data, "horario": horario}).status_code == 303


@pytest.mark.parametrize("status", ["Concluído", "Cancelado", "Inventado"])
def test_status_enviado_pelo_cliente_nao_altera_status_inicial(app, submit, appointment_data, status):
    assert submit({**appointment_data, "status": status}).status_code == 303
    with app.app_context():
        assert get_db().execute("SELECT status FROM agendamentos").fetchone()[0] == "Agendado"


def test_observacoes_opcionais(app, submit, appointment_data):
    data = {**appointment_data}
    data.pop("observacoes")
    assert submit(data).status_code == 303
    with app.app_context():
        assert get_db().execute("SELECT observacoes FROM agendamentos").fetchone()[0] is None


def test_limite_observacoes(submit, appointment_data):
    assert submit({**appointment_data, "observacoes": "a" * 2001}).status_code == 400


def test_listagem_exibe_relacionamento_correto(app, authed_client, appointment_data):
    with app.app_context():
        create_agendamento(**appointment_data)
        outro_tutor = create_tutor("Bruno Exemplo", "11988880000")
        outro_animal = create_animal("Luna", "Gato", "Pequeno", outro_tutor)
        create_agendamento(outro_animal, "Tosa", "2030-11-20", "10:00")
        rows = list_agendamentos()
        assert [(row["animal_nome"], row["tutor_nome"]) for row in rows] == [
            ("Bidu", "Ana Exemplo"), ("Luna", "Bruno Exemplo")
        ]
    response = authed_client.get("/agendamentos")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    for text in ("Bidu", "Ana Exemplo", "Luna", "Bruno Exemplo", "Banho", "Tosa", "20/11/2030", "09:30", "Agendado"):
        assert text in html


def test_agenda_ordenada_por_data_e_horario(app, authed_client, appointment_data):
    slots = [("2030-11-21", "08:00"), ("2030-11-20", "10:00"), ("2030-11-20", "09:30")]
    with app.app_context():
        for data, horario in slots:
            create_agendamento(**{**appointment_data, "data": data, "horario": horario})
        assert [(row["data"], row["horario"]) for row in list_agendamentos()] == sorted(slots)
    html = authed_client.get("/agendamentos").get_data(as_text=True)
    assert html.index("09:30") < html.index("10:00") < html.index("08:00")


def test_agenda_vazia(authed_client):
    response = authed_client.get("/agendamentos")
    assert response.status_code == 200
    assert "Nenhum agendamento cadastrado" in response.get_data(as_text=True)


@pytest.mark.parametrize("outro_animal", [False, True])
def test_conflito_mesma_data_e_horario(app, submit, appointment_data, outro_animal):
    with app.app_context():
        create_agendamento(**appointment_data)
        if outro_animal:
            id_tutor = create_tutor("Outro Tutor", "11988880000")
            new_animal = create_animal("Luna", "Gato", "Pequeno", id_tutor)
            appointment_data = {**appointment_data, "id_animal": str(new_animal)}
    response = submit(appointment_data)
    assert response.status_code == 400
    html = response.get_data(as_text=True)
    assert "Já existe um agendamento nesta data e horário" in html
    assert "UNIQUE" not in html
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM agendamentos").fetchone()[0] == 1


@pytest.mark.parametrize("change", [{"data": "2030-11-21"}, {"horario": "09:31"}])
def test_data_ou_horario_diferente_permitido(app, submit, appointment_data, change):
    with app.app_context():
        create_agendamento(**appointment_data)
    assert submit({**appointment_data, **change}).status_code == 303


def test_conflito_tambem_protegido_no_banco(app, appointment_data, animal_id):
    with app.app_context():
        create_agendamento(**appointment_data)
        with pytest.raises(sqlite3.IntegrityError):
            repository.insert("2030-11-20", "09:30", "Tosa", "Agendado", animal_id, None)


@pytest.mark.parametrize("servico,status", [("Consulta", "Agendado"), ("Banho", "Inventado")])
def test_banco_rejeita_servico_ou_status_desconhecido(app, animal_id, servico, status):
    with app.app_context(), pytest.raises(sqlite3.IntegrityError):
        repository.insert("2030-11-20", "09:30", servico, status, animal_id, None)


@pytest.mark.parametrize("status", ["Concluído", "Cancelado"])
def test_modelo_reserva_status_futuros(app, animal_id, status):
    # Valida somente o modelo, sem criar ações de conclusão ou cancelamento.
    with app.app_context():
        assert repository.insert("2030-11-20", "09:30", "Banho", status, animal_id, None) > 0


def test_banco_impede_agendamento_sem_animal_existente(app):
    with app.app_context(), pytest.raises(sqlite3.IntegrityError):
        repository.insert("2030-11-20", "09:30", "Banho", "Agendado", 999999, None)


def test_animal_sem_tutor_valido_nao_pode_ser_agendado(app, submit, appointment_data):
    with app.app_context():
        db = get_db()
        db.execute("PRAGMA foreign_keys = OFF")
        cursor = db.execute("""
            INSERT INTO animais (nome, especie, porte, id_tutor) VALUES (?, ?, ?, ?)
        """, ("Animal órfão de base antiga", "Cão", "Pequeno", 999999))
        db.commit()
        id_animal = cursor.lastrowid
        db.execute("PRAGMA foreign_keys = ON")
    response = submit({**appointment_data, "id_animal": str(id_animal)})
    assert response.status_code == 400
    assert "sem tutor válido" in response.get_data(as_text=True)


def test_formulario_identifica_animal_tutor_e_rotulos(authed_client, animal_id):
    html = authed_client.get("/agendamentos/novo").get_data(as_text=True)
    assert "Bidu" in html
    assert "Ana Exemplo" in html
    for field in ("id_animal", "servico", "data", "horario", "observacoes"):
        assert f'for="{field}"' in html
    assert 'type="date"' in html
    assert 'type="time"' in html


def test_formulario_sem_animais_orienta_cadastro(authed_client):
    html = authed_client.get("/agendamentos/novo").get_data(as_text=True)
    assert "Nenhum animal cadastrado com tutor válido" in html
    assert 'href="/animais/novo"' in html
    assert 'type="submit" disabled>Salvar agendamento' in html


def test_formulario_preserva_dados_apos_erro(submit, appointment_data, animal_id):
    html = submit({**appointment_data, "horario": ""}).get_data(as_text=True)
    assert f'value="{animal_id}" selected' in html
    assert 'value="Banho" selected' in html
    assert 'value="2030-11-20"' in html
    assert appointment_data["observacoes"] in html
    assert 'aria-describedby="horario-hint horario-error"' in html


@pytest.mark.parametrize("path", ["/agendamentos", "/agendamentos/novo"])
def test_rotas_exigem_autenticacao(client, path):
    response = client.get(path)
    assert response.status_code == 302
    assert response.location == "/login"


def test_post_sem_autenticacao_nao_cria(app, client, appointment_data):
    assert client.post("/agendamentos/novo", data=appointment_data).location == "/login"
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM agendamentos").fetchone()[0] == 0


@pytest.mark.parametrize("token", [None, "adulterado"])
def test_cadastro_exige_csrf(authed_client, appointment_data, token):
    data = {**appointment_data}
    if token is not None:
        data["csrf_token"] = token
    assert authed_client.post("/agendamentos/novo", data=data).status_code == 400


def test_menu_e_retorno_incluem_agenda(authed_client):
    html = authed_client.get("/").get_data(as_text=True)
    assert 'href="/agendamentos"' in html
    assert 'href="/agendamentos/novo"' in html
    agenda = authed_client.get("/agendamentos").get_data(as_text=True)
    assert "Voltar ao menu" in agenda


def test_observacoes_escapadas_e_consulta_parametrizada(app, authed_client, submit, appointment_data):
    text = "<script>alert(1)</script>'); DROP TABLE agendamentos; --"
    assert submit({**appointment_data, "observacoes": text}).status_code == 303
    html = authed_client.get("/agendamentos").get_data(as_text=True)
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    with app.app_context():
        assert get_db().execute("SELECT observacoes FROM agendamentos").fetchone()[0] == text


def test_init_db_atualiza_etapa3_e_preserva_dados(app, appointment_data):
    with app.app_context():
        db = get_db()
        before = {table: [tuple(row) for row in db.execute(f"SELECT * FROM {table}")]
                  for table in ("colaboradores", "tutores", "animais")}
        db.execute("DROP TABLE agendamentos")
    result = app.test_cli_runner().invoke(args=["init-db"])
    assert result.exit_code == 0
    with app.app_context():
        db = get_db()
        for table, rows in before.items():
            assert [tuple(row) for row in db.execute(f"SELECT * FROM {table}")] == rows
        assert create_agendamento(**appointment_data) > 0
    assert app.test_cli_runner().invoke(args=["init-db"]).exit_code == 0
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM agendamentos").fetchone()[0] == 1


def test_erro_banco_sem_detalhes_internos(app, submit, appointment_data):
    with app.app_context():
        get_db().execute("DROP TABLE agendamentos")
    response = submit(appointment_data)
    html = response.get_data(as_text=True)
    assert response.status_code == 503
    assert "Não foi possível concluir" in html
    assert app.config["DATABASE"] not in html
    assert "INSERT" not in html
    assert "sqlite" not in html.lower()
