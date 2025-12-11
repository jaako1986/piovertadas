import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from markupsafe import Markup

# ----------------------------------------------------
# APP PRINCIPAL (UNA SOLA)
# ----------------------------------------------------
app = Flask(__name__)

# ----------------------------------------------------
# CONFIGURACIÓN DE BASE DE DATOS
# ----------------------------------------------------
db_url = os.getenv("DATABASE_URL")
if db_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///grupos.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Año actual disponible para todas las plantillas
@app.context_processor
def inject_current_year():
    return {"current_year": datetime.utcnow().year}

# ----------------------------------------------------
# MODELOS
# ----------------------------------------------------
class GrupoScout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    provincia = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(100), nullable=True)

with app.app_context():
    db.create_all()

# ----------------------------------------------------
# RUTAS DEL SITIO PRINCIPAL
# ----------------------------------------------------
@app.route("/")
def home():
    return render_template("home_v2.html", now=datetime.now())

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
    grupos = GrupoScout.query.order_by(GrupoScout.nombre.asc()).all()
    return render_template("grupos.html", grupos=grupos)

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
                contacto=contacto or None
            )
            db.session.add(nuevo)
            db.session.commit()
            return redirect(url_for("ver_grupos"))

    return render_template("agregar_grupo.html")

@app.route("/editar_grupo/<int:id>", methods=["GET", "POST"])
def editar_grupo(id):
    grupo = GrupoScout.query.get_or_404(id)
    if request.method == "POST":
        grupo.nombre = request.form.get("nombre", grupo.nombre).strip()
        grupo.ciudad = request.form.get("ciudad", grupo.ciudad).strip()
        grupo.provincia = request.form.get("provincia", grupo.provincia).strip()
        grupo.contacto = request.form.get("contacto", grupo.contacto)
        db.session.commit()
        return redirect(url_for("ver_grupos"))

    return render_template("editar_grupo.html", grupo=grupo)

# ----------------------------------------------------
# BLOG - LECTURA DE ENTRADAS HTML
# ----------------------------------------------------
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

        base = nombre[:-5]  # sin .html
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

# ----------------------------------------------------
# EJECUCIÓN LOCAL
# ----------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
