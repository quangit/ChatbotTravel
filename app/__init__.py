from flask import Flask
from config import Config
import os

def create_app():
    # Define paths relative to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_folder = os.path.join(project_root, 'templates')
    static_folder = os.path.join(project_root, 'static')
    
    app = Flask(__name__, 
                template_folder=template_folder,
                static_folder=static_folder)
    app.config.from_object(Config)
    
    from app.routes import main
    app.register_blueprint(main)
    
    return app
