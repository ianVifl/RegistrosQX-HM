import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()


def _requerida(nombre: str) -> str:
    """Falla al arrancar con un mensaje claro si falta una variable obligatoria."""
    valor = os.getenv(nombre)
    if not valor:
        raise RuntimeError(f"Falta la variable de entorno {nombre}")
    return valor


url = URL.create(
    drivername="mysql+pymysql",
    username=_requerida("DB_USER"),
    password=_requerida("DB_PASSWORD"),
    host=_requerida("DB_HOST"),
    port=int(os.getenv("DB_PORT", "3306")),
    database=_requerida("DB_NAME"),
    query={"charset": "utf8mb4"},  # explícito: evita que "Quirófano" o "Cesárea" se corrompan
)
engine = create_engine(url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
