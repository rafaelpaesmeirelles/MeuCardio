"""RAG sobre a base científica institucional.

Diferença em relação à versão 2.2.0 do projeto: lá o contexto era montado
despejando os 20 primeiros protocolos, 30 medicamentos e 30 documentos da
biblioteca **independentemente da pergunta**, truncando por número de
caracteres. Com 164 documentos isso enche a janela com material irrelevante e
corta justamente o que importa.

Aqui a recuperação é dirigida pela pergunta e combina dois sinais:
  - semântico: embeddings dos trechos, distância de cosseno via pgvector;
  - léxico: full-text em português já existente na tabela `documents`.

As listas são fundidas por Reciprocal Rank Fusion, que dispensa normalizar
escores de escalas diferentes e é robusta quando um dos buscadores falha —
útil aqui, porque sigla clínica (CHA2DS2-VASc, ARNI, CRT-D) costuma ir mal
em embedding e muito bem em busca léxica.
"""

from __future__ import annotations

import json
import re

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.content import Document
from app.models.rag import AIConversation, AIMessage, DocumentChunk
from app.services.ia.provedor import obter_provedor, obter_provedor_embeddings

MAX_CHARS = 1400
MIN_CHARS = 200


def dividir(markdown: str) -> list[tuple[str | None, str]]:
    """Divide por seção `##`, mantendo o título junto do texto.

    O corpus migrado é fortemente seccionado (cada campo do JSON virou um `##`),
    então a seção é a unidade natural: cortar por número fixo de caracteres
    separaria dose de via de administração, por exemplo.
    """
    partes: list[tuple[str | None, str]] = []
    titulo_atual: str | None = None
    buffer: list[str] = []

    def descarregar() -> None:
        corpo = "\n".join(buffer).strip()
        if not corpo:
            return
        if len(corpo) < MIN_CHARS and partes:
            titulo_ant, corpo_ant = partes[-1]
            cabecalho = f"\n\n## {titulo_atual}\n" if titulo_atual else "\n\n"
            partes[-1] = (titulo_ant, f"{corpo_ant}{cabecalho}{corpo}")
        else:
            partes.append((titulo_atual, corpo))

    for linha in markdown.splitlines():
        if linha.startswith("## "):
            descarregar()
            titulo_atual = linha[3:].strip()
            buffer = []
        elif linha.startswith("# "):
            continue  # o título do documento já vem no metadado
        else:
            buffer.append(linha)
    descarregar()

    final: list[tuple[str | None, str]] = []
    for titulo, corpo in partes:
        if len(corpo) <= MAX_CHARS:
            final.append((titulo, corpo))
            continue
        atual = ""
        for paragrafo in corpo.split("\n\n"):
            # Parágrafo isolado maior que o teto: quebra dura por sentença,
            # senão o trecho passa do limite do modelo de embedding.
            while len(paragrafo) > MAX_CHARS:
                corte = paragrafo.rfind(". ", 0, MAX_CHARS)
                corte = corte + 1 if corte > MIN_CHARS else MAX_CHARS
                if atual:
                    final.append((titulo, atual.strip()))
                    atual = ""
                final.append((titulo, paragrafo[:corte].strip()))
                paragrafo = paragrafo[corte:].lstrip()
            if atual and len(atual) + len(paragrafo) > MAX_CHARS:
                final.append((titulo, atual.strip()))
                atual = paragrafo
            else:
                atual = f"{atual}\n\n{paragrafo}" if atual else paragrafo
        if atual.strip():
            final.append((titulo, atual.strip()))

    # Trechos minúsculos não sustentam recuperação: junta ao vizinho.
    compactado: list[tuple[str | None, str]] = []
    for titulo, corpo in final:
        if len(corpo) < MIN_CHARS and compactado:
            t_ant, c_ant = compactado[-1]
            if len(c_ant) + len(corpo) <= MAX_CHARS:
                compactado[-1] = (t_ant, f"{c_ant}\n\n{corpo}")
                continue
        compactado.append((titulo, corpo))
    return compactado


def indexar_documento(db: Session, doc: Document, provedor=None) -> int:
    provedor = provedor or obter_provedor_embeddings()
    db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()

    pedacos = dividir(doc.body_md)
    if not pedacos:
        db.commit()
        return 0

    # O título do documento entra em cada trecho: sem isso, um trecho "## Dose"
    # perde a informação de qual fármaco é.
    textos = [f"{doc.title}\n{t or ''}\n{c}".strip() for t, c in pedacos]

    vetores: list[list[float]] = []
    for i in range(0, len(textos), 64):  # respeita o limite de lote da API
        vetores.extend(provedor.embeddings(textos[i : i + 64]))

    for ordem, ((titulo, corpo), vetor) in enumerate(zip(pedacos, vetores)):
        db.add(DocumentChunk(
            document_id=doc.id, ordem=ordem, titulo_secao=titulo,
            conteudo=corpo, embedding=vetor, tokens_aprox=len(corpo) // 4,
        ))
    db.commit()
    return len(pedacos)


def indexar_tudo(db: Session, apenas_pendentes: bool = True) -> dict:
    """Indexa em lote. Só documentos PUBLICADOS entram no índice.

    O filtro por `published` aqui é defesa em profundidade: `recuperar()` já não
    devolve trecho de documento não publicado, mas manter o retido fora do índice
    evita gastar embedding com o que não pode ser servido e fecha a porta na
    origem. Documento publicado depois é pego na chamada seguinte, porque
    `apenas_pendentes` seleciona quem ainda não tem trecho — o fluxo de trabalho
    (publicar e então indexar) continua funcionando sem mudança.

    `indexar_documento()` NÃO recebeu esse filtro de propósito: ele é chamado
    diretamente para reindexar um documento específico cujo corpo mudou, e quem
    chama já sabe o que está fazendo.
    """
    provedor = obter_provedor_embeddings()
    q = db.query(Document).filter(Document.published.is_(True))
    if apenas_pendentes:
        q = q.filter(~Document.id.in_(select(DocumentChunk.document_id).distinct()))
    docs = q.all()
    total = sum(indexar_documento(db, d, provedor) for d in docs)
    return {"documentos": len(docs), "trechos": total}


# A metade léxica da busca híbrida precisa do MESMO filtro de `published` que a
# semântica — sem ele, bastaria a pergunta casar por texto para um documento
# retido voltar ao contexto da IA, mesmo com o lado vetorial já filtrado.
SQL_LEXICO = text("""
SELECT c.id AS chunk_id
FROM documents d
JOIN document_chunks c ON c.document_id = d.id
WHERE d.published = true
  AND d.search_vector @@ plainto_tsquery('portuguese', :q)
ORDER BY ts_rank(d.search_vector, plainto_tsquery('portuguese', :q)) DESC, c.ordem ASC
LIMIT :limite
""")


def _rrf(listas: list[list[int]], k: int = 60) -> list[int]:
    """Reciprocal Rank Fusion: soma 1/(k + posição) de cada lista."""
    escore: dict[int, float] = {}
    for lista in listas:
        for posicao, item in enumerate(lista):
            escore[item] = escore.get(item, 0.0) + 1.0 / (k + posicao + 1)
    return [i for i, _ in sorted(escore.items(), key=lambda x: -x[1])]


def recuperar(db: Session, pergunta: str, temas: list[str] | None = None) -> list[dict]:
    limite = settings.ai_top_k * 3
    vetor = obter_provedor_embeddings().embeddings([pergunta])[0]

    # O join com Document é INCONDICIONAL, e não só quando há filtro por tema:
    # é por ele que passa o `published`. Antes de 31/07/2026 o join só existia
    # no caminho com `temas`, então uma pergunta sem tema recuperava trechos de
    # documento não publicado — conteúdo retido esperando aval chegava à IA.
    consulta = (
        select(DocumentChunk.id)
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(Document.published.is_(True))
    )
    if temas:
        consulta = consulta.where(Document.theme.in_(temas))
    consulta = consulta.order_by(DocumentChunk.embedding.cosine_distance(vetor)).limit(limite)
    semanticos = [r[0] for r in db.execute(consulta).all()]
    lexicos = [
        r.chunk_id for r in db.execute(SQL_LEXICO, {"q": pergunta, "limite": limite}).mappings()
    ]

    ordenados = _rrf([semanticos, lexicos])[: settings.ai_top_k]
    if not ordenados:
        return []

    linhas = db.execute(
        select(DocumentChunk, Document)
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(DocumentChunk.id.in_(ordenados))
    ).all()
    posicao = {cid: i for i, cid in enumerate(ordenados)}
    linhas = sorted(linhas, key=lambda x: posicao[x[0].id])

    return [{
        "slug": doc.slug, "titulo": doc.title, "tema": doc.theme,
        "secao": chunk.titulo_secao, "conteudo": chunk.conteudo,
        "review_status": doc.review_status,
        # `gaps` é o campo que de fato marca incerteza: o importador o preenche
        # com o texto literal `VERIFICAÇÃO HUMANA NECESSÁRIA` encontrado no
        # corpo do documento. Sem trazê-lo até aqui, `montar_contexto` não tem
        # como avisar o modelo de que a fonte carrega ponto não conferido.
        "gaps": list(doc.gaps or []),
    } for chunk, doc in linhas]


def montar_contexto(trechos: list[dict]) -> tuple[str, list[dict]]:
    """Devolve o texto do contexto e a lista de fontes realmente usadas."""
    blocos: list[str] = []
    fontes: dict[str, dict] = {}
    tamanho = 0

    for i, t in enumerate(trechos, start=1):
        cabecalho = f"[F{i}] {t['titulo']}"
        if t["secao"]:
            cabecalho += f" — {t['secao']}"
        # O aviso sai de `gaps`, não de `review_status`. Esta linha comparava
        # `review_status` com "verificacao_humana_necessaria", valor que NUNCA
        # existiu no vocabulário de `documents.review_status` — ele só tem
        # `pendente_revisao` e `revisado`. A string vem do domínio das
        # calculadoras, onde é status de cálculo. Resultado: o aviso jamais
        # disparou, e a IA citava documento com marcação explícita de
        # verificação sem alertar ninguém. Medido em 29/07/2026: 38 documentos
        # com `gaps` preenchido, zero com aquele `review_status`.
        if t.get("gaps"):
            cabecalho += ("  (ATENÇÃO: este documento tem ponto declarado como "
                          "VERIFICAÇÃO HUMANA NECESSÁRIA — não apresente o dado "
                          "correspondente como confirmado)")
        bloco = f"{cabecalho}\n{t['conteudo']}"
        if tamanho + len(bloco) > settings.ai_max_context_chars:
            break
        blocos.append(bloco)
        tamanho += len(bloco)
        fontes.setdefault(t["slug"], {
            "referencia": f"F{i}", "slug": t["slug"], "titulo": t["titulo"],
            "tema": t["tema"], "review_status": t["review_status"],
            # Campo aditivo: permite que a lista de fontes mostre ao médico que
            # aquela fonte tem ponto não conferido, sem depender de o modelo
            # repetir o aviso na resposta. Inerte até o frontend consumi-lo.
            "gaps": t.get("gaps") or [],
        })
    return "\n\n---\n\n".join(blocos), list(fontes.values())


CPF = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
TELEFONE = re.compile(r"\b\(?\d{2}\)?\s?9?\d{4}[-\s]?\d{4}\b")
CARTAO_SUS = re.compile(r"\b\d{15}\b")
EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")


def identificadores_encontrados(texto: str) -> list[str]:
    """Detecta identificadores por formato, não por palavra solta.

    A versão 2.2.0 bloqueava a simples presença da palavra "prontuário", o que
    impede perguntas legítimas sobre o próprio Round. Aqui o critério é o
    padrão do dado.
    """
    achados = []
    for padrao, nome in ((CPF, "CPF"), (TELEFONE, "telefone"),
                         (CARTAO_SUS, "cartão SUS"), (EMAIL, "e-mail")):
        if padrao.search(texto):
            achados.append(nome)
    return achados


PROMPT_SISTEMA = """Você é o assistente clínico da Corvia.

Você tem à disposição uma ferramenta de busca na internet (web_search). Use-a como usaria \
em uma sessão normal do Claude — por conta própria, sem esperar o usuário pedir: sempre que \
o CONTEXTO INSTITUCIONAL e a LITERATURA PÚBLICA (PubMed) fornecidos não cobrirem a pergunta, \
ou quando informação atual, prática ou de caráter geral (por exemplo, novidade regulatória, \
mudança recente de bula, disponibilidade de um medicamento, notícia médica) puder ajudar a \
responder melhor. Não é uma ferramenta de último recurso — é parte normal de como você \
responde.

Como responder:
1. Baseie a resposta no CONTEXTO INSTITUCIONAL fornecido e cite os trechos usados pelo \
marcador correspondente, como [F1] ou [F3].
2. Se houver uma seção "LITERATURA PÚBLICA (PubMed/NCBI)" no contexto, você pode citá-la \
com o marcador [PM1], [PM2] etc. — deixe sempre claro que é uma fonte externa, pública, \
não parte da base institucional revisada.
3. Quando usar a busca na internet, cite o que dela vier com o marcador [W1], [W2] etc. \
— também fonte externa, não institucional. Nunca misture [F#], [PM#] e [W#] como se fossem \
a mesma coisa: cada marcador tem procedência própria e o leitor precisa poder distinguir.
4. Quando nem o contexto institucional, nem o PubMed, nem a busca na internet sustentarem \
a resposta, diga isso com todas as letras e separe claramente conhecimento geral de \
cardiologia do que consta em qualquer uma das três fontes.
5. Nunca invente dose, classe de recomendação, nível de evidência, desfecho de estudo, \
DOI ou referência. Não havendo o dado em nenhuma fonte, escreva: não consta nas fontes \
consultadas.
6. Se um trecho vier marcado como pendente de verificação humana, sinalize isso ao usar \
aquela informação.
7. Não peça nem repita identificadores de paciente.
8. Em instabilidade hemodinâmica ou emergência, oriente avaliação imediata à beira do \
leito e o protocolo local antes de qualquer detalhamento.
9. Escreva em português do Brasil, técnico e direto, sem repetir a pergunta.

Encerre com: "Apoio à decisão — não substitui julgamento clínico, bula e diretriz vigente."
"""


PROMPT_CASO = """Você é o assistente clínico da Corvia, ajudando um médico a conduzir um caso.

Você recebeu os dados estruturados de um paciente internado. Sua tarefa é produzir uma análise
de apoio à decisão completa, SEM nunca afirmar um diagnóstico como definitivo — sempre como
hipótese a ser confirmada pelo médico responsável.

Responda em português, em EXATAMENTE três seções, cada uma começando com o marcador abaixo
em uma linha própria (respeite a ortografia exata dos marcadores):

###HIPOTESES###
Para cada hipótese diagnóstica relevante (normalmente 3 a 6, não force número fixo):
- Nome da hipótese e por que ela encaixa no quadro apresentado (achados a favor).
- Achados que ainda faltam ou que pesam contra, se houver.
- Classifique implicitamente por probabilidade (mais provável primeiro), mas destaque
  separadamente, ao final da seção, qualquer diagnóstico grave/fatal que não pode ser perdido
  mesmo com probabilidade baixa ("não pode perder: ...").
- Se o quadro sugerir instabilidade ou emergência, diga isso já na PRIMEIRA linha da seção,
  antes de qualquer hipótese.

###INVESTIGACAO###
Organize os exames sugeridos em duas categorias, com a justificativa de cada exame (o que ele
ajuda a confirmar ou excluir, e de qual hipótese):
- "Urgente/imediato": exames que mudam conduta nas próximas horas.
- "Complementar": exames que ajudam a completar a investigação, sem urgência.
Não peça exame que os dados do caso já mostram ter sido feito (verifique os exames já
listados antes de sugerir).

###TRATAMENTO###
Para as hipóteses mais prováveis, considerações terapêuticas organizadas por:
- Medidas imediatas/suporte (se aplicável ao quadro).
- Classes de medicamento e por que se aplicam a esta hipótese específica (mecanismo/racional).
- Pontos de monitorização e sinais de alerta que indicariam necessidade de escalonar a conduta
  ou reavaliar o diagnóstico.
NUNCA prescreva dose específica sem que ela esteja explicitamente no CONTEXTO INSTITUCIONAL
fornecido — se a dose não constar no contexto, diga "consultar posologia na bula/protocolo",
não invente o número.

Regras que valem para as três seções:
- Baseie-se no CONTEXTO INSTITUCIONAL fornecido sempre que houver correspondência, citando
  o marcador [F1], [F2] etc. Quando não houver, use conhecimento geral de cardiologia e
  diga isso com todas as letras — não force uma citação que não existe.
- Se houver uma seção "LITERATURA PÚBLICA (PubMed/NCBI)", pode citá-la com [PM1], [PM2] etc.,
  sempre deixando claro que é fonte externa, pública, não institucional.
- Nunca invente dose, classe de recomendação, nível de evidência, valor de exame ou dado
  que o paciente não tem registrado no caso.
- Seja específico e clinicamente útil — evite generalidades vagas tipo "investigar conforme
  protocolo"; diga qual exame, qual medicamento, qual classe, com o racional.
- Nunca decida por internação, alta ou conduta definitiva — isso é sempre do médico.
"""


def _resumo_caso(patient) -> str:
    """Monta o resumo clínico enviado à IA. De propósito, NUNCA inclui nome,
    iniciais, número de prontuário, leito ou data de nascimento — só idade
    em anos (calculada) e sexo, que são clinicamente relevantes e não
    identificam o paciente sozinhos."""
    from datetime import date as _date

    partes = []
    if patient.birth_date:
        idade = _date.today().year - patient.birth_date.year
        partes.append(f"Idade: {idade} anos")
    if patient.sex:
        partes.append(f"Sexo: {'masculino' if patient.sex == 'M' else 'feminino' if patient.sex == 'F' else patient.sex}")
    if patient.chief_complaint:
        partes.append(f"Queixa principal: {patient.chief_complaint}")
    if patient.anamnesis:
        partes.append(f"Anamnese: {patient.anamnesis}")
    if patient.physical_exam:
        partes.append(f"Exame físico geral: {patient.physical_exam}")
    if patient.cardiac_exam:
        ce = patient.cardiac_exam
        campos_legiveis = {
            "ritmo": "Ritmo", "bulhas": "Bulhas", "b3": "B3", "b4": "B4",
            "sopro": "Sopro", "sopro_detalhes": "Detalhes do sopro", "ictus": "Ictus cordis",
            "turgencia_jugular": "Turgência jugular", "edema_mmii": "Edema de MMII",
            "pulsos_perifericos": "Pulsos periféricos", "perfusao_periferica": "Perfusão periférica",
        }
        ce_legivel = {k: ("presente" if v is True else "ausente" if v is False else v)
                      for k, v in ce.items()}
        ce_texto = "; ".join(f"{campos_legiveis.get(k, k)}: {v}" for k, v in ce_legivel.items() if v not in (None, ""))
        if ce_texto:
            partes.append(f"Exame físico cardiológico: {ce_texto}")
    if patient.vital_signs:
        sv = ", ".join(f"{k}: {v}" for k, v in patient.vital_signs.items())
        partes.append(f"Sinais vitais: {sv}")
    if patient.labs:
        lb = ", ".join(f"{k}: {v}" for k, v in patient.labs.items())
        partes.append(f"Exames laboratoriais: {lb}")
    if patient.imaging:
        partes.append(f"Achados de imagem: {patient.imaging}")
    if patient.diagnostic_hypothesis:
        partes.append(f"Hipóteses já aventadas pela equipe: {', '.join(patient.diagnostic_hypothesis)}")
    problemas_ativos = [p.label for p in patient.problems if p.status == "ativo"]
    if problemas_ativos:
        partes.append(f"Problemas ativos na lista: {', '.join(problemas_ativos)}")
    return "\n".join(partes)


def _dividir_secoes(texto: str) -> dict:
    marcadores = ["###HIPOTESES###", "###INVESTIGACAO###", "###TRATAMENTO###"]
    posicoes = {m: texto.find(m) for m in marcadores}
    ordenados = sorted((p, m) for m, p in posicoes.items() if p >= 0)
    secoes = {"differential_diagnosis": "", "suggested_workup": "", "treatment_considerations": ""}
    chave_por_marcador = {
        "###HIPOTESES###": "differential_diagnosis",
        "###INVESTIGACAO###": "suggested_workup",
        "###TRATAMENTO###": "treatment_considerations",
    }
    for i, (pos, marcador) in enumerate(ordenados):
        fim = ordenados[i + 1][0] if i + 1 < len(ordenados) else len(texto)
        conteudo = texto[pos + len(marcador):fim].strip()
        secoes[chave_por_marcador[marcador]] = conteudo
    return secoes


def analisar_caso(db: Session, patient) -> dict:
    """Gera hipóteses diagnósticas, sugestão de investigação e considerações
    terapêuticas para um paciente do Round. O resultado nunca é gravado como
    fato no prontuário — fica em registro separado (PatientAISuggestion),
    sempre rotulado como sugestão."""
    from app.services.pubmed import buscar_pubmed, montar_contexto_pubmed

    resumo = _resumo_caso(patient)
    consulta_busca = " ".join(filter(None, [
        patient.chief_complaint, patient.physical_exam,
        " ".join(patient.diagnostic_hypothesis or []),
    ])) or "cardiologia geral"

    trechos = recuperar(db, consulta_busca)
    contexto, fontes = montar_contexto(trechos)
    if not contexto:
        contexto = "[Nenhum trecho da base institucional correspondeu a este caso.]"

    artigos_pubmed = buscar_pubmed(consulta_busca)
    contexto_pubmed = montar_contexto_pubmed(artigos_pubmed)
    if contexto_pubmed:
        contexto = f"{contexto}\n\n{contexto_pubmed}"

    resposta = obter_provedor().responder(PROMPT_CASO, [
        {"role": "user", "content": f"CONTEXTO INSTITUCIONAL:\n{contexto}\n\nDADOS DO CASO:\n{resumo}"},
    ])

    secoes = _dividir_secoes(resposta.texto)
    return {
        **secoes,
        "case_snapshot": {"resumo_enviado": resumo},
        "sources": fontes,
        "sources_pubmed": artigos_pubmed,
        "model": resposta.modelo,
        "texto_completo": resposta.texto,
    }


def contar_uso_diario(db: Session, user_id: int) -> int:
    return db.execute(
        select(func.count(AIMessage.id))
        .join(AIConversation, AIMessage.conversation_id == AIConversation.id)
        .where(
            AIConversation.user_id == user_id,
            AIMessage.papel == "assistant",
            func.date(AIMessage.created_at) == func.current_date(),
        )
    ).scalar_one()


def escolher_modelo_automatico(pergunta: str) -> str:
    """Heurística v1 de seleção automática de modelo Claude, por tamanho da
    pergunta — perguntas longas/complexas tendem a se beneficiar de um modelo
    com mais capacidade de raciocínio (Fable 5); perguntas curtas/diretas vão
    para Opus 5. Ajustar o limiar depois com uso real."""
    return "claude-fable-5" if len(pergunta) >= 600 else "claude-opus-5"


def perguntar(
    db: Session,
    pergunta: str,
    historico: list[dict],
    temas: list[str] | None = None,
    modelo: str | None = None,
    usar_internet: bool = True,
) -> dict:
    from app.services.pubmed import buscar_pubmed, montar_contexto_pubmed

    trechos = recuperar(db, pergunta, temas)
    contexto, fontes = montar_contexto(trechos)
    if not contexto:
        contexto = "[Nenhum trecho da base institucional correspondeu à pergunta.]"

    artigos_pubmed = buscar_pubmed(pergunta)
    contexto_pubmed = montar_contexto_pubmed(artigos_pubmed)
    if contexto_pubmed:
        contexto = f"{contexto}\n\n{contexto_pubmed}"

    resposta = obter_provedor().responder(
        PROMPT_SISTEMA,
        [
            *historico[-8:],
            {"role": "user", "content": f"CONTEXTO INSTITUCIONAL:\n{contexto}\n\nPERGUNTA:\n{pergunta}"},
        ],
        modelo=modelo,
        usar_internet=usar_internet,
    )

    return {
        "texto": resposta.texto,
        "fontes": fontes,
        "fontes_pubmed": artigos_pubmed,
        "fontes_json": json.dumps(fontes, ensure_ascii=False),
        "modelo": resposta.modelo,
        "tokens_entrada": resposta.tokens_entrada,
        "tokens_saida": resposta.tokens_saida,
        "truncado": resposta.truncado,
    }


def perguntar_stream(
    db: Session,
    pergunta: str,
    historico: list[dict],
    temas: list[str] | None = None,
    modelo: str | None = None,
    usar_internet: bool = True,
):
    """Mesma lógica de `perguntar`, mas em streaming — existe para manter a
    conexão HTTP viva em perguntas longas com busca na internet ligada, que
    em produção passavam de 100s e caíam com "Failed to fetch" antes de a
    resposta pronta chegar ao navegador (a conexão parecia ociosa; o teto de
    tempo é do caminho de rede — NAT/proxy/browser —, não deste código).

    Gerador: produz {"delta": str} a cada pedaço de texto do modelo e termina
    com {"final": {...}} no mesmo formato de retorno de `perguntar`.
    """
    from app.services.pubmed import buscar_pubmed, montar_contexto_pubmed

    trechos = recuperar(db, pergunta, temas)
    contexto, fontes = montar_contexto(trechos)
    if not contexto:
        contexto = "[Nenhum trecho da base institucional correspondeu à pergunta.]"

    artigos_pubmed = buscar_pubmed(pergunta)
    contexto_pubmed = montar_contexto_pubmed(artigos_pubmed)
    if contexto_pubmed:
        contexto = f"{contexto}\n\n{contexto_pubmed}"

    gerador = obter_provedor().responder_stream(
        PROMPT_SISTEMA,
        [
            *historico[-8:],
            {"role": "user", "content": f"CONTEXTO INSTITUCIONAL:\n{contexto}\n\nPERGUNTA:\n{pergunta}"},
        ],
        modelo=modelo,
        usar_internet=usar_internet,
    )
    for evento in gerador:
        if "delta" in evento:
            yield {"delta": evento["delta"]}
        else:
            resposta = evento["final"]
            yield {"final": {
                "texto": resposta.texto,
                "fontes": fontes,
                "fontes_pubmed": artigos_pubmed,
                "fontes_json": json.dumps(fontes, ensure_ascii=False),
                "modelo": resposta.modelo,
                "tokens_entrada": resposta.tokens_entrada,
                "tokens_saida": resposta.tokens_saida,
                "truncado": resposta.truncado,
            }}
