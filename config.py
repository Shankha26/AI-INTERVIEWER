import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

class Config:
    # Flask security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'prepai_pro_super_secret_key_1337_abc!')
    
    # Upload Directories
    # When running on serverless environments like Vercel, route uploads to writable /tmp
    if os.environ.get('VERCEL') == '1':
        UPLOAD_FOLDER = '/tmp/uploads'
    else:
        UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
        
    RESUME_FOLDER = os.path.join(UPLOAD_FOLDER, 'resumes')
    VIDEO_FOLDER = os.path.join(UPLOAD_FOLDER, 'videos')
    AUDIO_FOLDER = os.path.join(UPLOAD_FOLDER, 'audio')
    PROFILE_FOLDER = os.path.join(UPLOAD_FOLDER, 'profiles')
    
    # Allowed extensions
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'webm', 'wav', 'mp3', 'mp4'}
    
    # Database Configuration
    # Fallback to SQLite local file database if MySQL/Postgres env details aren't provided
    db_user = os.environ.get('DB_USER')
    db_password = os.environ.get('DB_PASSWORD')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '3306')
    db_name = os.environ.get('DB_NAME')
    
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Convert older postgres:// prefix to postgresql:// required by SQLAlchemy 1.4+
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = database_url
    elif db_user and db_password and db_name:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
    else:
        # SQLite fallback for seamless development
        # When running on serverless hosts like Vercel, route SQLite file to writable /tmp
        if os.environ.get('VERCEL') == '1':
            SQLALCHEMY_DATABASE_URI = f"sqlite:////tmp/prepai_pro.db"
        else:
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'prepai_pro.db')}"
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session Cookie Security Configuration (Issue 3: Session Persist Protection)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # Secure flag is enabled only in production/Vercel scheme
    SESSION_COOKIE_SECURE = os.environ.get('VERCEL') == '1' or os.environ.get('NODE_ENV') == 'production'
    
    # Gemini API settings
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    
    # Max Upload Size: 32MB
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024
