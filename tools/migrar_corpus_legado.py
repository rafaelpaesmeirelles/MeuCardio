#!/usr/bin/env python3
"""Migra o corpus científico do CardioBene 2.2.0 (gerado no GPT/Perplexity)
para o formato de conteúdo desta base.

Os arquivos originais não são Markdown limpo. Cada um traz:
  - um título em `##`;
  - um bloco ```json``` com o conteúdo estruturado de verdade;
  - resíduo de conversa ("sigo o pipeline", "próximos itens serão...");
  - artefatos do Perplexity: marcadores [web:NNN], <span style="display:none">,
    listas de notas de rodapé [^47_1] e separadores <div align="center">⁂</div>.

Este script extrai o JSON, limpa o resíduo, deriva título/tema/referências,
marca o status de revisão e detecta duplicatas — sem inventar conteúdo.
Nada é descartado em silêncio: tudo que não puder ser migrado vai para o
relatório com o motivo.

Uso:
    python tools/migrar_corpus_legado.py <dir_knowledge_legado> [-o content]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

# --------------------------------------------------------------- limpeza ----

RESIDUO = [
    re.compile(r'<span style="display:none">.*?</span>', re.S),
    re.compile(r'<div align="center">.*?</div>', re.S),
    re.compile(r"^\[\^[^\]]+\]:.*$", re.M),          # lista de notas de rodapé
    re.compile(r"\[\^[^\]]+\]"),                      # chamadas de nota
    re.compile(r"\[web:\d+\]"),                       # marcador de busca do Perplexity
    re.compile(r"<br\s*/?>", re.I),
]

# Frases de conversa que sobraram do chat original.
CONVERSA = re.compile(
    r"^.*(sigo o pipeline|m[óo]dulos? conclu[íi]dos?|pr[óo]ximos? itens?|"
    r"pr[óo]ximo bloco|vou seguir|na pr[óo]xima resposta|continuo (a|na) seguir).*$",
    re.I | re.M,
)

TEMA_POR_CATEGORIA = {
    "protocolos": "Protocolos",
    "medicamentos": "Farmacologia",
    "calculadoras": "Calculadoras",
    "estudos": "Estudos e diretrizes",
}
KIND_POR_CATEGORIA = {
    "protocolos": "protocolo",
    "medicamentos": "farmacologia",
    "calculadoras": "calculadora",
    "estudos": "estudo",
}

# Temas clínicos reconhecidos, para reclassificar protocolos por assunto.
TEMAS_CLINICOS = [
    ("Insuficiência cardíaca", ["insuficiencia cardiaca", "icfer", "icfep", "ic aguda", "edema agudo"]),
    ("Fibrilação atrial", ["fibrilacao atrial", " fa ", "af-care", "flutter"]),
    ("Doença coronariana", ["coronarian", "sca", "iam", "infarto", "angina", "dor toracica"]),
    ("Arritmias", ["arritmia", "taquicardia", "bradicardia", "tv ", "fv ", "bav"]),
    ("Dispositivos", ["cdi", "marcapasso", "ressincroniz", "crt", "desfibrilador"]),
    ("Valvopatias", ["valvopatia", "estenose aortica", "insuficiencia mitral", "tavi", "valvar"]),
    ("Hipertensão", ["hipertens"]),
    ("Cardiomiopatias", ["cardiomiopatia", "miocardite", "amiloidose", "sarcoidose"]),
    ("Tromboembolismo", ["tromboembolismo", "tep", "tvp", "trombose"]),
    ("Terapia intensiva", ["choque", "parada cardio", "pcr", "vasopressor", "ecmo"]),
    ("Prevenção e lipídios", ["dislipidemia", "lipid", "estatina", "prevencao", "risco cardiovascular"]),
    ("Pericárdio", ["pericard", "tamponamento"]),
    ("Aorta", ["aorta", "disseccao", "aneurisma"]),
    ("Endocardite", ["endocardite"]),
    ("Síncope", ["sincope"]),
]


def sem_acento(t: str) -> str:
    return unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()


def limpar(texto: str) -> str:
    for padrao in RESIDUO:
        texto = padrao.sub("", texto)
    texto = CONVERSA.sub("", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def slugify(valor: str) -> str:
    valor = re.sub(r"[^\w\s-]", "", sem_acento(valor)).strip()
    return re.sub(r"[\s_-]+", "-", valor)[:180].strip("-")


def tema_clinico(texto: str, padrao: str) -> str:
    alvo = f" {sem_acento(texto)} "
    for tema, chaves in TEMAS_CLINICOS:
        if any(c in alvo for c in chaves):
            return tema
    return padrao


# ------------------------------------------------------------ extração ------

def extrair_json(bruto: str) -> dict | None:
    m = re.search(r"```json\s*(\{.*?\})\s*```", bruto, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except (ValueError, TypeError):
        return None


def titulo_de(dados: dict, arquivo: Path) -> str:
    for chave in ("titulo", "title", "nome_generico", "nome", "protocolo"):
        v = dados.get(chave)
        if isinstance(v, str) and v.strip():
            return v.strip()
    # Cai para o nome do arquivo, removendo prefixos de conversa.
    nome = arquivo.stem.replace("-", " ")
    nome = re.sub(
        r"^(modulo atualizado|banco de medicamentos|protocolo clinico|"
        r"biblioteca cientifica|calculadora s?)\s*",
        "", nome, flags=re.I,
    )
    nome = re.sub(
        r"\s*(dose completa|fecha lacuna anterior|agora completo|completo|"
        r"substitui versao anterior incompleta|complemento ao protocolo \d+|"
        r"completa a versao anterior|parcial)\s*$",
        "", nome, flags=re.I,
    )
    return nome.strip().capitalize() or arquivo.stem


def referencias_de(dados: dict) -> list[str]:
    refs = dados.get("referencias") or dados.get("references") or []
    saida: list[str] = []
    if isinstance(refs, str):
        return [refs.strip()] if refs.strip() else []
    for r in refs:
        if isinstance(r, str):
            saida.append(r.strip())
        elif isinstance(r, dict):
            partes = [
                str(r.get(k)).strip()
                for k in ("titulo", "title", "organizacao", "organization", "ano", "year",
                          "volume", "doi", "pmid", "url")
                if r.get(k)
            ]
            if partes:
                saida.append(" · ".join(partes))
    return [limpar(x) for x in saida if limpar(x)]


def corpo_markdown(dados: dict) -> str:
    """Converte o JSON estruturado em Markdown legível, preservando a ordem."""
    ignorar = {"id", "titulo", "title", "referencias", "references"}
    linhas: list[str] = []
    for chave, valor in dados.items():
        if chave in ignorar or valor in (None, "", [], {}):
            continue
        rotulo = chave.replace("_", " ").strip().capitalize()
        linhas.append(f"## {rotulo}")
        if isinstance(valor, str):
            linhas.append(limpar(valor))
        elif isinstance(valor, list):
            for item in valor:
                if isinstance(item, dict):
                    linhas.append(
                        "- " + "; ".join(
                            f"**{k.replace('_',' ')}**: {limpar(str(v))}" for k, v in item.items()
                        )
                    )
                else:
                    linhas.append(f"- {limpar(str(item))}")
        elif isinstance(valor, dict):
            for k, v in valor.items():
                linhas.append(f"- **{k.replace('_',' ')}**: {limpar(str(v))}")
        else:
            linhas.append(limpar(str(valor)))
        linhas.append("")
    return "\n".join(linhas).strip()


def yaml_lista(itens: list[str]) -> str:
    return "[" + ", ".join(json.dumps(i, ensure_ascii=False) for i in itens) + "]"


# ------------------------------------------------------------ migração ------

def migrar(origem: Path, destino: Path) -> dict:
    arquivos = sorted(origem.rglob("*.md"))
    relatorio: dict = {
        "lidos": len(arquivos),
        "migrados": 0,
        "sem_json": [],
        "duplicatas": [],
        "verificacao_humana": 0,
        "sem_referencias": 0,
        "por_tema": defaultdict(int),
    }
    # slug -> (tamanho_do_corpo, caminho_origem)
    vistos: dict[str, tuple[int, str]] = {}
    pendentes: list[dict] = []

    for arq in arquivos:
        bruto = arq.read_text(encoding="utf-8", errors="replace")
        categoria = arq.parent.name
        dados = extrair_json(bruto)

        if dados is None:
            # Sem bloco JSON: preserva o texto limpo em vez de descartar.
            corpo = limpar(re.sub(r"^##\s*", "# ", bruto, count=1, flags=re.M))
            if len(corpo) < 200:
                relatorio["sem_json"].append(f"{arq.name} (texto curto demais após limpeza)")
                continue
            dados, titulo, refs = {}, titulo_de({}, arq), []
        else:
            titulo = titulo_de(dados, arq)
            refs = referencias_de(dados)
            corpo = corpo_markdown(dados)

        if not corpo:
            relatorio["sem_json"].append(f"{arq.name} (sem conteúdo aproveitável)")
            continue

        precisa_revisao = "VERIFICAÇÃO HUMANA NECESSÁRIA" in bruto.upper()
        slug = slugify(titulo)
        chave = f"{categoria}/{slug}"

        if chave in vistos:
            anterior_tam, anterior_arq = vistos[chave]
            if len(corpo) <= anterior_tam:
                relatorio["duplicatas"].append(
                    f"{arq.name} → descartado, versão menor que {anterior_arq}"
                )
                continue
            relatorio["duplicatas"].append(
                f"{anterior_arq} → substituído pela versão maior em {arq.name}"
            )
            pendentes = [p for p in pendentes if p["chave"] != chave]

        vistos[chave] = (len(corpo), arq.name)

        tema = TEMA_POR_CATEGORIA.get(categoria, "Geral")
        if categoria in ("protocolos", "estudos"):
            tema = tema_clinico(f"{titulo} {corpo[:600]}", tema)

        pendentes.append({
            "chave": chave,
            "slug": slug,
            "titulo": titulo,
            "tema": tema,
            "kind": KIND_POR_CATEGORIA.get(categoria, "modulo"),
            "categoria": categoria,
            "refs": refs,
            "corpo": corpo,
            "revisao": "verificacao_humana_necessaria" if precisa_revisao else "pendente_revisao",
            "origem": str(arq.relative_to(origem)),
        })

    for item in pendentes:
        pasta = destino / item["tema"].replace(" ", "_")
        pasta.mkdir(parents=True, exist_ok=True)
        front = [
            "---",
            f'title: {json.dumps(item["titulo"], ensure_ascii=False)}',
            f'slug: {item["slug"]}',
            f'theme: {json.dumps(item["tema"], ensure_ascii=False)}',
            f'kind: {item["kind"]}',
            f'review_status: {item["revisao"]}',
            f'source_refs: {yaml_lista(item["refs"])}',
            f'legacy_source: {json.dumps(item["origem"], ensure_ascii=False)}',
            "---",
            "",
            f'# {item["titulo"]}',
            "",
            item["corpo"],
            "",
        ]
        (pasta / f'{item["slug"]}.md').write_text("\n".join(front), encoding="utf-8")
        relatorio["migrados"] += 1
        relatorio["por_tema"][item["tema"]] += 1
        if item["revisao"] == "verificacao_humana_necessaria":
            relatorio["verificacao_humana"] += 1
        if not item["refs"]:
            relatorio["sem_referencias"] += 1

    relatorio["por_tema"] = dict(sorted(relatorio["por_tema"].items(), key=lambda x: -x[1]))
    return relatorio


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("origem", type=Path, help="diretório knowledge/ do projeto legado")
    p.add_argument("-o", "--destino", type=Path, default=Path("content"))
    args = p.parse_args()

    if not args.origem.is_dir():
        print(f"Diretório não encontrado: {args.origem}", file=sys.stderr)
        return 1

    r = migrar(args.origem, args.destino)

    print(f"Lidos:    {r['lidos']}")
    print(f"Migrados: {r['migrados']}")
    print(f"Duplicatas resolvidas: {len(r['duplicatas'])}")
    print(f"Descartados: {len(r['sem_json'])}")
    print()
    print("Distribuição por tema:")
    for tema, n in r["por_tema"].items():
        print(f"  {n:4d}  {tema}")
    print()
    print(f"Marcados 'verificação humana necessária': {r['verificacao_humana']}")
    print(f"Sem nenhuma referência bibliográfica:     {r['sem_referencias']}")
    if r["sem_json"]:
        print("\nDescartados:")
        for x in r["sem_json"]:
            print(f"  - {x}")
    if r["duplicatas"]:
        print(f"\nDuplicatas ({len(r['duplicatas'])}):")
        for x in r["duplicatas"][:20]:
            print(f"  - {x}")
        if len(r["duplicatas"]) > 20:
            print(f"  … e mais {len(r['duplicatas']) - 20}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
