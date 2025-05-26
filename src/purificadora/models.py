from src.database.coneccion import db
from datetime import datetime

class Visita(db.Model):
    __tablename__ = 'visitas'

    id = db.Column(db.Integer, primary_key=True)
    rutina_id = db.Column(db.Integer, db.ForeignKey('rutinas.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    qr_codigo = db.Column(db.String(255), nullable=False)
    verificado = db.Column(db.Boolean, default=False)

class Pago(db.Model):
    __tablename__ = 'pagos'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    metodo = db.Column(db.String(50), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    referencia = db.Column(db.String(255))

class AuditoriaSistema(db.Model):
    __tablename__ = 'auditoria_sistema'

    id = db.Column(db.Integer, primary_key=True)
    entidad = db.Column(db.String(50), nullable=False)
    entidad_id = db.Column(db.Integer, nullable=False)
    campo = db.Column(db.String(255))
    valor_anterior = db.Column(db.Text)
    valor_nuevo = db.Column(db.Text)
    operacion = db.Column(db.String(10), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

class AsignacionRepartidor(db.Model):
    __tablename__ = 'asignacion_repartidor'

    id = db.Column(db.Integer, primary_key=True)
    repartidor_id = db.Column(db.Integer, db.ForeignKey('repartidores.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    total_asignado = db.Column(db.Integer, nullable=False)
    
class Repartidor(db.Model):
    __tablename__ = 'repartidores'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(50))
    capacidad_maxima = db.Column(db.Integer, nullable=False)
    activo = db.Column(db.Boolean, default=True)

    rutinas = db.relationship('Rutina', backref='repartidor')
    asignaciones = db.relationship('AsignacionRepartidor', backref='repartidor')