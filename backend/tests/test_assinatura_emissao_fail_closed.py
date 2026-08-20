from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.services.assinatura import emissao
from app.services.assinatura.provedor import Assinatura


class _ProvedorQueFingeSucesso:
    def assinar(self, _pdf, _medico, _contexto):
        return Assinatura(estado="assinado", pdf=b"%PDF-1.4\nsem assinatura digital")


def test_emissao_nao_persiste_pdf_quando_provedor_finge_que_assinou():
    db = SimpleNamespace(add=lambda _registro: pytest.fail("não deve persistir"))
    info = SimpleNamespace(nivel="QUALIFICADA")

    with pytest.raises(emissao.AssinaturaNaoDetectada):
        emissao.assinar_e_persistir(
            db,
            tipo=emissao.TIPO_RECEITA,
            referencia_id=123,
            metodo="A1_ARQUIVO",
            provedor=_ProvedorQueFingeSucesso(),
            info=info,
            pdf_visual=b"%PDF-1.4\noriginal",
            medico={"full_name": "Dr. Teste"},
            criado_por=1,
            data_emissao=datetime.now(timezone.utc),
        )
