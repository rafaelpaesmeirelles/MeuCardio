"""Decodifica texto de PDF cuja fonte é subset sem /ToUnicode, quando o mapa
glifo->caractere é um deslocamento constante (caso comum em PDF do Oxford
Academic: gid = codigo_ascii - 27).

Uso:  python3 decodifica_cid_offset.py <arquivo_extraido.txt> [offset]

Como funciona: o extrator devolve os trechos cifrados como pares
`caractere + \\x00` (o byte alto do CID). Os trechos legíveis do documento —
texto embutido em figura, por exemplo — não têm esse padrão. Só os pares são
deslocados; o resto do arquivo passa intacto.

Confirmação do offset: no PDF ehaf192 (ESC 2025), a sequência cifrada
`*\\x008\\x00(\\x00` corresponde a `ESC` — 0x2A+27=0x45 (E), 0x38+27=0x53 (S),
0x28+27=0x43 (C). Antes de confiar na saída, rodar com o texto conhecido e
conferir; offset errado produz texto plausível, mas errado.
"""
import re
import sys


def decodificar(bruto: str, offset: int = 27) -> str:
    def troca(m: re.Match) -> str:
        return "".join(chr(ord(c) + offset) for c in m.group(0)[::2])

    return re.sub(r"(?:[^\x00]\x00)+", troca, bruto)


if __name__ == "__main__":
    caminho = sys.argv[1]
    offset = int(sys.argv[2]) if len(sys.argv) > 2 else 27
    bruto = open(caminho, encoding="utf8", errors="replace").read()
    sys.stdout.write(decodificar(bruto, offset))
