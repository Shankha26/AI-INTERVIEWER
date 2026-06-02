import sqlite3
import pymysql
import os
from dotenv import load_dotenv

# Load configuration from .env
load_dotenv()

db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', '')
db_host = os.environ.get('DB_HOST', '127.0.0.1')
db_port = int(os.environ.get('DB_PORT', '3306'))
db_name = os.environ.get('DB_NAME', 'prepai_pro')

sqlite_db_path = 'prepai_pro.db'

tables_to_migrate = [
    'users',
    'questions',
    'resume_analysis',
    'interview_sessions',
    'aptitude_results',
    'career_guidance',
    'study_plans',
    'recommendations',
    'voice_interviews',
    'recordings'
]

def migrate_data():
    if not os.path.exists(sqlite_db_path):
        print(f"SQLite database '{sqlite_db_path}' not found. Skipping migration.")
        return

    print("Connecting to source SQLite database...")
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_cursor = sqlite_conn.cursor()

    print(f"Connecting to target MySQL database '{db_name}'...")
    try:
        mysql_conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            port=db_port,
            database=db_name
        )
        mysql_cursor = mysql_conn.cursor()
    except Exception as e:
        print(f"Failed to connect to MySQL database: {e}")
        print("Please ensure create_db.py has been run and your credentials in '.env' are correct.")
        sqlite_conn.close()
        return

    try:
        # Disable foreign key constraints during bulk insert to prevent insertion order conflicts
        print("Disabling foreign key checks in MySQL...")
        mysql_cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        mysql_conn.commit()

        for table in tables_to_migrate:
            print(f"Migrating table '{table}'...")
            
            # Check if table exists in SQLite
            sqlite_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not sqlite_cursor.fetchone():
                print(f"  - Table '{table}' does not exist in SQLite source. Skipping.")
                continue

            # Fetch columns info from SQLite
            sqlite_cursor.execute(f"PRAGMA table_info(`{table}`)")
            columns_info = sqlite_cursor.fetchall()
            column_names = [col[1] for col in columns_info]
            
            # Read all rows from SQLite
            sqlite_cursor.execute(f"SELECT * FROM `{table}`")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                print(f"  - Table '{table}' is empty. Skipping.")
                continue

            # Clear existing data in MySQL table to prevent duplicate primary keys
            mysql_cursor.execute(f"DELETE FROM `{table}`")
            mysql_conn.commit()

            # Construct INSERT statement
            # MySQL uses %s as placeholder
            placeholders = ", ".join(["%s"] * len(column_names))
            columns_str = ", ".join([f"`{col}`" for col in column_names])
            insert_query = f"INSERT INTO `{table}` ({columns_str}) VALUES ({placeholders})"
            
            # Insert into MySQL
            mysql_cursor.executemany(insert_query, rows)
            mysql_conn.commit()
            print(f"  - Successfully migrated {len(rows)} records into '{table}' table.")
            
        print("Enabling foreign key checks back...")
        mysql_cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        mysql_conn.commit()
        print("\nData migration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {e}")
        print("Rolling back MySQL transactions...")
        mysql_conn.rollback()
    finally:
        sqlite_conn.close()
        mysql_conn.close()

if __name__ == '__main__':
    migrate_data()
