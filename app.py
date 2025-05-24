import os
from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route("/")
def inicio():
    ruta = os.path.join(app.static_folder, "fotos")
    imagenes = [f"fotos/{img}" for img in os.listdir(ruta) if img.endswith((".jpg", ".png", ".jpeg", ".webp"))]
    return render_template("index.html", imagenes=imagenes)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
