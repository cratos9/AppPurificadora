from src.database.coneccion import db
from datetime import datetime

class Purificadora(db.Model):
    __tablename__ = 'purificadoras'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(50), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    calle = db.Column(db.String(255))
    numero_interior = db.Column(db.String(50))
    numero_exterior = db.Column(db.String(50))
    colonia = db.Column(db.String(255))
    horario_apertura = db.Column(db.Time)
    horario_cierre = db.Column(db.Time)
    dias_abiertos = db.Column(db.String(255))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    rutinas = db.relationship('Rutina', backref='purificadora', cascade='all, delete-orphan')
    calificaciones = db.relationship('Calificacion', backref='purificadora', cascade='all, delete-orphan')
    
class Calificacion(db.Model):
    __tablename__ = 'calificaciones'

    id = db.Column(db.Integer, primary_key=True)
    purificadora_id = db.Column(db.Integer, db.ForeignKey('purificadoras.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha = db.Column(db.Date, default=datetime.utcnow)
    calificacion = db.Column(db.Integer, nullable=False) 
    comentario = db.Column(db.Text)