from flask import Flask 
from src.database.coneccion import db
from src.purificadora.models import Purificadora, Calificacion
from src.rutinas.models import Rutina
from src.usuarios.models import Usuario

def create_app():
    
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DEBUG =True,
        SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db',
    )
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    @app.route('/')
    def index():
        return "Hello, World!"
    
    return app