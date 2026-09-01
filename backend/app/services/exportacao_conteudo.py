"""Exportação universal de conteúdo publicado do CorVIA.

O exportador resolve o objeto canônico no servidor e nunca aceita HTML ou texto
clínico arbitrário enviado pelo navegador. Assim, exportar muda o formato, não
o conteúdo: item retido/despublicado continua indisponível e referências,
proveniência e metadados estruturados acompanham o PDF.

O PDF é A4, usa o mesmo motor e a mesma marca já empregados nos documentos do
CorVIA. A marca CorVIA é obrigatória; a identificação profissional do assinante
é opt-in por exportação.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.checklist import DischargeChecklist
from app.models.clinical_case import ClinicalCase
from app.models.cmed import CmedApresentacao, CmedVersao
from app.models.content import Document
from app.models.drug import Drug
from app.models.emergency import EmergencyProtocol
from app.models.evidence import EvidenceRecord
from app.models.gallery import GalleryImage
from app.models.guideline import Guideline
from app.models.lab_test import LabTest
from app.models.patient_material import PatientMaterial
from app.models.specialty_guide import SpecialtyDisease
from app.models.study import ScientificStudy
from app.models.study_track import StudyTrack
from app.services import calculators as calc
from app.services.clinical_text import clinical_text_without_internal_overrides
from app.services.cmed_precos import preco_pmc
from app.services.pdf.layout import Documento
from app.services.pdf.marca import FIO, LOGO, NAVY, NEUTRO, TEAL, logo_disponivel
from app.services.pricing.kairos_provider import api_snapshot_for
from app.services.professional_profile import council_display, document_identity, professional_name, workplace_lines
from app.services.timeline_conhecimento import montar_timeline


TIPOS_EXPORTAVEIS = {
    "documento", "fluxograma", "evidencia", "estudo", "medicamento", "exame",
    "guideline", "doenca", "caso_clinico", "trilha", "checklist",
    "material_paciente", "emergencia", "galeria", "calculadora", "timeline",
}
ROTULOS_TIPO = {
    "documento": "Biblioteca",
    "fluxograma": "Fluxograma",
    "evidencia": "Evidência",
    "estudo": "Estudo",
    "medicamento": "Medicamento",
    "exame": "Exame",
    "guideline": "Guideline",
    "doenca": "Condição clínica",
    "caso_clinico": "Caso clínico",
    "trilha": "Trilha de estudo",
    "checklist": "Checklist",
    "material_paciente": "Material para paciente",
    "emergencia": "Protocolo de emergência",
    "galeria": "Galeria",
    "calculadora": "Calculadora",
    "timeline": "Timeline científica",
}


@dataclass
class SecaoExportacao:
    titulo: str
    paragrafos: list[str] = field(default_factory=list)
    itens: list[str] = field(default_factory=list)
    destaque: str | None = None


@dataclass
class ConteudoExportavel:
    tipo: str
    slug: str
    titulo: str
    tema: str | None
    subtitulo: str | None = None
    secoes: list[SecaoExportacao] = field(default_factory=list)


def _texto(valor: Any) -> str:
    if valor is None:
        return ""
    if isinstance(valor, bool):
        return "Sim" if valor else "Não"
    if isinstance(valor, (int, float)):
        return str(valor)
    if isinstance(valor, str):
        return valor.strip()
    if isinstance(valor, list):
        return "; ".join(_texto(item) for item in valor if _texto(item))
    if isinstance(valor, dict):
        partes = []
        for chave, item in valor.items():
            texto = _texto(item)
            if texto:
                partes.append(f"{_rotulo(chave)}: {texto}")
        return "; ".join(partes)
    return str(valor).strip()


def _rotulo(chave: str) -> str:
    return chave.replace("_", " ").strip().capitalize()


def _sem_markdown(texto: str | None) -> str:
    valor = (texto or "").strip()
    if not valor:
        return ""
    valor = re.sub(r"```(?:\w+)?\s*", "", valor)
    valor = valor.replace("```", "")
    valor = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", valor)
    valor = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", valor)
    valor = re.sub(r"<[^>]+>", " ", valor)
    valor = re.sub(r"^\s{0,3}#{1,6}\s*", "", valor, flags=re.M)
    valor = re.sub(r"[*_~`]", "", valor)
    valor = re.sub(r"\n{3,}", "\n\n", valor)
    return valor.strip()


def _secoes_markdown(texto: str | None) -> list[SecaoExportacao]:
    bruto = (texto or "").strip()
    if not bruto:
        return []
    partes = re.split(r"(?m)^\s{0,3}(#{1,6})\s+(.+?)\s*$", bruto)
    secoes: list[SecaoExportacao] = []
    inicial = _sem_markdown(partes[0])
    if inicial:
        secoes.append(SecaoExportacao("Conteúdo", paragrafos=[p.strip() for p in inicial.split("\n\n") if p.strip()]))
    for indice in range(1, len(partes), 3):
        titulo = _sem_markdown(partes[indice + 1])
        corpo = _sem_markdown(partes[indice + 2] if indice + 2 < len(partes) else "")
        if not titulo and not corpo:
            continue
        paragrafos, itens = [], []
        for bloco in [b.strip() for b in corpo.split("\n\n") if b.strip()]:
            linhas = [linha.strip() for linha in bloco.splitlines() if linha.strip()]
            if linhas and all(re.match(r"^(?:[-•*]|\d+[.)])\s+", linha) for linha in linhas):
                itens.extend(re.sub(r"^(?:[-•*]|\d+[.)])\s+", "", linha) for linha in linhas)
            else:
                paragrafos.append(" ".join(re.sub(r"^(?:[-•*]|\d+[.)])\s+", "", linha) for linha in linhas))
        secoes.append(SecaoExportacao(titulo or "Conteúdo", paragrafos=paragrafos, itens=itens))
    return secoes


def _secao(titulo: str, *valores: Any, itens: list[Any] | None = None, destaque: str | None = None) -> SecaoExportacao | None:
    paragrafos = [_texto(valor) for valor in valores if _texto(valor)]
    lista = [_texto(item) for item in (itens or []) if _texto(item)]
    if not paragrafos and not lista and not destaque:
        return None
    return SecaoExportacao(titulo, paragrafos=paragrafos, itens=lista, destaque=destaque)


def _append(lista: list[SecaoExportacao], item: SecaoExportacao | None) -> None:
    if item is not None:
        lista.append(item)


def _versao_cmed(db: Session) -> CmedVersao | None:
    return db.query(CmedVersao).order_by(CmedVersao.id.desc()).first()


def _cmed_secoes(db: Session, drug: Drug, uf: str | None) -> list[SecaoExportacao]:
    versao = _versao_cmed(db)
    if versao is None:
        return []
    linhas: list[str] = []
    rows = (
        db.query(CmedApresentacao)
        .filter(CmedApresentacao.drug_id == drug.id, CmedApresentacao.cmed_versao_id == versao.id)
        .order_by(CmedApresentacao.produto, CmedApresentacao.apresentacao)
        .limit(80)
        .all()
    )
    for row in rows:
        preco = preco_pmc(row.pmc_por_aliquota or {}, uf)
        valor = preco.get("valor")
        rotulo = preco.get("rotulo") or "PMC"
        final = f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if valor is not None else "sem PMC publicado"
        linhas.append(f"{row.produto} · {row.laboratorio} · {row.apresentacao} · {rotulo}: {final}")
    if not linhas:
        return []
    return [SecaoExportacao(
        "CMED / ANVISA — referência regulatória",
        paragrafos=["PMC é teto regulatório de referência e não representa necessariamente o preço final praticado pela farmácia."],
        itens=linhas,
    )]


def _kairos_secao(drug: Drug) -> SecaoExportacao | None:
    try:
        snapshot = api_snapshot_for(drug)
    except (OSError, ValueError, KeyError):
        return None
    registros = snapshot.get("records") or []
    if not registros:
        return None
    linhas: list[str] = []
    for registro in registros:
        produto = registro.get("product") or drug.generic_name
        laboratorio = registro.get("laboratory") or ""
        pagina = registro.get("page")
        for apresentacao in registro.get("presentations") or []:
            precos = []
            for campo, rotulo in (("pf20", "PF 20%"), ("pmc20", "PMC 20%"), ("pf18", "PF 18%"), ("pmc18", "PMC 18%"), ("pf17", "PF 17%"), ("pmc17", "PMC 17%"), ("pf12", "PF 12%"), ("pmc12", "PMC 12%")):
                if apresentacao.get(campo):
                    precos.append(f"{rotulo} R$ {apresentacao[campo]}")
            linhas.append(f"{produto} · {laboratorio} · {apresentacao.get('presentation', '')} · {' · '.join(precos)}" + (f" · p. {pagina}" if pagina else ""))
    return SecaoExportacao(
        f"K@iros — inteligência de mercado licenciada · edição {snapshot.get('issue') or ''}",
        paragrafos=[snapshot.get("regulatory_note") or "Fonte complementar de mercado; em divergência regulatória, prevalece CMED/ANVISA."],
        itens=linhas[:80],
    )


def _resolver_documento(db: Session, slug: str, tipo: str) -> ConteudoExportavel | None:
    query = db.query(Document).filter(Document.slug == slug, Document.published.is_(True))
    if tipo == "fluxograma":
        query = query.filter(Document.kind == "fluxograma")
    doc = query.first()
    if doc is None:
        return None
    secoes: list[SecaoExportacao] = []
    _append(secoes, _secao("Resumo", clinical_text_without_internal_overrides(doc.summary)))
    secoes.extend(_secoes_markdown(doc.body_md))
    _append(secoes, _secao("Nível de evidência", doc.evidence_level))
    _append(secoes, _secao("Referências", itens=list(doc.source_refs or [])))
    if doc.gaps:
        _append(secoes, _secao("Lacunas declaradas", itens=list(doc.gaps)))
    return ConteudoExportavel(tipo, doc.slug, doc.title, doc.theme, doc.kind, secoes)


def _resolver_evidencia(db: Session, slug: str) -> ConteudoExportavel | None:
    e = db.query(EvidenceRecord).filter(EvidenceRecord.slug == slug, EvidenceRecord.published.is_(True)).first()
    if e is None:
        return None
    secoes: list[SecaoExportacao] = []
    _append(secoes, _secao("Recomendação", e.statement, destaque=f"Classe {e.recommendation_class} · nível {e.evidence_level}"))
    evidence_summary = clinical_text_without_internal_overrides(e.summary)
    if evidence_summary and evidence_summary.strip() != e.statement.strip():
        _append(secoes, _secao("Resumo clínico", evidence_summary))
    _append(secoes, _secao("Diretriz de origem", f"{e.society} {e.year} · {e.guideline_title}"))
    refs = [x for x in [e.reference, f"DOI: {e.doi}" if e.doi else None, e.source_url] if x]
    _append(secoes, _secao("Referências e fonte", itens=refs))
    return ConteudoExportavel("evidencia", e.slug, e.statement[:180], e.theme, f"{e.society} {e.year}", secoes)


def _resolver_estudo(db: Session, slug: str) -> ConteudoExportavel | None:
    s = db.query(ScientificStudy).filter(ScientificStudy.slug == slug, ScientificStudy.published.is_(True)).first()
    if s is None:
        return None
    secoes: list[SecaoExportacao] = []
    _append(secoes, _secao("Resumo", s.summary))
    _append(secoes, _secao("Principais achados", s.key_findings))
    _append(secoes, _secao("Implicação clínica", s.clinical_implications))
    _append(secoes, _secao("Limitações", s.limitations))
    refs = [x for x in [s.authors, f"{s.journal} · {s.year}", f"DOI: {s.doi}" if s.doi else None, f"PMID: {s.pmid}" if s.pmid else None, s.url] if x]
    _append(secoes, _secao("Publicação original", itens=refs))
    return ConteudoExportavel("estudo", s.slug, s.title, s.theme, f"{s.journal} · {s.year}", secoes)


def _resolver_medicamento(db: Session, slug: str, uf: str | None) -> ConteudoExportavel | None:
    d = db.query(Drug).filter(Drug.slug == slug, Drug.published.is_(True)).first()
    if d is None:
        return None
    secoes: list[SecaoExportacao] = []
    _append(secoes, _secao("Classe e mecanismo", d.drug_class, d.mechanism))
    _append(secoes, _secao("Indicações", itens=list(d.indications or [])))
    _append(secoes, _secao("Doses", d.dosing))
    _append(secoes, _secao("Apresentações", itens=list(d.presentations or [])))
    _append(secoes, _secao("Ajuste renal", d.renal_adjustment))
    _append(secoes, _secao("Ajuste hepático", d.hepatic_adjustment))
    _append(secoes, _secao("Contraindicações", itens=list(d.contraindications or [])))
    _append(secoes, _secao("Interações", itens=list(d.interactions or [])))
    _append(secoes, _secao("Monitorização", itens=list(d.monitoring or [])))
    _append(secoes, _secao("Efeitos adversos", itens=list(d.adverse_effects or [])))
    _append(secoes, _secao("Gestação e lactação", d.pregnancy and f"Gestação: {d.pregnancy}", d.lactation and f"Lactação: {d.lactation}"))
    farmacocinetica = []
    if d.half_life_hours is not None:
        farmacocinetica.append(f"Meia-vida: {float(d.half_life_hours):g} h" + (f" · {d.half_life_note}" if d.half_life_note else ""))
    if d.duration_of_action_hours is not None:
        farmacocinetica.append(f"Duração de ação: {float(d.duration_of_action_hours):g} h" + (f" · {d.duration_of_action_note}" if d.duration_of_action_note else ""))
    _append(secoes, _secao("Farmacocinética", itens=farmacocinetica))
    if d.sbp_reduction_mmhg is not None or d.dbp_reduction_mmhg is not None:
        _append(secoes, _secao("Efeito hemodinâmico publicado", f"PAS: {d.sbp_reduction_mmhg if d.sbp_reduction_mmhg is not None else '—'} mmHg · PAD: {d.dbp_reduction_mmhg if d.dbp_reduction_mmhg is not None else '—'} mmHg", d.bp_evidence_source))
    _append(secoes, _secao("Referências", itens=list(d.references or [])))
    secoes.extend(_cmed_secoes(db, d, uf))
    _append(secoes, _kairos_secao(d))
    marcas = ", ".join(d.brand_names or []) or None
    return ConteudoExportavel("medicamento", d.slug, d.generic_name, "Farmacologia", marcas or d.drug_class, secoes)


def _resolver_exame(db: Session, slug: str) -> ConteudoExportavel | None:
    t = db.query(LabTest).filter(LabTest.slug == slug, LabTest.published.is_(True)).first()
    if t is None:
        return None
    secoes: list[SecaoExportacao] = []
    _append(secoes, _secao("O que mede", t.what_it_measures))
    _append(secoes, _secao("Valor de referência", t.reference_range))
    _append(secoes, _secao("Indicações", t.indications))
    _append(secoes, _secao("Interpretação", t.interpretation))
    _append(secoes, _secao("Limitações", t.limitations))
    _append(secoes, _secao("Fontes", itens=list(t.source_refs or [])))
    return ConteudoExportavel("exame", t.slug, t.name, t.theme, t.category, secoes)


def _resolver_guideline(db: Session, slug: str) -> ConteudoExportavel | None:
    g = db.query(Guideline).filter(Guideline.slug == slug).first()
    if g is None:
        return None
    secoes: list[SecaoExportacao] = []
    _append(secoes, _secao("Identificação", f"{g.org} · {g.ano}", f"Status de detecção: {g.detection_status}"))
    refs = [x for x in [f"DOI: {g.doi}" if g.doi else None, g.url] if x]
    _append(secoes, _secao("Fonte oficial", itens=refs))
    if g.superseded_by_id:
        _append(secoes, _secao("Atualização", "Esta diretriz está marcada no CorVIA como substituída por versão posterior."))
    return ConteudoExportavel("guideline", g.slug, g.titulo, g.tema, f"{g.org} {g.ano}", secoes)


def _resolver_doenca(db: Session, slug: str) -> ConteudoExportavel | None:
    d = db.query(SpecialtyDisease).filter(SpecialtyDisease.slug == slug, SpecialtyDisease.published.is_(True)).first()
    if d is None:
        return None
    secoes: list[SecaoExportacao] = []
    _append(secoes, _secao("Resumo", clinical_text_without_internal_overrides(d.summary)))
    _append(secoes, _secao("Epidemiologia", d.epidemiology))
    _append(secoes, _secao("Apresentação clínica", itens=list(d.presentation or [])))
    _append(secoes, _secao("Investigação e diagnóstico", d.diagnostic_approach))
    _append(secoes, _secao("Diagnósticos diferenciais", itens=list(d.differentials or [])))
    _append(secoes, _secao("Exames", itens=list(d.tests or [])))
    _append(secoes, _secao("Sinais de alerta", itens=list(d.red_flags or [])))
    _append(secoes, _secao("Fluxo ambulatorial", itens=list(d.ambulatory_flow or [])))
    _append(secoes, _secao("Fluxo de emergência", itens=list(d.emergency_flow or [])))
    _append(secoes, _secao("Tratamento", clinical_text_without_internal_overrides(d.treatment_summary)))
    _append(secoes, _secao("Monitorização", itens=list(d.monitoring or [])))
    _append(secoes, _secao("Populações especiais", itens=list(d.special_populations or [])))
    _append(secoes, _secao("Fontes", itens=list(d.source_refs or []) + list(d.source_urls or [])))
    return ConteudoExportavel("doenca", d.slug, d.name, d.area, d.category, secoes)


def _resolver_caso(db: Session, slug: str) -> ConteudoExportavel | None:
    c = db.query(ClinicalCase).filter(ClinicalCase.slug == slug, ClinicalCase.published.is_(True)).first()
    if c is None:
        return None
    secoes: list[SecaoExportacao] = []
    _append(secoes, _secao("Caso", _sem_markdown(c.enunciado)))
    _append(secoes, _secao("Pergunta", c.pergunta))
    _append(secoes, _secao("Alternativas", itens=[f"{chr(65+i)}. {_texto(v)}" for i, v in enumerate(c.opcoes or [])]))
    correta = c.opcoes[c.resposta_correta] if c.opcoes and 0 <= c.resposta_correta < len(c.opcoes) else None
    _append(secoes, _secao("Resposta e discussão", correta and f"Resposta correta: {correta}", _sem_markdown(c.explicacao)))
    _append(secoes, _secao("Fontes", itens=list(c.source_refs or [])))
    return ConteudoExportavel("caso_clinico", c.slug, c.titulo, c.tema, c.nivel, secoes)


def _titulo_etapa(db: Session, tipo: str, slug: str) -> str:
    mapas = {
        "documento": (Document, "title"), "medicamento": (Drug, "generic_name"),
        "estudo": (ScientificStudy, "title"), "evidencia": (EvidenceRecord, "statement"),
        "caso_clinico": (ClinicalCase, "titulo"), "checklist": (DischargeChecklist, "condicao"),
    }
    if tipo == "calculadora":
        return calc.REGISTRY.get(slug).name if slug in calc.REGISTRY else slug
    par = mapas.get(tipo)
    if not par:
        return slug
    modelo, campo = par
    item = db.query(modelo).filter(modelo.slug == slug).first()
    return _texto(getattr(item, campo, None)) or slug


def _resolver_trilha(db: Session, slug: str) -> ConteudoExportavel | None:
    t = db.query(StudyTrack).filter(StudyTrack.slug == slug, StudyTrack.published.is_(True)).first()
    if t is None:
        return None
    itens = []
    for etapa in t.etapas or []:
        nome = _titulo_etapa(db, etapa.get("item_type", ""), etapa.get("item_slug", ""))
        itens.append(f"{etapa.get('ordem', '')}. {nome} — {etapa.get('por_que', '')}".strip())
    secoes: list[SecaoExportacao] = []
    _append(secoes, _secao("Objetivo", t.objetivo))
    _append(secoes, _secao("Percurso", itens=itens))
    return ConteudoExportavel("trilha", t.slug, t.titulo, t.tema, t.nivel, secoes)


def _resolver_checklist(db: Session, slug: str) -> ConteudoExportavel | None:
    c = db.query(DischargeChecklist).filter(DischargeChecklist.slug == slug, DischargeChecklist.published.is_(True)).first()
    if c is None:
        return None
    itens = []
    for item in c.itens or []:
        if isinstance(item, dict):
            texto = item.get("texto") or item.get("text") or _texto(item)
            sufixo = " [obrigatório]" if item.get("obrigatorio") else ""
            itens.append(f"{texto}{sufixo}")
        else:
            itens.append(_texto(item))
    secoes: list[SecaoExportacao] = []
    _append(secoes, _secao("Resumo", clinical_text_without_internal_overrides(c.resumo)))
    _append(secoes, _secao("Itens", itens=itens))
    _append(secoes, _secao("Fontes", itens=list(c.source_refs or [])))
    return ConteudoExportavel("checklist", c.slug, c.condicao, c.theme, c.scope_type, secoes)


def _resolver_material(db: Session, slug: str) -> ConteudoExportavel | None:
    m = db.query(PatientMaterial).filter(PatientMaterial.slug == slug, PatientMaterial.published.is_(True)).first()
    if m is None:
        return None
    secoes: list[SecaoExportacao] = []
    _append(secoes, _secao("Resumo", m.resumo))
    for secao in m.secoes or []:
        if isinstance(secao, dict):
            _append(secoes, _secao(secao.get("titulo") or "Informação", *(secao.get("paragrafos") or []), itens=secao.get("itens") or []))
    _append(secoes, _secao("Sinais de alerta", itens=list(m.sinais_de_alerta or [])))
    _append(secoes, _secao("Perguntas para a consulta", itens=list(m.perguntas or [])))
    _append(secoes, _secao("Fontes", itens=list(m.fontes or [])))
    return ConteudoExportavel("material_paciente", m.slug, m.titulo, m.tema, m.subtitulo, secoes)


def _resolver_emergencia(db: Session, slug: str) -> ConteudoExportavel | None:
    p = db.query(EmergencyProtocol).filter(EmergencyProtocol.slug == slug, EmergencyProtocol.published.is_(True)).first()
    if p is None:
        return None
    doc = db.query(Document).filter(Document.slug == p.documento_slug, Document.published.is_(True)).first()
    secoes: list[SecaoExportacao] = []
    _append(secoes, _secao("Gatilho de reconhecimento", p.gatilho, destaque="PROTOCOLO DE EMERGÊNCIA"))
    if doc:
        _append(secoes, _secao("Resumo", clinical_text_without_internal_overrides(doc.summary)))
        secoes.extend(_secoes_markdown(doc.body_md))
        _append(secoes, _secao("Referências", itens=list(doc.source_refs or [])))
    if p.relacionados:
        _append(secoes, _secao("Relacionados", itens=list(p.relacionados or [])))
    return ConteudoExportavel("emergencia", p.slug, p.titulo, doc.theme if doc else None, "Modo Emergência", secoes)


def _resolver_galeria(db: Session, slug: str) -> ConteudoExportavel | None:
    g = db.query(GalleryImage).filter(GalleryImage.slug == slug, GalleryImage.published.is_(True)).first()
    if g is None:
        return None
    secoes: list[SecaoExportacao] = []
    _append(secoes, _secao("Achados", g.findings))
    _append(secoes, _secao("Pontos de ensino", g.teaching_points))
    _append(secoes, _secao("Origem e licença", f"{g.source_name} · {g.license}", g.attribution, g.source_url))
    return ConteudoExportavel("galeria", g.slug, g.title, g.theme, g.modality, secoes)


def _resolver_calculadora(slug: str) -> ConteudoExportavel | None:
    c = calc.REGISTRY.get(slug)
    if c is None or c.status != "implementada":
        return None
    campos = []
    for f in c.fields:
        texto = f.label + (f" ({f.unit})" if f.unit else "")
        if f.help:
            texto += f" — {f.help}"
        campos.append(texto)
    secoes: list[SecaoExportacao] = []
    _append(secoes, _secao("Finalidade", c.purpose))
    _append(secoes, _secao("Variáveis", itens=campos))
    _append(secoes, _secao("Referência", c.reference))
    _append(secoes, _secao("Limitações", itens=list(c.limitations or [])))
    _append(secoes, _secao("Resultado individual", "Para exportar um resultado calculado, use 'Gerar documento' dentro da calculadora: o CorVIA recalcula no servidor e não confia em números enviados pelo navegador."))
    return ConteudoExportavel("calculadora", c.slug, c.name, c.theme, c.kind, secoes)


def _resolver_timeline(db: Session, tema: str) -> ConteudoExportavel | None:
    timeline = montar_timeline(db, tema)
    if not timeline.get("marcos"):
        return None
    por_eixo: dict[str, list[str]] = {}
    for marco in timeline["marcos"]:
        refs = [marco.get("fonte") or ""]
        if marco.get("doi"):
            refs.append(f"DOI {marco['doi']}")
        if marco.get("pmid"):
            refs.append(f"PMID {marco['pmid']}")
        por_eixo.setdefault(marco.get("eixo") or "Evolução científica", []).append(
            f"{marco['ano']} — {marco['titulo']} — {marco.get('descricao') or ''} — {' · '.join(x for x in refs if x)}"
        )
    secoes = [SecaoExportacao(eixo, itens=itens) for eixo, itens in por_eixo.items()]
    periodo = ""
    if timeline.get("primeiro_ano") and timeline.get("ultimo_ano"):
        periodo = f"{timeline['primeiro_ano']}–{timeline['ultimo_ano']}"
    return ConteudoExportavel("timeline", tema, f"Timeline de evolução do conhecimento — {tema}", tema, periodo, secoes)


def resolver_conteudo(db: Session, tipo: str, slug: str, *, uf: str | None = None) -> ConteudoExportavel | None:
    tipo = (tipo or "").strip().lower()
    slug = (slug or "").strip()
    if tipo not in TIPOS_EXPORTAVEIS or not slug:
        return None
    if tipo in {"documento", "fluxograma"}:
        return _resolver_documento(db, slug, tipo)
    if tipo == "evidencia": return _resolver_evidencia(db, slug)
    if tipo == "estudo": return _resolver_estudo(db, slug)
    if tipo == "medicamento": return _resolver_medicamento(db, slug, uf)
    if tipo == "exame": return _resolver_exame(db, slug)
    if tipo == "guideline": return _resolver_guideline(db, slug)
    if tipo == "doenca": return _resolver_doenca(db, slug)
    if tipo == "caso_clinico": return _resolver_caso(db, slug)
    if tipo == "trilha": return _resolver_trilha(db, slug)
    if tipo == "checklist": return _resolver_checklist(db, slug)
    if tipo == "material_paciente": return _resolver_material(db, slug)
    if tipo == "emergencia": return _resolver_emergencia(db, slug)
    if tipo == "galeria": return _resolver_galeria(db, slug)
    if tipo == "calculadora": return _resolver_calculadora(slug)
    if tipo == "timeline": return _resolver_timeline(db, slug)
    return None


def _catalog_item(tipo: str, slug: str, titulo: str, tema: str | None, detalhe: str | None = None) -> dict:
    return {"tipo": tipo, "slug": slug, "titulo": titulo, "tema": tema, "detalhe": detalhe, "rotulo_tipo": ROTULOS_TIPO[tipo]}


def catalogo(db: Session, *, q: str | None = None, tipo: str | None = None, slug: str | None = None, limite: int = 120) -> list[dict]:
    """Catálogo pesquisável do construtor de PDF. Só expõe conteúdo elegível.

    Guideline segue a mesma regra da API pública atual (não possui `published`);
    todas as demais frentes de banco exigem `published=True`.
    """
    if tipo and tipo not in TIPOS_EXPORTAVEIS:
        return []
    termo = (q or "").strip().casefold()
    exato = (slug or "").strip()
    saida: list[dict] = []

    def aceita(item: dict) -> bool:
        if tipo and item["tipo"] != tipo:
            return False
        if exato and item["slug"] != exato:
            return False
        if termo and termo not in " ".join(str(item.get(k) or "") for k in ("titulo", "tema", "detalhe", "slug")).casefold():
            return False
        return True

    for d in db.query(Document).filter(Document.published.is_(True)).order_by(Document.title).limit(1200):
        kind = "fluxograma" if d.kind == "fluxograma" else "documento"
        item = _catalog_item(kind, d.slug, d.title, d.theme, d.kind)
        if aceita(item): saida.append(item)
    for e in db.query(EvidenceRecord).filter(EvidenceRecord.published.is_(True)).order_by(EvidenceRecord.theme, EvidenceRecord.year.desc()).limit(2500):
        item = _catalog_item("evidencia", e.slug, e.statement[:180], e.theme, f"{e.society} {e.year} · Classe {e.recommendation_class}/{e.evidence_level}")
        if aceita(item): saida.append(item)
    for s in db.query(ScientificStudy).filter(ScientificStudy.published.is_(True)).order_by(ScientificStudy.year.desc(), ScientificStudy.title).limit(1500):
        item = _catalog_item("estudo", s.slug, s.title, s.theme, f"{s.journal} · {s.year}")
        if aceita(item): saida.append(item)
    for d in db.query(Drug).filter(Drug.published.is_(True)).order_by(Drug.generic_name).limit(800):
        item = _catalog_item("medicamento", d.slug, d.generic_name, "Farmacologia", d.drug_class)
        if aceita(item): saida.append(item)
    for t in db.query(LabTest).filter(LabTest.published.is_(True)).order_by(LabTest.name).limit(800):
        item = _catalog_item("exame", t.slug, t.name, t.theme, t.category)
        if aceita(item): saida.append(item)
    for g in db.query(Guideline).order_by(Guideline.ano.desc(), Guideline.titulo).limit(600):
        item = _catalog_item("guideline", g.slug, g.titulo, g.tema, f"{g.org} · {g.ano}")
        if aceita(item): saida.append(item)
    for d in db.query(SpecialtyDisease).filter(SpecialtyDisease.published.is_(True)).order_by(SpecialtyDisease.name).limit(1000):
        item = _catalog_item("doenca", d.slug, d.name, d.area, d.category)
        if aceita(item): saida.append(item)
    for c in db.query(ClinicalCase).filter(ClinicalCase.published.is_(True)).order_by(ClinicalCase.titulo).limit(1000):
        item = _catalog_item("caso_clinico", c.slug, c.titulo, c.tema, c.nivel)
        if aceita(item): saida.append(item)
    for t in db.query(StudyTrack).filter(StudyTrack.published.is_(True)).order_by(StudyTrack.titulo).limit(800):
        item = _catalog_item("trilha", t.slug, t.titulo, t.tema, t.nivel)
        if aceita(item): saida.append(item)
    for c in db.query(DischargeChecklist).filter(DischargeChecklist.published.is_(True)).order_by(DischargeChecklist.condicao).limit(800):
        item = _catalog_item("checklist", c.slug, c.condicao, c.theme, c.scope_type)
        if aceita(item): saida.append(item)
    for m in db.query(PatientMaterial).filter(PatientMaterial.published.is_(True)).order_by(PatientMaterial.titulo).limit(800):
        item = _catalog_item("material_paciente", m.slug, m.titulo, m.tema, m.subtitulo)
        if aceita(item): saida.append(item)
    for p in db.query(EmergencyProtocol).filter(EmergencyProtocol.published.is_(True)).order_by(EmergencyProtocol.ordem).limit(400):
        item = _catalog_item("emergencia", p.slug, p.titulo, None, p.gatilho)
        if aceita(item): saida.append(item)
    for g in db.query(GalleryImage).filter(GalleryImage.published.is_(True)).order_by(GalleryImage.title).limit(1000):
        item = _catalog_item("galeria", g.slug, g.title, g.theme, g.modality)
        if aceita(item): saida.append(item)
    for c in sorted(calc.REGISTRY.values(), key=lambda item: item.name):
        if c.status != "implementada": continue
        item = _catalog_item("calculadora", c.slug, c.name, c.theme, c.purpose)
        if aceita(item): saida.append(item)

    # Timelines são entidades derivadas, uma por tema disponível. Evita criar
    # uma segunda base narrativa: a exportação chama o mesmo montar_timeline().
    temas_timeline = sorted({
        *[t for (t,) in db.query(EvidenceRecord.theme).filter(EvidenceRecord.published.is_(True)).distinct().all()],
        *[t for (t,) in db.query(ScientificStudy.theme).filter(ScientificStudy.published.is_(True)).distinct().all()],
    })
    for tema_timeline in temas_timeline:
        item = _catalog_item("timeline", tema_timeline, f"Timeline — {tema_timeline}", tema_timeline, "Evolução do conhecimento, investigação e tratamento")
        if aceita(item): saida.append(item)

    saida.sort(key=lambda item: (item["rotulo_tipo"], item["titulo"].casefold()))
    return saida[:max(1, min(limite, 200))]


class DocumentoExportacao(Documento):
    """Documento A4 com marca CorVIA também nas páginas internas."""

    def _cabecalho(self) -> None:
        topo = self.altura - 30
        if logo_disponivel():
            self._logo(self.margem, topo, 70)
            x_texto = self.margem + 82
        else:
            x_texto = self.margem
        self.pdf.texto(x_texto, topo - 12, "CORVIA · CARDIOLOGY SPACES", 7.5, NAVY, negrito=True, espaco_extra=0.7)
        self.pdf.linha(self.margem, self.altura - 58, self.largura - self.margem, self.altura - 58, FIO)
        self.y = self.altura - 78


def _registro_profissional(identidade: dict) -> str:
    conselho, uf = council_display(identidade)
    numero = identidade.get("council_number")
    registro = " ".join(x for x in [conselho, numero] if x)
    if uf:
        registro += f"/{uf}" if registro else uf
    rqe = identidade.get("rqe")
    if rqe:
        registro += f" · RQE {rqe}"
    return registro.strip()


def gerar_pdf(
    itens: list[ConteudoExportavel],
    *,
    user: Any,
    incluir_dados_assinante: bool,
    titulo: str | None = None,
) -> bytes:
    if not itens:
        raise ValueError("Nenhum conteúdo elegível para exportação.")
    identidade = document_identity(user)
    nome = professional_name(identidade) or "Assinante CorVIA"
    titulo_pdf = (titulo or (itens[0].titulo if len(itens) == 1 else "Seleção de conteúdo CorVIA")).strip()[:180]
    documento = DocumentoExportacao(
        titulo=titulo_pdf,
        autor=nome if incluir_dados_assinante else "CorVIA",
        assunto="Conteúdo clínico exportado do CorVIA",
        rodape=f"CorVIA · exportado em {datetime.now(timezone.utc).strftime('%d/%m/%Y')} · conteúdo publicado na plataforma",
    )
    subtitulo = itens[0].tema or ROTULOS_TIPO[itens[0].tipo] if len(itens) == 1 else f"{len(itens)} conteúdos selecionados"
    documento.capa_simples(titulo_pdf, subtitulo, "Exportação de conteúdo")

    if incluir_dados_assinante:
        linhas = [nome]
        registro = _registro_profissional(identidade)
        if registro: linhas.append(registro)
        if identidade.get("specialty"): linhas.append(_texto(identidade["specialty"]))
        linhas.extend(workplace_lines(identidade))
        documento.destaque(" · ".join(linhas), rotulo="Exportado por")

    documento.destaque(
        "Este arquivo reproduz conteúdo publicado no CorVIA na data da exportação. Referências e proveniência acompanham cada seção quando disponíveis. A exportação não cria nem atualiza recomendações clínicas.",
        rotulo="Proveniência",
    )

    for indice, item in enumerate(itens, start=1):
        if len(itens) > 1:
            documento.titulo(f"{indice}. {item.titulo}")
        else:
            documento.titulo(item.titulo)
        metadados = " · ".join(x for x in [ROTULOS_TIPO[item.tipo], item.tema, item.subtitulo] if x)
        if metadados:
            documento.paragrafo(metadados, tamanho=8.8, cor=NEUTRO)
        for secao in item.secoes:
            documento.titulo(secao.titulo)
            if secao.destaque:
                documento.destaque(secao.destaque, rotulo=secao.titulo)
            for paragrafo in secao.paragrafos:
                if paragrafo:
                    documento.paragrafo(_sem_markdown(paragrafo))
            if secao.itens:
                documento.itens([_sem_markdown(item_texto) for item_texto in secao.itens if item_texto])
        if indice < len(itens):
            documento.espaco(12)

    return documento.salvar_bytes()
