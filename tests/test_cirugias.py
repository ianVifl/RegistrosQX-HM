import pytest


# ---------- Alta ----------

def test_alta_valida_nace_programada(crear):
    r = crear(estatus="FINALIZADA")  # el alta ignora el estatus enviado: regla de negocio

    assert r.status_code == 201
    datos = r.json()
    assert datos["estatus"] == "PROGRAMADA"
    assert datos["fechaFinEstimada"] == "2026-10-20T11:00:00"
    assert "codigoPaciente" not in datos


def test_alta_limpia_texto(crear):
    r = crear(nombrePaciente="  Ana López  ", aseguradora="", diagnostico="   ", serviciosEspeciales="")

    datos = r.json()
    assert datos["nombrePaciente"] == "Ana López"
    assert datos["aseguradora"] == "No"
    assert datos["diagnostico"] is None
    assert datos["serviciosEspeciales"] is None


def test_edad_cero_es_valida(crear):
    assert crear(edad=0).status_code == 201


@pytest.mark.parametrize("campo, valor", [
    ("edad", 121), ("edad", -1), ("edad", 30.5),
    ("sexo", "OTRO"), ("sexo", "femenino"),
    ("duracionEstimada", 45), ("duracionEstimada", 0), ("duracionEstimada", 750),
    ("nombrePaciente", "   "),
])
def test_alta_rechaza_valores_invalidos(crear, campo, valor):
    assert crear(**{campo: valor}).status_code == 422


@pytest.mark.parametrize("campo", [
    "nombrePaciente", "edad", "sexo", "fechaCirugia", "procedimiento",
    "duracionEstimada", "cirujano", "quirofano",
])
def test_alta_exige_campos_obligatorios(client, base, campo):
    del base[campo]
    assert client.post("/cirugias", json=base).status_code == 422


# ---------- Traslapes ----------

def test_traslape_en_el_mismo_quirofano(crear):
    crear()  # 09:00 a 11:00

    r = crear(nombrePaciente="Luis", fechaCirugia="2026-10-20T10:00")

    assert r.status_code == 409
    assert "09:00 a 11:00" in r.json()["detail"]
    assert "Ana López" in r.json()["detail"]


def test_cirugias_contiguas_no_se_traslapan(crear):
    crear()  # termina a las 11:00
    assert crear(fechaCirugia="2026-10-20T11:00").status_code == 201


def test_otro_quirofano_no_se_traslapa(crear):
    crear()
    assert crear(quirofano="Quirófano 2").status_code == 201


def test_traslape_que_cruza_la_medianoche(crear):
    crear(fechaCirugia="2026-10-20T23:00")  # termina a las 01:00 del día siguiente
    assert crear(fechaCirugia="2026-10-21T00:30").status_code == 409


def test_una_cirugia_finalizada_libera_el_quirofano(client, crear):
    id_ = crear().json()["id"]
    client.patch(f"/cirugias/{id_}/estatus", json={"estatus": "FINALIZADA"})

    assert crear(fechaCirugia="2026-10-20T10:00").status_code == 201


def test_editar_no_choca_consigo_misma(client, crear, base):
    id_ = crear().json()["id"]
    r = client.put(f"/cirugias/{id_}", json={**base, "duracionEstimada": 180, "estatus": "PROGRAMADA"})
    assert r.status_code == 200


# ---------- Edición, estatus y baja ----------

def test_editar_actualiza_todos_los_campos(client, crear, base):
    id_ = crear().json()["id"]
    cambios = {**base, "sexo": "MASCULINO", "edad": 50, "serviciosEspeciales": "Banco de sangre", "estatus": "EN PROGRESO"}

    datos = client.put(f"/cirugias/{id_}", json=cambios).json()

    assert (datos["sexo"], datos["edad"], datos["serviciosEspeciales"], datos["estatus"]) == \
           ("MASCULINO", 50, "Banco de sangre", "EN PROGRESO")


def test_cambiar_estatus(client, crear):
    id_ = crear().json()["id"]

    assert client.patch(f"/cirugias/{id_}/estatus", json={"estatus": "EN PROGRESO"}).json()["estatus"] == "EN PROGRESO"
    assert client.patch(f"/cirugias/{id_}/estatus", json={"estatus": "CANCELADA"}).status_code == 422


def test_eliminar(client, crear):
    id_ = crear().json()["id"]

    assert client.delete(f"/cirugias/{id_}").status_code == 204
    assert client.get(f"/cirugias/{id_}").status_code == 404


@pytest.mark.parametrize("metodo, ruta, cuerpo", [
    ("get", "/cirugias/999", None),
    ("delete", "/cirugias/999", None),
    ("patch", "/cirugias/999/estatus", {"estatus": "FINALIZADA"}),
])
def test_cirugia_inexistente_da_404(client, metodo, ruta, cuerpo):
    kwargs = {"json": cuerpo} if cuerpo else {}
    assert getattr(client, metodo)(ruta, **kwargs).status_code == 404


def test_editar_inexistente_da_404(client, base):
    assert client.put("/cirugias/999", json={**base, "estatus": "PROGRAMADA"}).status_code == 404


# ---------- Listado ----------

def test_listar_por_rango_ordenado_por_hora(client, crear):
    crear(fechaCirugia="2026-10-21T12:00")
    crear(fechaCirugia="2026-10-20T08:00", quirofano="Quirófano 2")
    crear(fechaCirugia="2026-10-27T08:00")  # fuera del rango

    datos = client.get("/cirugias", params={"desde": "2026-10-20", "hasta": "2026-10-26"}).json()

    assert [c["fechaCirugia"] for c in datos] == ["2026-10-20T08:00:00", "2026-10-21T12:00:00"]


def test_listar_por_fecha(client, crear):
    crear(fechaCirugia="2026-10-20T08:00")
    crear(fechaCirugia="2026-10-21T08:00")

    assert len(client.get("/cirugias", params={"fecha": "2026-10-20"}).json()) == 1


@pytest.mark.parametrize("params", [
    {"desde": "2026-10-20"},                              # falta hasta
    {"desde": "2026-10-20", "hasta": "2026-10-19"},       # hasta antes que desde
    {"desde": "2026-10-01", "hasta": "2026-11-01"},       # más de 31 días
])
def test_listar_rango_invalido_da_400(client, params):
    assert client.get("/cirugias", params=params).status_code == 400


def test_rango_de_31_dias_es_valido(client):
    assert client.get("/cirugias", params={"desde": "2026-10-01", "hasta": "2026-10-31"}).status_code == 200
