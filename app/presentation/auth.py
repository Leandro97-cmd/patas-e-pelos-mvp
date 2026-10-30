"""Login, sessão e proteção das páginas internas por padrão."""

from flask import Blueprint, g, redirect, render_template, request, session, url_for

from app.services.auth import authenticate, load_colaborador

auth = Blueprint("auth", __name__)


@auth.before_app_request
def load_and_require_user():
    g.user = None
    if request.endpoint == "static":
        return
    user_id = session.get("user_id")
    if user_id is not None:
        g.user = load_colaborador(user_id)
        if g.user is None:
            session.clear()
    # Somente login e arquivos estáticos são públicos; novas páginas serão protegidas.
    if request.endpoint not in (None, "auth.login") and g.user is None:
        return redirect(url_for("auth.login"))


@auth.route("/login", methods=["GET", "POST"])
def login():
    if g.user is not None:
        return redirect(url_for("main.index"))
    error = None
    usuario = ""
    if request.method == "POST":
        usuario = request.form.get("usuario", "")
        user = authenticate(usuario, request.form.get("senha", ""))
        if user is not None:
            session.clear()
            session["user_id"] = user["id"]
            session.permanent = True
            return redirect(url_for("main.index"), code=303)
        error = "Usuário ou senha inválidos."
    return render_template("login.html", error=error, usuario=usuario), 401 if error else 200


@auth.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"), code=303)
