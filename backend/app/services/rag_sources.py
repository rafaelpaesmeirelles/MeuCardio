"""Registro das frentes científicas indexáveis em `knowledge_chunks` (Parte D
da correção coordenada de 02/09/2026 — RAG expandido além de `documents`).

Cada entrada descreve, para um `entity_type` do allowlist do grafo de
conhecimento (`app.models.knowledge.TIPOS_ENTIDADE_PERMITIDOS`), como extrair
um texto indexável de uma linha publicada. `documents` fica de fora deste
registro de propósito — continua no caminho já existente (`document_chunks`,
`rag.indexar_documento`), que não precisa mudar.

Nunca inclui `tema`/emergencia`/patient_*`: dado de paciente não entra aqui,
mesma regra do grafo (ver docstring de `app/models/knowledge.py`).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from sqlalchemy.orm import Session

from app.models.checklist import DischargeChecklist
from app.models.clinical_case import ClinicalCase
from app.models.emergency import EmergencyProtocol
from app.models.evidence import EvidenceRecord
from app.models.gallery import GalleryImage
from app.models.lab_test import LabTest
from app.models.drug import Drug
from app.models.patient_material import PatientMaterial
from app.models.specialty_guide import SpecialtyDisease, SymptomTriageGuide
from app.models.study import ScientificStudy
from app.models.study_track import StudyTrack


def _lista_texto(valor: Any) -> str:
    """Achata list[str] ou list[dict] num texto legível. Chaves comuns de
    texto em dict (pt/en) são priorizadas; o resto vira 'chave: valor'."""
    if not valor:
        return ""
    if isinstance(valor, str):
        return valor
    if isinstance(valor, dict):
        partes = []
        for chave in ("titulo", "title", "texto", "text", "descricao", "description", "nome", "name"):
            if valor.get(chave):
                partes.append(str(valor[chave]))
        if not partes:
            partes = [f"{k}: {v}" for k, v in valor.items() if isinstance(v, (str, int, float)) and v]
        return " — ".join(partes)
    if isinstance(valor, (list, tuple)):
        return "\n".join(_lista_texto(item) for item in valor if item)
    return str(valor)


def _texto_evidencia(item: EvidenceRecord) -> str:
    partes = [item.statement, item.summary, f"Diretriz: {item.guideline_title}", item.reference]
    return "\n\n".join(p for p in partes if p)


def _texto_estudo(item: ScientificStudy) -> str:
    partes = [item.summary, item.key_findings, item.clinical_implications, item.limitations]
    return "\n\n".join(p for p in partes if p)


def _texto_caso_clinico(item: ClinicalCase) -> str:
    partes = [item.enunciado, item.pergunta, item.explicacao]
    return "\n\n".join(p for p in partes if p)


def _texto_trilha(item: StudyTrack) -> str:
    partes = [item.objetivo, _lista_texto(item.etapas)]
    return "\n\n".join(p for p in partes if p)


def _texto_material_paciente(item: PatientMaterial) -> str:
    partes = [
        item.subtitulo, item.resumo, _lista_texto(item.secoes),
        _lista_texto(item.sinais_de_alerta), _lista_texto(item.perguntas),
    ]
    return "\n\n".join(p for p in partes if p)


def _texto_checklist(item: DischargeChecklist) -> str:
    partes = [item.condicao, item.resumo, _lista_texto(item.itens)]
    return "\n\n".join(p for p in partes if p)


def _texto_exame(item: LabTest) -> str:
    partes = [item.what_it_measures, item.reference_range, item.indications, item.interpretation, item.limitations]
    return "\n\n".join(p for p in partes if p)


def _texto_medicamento(item: Drug) -> str:
    partes = [
        item.drug_class, item.mechanism,
        _lista_texto(item.indications), _lista_texto(item.contraindications),
        _lista_texto(item.interactions), _lista_texto(item.adverse_effects),
        _lista_texto(item.monitoring), item.pregnancy, item.lactation,
    ]
    return "\n\n".join(p for p in partes if p)


def _texto_galeria(item: GalleryImage) -> str:
    partes = [item.findings, item.teaching_points]
    return "\n\n".join(p for p in partes if p)


def _texto_protocolo_emergencia(item: EmergencyProtocol) -> str:
    # Conteúdo profundo vive no Document referenciado por documento_slug (já
    # indexado em document_chunks) — aqui só o suficiente pra achar o
    # protocolo certo por sintoma/gatilho na busca semântica.
    partes = [item.titulo, item.gatilho]
    return "\n\n".join(p for p in partes if p)


def _texto_doenca(item: SpecialtyDisease) -> str:
    partes = [
        item.summary, item.epidemiology, item.treatment_summary,
        _lista_texto(item.red_flags), _lista_texto(item.differentials),
    ]
    return "\n\n".join(p for p in partes if p)


def _texto_triagem(item: SymptomTriageGuide) -> str:
    partes = [item.summary, _lista_texto(item.differentials), _lista_texto(item.red_flags)]
    return "\n\n".join(p for p in partes if p)


@dataclass(frozen=True)
class FonteRAG:
    entity_type: str
    model: type
    titulo_attr: str
    slug_attr: str
    texto: Callable[[Any], str]
    rota: str  # template de rota do frontend, {slug} é substituído na citação
    tema_attr: str | None = None  # nome do atributo theme/tema, quando existir


FONTES_RAG: tuple[FonteRAG, ...] = (
    FonteRAG("evidencia", EvidenceRecord, "guideline_title", "slug", _texto_evidencia, "/evidencias/{slug}", "theme"),
    FonteRAG("estudo", ScientificStudy, "title", "slug", _texto_estudo, "/estudos/{slug}", "theme"),
    FonteRAG("caso_clinico", ClinicalCase, "titulo", "slug", _texto_caso_clinico, "/casos-clinicos/{slug}", "tema"),
    FonteRAG("trilha", StudyTrack, "titulo", "slug", _texto_trilha, "/trilhas/{slug}", "tema"),
    FonteRAG("material_paciente", PatientMaterial, "titulo", "slug", _texto_material_paciente, "/material-paciente/{slug}", "tema"),
    FonteRAG("checklist", DischargeChecklist, "condicao", "slug", _texto_checklist, "/checklists/{slug}", "theme"),
    FonteRAG("exame", LabTest, "name", "slug", _texto_exame, "/exames/{slug}", "theme"),
    FonteRAG("medicamento", Drug, "generic_name", "slug", _texto_medicamento, "/medicamentos/{slug}", None),
    FonteRAG("galeria", GalleryImage, "title", "slug", _texto_galeria, "/galeria/{slug}", "theme"),
    FonteRAG("protocolo_emergencia", EmergencyProtocol, "titulo", "slug", _texto_protocolo_emergencia, "/emergencia", None),
    FonteRAG("doenca", SpecialtyDisease, "name", "slug", _texto_doenca, "/doencas/{slug}", "area"),
    FonteRAG("triagem_sintoma", SymptomTriageGuide, "name", "slug", _texto_triagem, "/triagem-sintomas/{slug}", None),
)

FONTES_POR_TIPO: dict[str, FonteRAG] = {fonte.entity_type: fonte for fonte in FONTES_RAG}


def publicados(db: Session, fonte: FonteRAG):
    return db.query(fonte.model).filter(fonte.model.published.is_(True)).all()
