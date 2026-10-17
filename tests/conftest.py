import os

# Antes de importar la app: config.py lee el entorno al importarse y load_dotenv no pisa
# variables ya definidas, así que DB_NAME apunta a la BD de tests y el resto sale del .env.
os.environ["DB_NAME"] = os.getenv("TEST_DB_NAME", "registros_cirugias_test")

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from app import config
from app.database import SessionLocal, engine
from app.main import app

RAIZ = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session", autouse=True)
def bd_de_tests():
    """Crea la BD de tests (si no existe) y le aplica todas las migraciones una vez por sesión."""
    if config.DB_HOST not in ("localhost", "127.0.0.1") or not config.DB_NAME.endswith("_test"):
        pytest.exit(f"Los tests solo corren contra una BD local *_test (actual: {config.DB_HOST}/{config.DB_NAME})")

    # URL.set(database=None) conserva el nombre actual; information_schema existe siempre.
    servidor = create_engine(engine.url.set(database="information_schema"))
    with servidor.connect() as conn:
        conn.execute(text(
            f"CREATE DATABASE IF NOT EXISTS `{config.DB_NAME}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        ))
    servidor.dispose()

    command.upgrade(Config(str(RAIZ / "alembic.ini")), "head")


@pytest.fixture(autouse=True)
def tabla_vacia():
    """Cada test empieza sin cirugías: los tests no dependen del orden ni de lo que dejó otro."""
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE cirugias"))


@pytest.fixture
def client():
    # Sin `with`: no se ejecuta el lifespan, así el scheduler no cambia estatus a mitad de un test.
    return TestClient(app)


@pytest.fixture
def db():
    with SessionLocal() as sesion:
        yield sesion


CIRUGIA = {
    "nombrePaciente": "Ana López",
    "edad": 45,
    "sexo": "FEMENINO",
    "fechaCirugia": "2026-10-20T09:00",
    "procedimiento": "Colecistectomía",
    "duracionEstimada": 120,
    "cirujano": "Dra. Sofía Martínez",
    "quirofano": "Quirófano 1",
    "aseguradora": "GNP",
    "diagnostico": "Colelitiasis",
    "serviciosEspeciales": None,
}


@pytest.fixture
def base():
    return dict(CIRUGIA)


@pytest.fixture
def crear(client):
    """Da de alta una cirugía con los datos base, sobrescribiendo los campos indicados."""
    def _crear(**cambios):
        return client.post("/cirugias", json={**CIRUGIA, **cambios})
    return _crear
