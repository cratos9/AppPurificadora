from flask import Flask, redirect, url_for
from src.database.coneccion import db

def create_app():
    
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DEBUG =True,
        SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db',
    )
    
    db.init_app(app)
    
    from src.usuarios.routes import bp as usuarios_bp
    app.register_blueprint(usuarios_bp)
    
    from src.rutinas.routes import bp as rutinas_bp
    app.register_blueprint(rutinas_bp)
    
    from src.purificadora.routes import bp as purificadora_bp
    app.register_blueprint(purificadora_bp)
    
    with app.app_context():
        db.create_all()
    
    @app.route('/')
    def index():
        return redirect(url_for('usuarios.inicio_sesion'))
    
    return app