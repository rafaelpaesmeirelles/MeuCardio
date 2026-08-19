import json

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from app.core.prescricao_especial_isolation import PrescricaoEspecialIsolationMiddleware
from app.models.clinical_docs import GeneratedDocument


async def _detail(_request):
    return JSONResponse({"ok": True})


async def _list(_request):
    return JSONResponse({
        "items": [
            {"id": 10, "doc_type": "atestado"},
            {"id": 11, "doc_type": "prescricao_livre_especial"},
        ],
        "page": 1,
        "page_size": 20,
        "has_more": False,
        "total": 2,
    })


def _app():
    app = Starlette(routes=[
        Route("/api/document-templates/gerados", _list, methods=["GET"]),
        Route("/api/document-templates/gerados/{gid:int}", _detail, methods=["GET"]),
        Route("/api/document-templates/gerados/{gid:int}/pdf", _detail, methods=["GET"]),
    ])
    app.add_middleware(PrescricaoEspecialIsolationMiddleware)
    return app


def test_listagem_generica_oculta_prescricao_especial():
    with TestClient(_app()) as client:
        response = client.get("/api/document-templates/gerados")
    assert response.status_code == 200
    assert response.json()["items"] == [{"id": 10, "doc_type": "atestado"}]
    assert response.json()["total"] == 1


def test_rota_generica_por_id_falha_fechada_para_prescricao_especial(db, criar_usuario):
    user, _ = criar_usuario(email="isolamento@teste.local")
    g = GeneratedDocument(
        created_by=user.id,
        doc_type="prescricao_livre_especial",
        title="Receituário",
        rendered_body="Texto",
        variables={},
    )
    db.add(g)
    db.commit()
    db.refresh(g)

    with TestClient(_app()) as client:
        detail = client.get(f"/api/document-templates/gerados/{g.id}")
        pdf = client.get(f"/api/document-templates/gerados/{g.id}/pdf")

    assert detail.status_code == 404
    assert pdf.status_code == 404
