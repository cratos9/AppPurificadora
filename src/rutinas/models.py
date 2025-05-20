from src.database.coneccion import db
from datetime import datetime

class Rutina(db.Model):
    __tablename__ = 'rutinas'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    purificadora_id = db.Column(db.Integer, db.ForeignKey('purificadoras.id'), nullable=False)
    dias = db.Column(db.String(255), nullable=False)  
    hora = db.Column(db.Time, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    marca = db.Column(db.String(255), nullable=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)