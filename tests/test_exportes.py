import io

import pytest
from openpyxl import load_workbook


@pytest.mark.parametrize("formato, firma, tipo", [
    ("pdf", b"%PDF", "application/pdf"),
    ("xlsx", b"PK", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
])
def test_exportar_cirugia(client, crear, formato, firma, tipo):
    id_ = crear().json()["id"]

    r = client.get(f"/cirugias/{id_}/exportar", params={"formato": formato})

    assert r.status_code == 200
    assert r.headers["content-type"] == tipo
    assert f'filename="cirugia_{id_}.{formato}"' in r.headers["content-disposition"]
    assert r.content.startswith(firma)


def test_exportar_rango_xlsx_contenido(client, crear):
    crear(serviciosEspeciales="Banco de sangre")

    r = client.get("/reportes/exportar", params={"formato": "xlsx", "desde": "2026-10-20", "hasta": "2026-10-26"})

    assert 'filename="cirugias_2026-10-20_a_2026-10-26.xlsx"' in r.headers["content-disposition"]
    hoja = load_workbook(io.BytesIO(r.content)).active
    encabezados, fila = [c.value for c in hoja[1]], [c.value for c in hoja[2]]
    assert "Código" not in encabezados
    registro = dict(zip(encabezados, fila))
    assert registro["Paciente"] == "Ana López"
    assert registro["Edad"] == 45
    assert registro["Sexo"] == "Femenino"
    assert registro["Diagnóstico"] == "Colelitiasis"
    assert registro["Servicios especiales"] == "Banco de sangre"


def test_exportar_un_dia_usa_nombre_simple(client):
    r = client.get("/reportes/exportar", params={"formato": "pdf", "desde": "2026-10-20", "hasta": "2026-10-20"})
    assert 'filename="cirugias_2026-10-20.pdf"' in r.headers["content-disposition"]


def test_exportar_formato_invalido_da_422(client, crear):
    id_ = crear().json()["id"]
    assert client.get(f"/cirugias/{id_}/exportar", params={"formato": "csv"}).status_code == 422


def test_exportar_inexistente_da_404(client):
    assert client.get("/cirugias/999/exportar", params={"formato": "pdf"}).status_code == 404


def test_historico_completo_xlsx_sin_limite_de_fechas(client, crear):
    crear(nombrePaciente="Reciente", fechaCirugia="2026-10-20T09:00")
    crear(nombrePaciente="Antigua", fechaCirugia="2023-01-15T09:00")  # fuera de cualquier rango de 31 días

    r = client.get("/reportes/historico")

    assert r.status_code == 200
    assert r.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert 'filename="cirugias_historico_completo_' in r.headers["content-disposition"]
    hoja = load_workbook(io.BytesIO(r.content)).active
    pacientes = [fila[3].value for fila in hoja.iter_rows(min_row=2)]
    assert pacientes == ["Antigua", "Reciente"]  # de la más antigua a la más reciente


def test_historico_permisos(sesion):
    assert sesion("andrea").get("/reportes/historico").status_code == 200
    assert sesion("tv").get("/reportes/historico").status_code == 403
