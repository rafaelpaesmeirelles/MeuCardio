"""Carrega as trilhas de estudo, validando cada referência.

A validação é o ponto deste carregador. Uma trilha é uma sequência de ponteiros
para conteúdo que já existe — se um ponteiro estiver quebrado, o médico clica e
não chega a lugar nenhum, e a trilha perde a credibilidade inteira por causa de
um slug digitado errado. Por isso: etapa que aponta para item inexistente
**bloqueia a carga daquela trilha**, com o motivo dito.

Uso:
    python -m app.services.carregar_trilhas /trilhas/metadados.json
"""

import json
import sys

from app.core.db import SessionLocal
from app.models.checklist import DischargeChecklist
from app.models.clinical_case import ClinicalCase
from app.models.content import Document
from app.models.drug import Drug
from app.models.evidence import EvidenceRecord
from app.models.study import ScientificStudy
from app.models.study_track import StudyTrack
from app.services.calculators import REGISTRY
from app.services.scientific_loader_safety import combined_review_note, enforce_safe_publication
from app.services.study_track_progress import stage_identity

CAMPOS = {"slug", "titulo", "tema", "objetivo", "nivel", "etapas", "review_status", "revisao"}


def _existe(db, item_type: str, slug: str) -> bool:
    if item_type == "documento":
        return db.query(Document).filter(Document.slug == slug).first() is not None
    if item_type == "medicamento":
        return db.query(Drug).filter(Drug.slug == slug).first() is not None
    if item_type == "estudo":
        return db.query(ScientificStudy).filter(ScientificStudy.slug == slug).first() is not None
    if item_type == "checklist":
        return db.query(DischargeChecklist).filter(DischargeChecklist.slug == slug).first() is not None
    if item_type == "evidencia":
        return db.query(EvidenceRecord).filter(EvidenceRecord.slug == slug).first() is not None
    if item_type == "caso_clinico":
        return db.query(ClinicalCase).filter(ClinicalCase.slug == slug).first() is not None
    if item_type == "calculadora":
        # Calculadoras vivem em código, mas o mesmo registro que alimenta a
        # rota permite validar o slug antes que um link quebrado seja publicado.
        return slug in REGISTRY
    return False


def carregar(caminho_json: str) -> dict:
    trilhas = json.load(open(caminho_json, encoding="utf-8"))
    db = SessionLocal()
    novos = atualizados = 0
    recusadas: list[str] = []
    try:
        for bruto in trilhas:
            item = {k: v for k, v in bruto.items() if k in CAMPOS}
            etapas = item.get("etapas") or []

            quebradas = [
                f"{e.get('item_type')}:{e.get('item_slug')}"
                for e in etapas if not _existe(db, e.get("item_type"), e.get("item_slug"))
            ]
            if quebradas:
                recusadas.append(f"{item.get('slug','?')}: referência inexistente -> {quebradas}")
                continue
            identidades = [
                stage_identity(str(e.get("item_type") or ""), str(e.get("item_slug") or ""))
                for e in etapas
            ]
            duplicadas = sorted({identidade for identidade in identidades if identidades.count(identidade) > 1})
            if duplicadas:
                recusadas.append(
                    f"{item.get('slug','?')}: identidade de etapa duplicada -> {duplicadas}"
                )
                continue
            sem_porque = [e.get("item_slug") for e in etapas if not e.get("por_que")]
            if sem_porque:
                recusadas.append(f"{item['slug']}: etapas sem 'por_que' -> {sem_porque}")
                continue

            item["etapas"] = sorted(etapas, key=lambda e: e.get("ordem", 0))
            existente = db.query(StudyTrack).filter(StudyTrack.slug == item["slug"]).first()
            note = combined_review_note(
                bruto,
                existing=getattr(existente, "revisao", None),
            )
            if note is not None:
                item["revisao"] = note
            if existente:
                for campo, valor in item.items():
                    setattr(existente, campo, valor)
                enforce_safe_publication(existente, bruto, is_new=False)
                atualizados += 1
            else:
                registro = StudyTrack(**item)
                enforce_safe_publication(registro, bruto, is_new=True)
                db.add(registro)
                novos += 1
        db.commit()
    finally:
        db.close()
    resultado = {"novos": novos, "atualizados": atualizados}
    if recusadas:
        resultado["recusadas"] = recusadas
    return resultado


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(1)
    print(json.dumps(carregar(sys.argv[1]), ensure_ascii=False, indent=2))
