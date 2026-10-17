import pytest


@pytest.fixture
def historial(crear):
    crear(nombrePaciente="Ana López", cirujano="Dr. Roberto Gómez", fechaCirugia="2025-03-10T09:00")
    crear(nombrePaciente="Luis Pérez", cirujano="Dra. Sofía Martínez", fechaCirugia="2026-10-20T09:00")
    crear(nombrePaciente="Ana María Ruiz", cirujano="Dra. Sofía Martínez", fechaCirugia="2026-10-21T09:00")


def _buscar(client, q, **params):
    return client.get("/cirugias/buscar", params={"q": q, **params})


def test_busca_por_paciente_en_todo_el_historial(client, historial):
    datos = _buscar(client, "Ana").json()

    assert [c["nombrePaciente"] for c in datos["items"]] == ["Ana María Ruiz", "Ana López"]  # más reciente primero
    assert datos["total"] == 2


def test_busca_por_cirujano(client, historial):
    assert _buscar(client, "Martínez").json()["total"] == 2


def test_ignora_mayusculas_y_acentos(client, historial):
    assert _buscar(client, "lopez").json()["items"][0]["nombrePaciente"] == "Ana López"


def test_comodines_de_like_se_buscan_literales(client, historial):
    assert _buscar(client, "%%").json()["total"] == 0


def test_paginacion(client, historial):
    datos = _buscar(client, "Dr", tamano=2, pagina=2).json()  # los 3 cirujanos
    assert (datos["total"], datos["paginas"], len(datos["items"])) == (3, 2, 1)


@pytest.mark.parametrize("params", [{"q": "a"}, {"q": "ab", "tamano": 101}, {"q": "ab", "pagina": 0}, {}])
def test_parametros_invalidos_dan_422(client, params):
    assert client.get("/cirugias/buscar", params=params).status_code == 422


def test_capturista_busca_y_visualizador_no(sesion, historial):
    assert _buscar(sesion("andrea"), "Ana").status_code == 200
    assert _buscar(sesion("tv"), "Ana").status_code == 403
