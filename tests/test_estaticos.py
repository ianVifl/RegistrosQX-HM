import pytest


@pytest.mark.parametrize("ruta", ["/", "/login.html", "/js/api.js", "/css/base.css"])
def test_estaticos_se_revalidan(anonimo, ruta):
    r = anonimo.get(ruta)
    assert r.status_code == 200
    assert r.headers["cache-control"] == "no-cache"


def test_archivo_sin_cambios_responde_304(anonimo):
    etag = anonimo.get("/js/api.js").headers["etag"]
    assert anonimo.get("/js/api.js", headers={"If-None-Match": etag}).status_code == 304
