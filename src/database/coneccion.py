from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

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