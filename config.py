import os

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///kynetik.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    
    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'mp4', 'mov'}
    
    # API Keys
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    
    # External URLs
    REPLIT_DEV_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')
    
    @staticmethod
    def get_domain():
        if os.environ.get('REPLIT_DEPLOYMENT') != '':
            return os.environ.get('REPLIT_DEV_DOMAIN')
        elif os.environ.get('REPLIT_DOMAINS'):
            return os.environ.get('REPLIT_DOMAINS').split(',')[0]
        else:
            return 'localhost:5000'
