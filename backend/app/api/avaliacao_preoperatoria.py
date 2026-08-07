"""Avaliação Cardiológica Pré-Operatória de Risco Cirúrgico (pedido do
Rafael, 07/08/2026): reúne as calculadoras de risco cirúrgico validadas
(RCRI, Gupta MICA — `app/services/calculators.py`) num documento clínico
pronto para impressão, assinatura digital e envio ao paciente.

Deliberadamente NÃO cria nenhuma infraestrutura nova de PDF, assinatura ou
e-mail — o documento gerado aqui é um `GeneratedDocument` como qualquer
outro (mesma tabela, mesmo `doc_type` só que próprio), e por isso as rotas
já existentes em `app/api/documents.py` (`/gerados/{id}/pdf`,
`/gerados/{id}/assinatura-externa`, `/gerados/{id}/enviar-email`) servem
este documento sem alteração nenhuma: mesma identidade visual Corvia + logo
pessoal opcional + endereço comercial/residencial (`documento_generico()`),
mesmo catálogo de provedores de assinatura (inclusive gov.br/Assinador ITI,
Trabalho 14), mesmo envio por CorvIA Mail. Este módulo só faz uma coisa que
os outros não fazem: montar o corpo do documento a partir do resultado das
calculadoras, recalculado aqui no servidor — nunca confia num número que o
cliente diga ter calculado.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.audit import AuditLog
from app.models.clinical_docs import GeneratedDocument
from app.models.round import Patient
from app.services import calculators as calc
from app.services import cofre
from app.services.professional_profile import document_identity

router = APIRouter(prefix="/api/avaliacao-preoperatoria", tags=["avaliacao-preoperatoria"])

DOC_TYPE = "avaliacao_preoperatoria"
TITULO_DOCUMENTO = "Avaliação Cardiológica Pré-Operatória de Risco Cirúrgico"


class GerarIn(BaseModel):
    patient_id: int | None = None
    patient_name: str | None = None
    idade: int | None = None
    procedimento_planejado: str
    indicacao_cirurgica: str | None = None
    capacidade_funcional: str | None = None  # texto livre: METs estimados, limitação
    rcri: dict | None = None       # payload de campos do calculators["rcri"]
    gupta: dict | None = None      # payload de campos do calculators["gupta-mica"]
    conduta_recomendada: str | None = None  # texto livre do médico
    endereco: str | None = None


def _resultado_calculadora(slug: str, payload: dict | None) -> tuple[dict, str] | None:
    if not payload:
        return None
    try:
        r = calc.run(slug, payload)
    except (KeyError, ValueError, TypeError, ZeroDivisionError) as e:
        raise HTTPException(status_code=422, detail=f"Dados inválidos para {slug}: {e}") from e
    return r["result"], r["interpretation"]


def _montar_corpo(dados: GerarIn, rcri: tuple[dict, str] | None, gupta: tuple[dict, str] | None) -> str:
    linhas: list[str] = []
    linhas.append("AVALIAÇÃO CARDIOLÓGICA PRÉ-OPERATÓRIA DE RISCO CIRÚRGICO")
    linhas.append("")
    if dados.idade is not None:
        linhas.append(f"Idade do paciente: {dados.idade} anos")
    linhas.append(f"Procedimento planejado: {dados.procedimento_planejado}")
    if dados.indicacao_cirurgica:
        linhas.append(f"Indicação cirúrgica: {dados.indicacao_cirurgica}")
    if dados.capacidade_funcional:
        linhas.append(f"Capacidade funcional: {dados.capacidade_funcional}")
    linhas.append("")

    if rcri:
        resultado, interpretacao = rcri
        linhas.append(
            f"RCRI (Índice de Risco Cardíaco Revisado, Lee 1999): "
            f"{resultado['pontos']} ponto(s) — Classe {resultado['classe']}."
        )
        linhas.append(interpretacao)
        linhas.append("")
    if gupta:
        resultado, interpretacao = gupta
        linhas.append(
            f"Gupta MICA (risco de IAM ou parada cardíaca perioperatória): {resultado['risco_pct']}%."
        )
        linhas.append(interpretacao)
        linhas.append("")

    if dados.conduta_recomendada:
        linhas.append("Conduta e recomendações do médico responsável:")
        linhas.append(dados.conduta_recomendada)
        linhas.append("")

    linhas.append(
        "Este documento é uma ferramenta de apoio à decisão clínica, construída a partir de "
        "escores de risco validados na literatura (ver referências no verbete de cada "
        "calculadora em Calculadoras > Avaliação Pré-Operatória, dentro da Corvia). Não "
        "substitui o julgamento clínico do médico responsável nem a avaliação anestésica."
    )
    return "\n".join(linhas)


@router.post("/gerar", status_code=201)
def gerar(dados: GerarIn, db: Session = Depends(get_db), user=Depends(current_user)):
    if not dados.procedimento_planejado.strip():
        raise HTTPException(status_code=422, detail="Informe o procedimento planejado.")
    if dados.patient_id is not None:
        p = db.get(Patient, dados.patient_id)
        if not p or p.created_by != user.id:
            raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    if dados.endereco not in (None, "residencial", "profissional"):
        raise HTTPException(status_code=422, detail="endereco precisa ser 'residencial', 'profissional' ou omitido.")
    if dados.rcri is None and dados.gupta is None:
        raise HTTPException(status_code=422, detail="Calcule ao menos um dos dois escores (RCRI ou Gupta MICA) antes de gerar o documento.")

    # Recalcula no servidor — nunca confia em resultado que o cliente diga
    # ter obtido, mesma régua de "nunca fabricar dado" aplicada aqui a
    # cálculo, não só a texto.
    rcri = _resultado_calculadora("rcri", dados.rcri)
    gupta = _resultado_calculadora("gupta-mica", dados.gupta)

    corpo = _montar_corpo(dados, rcri, gupta)

    variaveis = {
        "idade": str(dados.idade) if dados.idade is not None else "",
        "procedimento_planejado": dados.procedimento_planejado,
        "indicacao_cirurgica": dados.indicacao_cirurgica or "",
        "capacidade_funcional": dados.capacidade_funcional or "",
        "conduta_recomendada": dados.conduta_recomendada or "",
        "rcri": dados.rcri or {},
        "gupta": dados.gupta or {},
    }

    gerado = GeneratedDocument(
        patient_id=dados.patient_id, template_id=None, created_by=user.id,
        doc_type=DOC_TYPE, title=TITULO_DOCUMENTO, rendered_body=corpo,
        endereco_exibido=dados.endereco, variables=variaveis,
    )
    db.add(gerado)
    db.flush()
    nome_paciente = (dados.patient_name or "").strip()
    if nome_paciente:
        gerado.patient_name_cifrado = cofre.cifrar_campo(nome_paciente, gerado.id)

    db.add(AuditLog(
        user_id=user.id, action="gerar_avaliacao_preoperatoria", entity="generated_document",
        entity_id=str(gerado.id),
        detail={"tem_rcri": rcri is not None, "tem_gupta": gupta is not None},
    ))
    db.commit()
    db.refresh(gerado)
    return {
        "id": gerado.id, "title": gerado.title, "doc_type": gerado.doc_type,
        "rendered_body": gerado.rendered_body, "created_at": gerado.created_at,
        "patient_name": nome_paciente or None,
        "medico": document_identity(user),
        "rcri": rcri[0] if rcri else None,
        "gupta": gupta[0] if gupta else None,
    }
