"""Formulário e listagem de tutores."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.services.tutores import create_tutor, list_tutores
from app.services.validation import ValidationError

tutores = Blueprint("tutores", __name__, url_prefix="/tutores")


@tutores.get("")
def index():
    return render_template("tutores/list.html", tutores=list_tutores())


@tutores.route("/novo", methods=["GET", "POST"])
def novo():
    data = {field: request.form.get(field, "") for field in ("nome", "telefone", "observacoes")}
    errors = {}
    if request.method == "POST":
        try:
            create_tutor(**data)
        except ValidationError as error:
            errors = error.errors
        else:
            flash("Tutor cadastrado com sucesso.")
            return redirect(url_for("tutores.index"), code=303)
    return render_template("tutores/form.html", data=data, errors=errors), 400 if errors else 200
