"""Novo agendamento e consulta da agenda."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.services.agendamentos import SERVICOS, create_agendamento, list_agendamentos
from app.services.animais import list_animais
from app.services.validation import ValidationError

agendamentos = Blueprint("agendamentos", __name__, url_prefix="/agendamentos")


@agendamentos.get("")
def index():
    return render_template("agendamentos/list.html", agendamentos=list_agendamentos())


@agendamentos.route("/novo", methods=["GET", "POST"])
def novo():
    # Status é definido pelo serviço, nunca pelo formulário recebido.
    data = {field: request.form.get(field, "") for field in (
        "id_animal", "servico", "data", "horario", "observacoes"
    )}
    errors = {}
    if request.method == "POST":
        try:
            create_agendamento(**data)
        except ValidationError as error:
            errors = error.errors
        else:
            flash("Agendamento criado com sucesso.")
            return redirect(url_for("agendamentos.index"), code=303)
    return render_template(
        "agendamentos/form.html", data=data, errors=errors,
        animais=list_animais(), servicos=SERVICOS,
    ), 400 if errors else 200
