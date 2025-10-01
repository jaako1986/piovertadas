
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Crear la app
app = Flask(__name__)

# Configuración de base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grupos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de grupos
class GrupoScout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    provincia = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(100), nullable=True)

# Crear las tablas si no existen
with app.app_context():
    db.create_all()

# ---------- RUTAS ----------

# HOME → usa home_v2.html
@app.route("/")
def home():
    # cargar entradas desde static/entradas
    ruta = os.path.join(app.static_folder, "entradas")
    if not os.path.exists(ruta):
        os.makedirs(ruta)

    entradas = []
    for archivo in sorted(os.listdir(ruta), reverse=True):
        if archivo.endswith(".html"):
            with open(os.path.join(ruta, archivo), "r", encoding="utf-8") as f:
                contenido = f.read()
            entradas.append({
                "titulo": archivo[11:-5].replace("-", " ").capitalize(),
                "fecha": archivo[0:10],
                "contenido": contenido
            })

    # cargar grupos desde la base de datos
    grupos = GrupoScout.query.all()

    return render_template("home_v2.html", entradas=entradas, grupos=grupos)

# GALERÍA
@app.route("/galeria")
def galeria():
    return render_template("galeria.html")

# BLOG
@app.route("/blog")
def blog():
    return render_template("blog.html")

# GRUPOS (vista lista)
@app.route("/grupos")
def ver_grupos():
    grupos = GrupoScout.query.all()
    return render_template("grupos.html", grupos=grupos)

# AGREGAR GRUPO
@app.route("/agregar_grupo", methods=["GET", "POST"])
def agregar_grupo():
    if request.method == "POST":
        nombre = request.form["nombre"]
        ciudad = request.form["ciudad"]
        provincia = request.form["provincia"]
        contacto = request.form["contacto"]

        nuevo = GrupoScout(nombre=nombre, ciudad=ciudad, provincia=provincia, contacto=contacto)
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for("ver_grupos"))

    return render_template("agregar_grupo.html")

# EDITAR GRUPO
@app.route("/editar_grupo/<int:id>", methods=["GET", "POST"])
def editar_grupo(id):
    grupo = GrupoScout.query.get_or_404(id)

    if request.method == "POST":
        grupo.nombre = request.form["nombre"]
        grupo.ciudad = request.form["ciudad"]
        grupo.provincia = request.form["provincia"]
        grupo.contacto = request.form["contacto"]
        db.session.commit()
        return redirect(url_for("ver_grupos"))

    return render_template("editar_grupo.html", grupo=grupo)

# ----------------------------

if __name__ == "__main__":
    app.run(debug=True)
