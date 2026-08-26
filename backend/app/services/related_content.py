"""Cruzamento de conteúdo entre frentes do ecossistema Corvia, por tema.

Registro da tarefa (Rafael, 08/08/2026 à tarde): "integrar todo o conhecimento/
documentos de cada tema... para que a partir de 1 item, o usuário visualize
tudo que o ecossistema tem sobre esse tópico e acesse o conteúdo que desejar
imediatamente." Ver `CLAUDE.md`, seção "Regra permanente: todo conteúdo novo
precisa nascer com tema" — este módulo é o consumidor direto do campo que essa
regra protege.

**Por que este módulo existe, e não uma query genérica**: as onze frentes de
conteúdo abaixo não compartilham schema, e três detalhes tornam o cruzamento
menos óbvio do que parece:

1. **O nome do campo não é o mesmo em todo lugar.** `documents`,
   `evidence_records`, `scientific_studies`, `gallery_images`, `lab_tests` e
   `discharge_checklists` usam `theme` (inglês); `clinical_cases`,
   `study_tracks` e `patient_materials` usam `tema` (português). Os VALORES
   usam o mesmo vocabulário de 29 temas nos dois casos (conferido por query
   direta em produção, 08/08/2026) — só o nome da coluna diverge. Quem
   adicionar frente nova não deveria precisar redescobrir isso lendo o código
   de todo o resto; está centralizado aqui.
2. **`drugs` (medicamentos) não tem campo de tema — nem `theme` nem `tema`.**
   É a única das doze frentes sem esse dado hoje. Convenção já registrada em
   `CLAUDE.md` ("DIVISÃO DE PRODUÇÃO..."): "medicamentos/metadados.json...
   pareiam naturalmente com Farmacologia". Este módulo usa essa mesma
   convenção, não uma invenção nova: medicamentos só entram no cruzamento
   quando o tema pedido for exatamente `"Farmacologia"`, devolvendo os
   medicamentos publicados mais recentes — não é correspondência por
   palavra-chave dentro do texto do fármaco, é a associação estrutural que o
   projeto já usa em outro lugar.
3. **`emergency_protocols` também não tem tema próprio.** Aponta para um
   `documento_slug`; o tema vem por herança do `Document` referenciado.

Duas anomalias reais de dados já encontradas nesta auditoria (08/08/2026, ver
CLAUDE.md para o detalhe): um `patient_materials` com
`tema = "Doença arterial coronariana"` (o resto da base usa "Doença
coronariana") e um `documents` com `theme = "Choque cardiogênico"` (fora dos
29 temas canônicos). Os dois ficam **invisíveis para este cruzamento** — é
exatamente o efeito que a regra permanente do CLAUDE.md existe para prevenir
daqui para frente. Não corrigidos aqui de propósito (correção de conteúdo é
decisão de conteúdo, fora do escopo desta tarefa de infraestrutura) — ver nota
no CLAUDE.md.

**Não fabrica relação nenhuma**: cada consulta é `campo == tema` (exato, só
`strip()`), item publicado, limite razoável por categoria. Sem busca textual,
sem "parecido com", sem heurística de palavra-chave — a v1 documentada em
CLAUDE.md é deliberadamente simples.
"""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.checklist import DischargeChecklist
from app.models.clinical_case import ClinicalCase
from app.models.content import Document
from app.models.drug import Drug
from app.models.emergency import EmergencyProtocol
from app.models.evidence import EvidenceRecord
from app.models.gallery import GalleryImage
from app.models.lab_test import LabTest
from app.models.patient_material import PatientMaterial
from app.models.study import ScientificStudy
from app.models.study_track import StudyTrack
from app.services import calculators as calc

LIMITE_POR_CATEGORIA = 5

# Tema estrutural sob o qual os medicamentos entram no cruzamento — ver ponto
# 2 da nota de módulo acima. Não é o único tema em que Farmacologia aparece
# nas outras frentes (elas também têm o tema "Farmacologia" naturalmente),
# então isso não cria uma categoria vazia: é o ponto de encontro real.
TEMA_MEDICAMENTOS = "Farmacologia"


@dataclass
class ItemRelacionado:
    tipo: str
    slug: str
    titulo: str
    subtitulo: str | None
    rota: str


def _pular(tipo: str, slug: str, excluir_tipo: str | None, excluir_slug: str | None) -> bool:
    return excluir_tipo == tipo and excluir_slug == slug


def _grupo(tipo: str, rotulo: str, rota_lista: str, itens: list[ItemRelacionado]) -> dict:
    return {
        "tipo": tipo,
        "rotulo": rotulo,
        "rota_lista": rota_lista,
        "itens": [
            {"slug": i.slug, "titulo": i.titulo, "subtitulo": i.subtitulo, "rota": i.rota}
            for i in itens
        ],
    }


def buscar_relacionados(
    db: Session,
    tema: str,
    excluir_tipo: str | None = None,
    excluir_slug: str | None = None,
    limite_por_categoria: int = LIMITE_POR_CATEGORIA,
) -> dict:
    """Devolve, agrupado por tipo, o conteúdo publicado do mesmo tema em todas
    as frentes do ecossistema Corvia — o "Tudo sobre este tema" das páginas de
    detalhe. Nunca lança exceção por tema sem correspondência: cada grupo
    apenas vem com `itens: []`."""

    tema = (tema or "").strip()
    grupos: list[dict] = []

    if not tema:
        return {"tema": tema, "grupos": [], "total": 0}

    # --- documentos e fluxogramas (mesma tabela, categorias separadas) -----
    docs_q = select(Document).where(
        Document.theme == tema, Document.published.is_(True), Document.kind != "fluxograma"
    )
    if excluir_tipo == "documento" and excluir_slug:
        docs_q = docs_q.where(Document.slug != excluir_slug)
    docs = db.execute(
        docs_q.order_by(Document.updated_at.desc()).limit(limite_por_categoria)
    ).scalars().all()
    grupos.append(_grupo(
        "documento", "Documentos e protocolos", "/biblioteca",
        [ItemRelacionado("documento", d.slug, d.title, d.kind, f"/biblioteca/{d.slug}") for d in docs],
    ))

    fluxos_q = select(Document).where(
        Document.theme == tema, Document.published.is_(True), Document.kind == "fluxograma"
    )
    if excluir_tipo == "fluxograma" and excluir_slug:
        fluxos_q = fluxos_q.where(Document.slug != excluir_slug)
    fluxos = db.execute(
        fluxos_q.order_by(Document.updated_at.desc()).limit(limite_por_categoria)
    ).scalars().all()
    grupos.append(_grupo(
        "fluxograma", "Fluxogramas", "/fluxogramas",
        [ItemRelacionado("fluxograma", d.slug, d.title, "Árvore de decisão", f"/biblioteca/{d.slug}") for d in fluxos],
    ))

    # --- evidências ---------------------------------------------------------
    ev_q = select(EvidenceRecord).where(
        EvidenceRecord.theme == tema, EvidenceRecord.published.is_(True)
    )
    if excluir_tipo == "evidencia" and excluir_slug:
        ev_q = ev_q.where(EvidenceRecord.slug != excluir_slug)
    evidencias = db.execute(
        ev_q.order_by(EvidenceRecord.created_at.desc()).limit(limite_por_categoria)
    ).scalars().all()
    grupos.append(_grupo(
        "evidencia", "Evidências", "/evidencias",
        [
            ItemRelacionado(
                "evidencia", e.slug,
                (e.statement[:140] + "…") if len(e.statement) > 140 else e.statement,
                f"Classe {e.recommendation_class} · nível {e.evidence_level} · {e.society} {e.year}",
                f"/evidencias/{e.slug}",
            )
            for e in evidencias
        ],
    ))

    # --- estudos -------------------------------------------------------------
    est_q = select(ScientificStudy).where(
        ScientificStudy.theme == tema, ScientificStudy.published.is_(True)
    )
    if excluir_tipo == "estudo" and excluir_slug:
        est_q = est_q.where(ScientificStudy.slug != excluir_slug)
    estudos = db.execute(
        est_q.order_by(ScientificStudy.created_at.desc()).limit(limite_por_categoria)
    ).scalars().all()
    grupos.append(_grupo(
        "estudo", "Estudos", "/estudos",
        [ItemRelacionado("estudo", s.slug, s.title, f"{s.journal} · {s.year}", f"/estudos/{s.slug}") for s in estudos],
    ))

    # --- medicamentos (via convenção Farmacologia, ver nota de módulo) ------
    medicamentos: list[ItemRelacionado] = []
    if tema == TEMA_MEDICAMENTOS:
        drug_q = select(Drug).where(Drug.published.is_(True))
        if excluir_tipo == "medicamento" and excluir_slug:
            drug_q = drug_q.where(Drug.slug != excluir_slug)
        drogas = db.execute(
            drug_q.order_by(Drug.generic_name).limit(limite_por_categoria)
        ).scalars().all()
        medicamentos = [
            ItemRelacionado("medicamento", d.slug, d.generic_name, d.drug_class, f"/medicamentos?slug={d.slug}")
            for d in drogas
        ]
    grupos.append(_grupo("medicamento", "Medicamentos", "/medicamentos", medicamentos))

    # --- exames ----------------------------------------------------------------
    ex_q = select(LabTest).where(LabTest.theme == tema, LabTest.published.is_(True))
    if excluir_tipo == "exame" and excluir_slug:
        ex_q = ex_q.where(LabTest.slug != excluir_slug)
    exames = db.execute(
        ex_q.order_by(LabTest.name).limit(limite_por_categoria)
    ).scalars().all()
    grupos.append(_grupo(
        "exame", "Exames", "/exames",
        [ItemRelacionado("exame", t.slug, t.name, t.category, f"/exames/{t.slug}") for t in exames],
    ))

    # --- casos clínicos ----------------------------------------------------
    cc_q = select(ClinicalCase).where(ClinicalCase.tema == tema, ClinicalCase.published.is_(True))
    if excluir_tipo == "caso_clinico" and excluir_slug:
        cc_q = cc_q.where(ClinicalCase.slug != excluir_slug)
    casos = db.execute(
        cc_q.order_by(ClinicalCase.created_at.desc()).limit(limite_por_categoria)
    ).scalars().all()
    grupos.append(_grupo(
        "caso_clinico", "Casos clínicos", "/casos-clinicos",
        [ItemRelacionado("caso_clinico", c.slug, c.titulo, c.nivel, f"/casos-clinicos/{c.slug}") for c in casos],
    ))

    # --- trilhas de estudo ---------------------------------------------------
    tr_q = select(StudyTrack).where(StudyTrack.tema == tema, StudyTrack.published.is_(True))
    if excluir_tipo == "trilha" and excluir_slug:
        tr_q = tr_q.where(StudyTrack.slug != excluir_slug)
    trilhas = db.execute(
        tr_q.order_by(StudyTrack.created_at.desc()).limit(limite_por_categoria)
    ).scalars().all()
    grupos.append(_grupo(
        "trilha", "Trilhas de estudo", "/trilhas",
        [ItemRelacionado("trilha", t.slug, t.titulo, t.nivel, f"/trilhas/{t.slug}") for t in trilhas],
    ))

    # --- galeria de imagens --------------------------------------------------
    gal_q = select(GalleryImage).where(GalleryImage.theme == tema, GalleryImage.published.is_(True))
    if excluir_tipo == "galeria" and excluir_slug:
        gal_q = gal_q.where(GalleryImage.slug != excluir_slug)
    imagens = db.execute(
        gal_q.order_by(GalleryImage.created_at.desc()).limit(limite_por_categoria)
    ).scalars().all()
    grupos.append(_grupo(
        "galeria", "Galeria de imagens", "/galeria",
        [ItemRelacionado("galeria", g.slug, g.title, g.modality, f"/galeria/{g.slug}") for g in imagens],
    ))

    # --- calculadoras (registro em memória, não é tabela) --------------------
    calculadoras = [
        ItemRelacionado("calculadora", c.slug, c.name, c.purpose, f"/calculadoras/{c.slug}")
        for c in sorted(calc.REGISTRY.values(), key=lambda c: c.name)
        if c.theme == tema and c.status == "implementada"
        and not _pular("calculadora", c.slug, excluir_tipo, excluir_slug)
    ][:limite_por_categoria]
    grupos.append(_grupo("calculadora", "Calculadoras", "/calculadoras", calculadoras))

    # --- protocolos de emergência (tema herdado do Document referenciado) --
    prot_q = (
        select(EmergencyProtocol, Document.theme)
        .join(Document, Document.slug == EmergencyProtocol.documento_slug)
        .where(Document.theme == tema, EmergencyProtocol.published.is_(True))
    )
    if excluir_tipo == "protocolo_emergencia" and excluir_slug:
        prot_q = prot_q.where(EmergencyProtocol.slug != excluir_slug)
    protocolos = db.execute(
        prot_q.order_by(EmergencyProtocol.ordem)
    ).all()
    grupos.append(_grupo(
        "protocolo_emergencia", "Modo Emergência", "/emergencia",
        [
            ItemRelacionado("protocolo_emergencia", p.slug, p.titulo, p.gatilho, "/emergencia")
            for p, _tema_doc in protocolos[:limite_por_categoria]
        ],
    ))

    # --- checklists de alta --------------------------------------------------
    chk_q = select(DischargeChecklist).where(
        DischargeChecklist.theme == tema, DischargeChecklist.published.is_(True)
    )
    if excluir_tipo == "checklist" and excluir_slug:
        chk_q = chk_q.where(DischargeChecklist.slug != excluir_slug)
    checklists = db.execute(
        chk_q.order_by(DischargeChecklist.condicao).limit(limite_por_categoria)
    ).scalars().all()
    grupos.append(_grupo(
        "checklist", "Checklists de alta", "/checklists",
        [ItemRelacionado("checklist", c.slug, c.condicao, None, "/checklists") for c in checklists],
    ))

    # --- materiais do paciente ------------------------------------------------
    mat_q = select(PatientMaterial).where(
        PatientMaterial.tema == tema, PatientMaterial.published.is_(True)
    )
    if excluir_tipo == "material_paciente" and excluir_slug:
        mat_q = mat_q.where(PatientMaterial.slug != excluir_slug)
    materiais = db.execute(
        mat_q.order_by(PatientMaterial.titulo).limit(limite_por_categoria)
    ).scalars().all()
    grupos.append(_grupo(
        "material_paciente", "Material para o paciente", "/material-paciente",
        [ItemRelacionado("material_paciente", m.slug, m.titulo, m.subtitulo, "/material-paciente") for m in materiais],
    ))

    total = sum(len(g["itens"]) for g in grupos)
    return {"tema": tema, "grupos": grupos, "total": total}
