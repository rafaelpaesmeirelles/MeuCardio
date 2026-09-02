"""Avaliação Cardiológica Pré-Operatória de Risco Cirúrgico.

Reúne calculadoras perioperatórias validadas num documento clínico pronto para
impressão, assinatura digital e envio ao paciente. Os resultados são sempre
recalculados no servidor a partir dos campos brutos — nunca se confia em um
número enviado pelo cliente.

Fonte: ChatGPT nas extensões DASI/AUB-HAS2/VSG-CRI/GSCRI/SORT/S-MPM/FRAIL.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.audit import AuditLog
from app.models.clinical_docs import GeneratedDocument
from app.services import calculators as calc
from app.services import cofre
from app.services import patient_profile_service
from app.services.clinical_ownership import patient_for_user
from app.services.perioperative_calculators import PERIOPERATIVE_REGISTRY
from app.services.professional_profile import document_identity

calc.REGISTRY.update(PERIOPERATIVE_REGISTRY)

router = APIRouter(prefix="/api/avaliacao-preoperatoria", tags=["avaliacao-preoperatoria"])

DOC_TYPE = "avaliacao_preoperatoria"
TITULO_DOCUMENTO = "Avaliação Cardiológica Pré-Operatória de Risco Cirúrgico"


class GerarIn(BaseModel):
    patient_id: int | None = None
    patient_name: str | None = None
    # Cadastro reutilizável, opcional — mesma infraestrutura de
    # `app/api/documents.py`/`app/services/patient_profile_service.py`
    # (Parte 1 da correção coordenada de 02/09/2026). Prevalece sobre
    # `patient_name` quando presente; `patient_id` acima é campo diferente
    # (paciente anônimo do Round).
    patient_profile_id: int | None = None
    idade: int | None = None
    procedimento_planejado: str
    indicacao_cirurgica: str | None = None
    capacidade_funcional: str | None = None
    rcri: dict | None = None
    gupta: dict | None = None
    dasi: dict | None = None
    aub_has2: dict | None = None
    vsg_cri: dict | None = None
    gscri: dict | None = None
    sort: dict | None = None
    s_mpm: dict | None = None
    frail: dict | None = None
    conduta_recomendada: str | None = None
    endereco: str | None = None


def _resultado_calculadora(slug: str, payload: dict | None) -> tuple[dict, str] | None:
    if not payload:
        return None
    try:
        r = calc.run(slug, payload)
    except (KeyError, ValueError, TypeError, ZeroDivisionError) as e:
        raise HTTPException(status_code=422, detail=f"Dados inválidos para {slug}: {e}") from e
    return r["result"], r["interpretation"]


def _montar_corpo(
    dados: GerarIn,
    rcri: tuple[dict, str] | None,
    gupta: tuple[dict, str] | None,
    dasi: tuple[dict, str] | None,
    aub_has2: tuple[dict, str] | None,
    vsg_cri: tuple[dict, str] | None,
    gscri: tuple[dict, str] | None,
    sort: tuple[dict, str] | None,
    s_mpm: tuple[dict, str] | None,
    frail: tuple[dict, str] | None,
) -> str:
    linhas: list[str] = []
    linhas.append("AVALIAÇÃO CARDIOLÓGICA PRÉ-OPERATÓRIA DE RISCO CIRÚRGICO")
    linhas.append("")
    if dados.idade is not None:
        linhas.append(f"Idade do paciente: {dados.idade} anos")
    linhas.append(f"Procedimento planejado: {dados.procedimento_planejado}")
    if dados.indicacao_cirurgica:
        linhas.append(f"Indicação cirúrgica: {dados.indicacao_cirurgica}")
    if dados.capacidade_funcional:
        linhas.append(f"Capacidade funcional (descrição clínica): {dados.capacidade_funcional}")
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

    if dasi:
        resultado, interpretacao = dasi
        linhas.append(
            f"DASI (Duke Activity Status Index): {resultado['score']}/58,2 — "
            f"capacidade funcional: {resultado['capacidade_funcional'].replace('_', ' ')}."
        )
        linhas.append(interpretacao)
        linhas.append("")

    if aub_has2:
        resultado, interpretacao = aub_has2
        linhas.append(
            f"AUB-HAS2: {resultado['score']}/6 — categoria de risco {resultado['categoria']}."
        )
        linhas.append(interpretacao)
        linhas.append("")

    if vsg_cri:
        resultado, interpretacao = vsg_cri
        linhas.append(
            f"VSG-CRI (cirurgia vascular arterial): {resultado['score']} ponto(s) — "
            f"categoria de risco {resultado['categoria']}."
        )
        linhas.append(interpretacao)
        linhas.append("")

    if gscri:
        resultado, interpretacao = gscri
        linhas.append(
            f"GSCRI (pacientes ≥65 anos; risco de IAM ou parada cardíaca): {resultado['risco_pct']}%."
        )
        linhas.append(interpretacao)
        linhas.append("")

    if sort:
        resultado, interpretacao = sort
        linhas.append(
            f"SORT (mortalidade por todas as causas em 30 dias): {resultado['risco_pct']}%."
        )
        linhas.append(interpretacao)
        linhas.append("")

    if s_mpm:
        resultado, interpretacao = s_mpm
        linhas.append(
            f"S-MPM (mortalidade por todas as causas em 30 dias): "
            f"{resultado['score']}/9 — Classe {resultado['classe']} — {resultado['mortalidade_30d']}."
        )
        linhas.append(interpretacao)
        linhas.append("")

    if frail:
        resultado, interpretacao = frail
        rotulo = resultado["categoria"].replace("_", "-")
        linhas.append(
            f"FRAIL Scale (modificador de risco por fragilidade): "
            f"{resultado['score']}/5 — {rotulo}."
        )
        linhas.append(interpretacao)
        linhas.append("")

    linhas.append("INTEGRAÇÃO DOS MÉTODOS")
    linhas.append(
        "Os escores estimam desfechos diferentes e não devem ser somados, promediados nem usados "
        "isoladamente como autorização para cirurgia. A decisão integra doença cardiovascular ativa, "
        "risco do procedimento, modificadores de risco, capacidade funcional e possibilidade de que "
        "uma investigação adicional modifique o manejo. O VSG-CRI deve ser utilizado especificamente "
        "em cirurgia vascular arterial; o GSCRI foi desenvolvido para pacientes ≥65 anos; SORT e "
        "S-MPM estimam mortalidade cirúrgica global; a FRAIL Scale avalia fragilidade e reserva "
        "fisiológica, não risco cardíaco percentual."
    )
    linhas.append("")

    if dados.conduta_recomendada:
        linhas.append("Conduta e recomendações do médico responsável:")
        linhas.append(dados.conduta_recomendada)
        linhas.append("")

    linhas.append(
        "Este documento é uma ferramenta de apoio à decisão clínica baseada em metodologias "
        "validadas na literatura. Não substitui o julgamento clínico do médico responsável nem "
        "a avaliação anestésica. As árvores de decisão e referências completas estão disponíveis "
        "na Biblioteca da Corvia, tema Perioperatório."
    )
    return "\n".join(linhas)


@router.post("/gerar", status_code=201)
def gerar(dados: GerarIn, db: Session = Depends(get_db), user=Depends(current_user)):
    if not dados.procedimento_planejado.strip():
        raise HTTPException(status_code=422, detail="Informe o procedimento planejado.")
    if dados.patient_id is not None:
        patient_for_user(dados.patient_id, db, user)
    if dados.endereco not in (None, "residencial", "profissional"):
        raise HTTPException(status_code=422, detail="endereco precisa ser 'residencial', 'profissional' ou omitido.")
    if all(
        x is None
        for x in (
            dados.rcri,
            dados.gupta,
            dados.dasi,
            dados.aub_has2,
            dados.vsg_cri,
            dados.gscri,
            dados.sort,
            dados.s_mpm,
            dados.frail,
        )
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "Calcule ao menos um método (RCRI, Gupta MICA, DASI, AUB-HAS2, VSG-CRI, "
                "GSCRI, SORT, S-MPM ou FRAIL Scale) antes de gerar o documento."
            ),
        )

    rcri = _resultado_calculadora("rcri", dados.rcri)
    gupta = _resultado_calculadora("gupta-mica", dados.gupta)
    dasi = _resultado_calculadora("dasi", dados.dasi)
    aub_has2 = _resultado_calculadora("aub-has2", dados.aub_has2)
    vsg_cri = _resultado_calculadora("vsg-cri", dados.vsg_cri)
    gscri = _resultado_calculadora("gscri", dados.gscri)
    sort = _resultado_calculadora("sort", dados.sort)
    s_mpm = _resultado_calculadora("s-mpm", dados.s_mpm)
    frail = _resultado_calculadora("frail-scale-perioperatorio", dados.frail)

    corpo = _montar_corpo(dados, rcri, gupta, dasi, aub_has2, vsg_cri, gscri, sort, s_mpm, frail)

    variaveis = {
        "idade": str(dados.idade) if dados.idade is not None else "",
        "procedimento_planejado": dados.procedimento_planejado,
        "indicacao_cirurgica": dados.indicacao_cirurgica or "",
        "capacidade_funcional": dados.capacidade_funcional or "",
        "conduta_recomendada": dados.conduta_recomendada or "",
        "rcri": dados.rcri or {},
        "gupta": dados.gupta or {},
        "dasi": dados.dasi or {},
        "aub_has2": dados.aub_has2 or {},
        "vsg_cri": dados.vsg_cri or {},
        "gscri": dados.gscri or {},
        "sort": dados.sort or {},
        "s_mpm": dados.s_mpm or {},
        "frail": dados.frail or {},
        "fonte_producao_extensoes": "chatgpt",
    }

    nome_paciente_resolvido, snapshot, profile_id = patient_profile_service.resolver_paciente_documento(
        db, user, patient_profile_id=dados.patient_profile_id, patient_name_avulso=dados.patient_name,
    )

    gerado = GeneratedDocument(
        patient_id=dados.patient_id,
        template_id=None,
        created_by=user.id,
        doc_type=DOC_TYPE,
        title=TITULO_DOCUMENTO,
        rendered_body=corpo,
        endereco_exibido=dados.endereco,
        patient_profile_id=profile_id,
        variables=variaveis,
    )
    db.add(gerado)
    db.flush()
    nome_paciente = (nome_paciente_resolvido or "").strip()
    if nome_paciente:
        gerado.patient_name_cifrado = cofre.cifrar_campo(nome_paciente, gerado.id)
    if snapshot:
        gerado.patient_snapshot_cifrado = patient_profile_service.cifrar_snapshot(snapshot, gerado.id)

    db.add(
        AuditLog(
            user_id=user.id,
            action="gerar_avaliacao_preoperatoria",
            entity="generated_document",
            entity_id=str(gerado.id),
            detail={
                "tem_rcri": rcri is not None,
                "tem_gupta": gupta is not None,
                "tem_dasi": dasi is not None,
                "tem_aub_has2": aub_has2 is not None,
                "tem_vsg_cri": vsg_cri is not None,
                "tem_gscri": gscri is not None,
                "tem_sort": sort is not None,
                "tem_s_mpm": s_mpm is not None,
                "tem_frail": frail is not None,
            },
        )
    )
    db.commit()
    db.refresh(gerado)
    return {
        "id": gerado.id,
        "title": gerado.title,
        "doc_type": gerado.doc_type,
        "rendered_body": gerado.rendered_body,
        "created_at": gerado.created_at,
        "patient_name": nome_paciente or None,
        "patient_profile_id": profile_id,
        "medico": document_identity(user),
        "rcri": rcri[0] if rcri else None,
        "gupta": gupta[0] if gupta else None,
        "dasi": dasi[0] if dasi else None,
        "aub_has2": aub_has2[0] if aub_has2 else None,
        "vsg_cri": vsg_cri[0] if vsg_cri else None,
        "gscri": gscri[0] if gscri else None,
        "sort": sort[0] if sort else None,
        "s_mpm": s_mpm[0] if s_mpm else None,
        "frail": frail[0] if frail else None,
    }
