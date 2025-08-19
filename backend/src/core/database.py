import psycopg2
from src.config import Config


def ensure_database_exists():
    conn = psycopg2.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        port=Config.DB_PORT
    )
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute(
        f"SELECT 1 FROM pg_database WHERE datname='{Config.DB_NAME}'")
    if not cursor.fetchone():
        cursor.execute(f"CREATE DATABASE {Config.DB_NAME}")

    conn.close()