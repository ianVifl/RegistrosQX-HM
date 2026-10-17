import os

# Antes de importar la app: config.py lee el entorno al importarse y load_dotenv no pisa
# variables ya definidas, así que DB_NAME apunta a la BD de tests y el resto sale del .env.
os.environ["DB_NAME"] = os.getenv("TEST_DB_NAME", "registros_cirugias_test")
os.environ.setdefault("SECRET_KEY", "clave-solo-para-tests-" + "x" * 32)

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from app import config, seguridad
from app.database import SessionLocal, engine
from app.main import app
from app.models import Usuario

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


PASSWORD = "contraseña-de-prueba"
_HASH = seguridad.hashear(PASSWORD)  # Argon2 es lento a propósito: se calcula una sola vez
USUARIOS = {
    "admin": ("Admin Principal", "ADMIN"),
    "andrea": ("Andrea Villanueva", "CAPTURISTA"),
    "tv": ("Pantalla Quirófanos", "VISUALIZADOR"),
}


@pytest.fixture(autouse=True)
def bd_limpia():
    """Cada test empieza con las tablas vacías y un usuario por rol: no dependen del orden ni de otros tests."""
    ahora = config.ahora()
    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))  # TRUNCATE no se permite en tablas referenciadas por FK
        for tabla in ("bitacora", "cirugias", "usuarios"):
            conn.execute(text(f"TRUNCATE TABLE {tabla}"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    with SessionLocal() as db:
        db.add_all(
            Usuario(usuario=u, nombre=n, rol=r, passwordHash=_HASH, creadoEn=ahora, actualizadoEn=ahora)
            for u, (n, r) in USUARIOS.items()
        )
        db.commit()


@pytest.fixture
def anonimo():
    # Sin `with`: no se ejecuta el lifespan, así el scheduler no cambia estatus a mitad de un test.
    return TestClient(app)


@pytest.fixture
def sesion():
    """Fábrica de clientes con sesión iniciada: sesion("andrea") -> TestClient con la cookie de Andrea."""
    def _sesion(usuario: str) -> TestClient:
        c = TestClient(app)
        assert c.post("/auth/login", json={"usuario": usuario, "password": PASSWORD}).status_code == 200
        return c
    return _sesion


@pytest.fixture
def client(sesion):
    """Cliente por defecto: administrador (puede hacer todo)."""
    return sesion("admin")


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
