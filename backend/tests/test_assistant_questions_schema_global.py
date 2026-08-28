from pathlib import Path

from app.services.disease_manifest import load_disease_records


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "doencas" / "metadados.json"


def test_todas_as_perguntas_do_assistente_usam_label_e_nao_text():
    invalidas: list[str] = []
    for disease in load_disease_records(BASE):
        slug = str(disease.get("slug") or "?")
        for index, question in enumerate(disease.get("assistant_questions") or []):
            if not isinstance(question, dict):
                invalidas.append(f"{slug}[{index}]:nao_objeto")
                continue
            label = question.get("label")
            if not isinstance(label, str) or not label.strip():
                invalidas.append(f"{slug}[{index}]:label_ausente")
            if "text" in question:
                invalidas.append(f"{slug}[{index}]:campo_text_legado")
    assert invalidas == [], f"assistant_questions fora do schema canônico: {invalidas}"
