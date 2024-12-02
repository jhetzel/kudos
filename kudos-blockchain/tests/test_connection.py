import psycopg2
import os
import time

def get_db_url():
    is_docker = os.path.exists('/.dockerenv')
    host = "kudos-db" if is_docker else "localhost"
    return f"postgresql://kudos_user:kudos_pass@{host}:5432/kudos"

DB_URL = get_db_url()

try:
    conn = psycopg2.connect(DB_URL)
    print(f"DEBUG: Verwende DB_URL: {DB_URL}")
    conn.close()
except Exception as e:
    print(f"Fehler bei der Verbindung: {e}")