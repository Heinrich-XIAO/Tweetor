import psycopg2
from psycopg2 import sql

DATABASE = "postgres"
USER = "heinrichxiao"
PASSWORD = "your_postgres_password"
HOST = "localhost"
PORT = "5432"

def get_db():
    connection_params = {
        "dbname": DATABASE,
        "user": USER,
        "host": HOST,
        "port": PORT
    }
    db = psycopg2.connect(**connection_params)
    db.autocommit = True
    return db