from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class GrupoScout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    provincia = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(120), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())
