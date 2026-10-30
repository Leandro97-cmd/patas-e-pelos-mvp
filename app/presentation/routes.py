"""Rotas da página inicial."""

from flask import Blueprint, render_template

main = Blueprint("main", __name__)


@main.get("/")
def index():
    """Exibe a apresentação inicial do Patas e Pelos."""
    return render_template("index.html")
