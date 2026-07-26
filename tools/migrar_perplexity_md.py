#!/usr/bin/env python3
"""Extrai módulos de um arquivo Markdown único exportado do Perplexity/GPT
(formato "## Módulo — Título" + bloco ```json```) e funde com o `content/`
já existente, mantendo sempre a versão mais completa de cada documento.

Diferenças em relação a `migrar_corpus_legado.py`:
  - a entrada é um único arquivo grande, não uma pasta com um arquivo por módulo;
  - cabeçalhos vêm em três variantes: "## Módulo —", "## Módulo NOVO —",
    "## Módulo ATUALIZADO —";
  - alguns blocos JSON são uma lista (ex.: duas calculadoras no mesmo módulo) —
    cada item da lista vira um documento próprio;
  - a fusão compara com o `content/` já em disco, não só dentro do próprio lote.

Uso:
    python tools/migrar_perplexity_md.py <arquivo.md> -o content
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

CABECALHO = re.compile(r"^## Módulo(?: NOVO| ATUALIZADO)? ?—\s*(.+)$", re.M)

RESIDUO = [
    re.compile(r'<span style="display:none">.*?</span>', re.S),
    re.compile(r'<div align="center">.*?</div>', re.S),
    re.compile(r"^\[\^[^\]]+\]:.*$", re.M),
    re.compile(r"\[\^[^\]]+\]"),
    re.compile(r"\[web:\d+\]"),
    re.compile(r"<br\s*/?>", re.I),
    re.compile(r'<img[^>]*/?>'),
]
CONVERSA = re.compile(
    r"^.*(sigo o pipeline|m[óo]dulos? conclu[íi]dos?|pr[óo]ximos? itens?|"
    r"pr[óo]ximo bloco|entrego agora|entrego .*m[óo]dulos?|vou seguir|"
    r"marco natural de conclus[ãa]o|pr[óo]xima sugest[ãa]o|dois m[óo]dulos completos|"
    r"quatro m[óo]dulos simult[âa]neos).*$",
    re.I | re.M,
)

CATEGORIA_POR_PREFIXO = [
    (re.compile(r"^Banco de Medicamentos", re.I), "medicamentos"),
    (re.compile(r"^(Protocolo|Classifica[cç][ãa]o)", re.I), "protocolos"),
    (re.compile(r"^Calculadora", re.I), "calculadoras"),
    (re.compile(r"^Biblioteca Cient[íi]fica", re.I), "estudos"),
    (re.compile(r"^Escore\b", re.I), "calculadoras"),
    (re.compile(r"^Abla[cç][ãa]o", re.I), "protocolos"),
]
KIND_POR_CATEGORIA = {
    "protocolos": "protocolo", "medicamentos": "farmacologia",
    "calculadoras": "calculadora", "estudos": "estudo",
}
TEMA_POR_CATEGORIA = {
    "medicamentos": "Farmacologia", "calculadoras": "Calculadoras", "estudos": "Estudos e diretrizes",
}

# Ordem importa: vence o primeiro tema cujo termo aparecer. Temas estreitos e
# de vocabulário exclusivo (Pericárdio, Cardio-oncologia, Endocardite...) vêm
# antes dos temas amplos (Doença coronariana, Prevenção e lipídios...), porque
# palavras como "coronarian" ou "lipid" aparecem de passagem em quase qualquer
# texto de cardiologia e gerariam falso positivo se checadas primeiro.
TEMAS_CLINICOS = [
    ("Pericárdio", ["pericard", "tamponamento"]),
    ("Cardio-oncologia", ["cardio-oncologia", "cardiooncologia", "cardiotoxicidade",
                          "quimioterapia", "radioterapia"]),
    ("Endocardite", ["endocardite"]),
    ("Síncope", ["sincope"]),
    ("Febre reumática", ["febre reumatica", "cardiopatia reumatica"]),
    ("Cardiopatias congênitas", ["cardiopatia congenita"]),
    ("Gravidez", ["gestacao e doenca", "gravidez e doenca", "cardiopatia na gestacao", "puerperio"]),
    ("Saúde mental e cardiologia", ["saude mental e"]),
    ("Perioperatório", ["pre-operatoria", "perioperatorio", "avaliacao cardiovascular pre-operatoria"]),
    ("Hipertensão pulmonar", ["hipertensao pulmonar"]),
    ("Dispositivos", ["cdi ", "marcapasso", "ressincroniz", " crt", "desfibrilador", "cardiodesfibrilador"]),
    ("Diabetes e cardiologia", ["diabetes e doenca cardiovascular", "diabetes mellitus e doenca"]),
    ("Aorta e doença arterial periférica", ["disseccao de aorta", "aneurisma de aorta",
                                            "doenca arterial periferica", " paad"]),
    ("Tromboembolismo", ["tromboembolismo", " tep ", " tvp ", "trombose venosa"]),
    ("Valvopatias", ["valvopatia", "doenca valvar", "estenose aortica", "insuficiencia mitral",
                     "insuficiencia aortica", "prolapso mitral", "protese valvar", "tavi",
                     "regurgitacao valvar", "regurgitacao mitral", "regurgitacao aortica",
                     "regurgitacao tricuspide"]),
    # "valvar" sozinho foi removido de propósito: aparece dentro de "FA não valvar"
    # (= non-valvular), que é o oposto de valvopatia — um falso positivo real,
    # encontrado no estudo ROCKET-AF durante a curadoria.
    ("Fibrilação atrial", ["fibrilacao atrial", "af-care", " fa ", "flutter atrial"]),
    ("Cardiomiopatias", ["cardiomiopatia", "miocardite", "amiloidose", "sarcoidose"]),
    ("Insuficiência cardíaca", ["insuficiencia cardiaca", "icfer", "icfep", "ic aguda", "edema agudo"]),
    ("Terapia intensiva", ["choque cardiogenico", "parada cardio", " pcr ", "suporte circulatorio mecanico", "ecmo"]),
    ("Arritmias", ["arritmia ventricular", "taquicardia", "bradicardia", " tv ", " fv ", "bav", "morte subita"]),
    ("Hipertensão", ["hipertensao arterial", "hipertensao resistente", "emergencia hipertensiva"]),
    ("Prevenção e lipídios", ["dislipidemia", "hipercolesterolemia", "pcsk9", "prevencao cardiovascular primaria"]),
    ("Doença coronariana", ["coronarian", " sca ", "sindrome coronariana", "infarto", "angina", "dor toracica"]),
]


def sem_acento(t: str) -> str:
    return unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()


def limpar(texto: str) -> str:
    for p in RESIDUO:
        texto = p.sub("", texto)
    texto = CONVERSA.sub("", texto)
    return re.sub(r"\n{3,}", "\n\n", texto).strip()


def slugify(v: str) -> str:
    v = re.sub(r"[^\w\s-]", "", sem_acento(v)).strip()
    return re.sub(r"[\s_-]+", "-", v)[:180].strip("-")


def limpar_titulo(bruto: str) -> str:
    t = bruto.strip()
    for cat_re, _ in CATEGORIA_POR_PREFIXO:
        t = cat_re.sub("", t).strip(" :—-")
    t = re.sub(
        r"\s*\((item(?:ns)? [\d,\- ]+|parcial|completo|completa|dose completa[^)]*|"
        r"substitui[^)]*|fecha lacuna[^)]*|agora completo|v2|dados completos?|"
        r"an[aá]lise completa)\)\s*$",
        "", t, flags=re.I,
    ).strip()
    return t or bruto.strip()


def categoria_do_titulo(titulo_bruto: str) -> str | None:
    for cat_re, cat in CATEGORIA_POR_PREFIXO:
        if cat_re.match(titulo_bruto.strip()):
            return cat
    return None


def categoria_do_item(item: dict) -> str | None:
    """Classifica pelo formato dos campos do JSON — mais confiável que o
    título quando o cabeçalho do módulo (ex.: 'Módulo ATUALIZADO — Nome do
    Fármaco') não repete o prefixo de categoria."""
    chaves = set(item.keys())
    if chaves & {"nome_generico", "classe", "mecanismo_acao", "apresentacoes", "apresentacao"}:
        return "medicamentos"
    if chaves & {"formula", "variaveis", "interpretacao"}:
        return "calculadoras"
    if chaves & {"organizacao", "citacao", "pmid", "doi"} and "resumo" in chaves:
        return "estudos"
    return None


def tema_clinico(titulo: str, padrao: str, corpo: str = "") -> str:
    """Classifica priorizando o título: uma palavra-chave que aparece só de
    passagem no corpo (ex.: 'síncope' citada como complicação) não deve
    vencer o assunto que está literalmente no título do documento."""
    alvo_titulo = f" {sem_acento(titulo)} "
    for tema, chaves in TEMAS_CLINICOS:
        if any(c in alvo_titulo for c in chaves):
            return tema
    if corpo:
        alvo_corpo = f" {sem_acento(corpo)} "
        for tema, chaves in TEMAS_CLINICOS:
            if any(c in alvo_corpo for c in chaves):
                return tema
    return padrao


def referencias_de(dados: dict) -> list[str]:
    refs = dados.get("referencias") or dados.get("references") or []
    saida: list[str] = []
    if isinstance(refs, str):
        refs = [refs]
    for r in refs:
        if isinstance(r, str):
            saida.append(limpar(r))
        elif isinstance(r, dict):
            partes = [
                str(r.get(k)).strip() for k in
                ("titulo", "title", "organizacao", "organization", "ano", "year", "volume",
                 "doi", "pmid", "url")
                if r.get(k)
            ]
            if partes:
                saida.append(" · ".join(partes))
    return [x for x in saida if x]


def titulo_de(dados: dict, fallback: str) -> str:
    for chave in ("titulo", "title", "nome", "nome_generico"):
        v = dados.get(chave)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return fallback


def corpo_markdown(dados: dict) -> str:
    ignorar = {"id", "titulo", "title", "nome", "referencias", "references"}
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
                    linhas.append("- " + "; ".join(
                        f"**{k.replace('_',' ')}**: {limpar(str(v))}" for k, v in item.items()
                    ))
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


def extrair_modulos(texto: str) -> list[dict]:
    partes = re.split(r"(^## Módulo(?: NOVO| ATUALIZADO)? ?—.*$)", texto, flags=re.M)
    modulos = []
    for i in range(1, len(partes), 2):
        cabecalho = CABECALHO.match(partes[i].strip())
        titulo_bruto = cabecalho.group(1).strip() if cabecalho else partes[i].strip()
        corpo_bruto = partes[i + 1] if i + 1 < len(partes) else ""
        blocos = re.findall(r"```json\s*(.*?)```", corpo_bruto, re.S)
        modulos.append({
            "titulo_bruto": titulo_bruto,
            "blocos_json": blocos,
            "verificacao": "VERIFICAÇÃO HUMANA NECESSÁRIA" in corpo_bruto.upper(),
            "posicao": i,
        })
    return modulos


def migrar(origem: Path, destino: Path) -> dict:
    texto = origem.read_text(encoding="utf-8")
    modulos = extrair_modulos(texto)

    relatorio = {
        "lidos": len(modulos), "novos": 0, "atualizados": 0, "mantidos": 0,
        "sem_json": [], "json_invalido": [], "por_tema": {},
        "verificacao_humana": 0, "sem_referencias": 0,
    }
    por_tema: dict[str, int] = {}
    existentes_maiores: dict[str, tuple[int, Path]] = {}

    candidatos: list[dict] = []
    for mod in modulos:
        if not mod["blocos_json"]:
            relatorio["sem_json"].append(mod["titulo_bruto"])
            continue

        categoria_titulo = categoria_do_titulo(mod["titulo_bruto"])
        titulo_limpo = limpar_titulo(mod["titulo_bruto"])

        itens_json: list[dict] = []
        for bloco in mod["blocos_json"]:
            try:
                d = json.loads(bloco)
            except (ValueError, TypeError):
                relatorio["json_invalido"].append(mod["titulo_bruto"])
                continue
            itens_json.extend(d if isinstance(d, list) else [d])

        for item in itens_json:
            if not isinstance(item, dict):
                continue
            # O formato dos campos manda mais que o título: um módulo "ATUALIZADO —
            # Sacubitril/Valsartana" não repete o prefixo "Banco de Medicamentos",
            # mas o JSON tem nome_generico/classe/mecanismo_acao, que entrega a categoria.
            categoria = categoria_do_item(item) or categoria_titulo or "protocolos"
            titulo_item = titulo_de(item, titulo_limpo)
            corpo = corpo_markdown(item)
            if not corpo:
                continue
            refs = referencias_de(item)
            tema = TEMA_POR_CATEGORIA.get(categoria)
            if tema is None:
                tema = tema_clinico(titulo_item, "Geral", corpo[:800])
            candidatos.append({
                "slug": slugify(titulo_item), "titulo": titulo_item, "tema": tema,
                "kind": KIND_POR_CATEGORIA.get(categoria, "modulo"), "refs": refs,
                "corpo": corpo, "verificacao": mod["verificacao"],
                "origem": mod["titulo_bruto"],
            })

    # dedup dentro do próprio lote: mantém o maior por (tema, slug)
    melhores: dict[str, dict] = {}
    for c in candidatos:
        chave = f"{c['tema']}/{c['slug']}"
        atual = melhores.get(chave)
        if atual is None or len(c["corpo"]) > len(atual["corpo"]):
            melhores[chave] = c

    for chave, c in melhores.items():
        pasta = destino / c["tema"].replace(" ", "_")
        pasta.mkdir(parents=True, exist_ok=True)
        arq = pasta / f"{c['slug']}.md"

        if arq.exists():
            corpo_existente = arq.read_text(encoding="utf-8")
            if len(corpo_existente) >= len(c["corpo"]) + 200:
                # o arquivo em disco já tem front matter; a comparação de tamanho
                # com folga de 200 caracteres evita trocar por diferença de ruído.
                relatorio["mantidos"] += 1
                continue
            relatorio["atualizados"] += 1
        else:
            relatorio["novos"] += 1

        revisao = "verificacao_humana_necessaria" if c["verificacao"] else "pendente_revisao"
        front = [
            "---",
            f'title: {json.dumps(c["titulo"], ensure_ascii=False)}',
            f'slug: {c["slug"]}',
            f'theme: {json.dumps(c["tema"], ensure_ascii=False)}',
            f'kind: {c["kind"]}',
            f'review_status: {revisao}',
            f'source_refs: {yaml_lista(c["refs"])}',
            f'legacy_source: {json.dumps(c["origem"], ensure_ascii=False)}',
            "---", "", f'# {c["titulo"]}', "", c["corpo"], "",
        ]
        arq.write_text("\n".join(front), encoding="utf-8")

        por_tema[c["tema"]] = por_tema.get(c["tema"], 0) + 1
        if revisao == "verificacao_humana_necessaria":
            relatorio["verificacao_humana"] += 1
        if not c["refs"]:
            relatorio["sem_referencias"] += 1

    relatorio["por_tema"] = dict(sorted(por_tema.items(), key=lambda x: -x[1]))
    relatorio["documentos_finais"] = len(melhores)
    return relatorio


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("origem", type=Path)
    p.add_argument("-o", "--destino", type=Path, default=Path("content"))
    args = p.parse_args()
    if not args.origem.is_file():
        print(f"Arquivo não encontrado: {args.origem}", file=sys.stderr)
        return 1

    r = migrar(args.origem, args.destino)
    print(f"Módulos lidos no arquivo:     {r['lidos']}")
    print(f"Sem bloco JSON (descartados): {len(r['sem_json'])}")
    print(f"JSON inválido (descartados):  {len(r['json_invalido'])}")
    print(f"Documentos únicos extraídos:  {r['documentos_finais']}")
    print(f"  novos:       {r['novos']}")
    print(f"  atualizados: {r['atualizados']} (substituíram versão menor já em content/)")
    print(f"  mantidos:    {r['mantidos']} (o que já estava em content/ era maior ou igual)")
    print()
    print("Por tema (apenas novos/atualizados nesta execução):")
    for tema, n in r["por_tema"].items():
        print(f"  {n:4d}  {tema}")
    print()
    print(f"Marcados 'verificação humana necessária': {r['verificacao_humana']}")
    print(f"Sem nenhuma referência bibliográfica:     {r['sem_referencias']}")
    if r["sem_json"]:
        print(f"\nSem bloco JSON ({len(r['sem_json'])}):")
        for t in r["sem_json"]:
            print(f"  - {t}")
    if r["json_invalido"]:
        print(f"\nJSON inválido ({len(r['json_invalido'])}):")
        for t in r["json_invalido"]:
            print(f"  - {t}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
