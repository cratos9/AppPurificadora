from flask import Flask,  redirect, url_for
from sqlalchemy import create_engine, text
from src.database.coneccion import db  
from sqlalchemy import text
import pymysql

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DEBUG=True,
        # SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db',
        SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:@127.0.0.1:3306/purificadora"
    )

    engine = create_engine(
        "mysql+pymysql://root:@127.0.0.1:3306/",
        echo=False
    )
    with engine.connect() as conn:
        conn.execute(text(
            "CREATE DATABASE IF NOT EXISTS purificadora "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        ))

    db.init_app(app)
    
    from src.usuarios.routes import bp as usuarios_bp
    app.register_blueprint(usuarios_bp)
    
    from src.rutinas.routes import bp as rutinas_bp
    app.register_blueprint(rutinas_bp)
    
    from src.purificadora.routes import bp as purificadora_bp
    app.register_blueprint(purificadora_bp)
    
    @app.route('/')
    def index():
        return redirect(url_for('usuarios.inicio_sesion'))
    
    with app.app_context():
        db.create_all()

    return app