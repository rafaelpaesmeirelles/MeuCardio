"""Extrai a tabela `drugs` de volta a partir dos documentos de content/Farmacologia.

Por que este script existe: a seção Medicamentos nasceu vazia porque o
`popular_drugs.py` lê `knowledge/medicamentos/*.md`, formato do ZIP original do
projeto que não existe mais no servidor nem no histórico do git. Mas a conversão
para Markdown preservou a estrutura muito melhor do que se supunha — 99 dos 100
documentos mantêm "## Nome generico", "## Classe" e "## Mecanismo acao", 97 têm
seção de dose e 88 usam o padrão de bullet `- **chave**: valor`. Dá para
reconstruir os campos estruturados a partir daí.

Duas regras que este extrator segue sem exceção:

1. **Campo ausente no Markdown fica vazio.** Nada é inferido, deduzido de outro
   campo ou preenchido com valor "típico" da classe. Um extrator que adivinha
   produz exatamente o tipo de dado sem procedência que a Fase B passou semanas
   removendo.
2. **Três campos nunca são preenchidos aqui**, por decisão registrada no próprio
   modelo: `half_life_hours` (exige escolha de um valor representativo por quem
   revisa), `sbp_reduction_mmhg`/`dbp_reduction_mmhg` (exigem fonte específica) e
   `commercial_presentations` (dado comercial que só vale vindo de bula/ANVISA).

O resultado sai como JSON no formato que `carregar_drugs.py` já consome, e nasce
com `review_status: pendente_revisao` — conteúdo antigo, ainda não conferido
contra fonte.
"""

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

# Mapa de prefixo de seção -> campo do modelo. A ordem importa: o primeiro
# prefixo que casar vence, então prefixos mais específicos vêm antes.
# Casamento é por prefixo porque os 100 documentos têm 200+ cabeçalhos distintos
# ("Dose", "Dose e administracao", "Dose — ICP", "Dose titulacao"...), quase
# todos variações dos mesmos poucos conceitos.
MAPA = [
    ("nome generico", "generic_name"),
    ("nomes comerciais", "brand_names"),
    ("classe", "drug_class"),
    ("mecanismo", "mechanism"),
    ("apresentac", "presentations"),
    ("ajuste renal", "renal_adjustment"),
    ("ajuste hepatico", "hepatic_adjustment"),
    ("ajuste em disfuncao hepatica", "hepatic_adjustment"),
    ("dose", "dosing"),
    ("contraindicac", "contraindications"),
    ("interac", "interactions"),
    ("monitorizac", "monitoring"),
    ("gravidez", "pregnancy"),
    ("gestacao", "pregnancy"),
    ("toxicidade embriofetal", "pregnancy"),
    ("lactacao", "lactation"),
    ("evidencia", "outcomes"),
    ("indicac", "indications"),
    ("efeitos adversos", "adverse_effects"),
]

LISTAS = {"brand_names", "presentations", "contraindications", "interactions",
          "monitoring", "indications", "adverse_effects"}
TEXTOS = {"generic_name", "drug_class", "mechanism", "renal_adjustment",
          "hepatic_adjustment", "pregnancy", "lactation"}


def _sem_acento(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().strip()


def _campo_de(titulo: str) -> str | None:
    t = _sem_acento(titulo)
    for prefixo, campo in MAPA:
        if t.startswith(prefixo):
            return campo
    return None


def _secoes(corpo: str) -> list[tuple[str, str]]:
    partes = re.split(r"^## (.+)$", corpo, flags=re.M)[1:]
    return [(partes[i].strip(), partes[i + 1].strip()) for i in range(0, len(partes) - 1, 2)]


def _bullets(texto: str) -> dict[str, str]:
    """Extrai o padrão `- **chave**: valor` usado nas seções de dose."""
    return {k.strip(): v.strip() for k, v in re.findall(r"^- \*\*(.+?)\*\*:\s*(.+)$", texto, re.M)}


def _itens(texto: str) -> list[str]:
    """Bullets simples viram lista; prosa vira um item só — dividir prosa por
    pontuação produziria fragmentos sem sentido clínico."""
    itens = [m.strip() for m in re.findall(r"^-\s+(?!\*\*)(.+)$", texto, re.M)]
    if itens:
        return itens
    limpo = re.sub(r"\s+", " ", texto).strip()
    return [limpo] if limpo else []


def extrair(pasta: str = "content/Farmacologia") -> tuple[list[dict], dict]:
    fármacos, sem_mapeamento, falhas = [], Counter(), []

    for md in sorted(Path(pasta).glob("*.md")):
        bruto = md.read_text(encoding="utf-8")
        fm = re.match(r"^---\n(.*?)\n---\n(.*)$", bruto, re.S)
        if not fm:
            falhas.append(f"{md.name}: sem front matter")
            continue
        meta, corpo = fm.group(1), fm.group(2)

        def campo_fm(nome, padrao=""):
            m = re.search(rf'^{nome}:\s*"?(.*?)"?\s*$', meta, re.M)
            return m.group(1).strip() if m else padrao

        slug = campo_fm("slug")
        titulo = campo_fm("title")
        if not slug:
            falhas.append(f"{md.name}: sem slug")
            continue

        d: dict = {"slug": slug, "review_status": "pendente_revisao"}
        dosing: dict = {}
        outcomes: dict = {}
        notes: dict = {}

        for cabecalho, texto in _secoes(corpo):
            campo = _campo_de(cabecalho)
            if campo is None:
                # Nada curado é descartado: o que não tem campo próprio vira
                # nota com o título de origem como chave.
                sem_mapeamento[cabecalho] += 1
                notes[cabecalho] = re.sub(r"\s+", " ", texto)
                continue
            if campo == "dosing":
                achados = _bullets(texto)
                if achados:
                    dosing.update(achados)
                else:
                    dosing[_sem_acento(cabecalho).replace(" ", "_")] = re.sub(r"\s+", " ", texto)
            elif campo == "outcomes":
                outcomes[cabecalho] = re.sub(r"\s+", " ", texto)
            elif campo in LISTAS:
                d.setdefault(campo, [])
                d[campo] += _itens(texto)
            elif campo in TEXTOS:
                # Seções repetidas do mesmo campo (ex.: "Contraindicacoes" e
                # "Contraindicacoes absolutas") são concatenadas, não sobrescritas.
                novo = re.sub(r"\s+", " ", texto).strip()
                d[campo] = f"{d[campo]} {novo}".strip() if d.get(campo) else novo

        if dosing:
            d["dosing"] = dosing
        if outcomes:
            d["outcomes"] = outcomes
        if notes:
            d["notes"] = notes

        # `brand_names` costuma vir como uma linha com marcas separadas por vírgula.
        if d.get("brand_names"):
            marcas = []
            for linha in d["brand_names"]:
                marcas += [p.strip() for p in re.split(r"[,;]", linha) if p.strip()]
            d["brand_names"] = marcas

        # Campos obrigatórios do modelo: sem eles a linha não pode ser criada.
        if not d.get("generic_name"):
            d["generic_name"] = titulo or slug.replace("-", " ").title()
        if not d.get("drug_class"):
            falhas.append(f"{md.name}: sem classe — não extraído")
            continue

        # A procedência do documento de origem vira referência do fármaco.
        refs = campo_fm("source_refs")
        if refs:
            try:
                d["references"] = json.loads(refs) if refs.startswith("[") else [refs]
            except Exception:
                d["references"] = [refs]

        fármacos.append(d)

    preenchimento = Counter()
    for f in fármacos:
        for k, v in f.items():
            if v not in (None, "", [], {}):
                preenchimento[k] += 1

    return fármacos, {
        "extraidos": len(fármacos),
        "falhas": falhas,
        "preenchimento": dict(preenchimento),
        "secoes_sem_mapeamento": sem_mapeamento.most_common(),
    }


if __name__ == "__main__":
    import sys

    destino = sys.argv[1] if len(sys.argv) > 1 else "drugs_data.json"
    dados, relatorio = extrair()
    Path(destino).write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(relatorio, ensure_ascii=False, indent=2))
