"""Contrato do lote "vincular Tudo com Tudo" de 29/08/2026 — ficha
`arritmias-na-gravidez` (área `gravidez`) em doencas/metadados.json.

ACHADO PRINCIPAL DESTE LOTE: a tarefa foi aberta a partir da leitura do
registro-base em doencas/metadados.json, onde o campo
`related_document_slugs` está de fato ausente. Mas o registro efetivamente
servido pela aplicação passa por `load_disease_records`, que aplica
correções aditivas de `doencas/correcoes/*.json` por cima da base. Existe
uma correção pré-existente e já mesclada em `origin/main` —
`doencas/correcoes/zz-release36h-pr663-arritmias-na-gravidez.json`
(mesclada no commit "release: integrar e revisar toda produção científica
das últimas 36h", parte da PR #663 anterior) — que faz `set` de
praticamente todo o registro, incluindo `related_document_slugs` com 7
vínculos, `completeness: completo` e `review_status: revisado`.

Ou seja: a regra "Tudo com Tudo" **já estava satisfeita** no registro
composto antes deste lote começar. Nenhuma correção de conteúdo foi
necessária — editar `related_document_slugs` na base seria inócuo, pois a
correção usa `set` (substituição incondicional da chave) e sobrescreveria
qualquer valor escrito na base na composição final. Este arquivo apenas
trava esse estado em um teste de regressão, para que trabalho futuro não
tente "consertar" algo que já está corrigido.

Os 6 candidatos levantados na tarefa (excluindo intencionalmente qualquer
documento de foco em arritmia FETAL) foram lidos por completo:

- pre-eclampsia-grave-hellp-e-arritmias-supraventriculares-na-gestacao
- arritmias-maternas-desfechos-cardiacos-perinatais-epic-cosmos-2026
- fluxograma-taquiarritmia-na-gestacao-com-instabilidade-hemodinamica
- taquiarritmia-na-gestacao-com-instabilidade-hemodinamica
- fluxograma-taquicardia-ventricular-polimorfica-catecolaminergica-na-gestacao-e-puerperio
- taquicardia-ventricular-polimorfica-catecolaminergica-na-gestacao-e-puerperio

Todos os 6 são centrais em arritmia MATERNA (não fetal) na gestação. 4
deles já estavam entre os 7 vínculos da correção pré-existente (a versão
em prosa de cada par fluxograma/texto-completo). Os 2 fluxogramas
("fluxograma-taquiarritmia-..." e "fluxograma-taquicardia-ventricular-
polimorfica-...") NÃO foram adicionados porque o registro composto já
está no teto de 7 vínculos definido pela regra Tudo com Tudo — adicioná-
los excederia o máximo sem remover nenhum vínculo já revisado e
publicado, o que está fora do escopo deste lote.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.services.disease_manifest import load_disease_records


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOENCAS_PATH = REPOSITORY_ROOT / "doencas/metadados.json"
CORRECAO_PATH = REPOSITORY_ROOT / "doencas/correcoes/zz-release36h-pr663-arritmias-na-gravidez.json"
SLUG = "arritmias-na-gravidez"

PASTAS_NAO_DOCUMENTO = ("Farmacologia", "Calculadoras", "Exames")
TERMOS_TEMA = ("arritmia", "taquicardia", "fibrilação", "flutter", "bradicardia", "qt longo", "cpvt")

VINCULOS_ESPERADOS = {
    "taquiarritmia-na-gestacao-com-instabilidade-hemodinamica",
    "fibrilacao-atrial-de-inicio-na-gestacao-incidencia-causas-e-controle-agudo",
    "bradicardia-sintomatica-e-bloqueio-av-de-alto-grau-na-gestacao",
    "taquicardia-ventricular-polimorfica-catecolaminergica-na-gestacao-e-puerperio",
    "sindrome-do-qt-longo-e-risco-arritmico-no-puerperio",
    "arritmias-maternas-desfechos-cardiacos-perinatais-epic-cosmos-2026",
    "pre-eclampsia-grave-hellp-e-arritmias-supraventriculares-na-gestacao",
}


def _load_doencas() -> dict[str, dict]:
    return {item["slug"]: item for item in load_disease_records(DOENCAS_PATH)}


def _all_document_paths() -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in (REPOSITORY_ROOT / "content").rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        slug = None
        if text.startswith("---"):
            frontmatter = text.split("---", 2)[1]
            match = re.search(r'^slug:\s*["\']?([^"\'\n]+)', frontmatter, re.MULTILINE)
            if match:
                slug = match.group(1).strip()
        result[slug or path.stem] = path
    return result


def test_ficha_continua_existindo_com_mesmo_slug():
    assert SLUG in _load_doencas()


def test_registro_base_nao_tem_related_document_slugs_mas_correcao_ja_existe():
    """Documenta o achado: a base está vazia; a correção pré-existente resolve."""
    base = json.loads(DOENCAS_PATH.read_text(encoding="utf-8"))
    base_item = next(item for item in base if item.get("slug") == SLUG)
    assert "related_document_slugs" not in base_item or not base_item.get("related_document_slugs")

    assert CORRECAO_PATH.exists(), "correção pré-existente pr663 deveria estar versionada em main"
    correcoes = json.loads(CORRECAO_PATH.read_text(encoding="utf-8"))
    patch = next(c for c in correcoes if c.get("slug") == SLUG)
    assert set(patch["set"]["related_document_slugs"]) == VINCULOS_ESPERADOS


def test_marcacao_editorial_preservada():
    item = _load_doencas()[SLUG]
    assert item.get("review_status") == "revisado"
    assert item.get("completeness") == "completo"
    assert item.get("version") == 2


def test_vinculos_tudo_com_tudo_resolvem_e_sao_documentos_narrativos():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()

    related = item.get("related_document_slugs") or []
    assert set(related) == VINCULOS_ESPERADOS
    assert 3 <= len(related) <= 7, "regra Tudo com Tudo pede entre 3 e 7 links"

    nao_resolvidos = [slug for slug in related if slug not in documentos]
    assert nao_resolvidos == [], f"related_document_slugs aponta para documento inexistente: {nao_resolvidos}"

    fora_de_escopo = [
        slug for slug in related
        if any(pasta in str(documentos[slug]) for pasta in PASTAS_NAO_DOCUMENTO)
    ]
    assert fora_de_escopo == [], f"related_document_slugs aponta para fora do escopo permitido: {fora_de_escopo}"

    assert len(related) == len(set(related)), "related_document_slugs contém duplicatas"


def test_related_document_slugs_mencionam_tema():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()
    for slug in item.get("related_document_slugs") or []:
        texto = documentos[slug].read_text(encoding="utf-8", errors="replace").casefold()
        assert any(termo in texto for termo in TERMOS_TEMA), (
            f"{slug}: documento vinculado não menciona arritmia/taquicardia/etc. no texto"
        )


def test_vinculos_sao_foco_materno_nao_fetal():
    """Nenhum dos vínculos é um documento centrado em arritmia FETAL
    (esse cluster pertence a outra frente de trabalho, pediátrica/fetal)."""
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()
    for slug in item.get("related_document_slugs") or []:
        assert "fetal" not in slug, f"{slug}: slug sugere foco fetal, fora de escopo deste lote"
        titulo_linha = documentos[slug].read_text(encoding="utf-8", errors="replace").split("\n", 3)
        cabecalho = "\n".join(titulo_linha[:6]).casefold()
        assert "arritmia fetal" not in cabecalho


def test_teto_de_sete_vinculos_ja_atingido_fluxogramas_nao_adicionados():
    """Os 2 fluxogramas irmãos (mesmo tema em formato de árvore de decisão)
    não entraram porque o registro composto já está no teto de 7 vínculos
    da regra Tudo com Tudo."""
    item = _load_doencas()[SLUG]
    related = set(item.get("related_document_slugs") or [])
    assert len(related) == 7
    assert "fluxograma-taquiarritmia-na-gestacao-com-instabilidade-hemodinamica" not in related
    assert "fluxograma-taquicardia-ventricular-polimorfica-catecolaminergica-na-gestacao-e-puerperio" not in related
