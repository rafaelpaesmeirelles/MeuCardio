"""Confere o layout: texto que sai da caixa da página.

A validação de estrutura diz que o arquivo abre; não diz que está legível.
Aqui cada trecho de texto é reposicionado e medido para ver se cabe onde foi
colocado — é o defeito que só apareceria imprimindo.
"""
import re, sys, zlib
sys.path.insert(0, ".")
from pdf import largura_texto

# O tamanho da página é lido do /MediaBox do próprio arquivo, não fixado aqui:
# a apresentação é paisagem e a versão anterior, com A4 retrato no código,
# acusava 40 falsos positivos num documento correto. Validador que não sabe o
# tamanho da folha não valida enquadramento — inventa erro.
def _pagina(b):
    m = re.search(rb"/MediaBox\s*\[\s*([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)", b)
    if not m:
        return 595.28, 841.89
    return float(m.group(3)) - float(m.group(1)), float(m.group(4)) - float(m.group(2))

def analisar(caminho, margem=None):
    b = open(caminho, "rb").read()
    LARG, ALT = _pagina(b)
    # Margem deduzida do próprio documento: é o menor x em que algo é escrito,
    # descontando o recuo de marcador. Assim o mesmo validador serve para
    # retrato e paisagem sem precisar saber o layout de cada um.
    MARGEM = margem if margem is not None else _margem_observada(b)
    LIM_DIR, LIM_BAIXO, LIM_CIMA = LARG - MARGEM + 1.5, 20.0, ALT - 20.0
    problemas, trechos = [], 0
    for fluxo in re.findall(rb"stream\r?\n(.*?)\r?\nendstream", b, re.S):
        try: d = zlib.decompress(fluxo).decode("cp1252", "replace")
        except Exception: continue
        if " Tj" not in d: continue
        # `Tc` é estado que persiste entre blocos de texto: medir sem ele
        # deixou passar um defeito real, em que um rótulo com espaçamento
        # alargava todo o texto seguinte da página.
        tc_atual = 0.0
        for m in re.finditer(
            r"([\d.-]+) Tc|/(F1|FB|FI) ([\d.]+) Tf [\d.]+ [\d.]+ [\d.]+ rg ([\d.-]+) ([\d.-]+) Td \((.*?)\) Tj", d):
            if m.group(1) is not None:
                tc_atual = float(m.group(1)); continue
            fonte, tam, x, y, txt = m.group(2), float(m.group(3)), float(m.group(4)), float(m.group(5)), m.group(6)
            txt = txt.replace("\\(", "(").replace("\\)", ")").replace("\\\\", "\\")
            trechos += 1
            fim = x + largura_texto(txt, tam, fonte == "FB") + tc_atual * len(txt)
            rotulo = txt[:46] + ("…" if len(txt) > 46 else "")
            if fim > LIM_DIR:
                problemas.append(f"sai {fim-LIM_DIR:5.1f}pt à direita: {rotulo!r}")
            if x < MARGEM - 1.5 and y < ALT - 0.45 * ALT:   # capa usa a página inteira
                problemas.append(f"sai {MARGEM-x:5.1f}pt à esquerda: {rotulo!r}")
            if y < LIM_BAIXO:
                problemas.append(f"abaixo do rodapé (y={y:.0f}): {rotulo!r}")
            if y > LIM_CIMA:
                problemas.append(f"acima do topo (y={y:.0f}): {rotulo!r}")
        # Dois textos diferentes na mesma coordenada = sobreposição ilegível.
        # Foi assim que apareceu o cabeçalho desenhado duas vezes na abertura
        # de capítulo, com o nome da seção anterior por baixo do novo.
        vistos = {}
        for m in re.finditer(r"([\d.-]+) ([\d.-]+) Td \((.*?)\) Tj", d):
            chave = (round(float(m.group(1)), 1), round(float(m.group(2)), 1))
            if chave in vistos and vistos[chave] != m.group(3):
                problemas.append(f"sobreposto em {chave}: {vistos[chave][:28]!r} / {m.group(3)[:28]!r}")
            vistos[chave] = m.group(3)
    return trechos, problemas

def _margem_observada(b):
    xs = []
    for fluxo in re.findall(rb"stream\r?\n(.*?)\r?\nendstream", b, re.S):
        try:
            d = zlib.decompress(fluxo).decode("cp1252", "replace")
        except Exception:
            continue
        xs += [float(v) for v in re.findall(r"([\d.-]+) [\d.-]+ Td \(", d)]
    return min(xs) if xs else 56.0


for c in sys.argv[1:]:
    n, p = analisar(c)
    print(f"\n{c.split('/')[-1]} — {n} trechos medidos")
    if not p: print("  OK — nada fora da caixa")
    else:
        for x in dict.fromkeys(p): print("  " + x)
