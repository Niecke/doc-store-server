from flask import Flask
from flask_migrate import Migrate
import logging
import sys
from config import (
    MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DB,
    SECRET_KEY, SQLALCHEMY_TRACK_MODIFICATIONS, SQLALCHEMY_ENGINE_OPTIONS, DEBUG
)

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    if DEBUG:
        app.config['DEBUG'] = True  # Auto-reloads templates!
        app.jinja_env.auto_reload = True
        app.jinja_env.cache_size = 0

    # Config
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        "?ssl_disabled=0&client_flag=4"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = SQLALCHEMY_ENGINE_OPTIONS
    
    # Logging
    app.logger.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    
    # Init extensions
    from models import db
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints/routes
    from routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app
