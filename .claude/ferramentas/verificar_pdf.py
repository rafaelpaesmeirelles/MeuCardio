"""Confere um PDF relendo o arquivo do zero, sem usar o gerador.

O gerador não pode ser sua própria prova: se ele calcula um deslocamento
errado, calcula errado nos dois lados. Aqui o arquivo é lido como um leitor de
PDF leria — tabela xref, resolução de objeto, descompressão de fluxo.
"""
import re, sys, zlib

def verificar(caminho):
    b = open(caminho, "rb").read()
    erros, notas = [], []

    if not b.startswith(b"%PDF-"): erros.append("sem cabeçalho %PDF")
    if not b.rstrip().endswith(b"%%EOF"): erros.append("sem %%EOF")

    m = re.search(rb"startxref\s+(\d+)", b)
    if not m: return ["sem startxref"], []
    inicio = int(m.group(1))
    if b[inicio:inicio+4] != b"xref": erros.append("startxref não aponta para 'xref'")

    cab = re.match(rb"xref\s+(\d+)\s+(\d+)\s+", b[inicio:])
    total = int(cab.group(2))
    corpo = b[inicio + cab.end():]
    entradas = re.findall(rb"(\d{10}) (\d{5}) ([nf])", corpo[:20*total])
    if len(entradas) != total: erros.append(f"xref: {len(entradas)} entradas, esperado {total}")

    objetos = {}
    for i, (off, _, tipo) in enumerate(entradas):
        if tipo == b"f": continue
        pos = int(off)
        esperado = f"{i} 0 obj".encode()
        if b[pos:pos+len(esperado)] != esperado:
            erros.append(f"obj {i}: xref aponta para {b[pos:pos+22]!r}")
        else:
            fim = b.find(b"\nendobj", pos)
            objetos[i] = b[pos+len(esperado):fim]

    tr = b[b.rfind(b"trailer"):]
    raiz = int(re.search(rb"/Root (\d+)", tr).group(1))
    if b"/Catalog" not in objetos.get(raiz, b""): erros.append("/Root não é /Catalog")
    npages = int(re.search(rb"/Pages (\d+)", objetos[raiz]).group(1))
    pages = objetos.get(npages, b"")
    if b"/Type /Pages" not in pages: erros.append(f"obj {npages} não é /Pages")
    count = int(re.search(rb"/Count (\d+)", pages).group(1))
    kids = re.findall(rb"(\d+) 0 R", re.search(rb"/Kids \[(.*?)\]", pages, re.S).group(1))
    if len(kids) != count: erros.append(f"/Count {count} != {len(kids)} kids")

    # Todo fluxo tem de descomprimir e o /Length tem de bater com o real.
    texto_total, fluxos = 0, 0
    for i, corpo_obj in objetos.items():
        # `stream` tem de ser a palavra-chave que abre o fluxo, não qualquer
        # ocorrência: o titulo "rastreamento" contem a substring e fazia o
        # validador tratar o objeto /Info como se fosse um fluxo.
        if not re.search(rb">>\s*stream\r?\n", corpo_obj): continue
        fluxos += 1
        ini = re.search(rb">>\s*stream\r?\n", corpo_obj).end()
        fim = corpo_obj.rfind(b"endstream")
        dados = corpo_obj[ini:fim].strip(b"\r\n")
        declarado = int(re.search(rb"/Length (\d+)", corpo_obj).group(1))
        if declarado != len(dados):
            erros.append(f"obj {i}: /Length {declarado} != {len(dados)} reais")
        if b"/FlateDecode" in corpo_obj:
            try:
                d = zlib.decompress(dados)
                texto_total += len(re.findall(rb"\(.*?\) Tj", d))
            except Exception as e:
                erros.append(f"obj {i}: fluxo não descomprime ({e})")

    # Toda página tem de referenciar os recursos que usa.
    for k in kids:
        pg = objetos[int(k)]
        for ref in re.findall(rb"/(?:F1|FB|FI|Logo) (\d+) 0 R", pg):
            if int(ref) not in objetos: erros.append(f"página {k}: recurso {ref} não existe")

    notas = [f"{count} páginas", f"{len(objetos)} objetos", f"{fluxos} fluxos",
             f"{texto_total} trechos de texto"]
    return erros, notas

for c in sys.argv[1:]:
    erros, notas = verificar(c)
    print(f"\n{c.split('/')[-1]}")
    print("  " + "  ·  ".join(notas))
    print("  OK — estrutura íntegra" if not erros else "\n".join("  ERRO " + e for e in erros))
