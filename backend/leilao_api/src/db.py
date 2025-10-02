import psycopg2
from psycopg2 import pool
from src.config import Config

# Pool de conexões para melhor performance
connection_pool = None

def init_db_pool():
    """Inicializa o pool de conexões com o banco de dados."""
    global connection_pool
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 20,
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        print("Pool de conexões criado com sucesso!")
    except Exception as e:
        print(f"Erro ao criar pool de conexões: {e}")
        raise

def get_db_connection():
    """Obtém uma conexão do pool."""
    if connection_pool:
        return connection_pool.getconn()
    raise Exception("Pool de conexões não inicializado")

def release_db_connection(conn):
    """Devolve a conexão ao pool."""
    if connection_pool:
        connection_pool.putconn(conn)

def close_db_pool():
    """Fecha todas as conexões do pool."""
    if connection_pool:
        connection_pool.closeall()
        print("Pool de conexões fechado!")
