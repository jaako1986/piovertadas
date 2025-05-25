import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def inicio():
    ruta = os.path.join(app.static_folder, "entradas")
    if not os.path.exists(ruta):
        os.makedirs(ruta)
    entradas = sorted(os.listdir(ruta), reverse=True)
    return render_template("index.html", entradas=entradas)

@app.route("/galeria")
def galeria():
    ruta = os.path.join(app.static_folder, "fotos")
    imagenes = [f"fotos/{img}" for img in os.listdir(ruta) if img.endswith((".jpg", ".png", ".jpeg", ".webp"))]
    return render_template("galeria.html", imagenes=imagenes)

@app.route("/material")
def material():
    archivos = os.listdir(os.path.join(app.static_folder, "material"))
    pdfs = [f for f in archivos if f.endswith(".pdf")]
    return render_template("material.html", pdfs=pdfs)




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
