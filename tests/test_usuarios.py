import pytest

from app.models import Usuario

NUEVO = {"usuario": "carlos.r", "nombre": "Carlos Ruiz", "rol": "CAPTURISTA", "password": "segura-123"}


def _id(db, usuario):
    return db.query(Usuario).filter_by(usuario=usuario).one().id


def test_crear_usuario_y_que_pueda_entrar(client, anonimo):
    r = client.post("/usuarios", json=NUEVO)

    assert r.status_code == 201
    assert r.json()["activo"] is True
    assert "password" not in r.json() and "passwordHash" not in r.json()
    assert anonimo.post("/auth/login", json={"usuario": "carlos.r", "password": "segura-123"}).status_code == 200


def test_usuario_duplicado_da_409(client):
    assert client.post("/usuarios", json={**NUEVO, "usuario": "andrea"}).status_code == 409


@pytest.mark.parametrize("campo, valor", [
    ("password", "corta"),                 # menos de 8 caracteres
    ("usuario", "con espacio"),
    ("usuario", "ñandú"),
    ("usuario", "ab"),
    ("rol", "SUPERADMIN"),
    ("nombre", "   "),
])
def test_crear_usuario_invalido_da_422(client, campo, valor):
    assert client.post("/usuarios", json={**NUEVO, campo: valor}).status_code == 422


def test_listar_usuarios(client):
    assert {u["usuario"] for u in client.get("/usuarios").json()} == {"admin", "andrea", "tv"}


def test_editar_nombre_y_rol(client, db):
    r = client.put(f"/usuarios/{_id(db, 'andrea')}", json={"nombre": "Andrea Villanueva Ruiz", "rol": "ADMIN"})
    assert (r.json()["nombre"], r.json()["rol"]) == ("Andrea Villanueva Ruiz", "ADMIN")


def test_desactivar_y_reactivar(client, anonimo, db):
    id_ = _id(db, "andrea")

    assert client.patch(f"/usuarios/{id_}/activo", json={"activo": False}).json()["activo"] is False
    assert anonimo.post("/auth/login", json={"usuario": "andrea", "password": "contraseña-de-prueba"}).status_code == 401

    assert client.patch(f"/usuarios/{id_}/activo", json={"activo": True}).json()["activo"] is True


def test_restablecer_password(client, anonimo, db):
    assert client.put(f"/usuarios/{_id(db, 'andrea')}/password", json={"password": "nueva-clave-1"}).status_code == 204

    assert anonimo.post("/auth/login", json={"usuario": "andrea", "password": "nueva-clave-1"}).status_code == 200
    assert anonimo.post("/auth/login", json={"usuario": "andrea", "password": "contraseña-de-prueba"}).status_code == 401


def test_admin_no_puede_desactivarse_ni_quitarse_el_rol(client, db):
    id_ = _id(db, "admin")

    assert client.patch(f"/usuarios/{id_}/activo", json={"activo": False}).status_code == 400
    assert client.put(f"/usuarios/{id_}", json={"nombre": "Admin", "rol": "CAPTURISTA"}).status_code == 400
    assert client.put(f"/usuarios/{id_}", json={"nombre": "Admin Renombrado", "rol": "ADMIN"}).status_code == 200


def test_usuario_inexistente_da_404(client):
    assert client.put("/usuarios/999", json={"nombre": "X", "rol": "ADMIN"}).status_code == 404
    assert client.patch("/usuarios/999/activo", json={"activo": False}).status_code == 404
    assert client.put("/usuarios/999/password", json={"password": "12345678"}).status_code == 404


@pytest.mark.parametrize("quien", ["andrea", "tv"])
def test_solo_el_admin_gestiona_usuarios(sesion, quien):
    c = sesion(quien)
    assert c.get("/usuarios").status_code == 403
    assert c.post("/usuarios", json=NUEVO).status_code == 403
