import os
import pymysql
from dotenv import load_dotenv

# Load configuration from .env
load_dotenv()

db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', '')
db_host = os.environ.get('DB_HOST', '127.0.0.1')
db_port = int(os.environ.get('DB_PORT', '3306'))
db_name = os.environ.get('DB_NAME', 'prepai_pro')

def init_mysql_db():
    print(f"Connecting to MySQL server at {db_host}:{db_port}...")
    try:
        # Establish a connection to the server without a database name
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            port=db_port
        )
        cursor = conn.cursor()
        
        # Create database
        print(f"Creating database '{db_name}' if it does not exist...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.commit()
        conn.close()
        print("Database created successfully!")
        
        # Now import flask app and initialize tables
        print("Initializing database tables via SQLAlchemy...")
        from app import create_app
        from models.database import db
        
        app = create_app()
        with app.app_context():
            db.create_all()
            print("All database tables created successfully!")
            
    except Exception as e:
        print(f"Error initializing MySQL database: {e}")
        print("\nPlease make sure:")
        print("1. Your MySQL server is running locally.")
        print("2. You have configured the correct credentials in your '.env' file.")

if __name__ == '__main__':
    init_mysql_db()
