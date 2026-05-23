import hmac
import os
from datetime import datetime
from functools import wraps

from flask import Flask, abort, redirect, render_template, request, session, url_for
from markupsafe import Markup

from models import GrupoScout, db

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or os.getenv("FLASK_SECRET_KEY") or "dev-secret-key-change-me"

# CONFIG DB (Render + local)
db_url = os.getenv("DATABASE_URL")

if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///grupos.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# conectar db con la app
db.init_app(app)

# crear tablas si no existen
with app.app_context():
    db.create_all()


def admin_enabled():
    return bool(os.getenv("ADMIN_PASSWORD"))


def is_admin():
    return bool(session.get("is_admin"))


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not admin_enabled():
            abort(404)
        if not is_admin():
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


# año global para templates
@app.context_processor
def inject_template_globals():
    return {
        "current_year": datetime.utcnow().year,
        "admin_enabled": admin_enabled(),
        "is_admin": is_admin(),
    }


# -------------------- RUTAS --------------------

@app.route("/")
def home():
    entradas = obtener_entradas()
    return render_template("home_v2.html", now=datetime.now(), entradas=entradas)


@app.route("/galeria")
def galeria():
    fotos_dir = os.path.join(app.static_folder, "fotos")
    fotos = []
    if os.path.isdir(fotos_dir):
        for f in sorted(os.listdir(fotos_dir)):
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                fotos.append(f"fotos/{f}")
    return render_template("galeria.html", fotos=fotos)


@app.route("/materiales")
def materiales():
    mats_dir = os.path.join(app.static_folder, "materiales")
    mats = []
    if os.path.isdir(mats_dir):
        for f in sorted(os.listdir(mats_dir)):
            if f.lower().endswith(".pdf"):
                mats.append({
                    "nombre": os.path.splitext(f)[0].replace("-", " ").title(),
                    "ruta": f"materiales/{f}",
                })
    return render_template("materiales.html", materiales=mats)


@app.route("/grupos")
def ver_grupos():
    grupos = GrupoScout.query.order_by(GrupoScout.provincia.asc(), GrupoScout.ciudad.asc(), GrupoScout.nombre.asc()).all()
    return render_template("grupos.html", grupos=grupos)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if not admin_enabled():
        abort(404)

    error = None
    next_url = request.args.get("next") or url_for("ver_grupos")
    if not next_url.startswith("/"):
        next_url = url_for("ver_grupos")

    if request.method == "POST":
        password = request.form.get("password", "")
        expected = os.getenv("ADMIN_PASSWORD", "")
        if hmac.compare_digest(password, expected):
            session["is_admin"] = True
            return redirect(next_url)
        error = "Contraseña incorrecta."

    return render_template("admin_login.html", error=error, next_url=next_url)


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("ver_grupos"))


@app.route("/agregar_grupo", methods=["GET", "POST"])
def agregar_grupo():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        ciudad = request.form.get("ciudad", "").strip()
        provincia = request.form.get("provincia", "").strip()
        contacto = request.form.get("contacto", "").strip()

        if nombre and ciudad and provincia:
            nuevo = GrupoScout(
                nombre=nombre,
                ciudad=ciudad,
                provincia=provincia,
                contacto=contacto
            )
            db.session.add(nuevo)
            db.session.commit()
            return redirect(url_for("ver_grupos"))

    return render_template("agregar_grupo.html")


@app.route("/editar_grupo/<int:id>", methods=["GET", "POST"])
@admin_required
def editar_grupo(id):
    grupo = GrupoScout.query.get_or_404(id)

    if request.method == "POST":
        grupo.nombre = request.form.get("nombre", grupo.nombre).strip()
        grupo.ciudad = request.form.get("ciudad", grupo.ciudad).strip()
        grupo.provincia = request.form.get("provincia", grupo.provincia).strip()
        grupo.contacto = request.form.get("contacto", grupo.contacto).strip()
        db.session.commit()
        return redirect(url_for("ver_grupos"))

    return render_template("editar_grupo.html", grupo=grupo)


# -------------------- BLOG --------------------

def obtener_entradas():
    entradas_dir = os.path.join(app.static_folder, "entradas")

    if not os.path.isdir(entradas_dir):
        return []

    archivos = [f for f in os.listdir(entradas_dir) if f.endswith(".html")]
    archivos.sort(reverse=True)

    lista = []
    for nombre in archivos:
        ruta = os.path.join(entradas_dir, nombre)
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read()

        base = nombre[:-5]
        fecha = base[:10] if len(base) >= 10 else ""
        titulo = base[11:].replace("-", " ").capitalize() if len(base) > 11 else base

        lista.append({
            "archivo": nombre,
            "fecha": fecha,
            "titulo": titulo,
            "contenido": Markup(contenido)
        })

    return lista


@app.route("/blog")
def blog():
    entradas = obtener_entradas()
    return render_template("blog.html", entradas=entradas)


# -------------------- RUN --------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
