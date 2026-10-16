import os
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

TZ = ZoneInfo(os.getenv("APP_TZ", "America/Mexico_City"))
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

# Cada cuántos minutos (alineado al reloj: :00 y :30) las cirugías programadas cuya
# hora ya llegó pasan a "EN PROGRESO".
ACTUALIZAR_CADA_MIN = int(os.getenv("ACTUALIZAR_CADA_MIN", "30"))
MAX_DIAS_RANGO = 31
