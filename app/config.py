import os
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()


def _requerida(nombre: str) -> str:
    """Falla al arrancar con un mensaje claro si falta una variable obligatoria."""
    valor = os.getenv(nombre)
    if not valor:
        raise RuntimeError(f"Falta la variable de entorno {nombre}")
    return valor


# Base de datos
DB_USER = _requerida("DB_USER")
DB_PASSWORD = _requerida("DB_PASSWORD")
DB_HOST = _requerida("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = _requerida("DB_NAME")

# Aplicación
TZ = ZoneInfo(os.getenv("APP_TZ", "America/Mexico_City"))
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

# Cada cuántos minutos (alineado al reloj) las cirugías programadas cuya
# hora ya llegó pasan a "EN PROGRESO".
ACTUALIZAR_CADA_MIN = int(os.getenv("ACTUALIZAR_CADA_MIN", "30"))
MAX_DIAS_RANGO = 31
