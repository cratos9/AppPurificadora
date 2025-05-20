from src.database.coneccion import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(50), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    calle = db.Column(db.String(255))
    numero_interior = db.Column(db.String(50))
    numero_exterior = db.Column(db.String(50))
    colonia = db.Column(db.String(255))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    rutinas = db.relationship('Rutina', backref='usuario', cascade='all, delete-orphan')
    calificaciones = db.relationship('Calificacion', backref='usuario', cascade='all, delete-orphan')