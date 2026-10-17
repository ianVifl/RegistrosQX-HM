from datetime import timedelta

import jwt
import pytest
from starlette.websockets import WebSocketDisconnect

from app import config, seguridad
from app.models import Usuario
from tests.conftest import PASSWORD


# ---------- Login y logout ----------

def test_login_correcto_entrega_cookie_httponly(anonimo):
    r = anonimo.post("/auth/login", json={"usuario": "andrea", "password": PASSWORD})

    assert r.status_code == 200
    assert r.json()["rol"] == "CAPTURISTA"
    assert "passwordHash" not in r.json()
    cookie = r.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=lax" in cookie
    assert "max-age=86400" in cookie  # capturista: 24 h


@pytest.mark.parametrize("usuario, horas", [("admin", 12), ("andrea", 24), ("tv", 24 * 30)])
def test_duracion_de_sesion_por_rol(anonimo, usuario, horas):
    r = anonimo.post("/auth/login", json={"usuario": usuario, "password": PASSWORD})
    assert f"max-age={horas * 3600}" in r.headers["set-cookie"].lower()


@pytest.mark.parametrize("usuario, password", [("andrea", "incorrecta"), ("noexiste", PASSWORD)])
def test_login_incorrecto_da_401_con_mensaje_generico(anonimo, usuario, password):
    r = anonimo.post("/auth/login", json={"usuario": usuario, "password": password})

    assert r.status_code == 401
    assert r.json()["detail"] == "Usuario o contraseña incorrectos"  # no revela si el usuario existe


def test_usuario_desactivado_no_puede_entrar(anonimo, db):
    db.query(Usuario).filter_by(usuario="andrea").update({"activo": False})
    db.commit()

    assert anonimo.post("/auth/login", json={"usuario": "andrea", "password": PASSWORD}).status_code == 401


def test_yo_y_logout(sesion):
    c = sesion("andrea")
    assert c.get("/auth/yo").json()["nombre"] == "Andrea Villanueva"

    assert c.post("/auth/logout").status_code == 204
    assert c.get("/auth/yo").status_code == 401


# ---------- Validez del token ----------

def _token(sub, delta=timedelta(hours=1), clave=None):
    return jwt.encode({"sub": sub, "exp": config.ahora_utc() + delta}, clave or config.SECRET_KEY, algorithm="HS256")


def _id(db, usuario):
    return str(db.query(Usuario).filter_by(usuario=usuario).one().id)


@pytest.mark.parametrize("caso", ["expirado", "otra_clave", "basura", "sub_invalido"])
def test_tokens_invalidos_dan_401(anonimo, db, caso):
    token = {
        "expirado": lambda: _token(_id(db, "admin"), delta=timedelta(seconds=-1)),
        "otra_clave": lambda: _token(_id(db, "admin"), clave="otra-clave-de-al-menos-32-bytes-xxxxxx"),
        "basura": lambda: "no.es.un.jwt",
        "sub_invalido": lambda: _token("abc"),
    }[caso]()
    anonimo.cookies.set(seguridad.COOKIE, token)

    assert anonimo.get("/auth/yo").status_code == 401


def test_desactivar_invalida_la_sesion_abierta_de_inmediato(sesion, db):
    c = sesion("andrea")
    db.query(Usuario).filter_by(usuario="andrea").update({"activo": False})
    db.commit()

    assert c.get("/cirugias").status_code == 401


def test_cambio_de_rol_aplica_de_inmediato(sesion, db, crear):
    c = sesion("andrea")
    db.query(Usuario).filter_by(usuario="andrea").update({"rol": "VISUALIZADOR"})
    db.commit()

    assert c.post("/cirugias", json={}).status_code == 403


# ---------- Matriz de permisos ----------

def test_sin_sesion_todo_da_401(anonimo):
    assert anonimo.get("/cirugias").status_code == 401
    assert anonimo.post("/cirugias", json={}).status_code == 401
    assert anonimo.get("/reportes/exportar", params={"formato": "pdf", "desde": "2026-10-20", "hasta": "2026-10-20"}).status_code == 401


def test_capturista_crea_y_edita_pero_no_elimina(sesion, base):
    c = sesion("andrea")
    r = c.post("/cirugias", json=base)
    assert r.status_code == 201
    id_ = r.json()["id"]

    assert c.put(f"/cirugias/{id_}", json={**base, "estatus": "PROGRAMADA", "edad": 46}).status_code == 200
    assert c.patch(f"/cirugias/{id_}/estatus", json={"estatus": "EN PROGRESO"}).status_code == 200
    assert c.get(f"/cirugias/{id_}/exportar", params={"formato": "pdf"}).status_code == 200
    assert c.delete(f"/cirugias/{id_}").status_code == 403


def test_visualizador_solo_consulta(sesion, crear, base):
    id_ = crear().json()["id"]
    c = sesion("tv")

    assert c.get("/cirugias", params={"fecha": "2026-10-20"}).status_code == 200
    assert c.post("/cirugias", json=base).status_code == 403
    assert c.put(f"/cirugias/{id_}", json={**base, "estatus": "PROGRAMADA"}).status_code == 403
    assert c.patch(f"/cirugias/{id_}/estatus", json={"estatus": "FINALIZADA"}).status_code == 403
    assert c.delete(f"/cirugias/{id_}").status_code == 403
    assert c.get(f"/cirugias/{id_}/exportar", params={"formato": "pdf"}).status_code == 403
    assert c.get("/reportes/exportar", params={"formato": "pdf", "desde": "2026-10-20", "hasta": "2026-10-20"}).status_code == 403


# ---------- WebSocket ----------

def test_websocket_sin_sesion_se_rechaza(anonimo):
    with pytest.raises(WebSocketDisconnect) as e:
        with anonimo.websocket_connect("/ws") as ws:
            ws.receive_text()
    assert e.value.code == 1008


def test_websocket_con_sesion_recibe_avisos(sesion, base):
    c = sesion("tv")
    with c.websocket_connect("/ws") as ws:
        sesion("andrea").post("/cirugias", json=base)
        assert ws.receive_text() == "cambio"
