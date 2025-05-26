from src.database.coneccion import db
from datetime import datetime

class Ruta(db.Model):
    __tablename__ = 'rutas'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    zona = db.Column(db.String(255))

    rutinas = db.relationship('Rutina', backref='ruta')

class Rutina(db.Model):
    __tablename__ = 'rutinas'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    dias = db.Column(db.String(255), nullable=False)
    hora = db.Column(db.Time, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    marca = db.Column(db.String(255))
    garrafones = db.Column(db.Integer)
    repartidor_id = db.Column(db.Integer, db.ForeignKey('repartidores.id'))
    ruta_id = db.Column(db.Integer, db.ForeignKey('rutas.id'))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    visitas = db.relationship('Visita', backref='rutina')