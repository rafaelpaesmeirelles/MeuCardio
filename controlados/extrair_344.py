# -*- coding: utf-8 -*-
"""Extrai as listas da Portaria SVS/MS 344/98 a partir da republicação
consolidada da RDC 999/2025, em PDF oficial da Anvisa.

Regra que governa este extrator: ele **transcreve**, não interpreta. O tipo de
receituário de cada lista sai do subtítulo da própria norma, literal; os adendos
saem verbatim, sem tentativa de virar regra de máquina. Adendo é prosa normativa
com condição de dose, forma farmacêutica e associação — quem transformar isso em
`if` precisa ser humano, e o campo `regras_condicionais` existe para marcar que
o trabalho não foi feito, em vez de fingir que não existe.

Uso:  python3 extrair_344.py <rdc999.txt> <saida.json>
"""
import json
import re
import sys

# Mapa lista -> tipo do SNCR. Cada valor foi lido no subtítulo da própria norma
# (campo `receituario_literal` da saída), não inferido. As listas D2, E e F não
# geram receituário médico e por isso não têm tipo.
TIPO_SNCR = {
    "A1": "NRA", "A2": "NRA", "A3": "NRA",
    "B1": "NRB", "B2": "NRB2",
    "C1": "RCE", "C5": "RCE",
    "C2": "NRR", "C3": "NRT",
    "D1": None, "D2": None, "E": None,
    # F1 a F4 são substâncias PROSCRITAS: não há receituário que as autorize.
    "F1": None, "F2": None, "F3": None, "F4": None,
}
PROSCRITAS = {"E", "F1", "F2", "F3", "F4"}

# Dois formatos de cabeçalho convivem no mesmo PDF: "LISTA - A1" e "LISTA F1 - ".
# Ignorar o segundo faz a lista F inteira virar um bloco só, e as sublistas F2 a
# F4 somem sem erro nenhum — foi o que aconteceu na primeira execução.
CAB = re.compile(r"^\s*LISTA\s*(?:-\s*([A-F]\d?)|([A-F]\d)\s*-)", re.M)
ITEM = re.compile(r"^\s*(\d+)\.\s+(.*)$")
RODAPE = re.compile(r"Anexo I da Portaria|Página \d+|^\s*\d+\s*$", re.I)
# Um item do adendo muda o receituário quando cita outro documento nominalmente.
MUDA_RECEITUARIO = re.compile(r"receita de controle especial|notificação de receita", re.I)


def _limpar(linha: str) -> str:
    return re.sub(r"\s{2,}", " ", linha.strip())


def _substancias(bloco: str) -> list[str]:
    """Lê os itens numerados até o ADENDO. Nomes quebrados em várias linhas são
    remontados: a continuação é a linha seguinte que não abre item novo."""
    itens: dict[int, list[str]] = {}
    atual = None
    for linha in bloco.split("\n"):
        if re.match(r"^\s*ADENDO", linha):
            break
        if RODAPE.search(linha) and not ITEM.match(linha):
            continue
        m = ITEM.match(linha)
        if m:
            atual = int(m.group(1))
            itens.setdefault(atual, []).append(_limpar(m.group(2)))
        elif atual is not None and linha.strip():
            itens[atual].append(_limpar(linha))
    fora = []
    for n in sorted(itens):
        nome = " ".join(p for p in itens[n] if p).strip()
        nome = re.sub(r"\s+ou\s+", " | ", nome)   # sinônimos vêm após "ou"
        if nome:
            fora.append(nome)
    return fora


def _adendo(bloco: str) -> list[str]:
    m = re.search(r"^\s*ADENDO:?\s*$", bloco, re.M)
    if not m:
        return []
    texto = bloco[m.end():]
    itens, atual = [], []
    for linha in texto.split("\n"):
        if RODAPE.search(linha) and not re.match(r"^\s*\d+\)", linha):
            continue
        if re.match(r"^\s*\d+(\.\d+)?\)", linha.strip()):
            if atual:
                itens.append(" ".join(atual))
            atual = [_limpar(linha)]
        elif atual and linha.strip():
            atual.append(_limpar(linha))
    if atual:
        itens.append(" ".join(atual))
    return [i for i in itens if len(i) > 15]


def extrair(caminho_txt: str) -> dict:
    t = open(caminho_txt, encoding="utf-8", errors="replace").read()
    cabecalhos = list(CAB.finditer(t))
    if not cabecalhos:
        raise SystemExit("Nenhum cabeçalho de lista encontrado — PDF mudou de formato.")

    listas = []
    for i, m in enumerate(cabecalhos):
        nome = m.group(1) or m.group(2)
        fim = cabecalhos[i + 1].start() if i + 1 < len(cabecalhos) else len(t)
        bloco = t[m.end():fim]

        titulo = ""
        for linha in bloco.split("\n")[:8]:
            if "LISTA DE" in linha or "LISTA DAS" in linha:
                titulo = _limpar(linha)
                break
        lit = re.search(r"^\s*\((Sujeit[^)]+)\)\s*$", bloco, re.M)
        receituario_literal = f"({lit.group(1)})" if lit else None

        adendo = _adendo(bloco)
        condicionais = [a for a in adendo if MUDA_RECEITUARIO.search(a)]

        listas.append({
            "lista": nome,
            "titulo": titulo,
            "receituario_literal": receituario_literal,
            "tipo_sncr": TIPO_SNCR.get(nome),
            "proscrita": nome in PROSCRITAS,
            "substancias": _substancias(bloco),
            "adendo": adendo,
            "regras_condicionais": condicionais,
            "regras_condicionais_codificadas": False,
        })
    return {
        "fonte": {
            "norma_base": "Portaria SVS/MS nº 344, de 12 de maio de 1998",
            "republicacao_consolidada": "RDC Anvisa nº 999/2025",
            "url": "https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/"
                   "controlados/RDC9992025.pdf",
            "extraido_em": "2026-07-29",
            "metodo": "pdftotext -layout + extrair_344.py (transcrição, sem interpretação)",
            "atualizacoes_posteriores_nao_aplicadas": [
                "RDC 1.011/2026", "RDC 1.021/2026",
            ],
        },
        "aviso": (
            "O tipo de receituário NÃO é função apenas da lista da substância. "
            "Os adendos das listas A1, A2 e B1 rebaixam preparações específicas — "
            "por dose por unidade, forma farmacêutica ou associação — para Receita "
            "de Controle Especial. Ver `regras_condicionais`. Enquanto "
            "`regras_condicionais_codificadas` for falso, a classificação "
            "automática precisa cair para revisão humana nessas listas."
        ),
        "listas": listas,
    }


if __name__ == "__main__":
    dados = extrair(sys.argv[1])
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
        f.write("\n")
    total = sum(len(l["substancias"]) for l in dados["listas"])
    print(f"listas: {len(dados['listas'])} | substâncias: {total}")
    for l in dados["listas"]:
        print(f"  {l['lista']:3} {len(l['substancias']):4} subst. | "
              f"adendo {len(l['adendo']):2} itens | condicionais {len(l['regras_condicionais'])}"
              f" | {l['tipo_sncr'] or '—'}")
