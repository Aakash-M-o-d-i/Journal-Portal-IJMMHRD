import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-me')
    
    # DB Configuration: MySQL by default, SQLite fallback for zero-config local testing
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASS = os.getenv('DB_PASS', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'ijmmhrd')
    USE_SQLITE = os.getenv('USE_SQLITE', 'false').lower() in ('true', '1', 'yes')
    
    if USE_SQLITE:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ijmmhrd.db')}"
    else:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}?charset=utf8mb4"
        )
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        os.getenv('UPLOAD_FOLDER', 'uploads')
    )
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
