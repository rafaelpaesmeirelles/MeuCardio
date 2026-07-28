"""Extrai o vínculo com a diretriz de origem a partir das `source_refs`.

Pré-requisito da Tarefa 9: hoje a diretriz que embasa cada documento existe
apenas dentro de texto livre. Isso é legível por gente e inconsultável por
código — não dá para perguntar "quem depende da ESC de fibrilação atrial".

Duas decisões que este extrator segue:

1. **Vínculo extraído nasce não confirmado.** A regex acerta muito e erra
   alguma coisa; marcar tudo como verdade criaria o mesmo problema que o
   `review_status` carimbado automaticamente já causou neste projeto. O admin
   confirma pela rota, e só então o vínculo vira base para alerta.
2. **Ausência de diretriz não é defeito.** Os documentos de Farmacologia se
   apoiam em bula aprovada, e ensaio clínico se apoia no próprio artigo. Nenhum
   dos dois tem diretriz de origem, e forçar um vínculo ali seria inventar
   procedência.
"""

import re
import unicodedata

# Ordem importa: a primeira sociedade que casar é a principal do documento.
# ESC vem antes de EACTS e ERS porque as diretrizes conjuntas são publicadas
# sob a ESC e é assim que o cardiologista as procura.
SOCIEDADES = [
    (r'\bESC\b|European Society of Cardiology|Eur Heart J', 'ESC'),
    (r'\bAHA\b|American Heart Association|\bCirculation\b', 'AHA'),
    (r'\bACC\b|American College of Cardiology|J Am Coll Cardiol', 'ACC'),
    (r'\bSBC\b|Sociedade Brasileira de Cardiologia|Arq Bras Cardiol', 'SBC'),
    (r'\bEACTS\b', 'EACTS'),
    (r'\bERS\b|European Respiratory', 'ERS'),
    (r'\bEAS\b', 'EAS'),
    (r'\bSCAI\b', 'SCAI'),
    (r'\bWHO\b|World Health Organization|\bOMS\b', 'OMS'),
]

# Só conta como diretriz o que se anuncia como tal. Sem isto, qualquer artigo
# publicado no Eur Heart J viraria "diretriz da ESC".
MARCA_DIRETRIZ = re.compile(
    r'guideline|diretriz|consensus statement|consenso|expert consensus|focused update|'
    r'position paper|scientific statement', re.I
)

ANO = re.compile(r'\b(19[89]\d|20[0-4]\d)\b')
DOI = re.compile(r'\b(10\.\d{4,9}/[^\s,;)\]]+)')


# Trecho bibliográfico que costuma vir colado ao título e que não identifica a
# diretriz: nome da revista, volume, fascículo e páginas. Sem remover isto, a
# mesma diretriz gera dois slugs — um com a citação e outro sem —, e o alerta
# passa a avisar metade dos documentos que dependem dela.
CITACAO = re.compile(
    r'\b(eur heart j|circulation|j am coll cardiol|arq bras cardiol|lancet|'
    r'n engl j med|europace|eur respir j|bmj)\b.*$', re.I
)


def _slug(org: str, ano: int, titulo: str) -> str:
    titulo = CITACAO.sub(' ', titulo)
    titulo = re.sub(r'\d+\s*\(\d+\)\s*:\s*[\d-]+', ' ', titulo)
    base = unicodedata.normalize('NFKD', titulo).encode('ascii', 'ignore').decode().lower()
    base = re.sub(r'\b(20\d\d|19\d\d)\b', ' ', base)
    base = re.sub(r'\b(esc|aha|acc|sbc|eacts|ers|eas|scai|guidelines?|for|the|of|and|on|management|diagnosis|treatment|update|focused)\b', ' ', base)
    base = re.sub(r'[^a-z0-9]+', '-', base).strip('-')
    return f"{org.lower()}-{ano}-{base[:80]}".strip('-')


def analisar_referencia(ref: str) -> dict | None:
    """Devolve a diretriz descrita por uma referência, ou None se não for uma."""
    if not MARCA_DIRETRIZ.search(ref):
        return None
    # A sociedade principal é a que aparece PRIMEIRO no texto, não a primeira da
    # nossa lista. Numa diretriz conjunta como "2024 ACC/AHA/Multisociety", a
    # ordem do próprio título é quem manda — trocar isso muda como o
    # cardiologista encontra o documento.
    encontrados = [(m.start(), nome) for padrao, nome in SOCIEDADES
                   if (m := re.search(padrao, ref, re.I))]
    if not encontrados:
        return None
    org = min(encontrados)[1]
    anos = [int(a) for a in ANO.findall(ref)]
    if not anos:
        return None
    # O ano da diretriz costuma ser o menor citado: o maior tende a ser o ano da
    # revista quando a publicação impressa saiu no ano seguinte, como em
    # "2021 ESC/EACTS Guidelines ... Eur Heart J. 2022;43(7)".
    ano = min(anos)

    titulo = re.split(r'\s·\s|\s\|\s|\. DOI|\. PMID', ref)[0].strip()
    titulo = re.sub(r'^\s*[-–]\s*', '', titulo)
    # Referência no padrão Vancouver começa pelos autores. Cortar até o "et al."
    # (ou até o ano, quando não há "et al.") evita que a lista de nomes vire o
    # título da diretriz — foi o que aconteceu com a ESC 2024 de fibrilação
    # atrial no primeiro teste, cujo slug saiu com "van-gelder-ic-rienstra-m".
    corte = re.search(r'et al\.\s*', titulo)
    if corte:
        titulo = titulo[corte.end():]
    else:
        inicio_diretriz = re.search(r'\b(19[89]\d|20[0-4]\d)\s+(ESC|AHA|ACC|SBC|EACTS|ERS|EAS|SCAI)', titulo)
        if inicio_diretriz:
            titulo = titulo[inicio_diretriz.start():]
    # A citação bibliográfica também sai do título, não só do slug: ela
    # identifica onde a diretriz foi publicada, não qual diretriz é, e
    # polui a lista que o admin lê para decidir substituições.
    titulo = CITACAO.sub('', titulo).strip().rstrip('.,;')
    titulo = titulo.strip()[:300]

    doi = DOI.search(ref)
    url = re.search(r'https?://\S+', ref)
    return {
        "org": org,
        "ano": ano,
        "titulo": titulo,
        "slug": _slug(org, ano, titulo),
        "doi": doi.group(1).rstrip('.') if doi else None,
        "url": url.group(0).rstrip('.,;)') if url else None,
        "trecho": ref[:500],
    }


def extrair(refs: list[str]) -> list[dict]:
    """Todas as diretrizes distintas descritas numa lista de referências."""
    vistos, saida = set(), []
    for ref in refs or []:
        d = analisar_referencia(ref)
        if d and d["slug"] not in vistos:
            vistos.add(d["slug"])
            saida.append(d)
    return saida
