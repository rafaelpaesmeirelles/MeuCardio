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

from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import logging
import re
import time
import unicodedata

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.content import Document
from app.models.rag import AIConversation, AIMessage, DocumentChunk, KnowledgeChunk
from app.services.ia.assistant_tools import ASSISTANT_TOOLS_SCHEMA, executar_tool_assistente
from app.services.ia.provedor import obter_provedor, obter_provedor_embeddings

log = logging.getLogger("corvia.rag")

MAX_CHARS = 1400
MIN_CHARS = 200


class EmbeddingDimensionError(RuntimeError):
    """Levantada quando o provedor devolve vetor de dimensão diferente da
    configurada (`settings.embedding_dim`), ou quando o schema do banco não
    bate com essa configuração — nunca deve ser engolida como falha
    transitória de rede: é erro de configuração/modelo, precisa de
    intervenção humana antes de qualquer coisa ser gravada."""


def content_hash(texto: str) -> str:
    """sha256 do texto-fonte, usado como `content_hash` em `DocumentChunk` e
    `KnowledgeChunk` — mesma função para as duas tabelas, uma só definição."""
    return hashlib.sha256((texto or "").encode("utf-8")).hexdigest()


def verificar_dimensao_embedding(db: Session) -> None:
    """Falha de forma explícita se `settings.embedding_dim` divergir da
    dimensão real da coluna `embedding` no banco (pgvector guarda a dimensão
    em `atttypmod`). Sem isto, uma mudança de `EMBEDDING_DIM` sem migration
    correspondente só apareceria como erro de driver no primeiro INSERT —
    esta checagem é barata (um SELECT de catálogo, sem tocar em nenhuma
    linha de dado) e roda antes de qualquer chamada ao provedor."""
    linhas = db.execute(
        text(
            "SELECT c.relname, a.atttypmod "
            "FROM pg_attribute a JOIN pg_class c ON c.oid = a.attrelid "
            "WHERE c.relname IN ('document_chunks', 'knowledge_chunks') "
            "AND a.attname = 'embedding' AND a.attnum > 0 AND NOT a.attisdropped"
        )
    ).all()
    for tabela, atttypmod in linhas:
        # pgvector grava a dimensão diretamente em atttypmod (sem o desconto de
        # 4 bytes usado por tipos varlena como varchar) — confirmado lendo o
        # tipo `vector` da extensão: atttypmod > 0 é a dimensão em si.
        if atttypmod > 0 and atttypmod != settings.embedding_dim:
            raise EmbeddingDimensionError(
                f"embedding_dim configurado ({settings.embedding_dim}) diverge da "
                f"dimensão real da coluna {tabela}.embedding no banco ({atttypmod}). "
                "Corrija EMBEDDING_DIM ou aplique a migration correta antes de indexar "
                "— gravar agora misturaria vetores incompatíveis na mesma tabela."
            )


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


def indexar_documento(db: Session, doc: Document, provedor=None, *, forcar: bool = False) -> int:
    """Upsert idempotente por CONTEÚDO, não só por presença de chunk.

    `forcar=True` pula a checagem de hash e reprocessa mesmo que o conteúdo
    esteja idêntico ao já indexado — único caso legítimo é depois de trocar
    de modelo/dimensão de embedding, quando o hash do TEXTO não mudou mas o
    VETOR precisa ser regerado com o modelo novo.

    Fluxo, nesta ordem (correção coordenada de 03/09/2026, seção "content_hash"):
      1. calcula o hash do corpo atual — se já bate com o hash gravado no
         chunk existente, o documento está atual: devolve sem tocar no banco
         nem chamar o provedor.
      2. divide o texto em trechos (sem rede, sem banco).
      3. chama o provedor de embeddings ANTES de qualquer DELETE — uma falha
         aqui nunca apaga o índice anterior, porque o índice anterior ainda
         nem foi tocado.
      4. só com os vetores em mãos, abre uma transação curta: apaga os
         chunks antigos da entidade e insere os novos, commit.

    Isto substitui o desenho anterior (DELETE logo no início, embeddings
    chamados com o DELETE já pendente na transação) — que mantinha uma
    transação Postgres aberta pelo tempo inteiro da chamada de rede (até
    ~30min no pior caso, sem `idle_in_transaction_session_timeout`
    configurado no servidor) e, em caso de falha, dependia do `rollback()` do
    CHAMADOR para desfazer o DELETE. Agora uma falha do provedor não abre
    transação destrutiva nenhuma."""
    provedor = provedor or obter_provedor_embeddings()

    hash_atual = content_hash(doc.body_md)
    if not forcar:
        hash_existente = db.execute(
            select(DocumentChunk.content_hash)
            .where(DocumentChunk.document_id == doc.id)
            .limit(1)
        ).scalar_one_or_none()
        if hash_existente == hash_atual:
            return 0  # conteúdo inalterado desde a última indexação — zero chamadas de rede

    pedacos = dividir(doc.body_md)
    if not pedacos:
        apagados = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()
        if apagados:
            db.commit()
        return 0

    # O título do documento entra em cada trecho: sem isso, um trecho "## Dose"
    # perde a informação de qual fármaco é.
    textos = [f"{doc.title}\n{t or ''}\n{c}".strip() for t, c in pedacos]

    vetores: list[list[float]] = []
    for i in range(0, len(textos), 64):  # respeita o limite de lote da API
        vetores.extend(provedor.embeddings(textos[i : i + 64]))
    if len(vetores) != len(pedacos):
        raise EmbeddingDimensionError(
            f"Provedor devolveu {len(vetores)} vetores para {len(pedacos)} trechos "
            f"(documento id={doc.id} slug={doc.slug})."
        )
    for vetor in vetores:
        if len(vetor) != settings.embedding_dim:
            raise EmbeddingDimensionError(
                f"Vetor de dimensão {len(vetor)} não bate com embedding_dim="
                f"{settings.embedding_dim} (documento id={doc.id} slug={doc.slug})."
            )

    db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()
    for ordem, ((titulo, corpo), vetor) in enumerate(zip(pedacos, vetores)):
        db.add(DocumentChunk(
            document_id=doc.id, ordem=ordem, titulo_secao=titulo,
            conteudo=corpo, embedding=vetor, tokens_aprox=len(corpo) // 4,
            content_hash=hash_atual, embedding_model=settings.openai_embedding_model,
        ))
    db.commit()
    return len(pedacos)


def indexar_tudo(db: Session, apenas_pendentes: bool = True, *, limite: int | None = None) -> dict:
    """Indexa em lote. Só documentos PUBLICADOS entram no índice.

    O filtro por `published` aqui é defesa em profundidade: `recuperar()` já não
    devolve trecho de documento não publicado, mas manter o retido fora do índice
    evita gastar embedding com o que não pode ser servido e fecha a porta na
    origem.

    `apenas_pendentes=True` agora significa "sem chunk OU com corpo alterado
    desde a última indexação" — `indexar_documento()` decide isso sozinho por
    `content_hash` (seção "content_hash" da correção coordenada de 03/09/2026).
    Antes, um documento com QUALQUER chunk era considerado "em dia" para
    sempre; editar o corpo de um documento já publicado nunca disparava
    reindexação automática, só uma chamada manual de `indexar_documento()`
    para aquele slug específico. `apenas_pendentes=False` força reprocessar
    mesmo quem já está com o hash em dia (raro — só faz sentido depois de
    trocar de modelo/dimensão de embedding).

    `indexar_documento()` NÃO recebeu o filtro de `published` de propósito:
    ele é chamado diretamente para reindexar um documento específico, e quem
    chama já sabe o que está fazendo.

    `limite`, se dado, para o lote depois de processar essa quantidade de
    documentos (efetivamente reindexados, não contando os que já estavam em
    dia) — permite ao operador rodar o backfill em lotes pequenos e seguros
    em vez de tentar o backlog inteiro numa chamada só. Não é falha: entra em
    `backlog_restante` normalmente, e a próxima chamada retoma de onde parou
    (idempotente por `content_hash`, sem precisar guardar cursor).
    """
    verificar_dimensao_embedding(db)
    provedor = obter_provedor_embeddings()
    docs = db.query(Document).filter(Document.published.is_(True)).all()
    total = 0
    processados = 0
    falhas = 0
    falhas_seguidas = 0
    pendentes_restantes = 0
    for indice, d in enumerate(docs):
        # Parte 3 da correção coordenada de 02/09/2026, preservada: um
        # documento cuja chamada ao provedor falhe (crédito, rede, provedor
        # fora do ar) não pode travar o lote inteiro. Como o embedding agora
        # é obtido ANTES de qualquer DELETE (ver `indexar_documento`), uma
        # falha aqui não deixa nenhum DML pendente para desfazer — só
        # incrementa o contador de falha e segue.
        #
        # Falha seguida 3x é tratada como provedor fora do ar (crédito/rede),
        # não como conteúdo ruim de um item específico: interrompe o lote em
        # vez de repetir a mesma chamada fadada centenas/milhares de vezes
        # (achado ao ligar isto em `reconcile_content`, que roda contra o
        # acervo inteiro). Tudo que não foi tentado continua pendente e entra
        # na próxima chamada normalmente.
        try:
            trechos = indexar_documento(db, d, provedor, forcar=not apenas_pendentes)
            if trechos == 0 and apenas_pendentes:
                # devolveu 0 porque já estava em dia (hash bateu) — não conta
                # como "processado" nem reseta o circuito de falhas seguidas,
                # simplesmente não havia nada a fazer aqui.
                continue
            total += trechos
            processados += 1
            falhas_seguidas = 0
            if limite is not None and processados >= limite:
                pendentes_restantes = len(docs) - (indice + 1)
                log.info("Limite de %d documentos atingido — %d ainda pendentes para a próxima chamada.", limite, pendentes_restantes)
                break
        except Exception:
            log.exception("Falha ao indexar documento id=%s slug=%s — segue pendente.", d.id, d.slug)
            db.rollback()
            falhas += 1
            falhas_seguidas += 1
            if falhas_seguidas >= 3:
                pendentes_restantes = len(docs) - (indice + 1)
                log.warning(
                    "3 falhas seguidas ao indexar documentos — provedor parece indisponível, "
                    "lote interrompido (%d de %d ainda pendentes).",
                    pendentes_restantes, len(docs),
                )
                break
    return {
        "documentos": processados, "trechos": total, "falhas": falhas,
        "backlog_restante": pendentes_restantes,
    }


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
    # Import tardio: rag_multi importa rag (dividir/obter_provedor_embeddings)
    # — import no topo do arquivo criaria ciclo no boot do pacote.
    from app.services.rag_multi import buscar_lexico_multi, ids_semanticos_multi, resolver_trechos_multi

    limite = settings.ai_top_k * 3

    # Léxico (documento + as outras 12 frentes + calculadoras) não depende
    # do provedor de embeddings — lê direto das tabelas publicadas, mesma
    # consulta de `/api/search`. Roda sempre, antes de qualquer chamada ao
    # provedor, para nunca competir por crédito/latência com a parte que
    # pode falhar.
    lexicos = [
        r.chunk_id for r in db.execute(SQL_LEXICO, {"q": pergunta, "limite": limite}).mappings()
    ]
    try:
        lexicos_multi = buscar_lexico_multi(db, pergunta, limite)
    except Exception:
        log.exception("Falha na busca léxica multi-frente — RAG segue só com o que já tiver.")
        lexicos_multi = []

    # Semântico depende do provedor de embeddings. Sem crédito/indisponível
    # (Parte 3 da correção coordenada de 02/09/2026 — o provedor está sem
    # crédito HOJE), a IA não pode parar de responder: cai para léxico-only
    # em vez de propagar a exceção pro chamador e quebrar toda pergunta.
    semanticos: list[int] = []
    semanticos_multi: list[int] = []
    try:
        vetor = obter_provedor_embeddings().embeddings([pergunta])[0]
    except Exception:
        log.warning("Provedor de embeddings indisponível na recuperação — RAG segue só léxico.", exc_info=True)
        vetor = None
    if vetor is not None:
        # O join com Document é INCONDICIONAL, e não só quando há filtro por
        # tema: é por ele que passa o `published`. Antes de 31/07/2026 o join
        # só existia no caminho com `temas`, então uma pergunta sem tema
        # recuperava trechos de documento não publicado — conteúdo retido
        # esperando aval chegava à IA.
        consulta = (
            select(DocumentChunk.id)
            .join(Document, Document.id == DocumentChunk.document_id)
            .where(Document.published.is_(True))
        )
        if temas:
            consulta = consulta.where(Document.theme.in_(temas))
        consulta = consulta.order_by(DocumentChunk.embedding.cosine_distance(vetor)).limit(limite)
        semanticos = [r[0] for r in db.execute(consulta).all()]
        semanticos_multi = ids_semanticos_multi(db, vetor, limite)

    # Auditoria de 02/09/2026, Parte D/F: o RAG cobria só `documents`. As
    # outras 12 frentes elegíveis entram aqui como uma segunda "gaveta" no
    # mesmo RRF — mesmo prestígio que semântico/léxico de documento, sem
    # virar um "blob" sem identidade (cada resultado carrega `entity_type`
    # até `montar_contexto`, então a resposta ainda pode citar a origem
    # certa). Dentro da gaveta multi-frente, semântico (por chunk, id
    # inteiro) e léxico (por item inteiro, chave `(entity_type, slug)`) têm
    # granularidades diferentes — não colidem por acaso porque um `int`
    # nunca é igual a uma `tuple`, mas o RRF ainda funciona por serem
    # apenas chaves hasheáveis, ranqueadas independente do tipo.
    #
    # `document_chunks.id` e `knowledge_chunks.id` são sequences INDEPENDENTES
    # — o mesmo inteiro pode existir nas duas tabelas sem relação nenhuma.
    # Cada id entra no RRF marcado com a origem ("doc"/"multi") para nunca
    # fundir por acaso a pontuação de dois chunks de tabelas diferentes.
    ordenados_doc = _rrf([[("doc", i) for i in semanticos], [("doc", i) for i in lexicos]])
    lex_multi_chaves = [(item["entity_type"], item["slug"]) for item in lexicos_multi]
    ordenados_multi_inner = _rrf([semanticos_multi, lex_multi_chaves])
    ordenados_multi = [("multi", i) for i in ordenados_multi_inner]
    ordenados = _rrf([ordenados_doc, ordenados_multi])[: settings.ai_top_k]

    if not ordenados:
        return []

    ids_doc = [chave for origem, chave in ordenados if origem == "doc"]
    ids_multi_raw = [chave for origem, chave in ordenados if origem == "multi"]
    ids_multi_chunk = [i for i in ids_multi_raw if isinstance(i, int)]
    chaves_multi_lex = [i for i in ids_multi_raw if not isinstance(i, int)]

    linhas = db.execute(
        select(DocumentChunk, Document)
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(DocumentChunk.id.in_(ids_doc))
    ).all() if ids_doc else []

    trechos_por_chave: dict[tuple, dict] = {
        ("doc", chunk.id): {
            "slug": doc.slug, "titulo": doc.title, "tema": doc.theme,
            "secao": chunk.titulo_secao, "conteudo": chunk.conteudo,
            "review_status": doc.review_status,
            # `gaps` é o campo que de fato marca incerteza: o importador o
            # preenche com o texto literal `VERIFICAÇÃO HUMANA NECESSÁRIA`
            # encontrado no corpo do documento — sem trazê-lo até aqui,
            # `montar_contexto` não tem como avisar o modelo.
            "gaps": list(doc.gaps or []),
            "rota": f"/biblioteca/{doc.slug}",
            "entity_type": "documento",
        }
        for chunk, doc in linhas
    }
    for chunk_id, trecho in resolver_trechos_multi(db, ids_multi_chunk).items():
        trechos_por_chave[("multi", chunk_id)] = trecho
    lex_multi_por_chave = {(item["entity_type"], item["slug"]): item for item in lexicos_multi}
    for chave_lex in chaves_multi_lex:
        trecho = lex_multi_por_chave.get(chave_lex)
        if trecho:
            trechos_por_chave[("multi", chave_lex)] = trecho

    return [trechos_por_chave[chave] for chave in ordenados if chave in trechos_por_chave]


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
            # Correção coordenada de 03/09/2026: `t["rota"]`/`t["entity_type"]`
            # já vêm preenchidos por `recuperar()` para TODAS as frentes
            # (documento e as 12 do RAG multi-frente), mas até aqui eram
            # descartados nesta montagem — o frontend caía sempre em
            # `/biblioteca/{slug}`, rota que só existe de fato para
            # `entity_type == "documento"`. Toda citação de evidência, estudo,
            # medicamento etc. virava link quebrado. `rota` é a fonte da
            # verdade de navegação a partir de agora; nenhum consumidor deve
            # recompor a URL a partir do slug sozinho.
            "rota": t.get("rota"),
            "entity_type": t.get("entity_type"),
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


# Anexado a PROMPT_SISTEMA somente quando as ferramentas de agenda/e-mail
# estão habilitadas para esta pergunta (settings.ai_assistant_tools_enabled
# E o médico consentiu) — ver `_ferramentas_para` mais abaixo. Sem isto
# escrito explicitamente, o modelo tem o tool_use disponível na API mas não
# sabe que deve usá-lo por conta própria (mesmo problema já resolvido aqui
# antes para a web_search: a ferramenta ficava disponível e nunca era
# chamada até o prompt autorizar de forma explícita).
PROMPT_FERRAMENTAS = """

Você também tem ferramentas que agem sobre a AGENDA e a caixa de E-MAIL \
(CorvIA Mail) do próprio médico com quem você conversa agora — nunca de outra \
pessoa. Use-as quando a pergunta pedir isso: ver compromissos, marcar/\
reagendar/cancelar um compromisso, saber o próximo local de trabalho e o \
trânsito até lá, ou ler algo da caixa de e-mail dele.

Regras adicionais só para estas ferramentas:
- Nunca chame uma ferramenta que CRIA, REAGENDA ou CANCELA compromisso sem o \
médico ter pedido isso claramente nesta conversa — nunca por iniciativa própria.
- Se os dados para criar/reagendar/cancelar estiverem ambíguos (data relativa \
sem confirmação, qual compromisso entre vários), pergunte antes de agir; se \
estiverem claros, execute e relate o resultado.
- Se uma ferramenta devolver erro ou indisponibilidade, diga isso ao médico com \
honestidade — nunca finja que a ação funcionou nem invente dado (distância, \
trânsito, conteúdo de e-mail) que a ferramenta não devolveu.
- Resuma e-mail longo em vez de citá-lo por inteiro; nunca peça nem repita \
identificador de paciente que porventura apareça num e-mail.
- Isto é ação administrativa, não conteúdo clínico: não use aqui os marcadores \
[F#], [PM#] ou [W#].
"""


# Trabalho 15 (07/08/2026): a Corvia passou a oferecer dois modos de
# assistente — Clínica (o que já existia, PROMPT_SISTEMA acima, focado no
# corpus institucional/PubMed/busca científica) e Pessoal (este prompt),
# para rotina do dia a dia e temas gerais, com acesso às ferramentas de
# agenda/e-mail (PROMPT_FERRAMENTAS, anexado só quando as duas travas de
# `_ferramentas_para` liberam). Nunca usa o CONTEXTO INSTITUCIONAL nem o
# PubMed — `perguntar()`/`perguntar_stream()` pulam essa etapa inteira
# quando `modo == "pessoal"`, então este prompt nem finge que essas fontes
# existem na conversa.
PROMPT_PESSOAL = """Você é o assistente PESSOAL da Corvia — o mesmo produto do \
Assistente Clínica, mas neste modo você ajuda o médico com a rotina do dia a dia \
e temas gerais, não com conteúdo científico/clínico.

Você tem à disposição uma ferramenta de busca na internet (web_search). Use-a \
livremente para qualquer pergunta de conhecimento geral, prática ou atual — \
notícia, trânsito, previsão do tempo, informação sobre um lugar, etc.

Regras:
1. Se a pergunta for sobre agenda, compromissos ou deslocamento, e as \
ferramentas correspondentes estiverem disponíveis nesta conversa, use-as em \
vez de responder de memória — nunca invente horário, endereço ou distância.
2. Se a pergunta pedir orientação clínica, científica ou de conduta médica \
(dose, diagnóstico, diretriz, interpretação de exame, literatura, prescrição), \
diga que isso é papel do Assistente Clínica e sugira trocar para ele — não \
tente responder aqui, mesmo que soubesse a resposta. A separação existe \
exatamente para que conteúdo clínico sempre passe pela disciplina de citação \
de fonte do outro modo, nunca por aqui.
3. Escreva em português do Brasil, direto e natural — sem os marcadores de \
citação [F#]/[PM#]/[W#] do modo Clínica; aqui, quando usar uma fonte da \
busca na internet, basta mencionar de onde veio em prosa normal.
4. Não peça nem repita identificador de paciente, mesmo que apareça em \
e-mail ou compromisso lido por uma ferramenta.
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


MODELO_RAPIDO = "claude-haiku-4-5"
MODELO_EQUILIBRADO = "claude-sonnet-5"
MODELO_COMPLEXO = "claude-opus-5"
HISTORICO_MAX_MENSAGENS = 6
HISTORICO_MAX_CHARS = 16_000

# Termos que transformam uma consulta curta em decisão clínica: estas
# perguntas não devem cair no modelo mais leve só porque têm poucos caracteres.
MARCADORES_DECISAO = (
    "ajuste de dose", "anticoag", "contraindic", "diagnostico", "dose",
    "emergencia", "gesta", "indicacao", "interacao", "lacta", "neonat",
    "oncolog", "pediatr", "prescri", "prognost", "risco", "tratamento",
)
MARCADORES_COMPLEXIDADE = (
    "caso clinico", "comorbidades", "diagnostico diferencial", "evidencias conflitantes",
    "fragilidade", "multimorbidade", "multiplas diretrizes", "polifarmacia",
)


def _normalizar(texto: str) -> str:
    decompondo = unicodedata.normalize("NFKD", texto.casefold())
    return "".join(caractere for caractere in decompondo if not unicodedata.combining(caractere))


def escolher_modelo_automatico(pergunta: str) -> str:
    """Seleciona capacidade proporcional à complexidade, não apenas ao tamanho.

    A regra anterior enviava toda pergunta curta para Opus. Em produção, uma
    consulta direta medida levou ~21 s; a mesma recuperação fundamentada com
    Haiku levou ~7 s. Decisões terapêuticas continuam, no mínimo, no Sonnet, e
    casos longos ou com múltiplos fatores sobem para Opus.
    """
    texto = _normalizar(pergunta)
    marcadores_complexos = sum(marcador in texto for marcador in MARCADORES_COMPLEXIDADE)
    if len(pergunta) >= 600 or marcadores_complexos >= 2:
        return MODELO_COMPLEXO
    if len(pergunta) >= 180 or marcadores_complexos or any(
        marcador in texto for marcador in MARCADORES_DECISAO
    ):
        return MODELO_EQUILIBRADO
    return MODELO_RAPIDO


def limitar_historico(historico: list[dict]) -> list[dict]:
    """Mantém continuidade sem reenviar conversas enormes ao modelo.

    Respostas anteriores podem chegar a 4.096 tokens cada. O antigo `[-8:]`
    permitia dezenas de milhares de caracteres extras a cada turno, fazendo a
    latência crescer conforme a conversa avançava. Preservamos as mensagens
    mais recentes, em pares completos sempre que couberem no orçamento.
    """
    selecionadas: list[dict] = []
    total = 0
    for mensagem in reversed(historico[-HISTORICO_MAX_MENSAGENS:]):
        conteudo = str(mensagem.get("content") or "")
        if total + len(conteudo) > HISTORICO_MAX_CHARS:
            continue
        selecionadas.append(mensagem)
        total += len(conteudo)
    return list(reversed(selecionadas))


def _preparar_contexto(
    db: Session,
    pergunta: str,
    temas: list[str] | None,
) -> tuple[str, list[dict], list[dict], dict[str, int]]:
    """Recupera base institucional e PubMed em paralelo.

    O PubMed não usa a sessão do banco e pode executar em outra thread. Assim,
    uma lentidão do NCBI deixa de ser somada integralmente ao embedding e à
    consulta vetorial. Nenhum texto da pergunta é registrado em log.
    """
    from app.services.pubmed import buscar_pubmed, montar_contexto_pubmed

    inicio = time.perf_counter()
    with ThreadPoolExecutor(max_workers=1, thread_name_prefix="corvia-pubmed") as executor:
        futuro_pubmed = executor.submit(buscar_pubmed, pergunta)
        trechos = recuperar(db, pergunta, temas)
        apos_rag = time.perf_counter()
        artigos_pubmed = futuro_pubmed.result()
    apos_fontes = time.perf_counter()

    contexto, fontes = montar_contexto(trechos)
    if not contexto:
        contexto = "[Nenhum trecho da base institucional correspondeu à pergunta.]"
    contexto_pubmed = montar_contexto_pubmed(artigos_pubmed)
    if contexto_pubmed:
        contexto = f"{contexto}\n\n{contexto_pubmed}"

    metricas = {
        "rag_ms": round((apos_rag - inicio) * 1000),
        "fontes_ms": round((apos_fontes - inicio) * 1000),
        "trechos": len(trechos),
        "pubmed": len(artigos_pubmed),
    }
    return contexto, fontes, artigos_pubmed, metricas


def _ferramentas_para(db: Session, user) -> tuple[str, list[dict] | None, object]:
    """Decide se esta pergunta ganha acesso às tools de agenda/e-mail.

    As duas condições — flag de instalação e consentimento individual —
    precisam estar de acordo; nenhuma delas sozinha libera. Sem `user` (ex.:
    análise de caso do Round, que não passa usuário autenticado a este ponto),
    nunca libera.
    """
    if not settings.ai_assistant_tools_enabled or user is None or getattr(user, "ia_ferramentas_consent_em", None) is None:
        return "", None, None
    executor = lambda nome, argumentos: executar_tool_assistente(nome, argumentos, db, user)  # noqa: E731
    return PROMPT_FERRAMENTAS, ASSISTANT_TOOLS_SCHEMA, executor


def _preparar_por_modo(
    db: Session, pergunta: str, temas: list[str] | None, modo: str, user,
) -> tuple[str, str, list[dict], list[dict], dict[str, int], list[dict] | None, object]:
    """Ponto único onde os dois modos do assistente (Trabalho 15) divergem.

    Clínica: exatamente o comportamento de sempre — base institucional +
    PubMed, PROMPT_SISTEMA, sem ferramentas de agenda/e-mail (o modo Pessoal
    existe justamente para isolar isso).

    Pessoal: nunca consulta a base institucional nem o PubMed — não faz
    sentido fingir fonte científica numa pergunta de agenda —, usa
    PROMPT_PESSOAL, e SEMPRE tenta oferecer as ferramentas (é o propósito do
    modo); `_ferramentas_para` continua sendo quem decide se elas de fato
    liberam, pelas duas travas de sempre.
    """
    if modo == "pessoal":
        prompt_extra, ferramentas, executor_ferramenta = _ferramentas_para(db, user)
        return (
            PROMPT_PESSOAL + prompt_extra,
            f"PERGUNTA:\n{pergunta}",
            [], [], {"rag_ms": 0, "fontes_ms": 0, "trechos": 0, "pubmed": 0},
            ferramentas, executor_ferramenta,
        )
    contexto, fontes, artigos_pubmed, metricas = _preparar_contexto(db, pergunta, temas)
    return (
        PROMPT_SISTEMA,
        f"CONTEXTO INSTITUCIONAL:\n{contexto}\n\nPERGUNTA:\n{pergunta}",
        fontes, artigos_pubmed, metricas,
        None, None,
    )


def perguntar(
    db: Session,
    pergunta: str,
    historico: list[dict],
    temas: list[str] | None = None,
    modelo: str | None = None,
    usar_internet: bool = False,
    user=None,
    modo: str = "clinica",
) -> dict:
    inicio = time.perf_counter()
    prompt_sistema, conteudo_usuario, fontes, artigos_pubmed, metricas, ferramentas, executor_ferramenta = (
        _preparar_por_modo(db, pergunta, temas, modo, user)
    )

    resposta = obter_provedor().responder(
        prompt_sistema,
        [
            *limitar_historico(historico),
            {"role": "user", "content": conteudo_usuario},
        ],
        modelo=modelo,
        usar_internet=usar_internet,
        ferramentas=ferramentas,
        executor_ferramenta=executor_ferramenta,
    )
    log.info(
        "ai_request_completed modo=%s model=%s internet=%s sources_ms=%s total_ms=%s chunks=%s pubmed=%s",
        modo, resposta.modelo, usar_internet, metricas["fontes_ms"],
        round((time.perf_counter() - inicio) * 1000), metricas["trechos"], metricas["pubmed"],
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
    usar_internet: bool = False,
    user=None,
    modo: str = "clinica",
):
    """Mesma lógica de `perguntar`, mas em streaming — existe para manter a
    conexão HTTP viva em perguntas longas com busca na internet ligada, que
    em produção passavam de 100s e caíam com "Failed to fetch" antes de a
    resposta pronta chegar ao navegador (a conexão parecia ociosa; o teto de
    tempo é do caminho de rede — NAT/proxy/browser —, não deste código).

    Gerador: produz {"delta": str} a cada pedaço de texto do modelo e termina
    com {"final": {...}} no mesmo formato de retorno de `perguntar`.
    """
    inicio = time.perf_counter()
    yield {"status": (
        "Consultando a base científica e o PubMed…" if modo != "pessoal"
        else "Preparando a resposta…"
    )}
    prompt_sistema, conteudo_usuario, fontes, artigos_pubmed, metricas, ferramentas, executor_ferramenta = (
        _preparar_por_modo(db, pergunta, temas, modo, user)
    )
    if modo != "pessoal":
        yield {"status": "Fontes localizadas. Preparando a síntese clínica…"}

    gerador = obter_provedor().responder_stream(
        prompt_sistema,
        [
            *limitar_historico(historico),
            {"role": "user", "content": conteudo_usuario},
        ],
        modelo=modelo,
        usar_internet=usar_internet,
        ferramentas=ferramentas,
        executor_ferramenta=executor_ferramenta,
    )
    primeiro_token_ms: int | None = None
    for evento in gerador:
        # O provedor também emite eventos de status ao iniciar uma tool de
        # agenda/e-mail. Antes, qualquer evento que não fosse ``delta`` caía
        # no ramo de ``final`` e ``evento["final"]`` levantava KeyError.
        if "status" in evento:
            yield {"status": evento["status"]}
        elif "delta" in evento:
            if primeiro_token_ms is None:
                primeiro_token_ms = round((time.perf_counter() - inicio) * 1000)
            yield {"delta": evento["delta"]}
        elif "final" in evento:
            resposta = evento["final"]
            log.info(
                "ai_stream_completed modo=%s model=%s internet=%s sources_ms=%s first_token_ms=%s total_ms=%s chunks=%s pubmed=%s",
                modo, resposta.modelo, usar_internet, metricas["fontes_ms"],
                primeiro_token_ms, round((time.perf_counter() - inicio) * 1000),
                metricas["trechos"], metricas["pubmed"],
            )
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
        else:
            raise ValueError("Evento inválido recebido do provedor de IA.")
