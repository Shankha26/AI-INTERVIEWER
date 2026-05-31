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
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    RESUME_FOLDER = os.path.join(UPLOAD_FOLDER, 'resumes')
    VIDEO_FOLDER = os.path.join(UPLOAD_FOLDER, 'videos')
    AUDIO_FOLDER = os.path.join(UPLOAD_FOLDER, 'audio')
    PROFILE_FOLDER = os.path.join(UPLOAD_FOLDER, 'profiles')
    
    # Allowed extensions
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'webm', 'wav', 'mp3', 'mp4'}
    
    # Database Configuration
    # Fallback to SQLite local file database if MySQL env details aren't provided
    db_user = os.environ.get('DB_USER')
    db_password = os.environ.get('DB_PASSWORD')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '3306')
    db_name = os.environ.get('DB_NAME')
    
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        SQLALCHEMY_DATABASE_URI = database_url
    elif db_user and db_password and db_name:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
    else:
        # SQLite fallback for seamless development
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'prepai_pro.db')}"
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Gemini API settings
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    
    # Max Upload Size: 32MB
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024
