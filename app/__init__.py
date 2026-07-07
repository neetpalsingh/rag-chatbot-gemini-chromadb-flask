from flask import Flask
from app.config import config

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    config[config_name].init_app(app)
    
    from app.routes import api
    app.register_blueprint(api.bp)
    
    return app
