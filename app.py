import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route("/galeria")
def galeria():
    ruta = os.path.join(app.static_folder, "fotos")
    imagenes = [f"fotos/{img}" for img in os.listdir(ruta) if img.endswith((".jpg", ".png", ".jpeg", ".webp"))]
    return render_template("galeria.html", imagenes=imagenes)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
