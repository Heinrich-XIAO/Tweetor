import psycopg2
from psycopg2 import sql
import os

# Retrieve database connection parameters from environment variables
DATABASE = os.environ.get("DB_NAME", "postgres")
USER = os.environ.get("DB_USER")
PASSWORD = os.environ.get("DB_PASSWORD")
HOST = os.environ.get("DB_HOST", "localhost")
PORT = os.environ.get("DB_PORT", "5432")

def get_db():
    connection_params = {
        "dbname": DATABASE,
        "user": USER,
        "password": PASSWORD,
        "host": HOST,
        "port": PORT
    }
    db = psycopg2.connect(**connection_params)
    db.autocommit = True
    return db