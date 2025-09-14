import os

from flask import Flask, render_template
from models import db, GrupoScout

app = Flask(__name__)

from flask import session

app.secret_key = 'PioVers2025'  # Cambiá por algo tuyo

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grupos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
# --- Toggle Home V2 ---
from datetime import datetime
from flask import render_template, request

USE_HOME_V2 = True  # ponlo en False si querés forzar el home viejo

@app.context_processor
def inject_now():
    return {"now": datetime.utcnow}

@app.route("/")
def home():
    # Datos de ejemplo (borrá si ya traés de DB):
    eventos = [
        {"titulo":"Guardianes del Fuego", "fecha":"26/07/2025", "descripcion":"Campamento de mitos y leyendas.", "link":"#"},
        {"titulo":"Patio Criollo", "fecha":"10/10/2025", "descripcion":"Jornada solidaria y feria.", "link":"#"},
    ]
    galeria = [
        {"src":"/static/img/gal/1.jpg","alt":"Fogón","caption":"Fogón Rover"},
        {"src":"/static/img/gal/2.jpg","alt":"Campamento"},
        {"src":"/static/img/gal/3.jpg","alt":"Taller nudos","caption":"Amarre cuadrado"},
    ]
    materiales = [
        {"nombre":"Técnicas Scout","items":[
            {"titulo":"Fogones seguros (PDF)","tipo":"PDF","url":"#"},
            {"titulo":"Guía de nudos básicos","tipo":"Artículo","url":"#"}]},
        {"nombre":"Historia Aeronaval","items":[
            {"titulo":"Símbolos y tradición","tipo":"PDF","url":"#"}]},
    ]
    grupos = [
        {"nombre":"Islas Malvinas Base VIII","ciudad":"Comodoro Rivadavia","web":"#"},
        {"nombre":"Grupo X","ciudad":"Rada Tilly","web":None},
    ]

    return render_template("home_v2.html", eventos=eventos, galeria=galeria, materiales=materiales, grupos=grupos)
# --- Fin Toggle ---

@app.route('/blog')
def inicio():
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

    grupos = GrupoScout.query.all()
    return render_template("index.html", entradas=entradas, grupos=grupos)


@app.route("/galeria")
def galeria():
    ruta = os.path.join(app.static_folder, "fotos")
    imagenes = [f"fotos/{img}" for img in os.listdir(ruta) if img.endswith((".jpg", ".png", ".jpeg", ".webp"))]
    return render_template("galeria.html", imagenes=imagenes)

@app.route("/material")
def material():
    archivos = os.listdir(os.path.join(app.static_folder, "material"))
    formatos_validos = (".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx")
    materiales = [f for f in archivos if f.endswith(formatos_validos)]
    return render_template("material.html", pdfs=materiales)
@app.route('/grupos')
def mostrar_grupos():
    grupos = GrupoScout.query.all()
    return render_template('grupos.html', grupos=grupos)

from flask import request, redirect, url_for

@app.route('/agregar-grupo', methods=['GET', 'POST'])
def agregar_grupo():
    if request.method == 'POST':
        nuevo_grupo = GrupoScout(
            nombre=request.form['nombre'],
            ciudad=request.form['ciudad'],
            provincia=request.form['provincia'],
            contacto=request.form['contacto']
        )
        db.session.add(nuevo_grupo)
        db.session.commit()
        return redirect(url_for('inicio'))  # 👈 Vuelve al home
    return render_template('agregar_grupo.html')
@app.route('/editar-grupo/<int:id>', methods=['GET', 'POST'])
def editar_grupo(id):
    if not session.get('admin'):
        return "Acceso denegado", 403
    grupo = GrupoScout.query.get_or_404(id)
    if request.method == 'POST':
        grupo.nombre = request.form['nombre']
        grupo.ciudad = request.form['ciudad']
        grupo.provincia = request.form['provincia']
        grupo.contacto = request.form['contacto']
        db.session.commit()
        return redirect(url_for('mostrar_grupos'))
    return render_template('editar_grupo.html', grupo=grupo)

@app.route('/borrar-grupo/<int:id>', methods=['POST'])
def borrar_grupo(id):
    if not session.get('admin'):
        return "Acceso denegado", 403
    grupo = GrupoScout.query.get_or_404(id)
    db.session.delete(grupo)
    db.session.commit()
    return redirect(url_for('mostrar_grupos'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == 'PioVers2025':  # Cambiá la clave
            session['admin'] = True
            return redirect(url_for('mostrar_grupos'))
        else:
            return "Clave incorrecta", 403
    return '''
        <form method="POST" style="text-align:center; margin-top:50px;">
            <input type="password" name="password" placeholder="Clave" style="padding:8px;">
            <button type="submit" style="padding:8px 12px;">Ingresar</button>
        </form>
    '''

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('mostrar_grupos'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)

