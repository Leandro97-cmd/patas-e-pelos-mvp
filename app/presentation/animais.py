"""Formulário e listagem de animais."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.services.animais import create_animal, list_animais
from app.services.tutores import list_tutores
from app.services.validation import ValidationError

animais = Blueprint("animais", __name__, url_prefix="/animais")


@animais.get("")
def index():
    return render_template("animais/list.html", animais=list_animais())


@animais.route("/novo", methods=["GET", "POST"])
def novo():
    data = {field: request.form.get(field, "") for field in (
        "nome", "especie", "raca", "porte", "observacoes", "id_tutor"
    )}
    errors = {}
    if request.method == "POST":
        try:
            create_animal(**data)
        except ValidationError as error:
            errors = error.errors
        else:
            flash("Animal cadastrado com sucesso.")
            return redirect(url_for("animais.index"), code=303)
    return render_template(
        "animais/form.html", data=data, errors=errors, tutores=list_tutores()
    ), 400 if errors else 200
