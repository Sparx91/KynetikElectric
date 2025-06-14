import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "kynetik-electric-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///kynetik_electric.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'worker_login'
login_manager.login_message = 'Please log in to access this page.'

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models to ensure tables are created
    import models  # noqa: F401
    db.create_all()

# Set up user loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    # Try to load admin user first
    from models import Admin
    admin = Admin.query.get(int(user_id)) if user_id.isdigit() else None
    if admin:
        return admin
    
    # Try to load worker user
    from worker_auth import Worker
    from firebase_service import firebase_service
    worker_data = firebase_service.get_worker_by_id(user_id)
    if worker_data:
        return Worker(worker_data)
    
    return None

# Import routes after app creation
import routes  # noqa: F401

# Initialize default data after everything is set up
with app.app_context():
    from routes import create_default_data
    create_default_data()
