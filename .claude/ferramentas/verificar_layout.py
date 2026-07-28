"""Confere o layout: texto que sai da caixa da página.

A validação de estrutura diz que o arquivo abre; não diz que está legível.
Aqui cada trecho de texto é reposicionado e medido para ver se cabe onde foi
colocado — é o defeito que só apareceria imprimindo.
"""
import re, sys, zlib
sys.path.insert(0, ".")
from pdf import largura_texto

LARG, ALT, MARGEM = 595.28, 841.89, 62.0
LIM_DIR, LIM_BAIXO, LIM_CIMA = LARG - MARGEM + 1.5, 34.0, ALT - 30.0

def analisar(caminho):
    b = open(caminho, "rb").read()
    problemas, trechos = [], 0
    for fluxo in re.findall(rb"stream\r?\n(.*?)\r?\nendstream", b, re.S):
        try: d = zlib.decompress(fluxo).decode("cp1252", "replace")
        except Exception: continue
        if " Tj" not in d: continue
        for m in re.finditer(
            r"/(F1|FB|FI) ([\d.]+) Tf [\d.]+ [\d.]+ [\d.]+ rg ([\d.-]+) ([\d.-]+) Td \((.*?)\) Tj", d):
            fonte, tam, x, y, txt = m.group(1), float(m.group(2)), float(m.group(3)), float(m.group(4)), m.group(5)
            txt = txt.replace("\\(", "(").replace("\\)", ")").replace("\\\\", "\\")
            trechos += 1
            fim = x + largura_texto(txt, tam, fonte == "FB")
            rotulo = txt[:46] + ("…" if len(txt) > 46 else "")
            if fim > LIM_DIR:
                problemas.append(f"sai {fim-LIM_DIR:5.1f}pt à direita: {rotulo!r}")
            if x < MARGEM - 1.5 and y < ALT - 300:   # capa usa a página inteira
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

for c in sys.argv[1:]:
    n, p = analisar(c)
    print(f"\n{c.split('/')[-1]} — {n} trechos medidos")
    if not p: print("  OK — nada fora da caixa")
    else:
        for x in dict.fromkeys(p): print("  " + x)
