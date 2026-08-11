"""Regressão preventiva da mesma classe de bug do incidente de deploy de
11/08/2026 (issue #52, commit `4e8fb339`): `carregar_galeria.py`,
`carregar_exames.py`, `carregar_evidencias.py` e `carregar_estudos.py`
construíam o registro NOVO via `Model(**item)` sem filtrar pelas colunas
reais do modelo — mesmo padrão que derrubou `carregar_drugs.py` em produção.

Nenhum dos quatro tinha, no conteúdo real do repositório, um campo fora do
modelo no momento da correção (auditado explicitamente) — mas o risco
estrutural é idêntico ao de `drugs`, e o custo do filtro é desprezível.
Este arquivo prova que os quatro sobrevivem a uma chave desconhecida no
JSON sem quebrar, com o mesmo cenário mínimo que derrubou `drugs`.
"""
import json

import pytest
from sqlalchemy import text

from app.models.evidence import EvidenceRecord
from app.models.gallery import GalleryImage
from app.models.lab_test import LabTest
from app.models.study import ScientificStudy
from app.services.carregar_estudos import carregar as carregar_estudos
from app.services.carregar_evidencias import carregar as carregar_evidencias
from app.services.carregar_exames import carregar as carregar_exames
from app.services.carregar_galeria import carregar as carregar_galeria

_TABELAS = ("gallery_images", "lab_tests", "evidence_records", "scientific_studies")


@pytest.fixture(autouse=True)
def _limpar(db):
    db.execute(text(f"TRUNCATE {', '.join(_TABELAS)} RESTART IDENTITY CASCADE"))
    db.commit()
    yield


def _escrever_json(tmp_path, nome, registros):
    caminho = tmp_path / nome
    caminho.write_text(json.dumps(registros, ensure_ascii=False), encoding="utf-8")
    return str(caminho)


def test_galeria_registro_novo_com_chave_desconhecida_nao_derruba_a_carga(db, tmp_path):
    # carregar_galeria.py também exige o arquivo de imagem no disco — cria um
    # arquivo vazio ao lado do manifesto, que é o fallback de `_asset_root`
    # quando o volume de produção `/galeria` não existe.
    (tmp_path / "imagem-teste.jpg").write_bytes(b"\xff\xd8\xff")
    caminho = _escrever_json(
        tmp_path,
        "galeria.json",
        [
            {
                "slug": "achado-teste-galeria",
                "title": "Achado de teste",
                "modality": "ECG",
                "theme": "Teste",
                "findings": "Achado descrito para teste.",
                "file_path": "imagem-teste.jpg",
                "source_name": "Fonte de teste",
                "source_url": "https://exemplo.test/imagem",
                "license": "CC0",
                "attribution": "Domínio público, uso de teste",
                "review_status": "revisado",
                "review_note": "Campo de documentação sem coluna em GalleryImage.",
            }
        ],
    )

    resultado = carregar_galeria(caminho)

    assert resultado["novos"] == 1
    assert not resultado["sem_arquivo"]
    registro = db.query(GalleryImage).filter(GalleryImage.slug == "achado-teste-galeria").first()
    assert registro is not None
    assert registro.title == "Achado de teste"


def test_exames_registro_novo_com_chave_desconhecida_nao_derruba_a_carga(db, tmp_path):
    caminho = _escrever_json(
        tmp_path,
        "exames.json",
        [
            {
                "slug": "exame-teste",
                "name": "Exame de teste",
                "category": "laboratorial",
                "what_it_measures": "O que mede, para teste.",
                "indications": "Indicação de teste.",
                "interpretation": "Interpretação de teste.",
                "theme": "Teste",
                "review_status": "revisado",
                "review_note": "Campo de documentação sem coluna em LabTest.",
            }
        ],
    )

    resultado = carregar_exames(caminho)

    assert resultado["novos"] == 1
    registro = db.query(LabTest).filter(LabTest.slug == "exame-teste").first()
    assert registro is not None
    assert registro.name == "Exame de teste"


def test_evidencias_registro_novo_com_chave_desconhecida_nao_derruba_a_carga(db, tmp_path):
    caminho = _escrever_json(
        tmp_path,
        "evidencias.json",
        [
            {
                "slug": "evidencia-teste",
                "statement": "Recomendação de teste.",
                "recommendation_class": "I",
                "evidence_level": "A",
                "society": "SBC",
                "year": 2026,
                "guideline_title": "Diretriz de teste",
                "reference": "Referência de teste",
                "theme": "Teste",
                "review_status": "revisado",
                # `review_note` já é coluna real de EvidenceRecord — a chave
                # genuinamente desconhecida aqui é outra, para provar que o
                # filtro é por coluna, não por lista de nomes conhecidos.
                "campo_que_nao_existe_em_evidence_record": "nunca deveria chegar ao construtor",
            }
        ],
    )

    resultado = carregar_evidencias(caminho)

    assert resultado["novos"] == 1
    registro = db.query(EvidenceRecord).filter(EvidenceRecord.slug == "evidencia-teste").first()
    assert registro is not None
    assert registro.statement == "Recomendação de teste."


def test_estudos_registro_novo_com_chave_desconhecida_nao_derruba_a_carga(db, tmp_path):
    caminho = _escrever_json(
        tmp_path,
        "estudos.json",
        [
            {
                "slug": "estudo-teste",
                "title": "Estudo de teste",
                "study_type": "ensaio_clinico",
                "journal": "Revista de teste",
                "year": 2026,
                "summary": "Resumo de teste.",
                "key_findings": "Achados de teste.",
                "clinical_implications": "Implicação de teste.",
                "theme": "Teste",
                "review_status": "revisado",
                "review_note": "Campo de documentação sem coluna em ScientificStudy.",
            }
        ],
    )

    resultado = carregar_estudos(caminho)

    assert resultado["novos"] == 1
    registro = db.query(ScientificStudy).filter(ScientificStudy.slug == "estudo-teste").first()
    assert registro is not None
    assert registro.title == "Estudo de teste"
