# MeuCardio — Serviço de Cardiologia

Plataforma clínica do Serviço de Cardiologia da [hospital não vinculado — remover ou ajustar].
Responsável técnico: Dr. Rafael Paes Meirelles — CRM-SP 138266 · RQE 134798.

## O que já roda

| Área | Estado |
|---|---|
| Autenticação JWT com perfis (admin, médico, residente, leitor) | funcional |
| Biblioteca científica com temas, versionamento e revisões | funcional |
| Busca full-text em português (tsvector + pg_trgm, com destaque) | funcional |
| Calculadoras: CHA₂DS₂-VASc, HAS-BLED, HEART, CKD-EPI 2021, Cockcroft-Gault | funcional |
| Banco de medicamentos + comparador lado a lado (até 4) | funcional, banco vazio |
| Base científica migrada do projeto 2.2.0 | 164 documentos |
| Round hospitalar: pacientes, problemas, evolução, resumo | funcional |
| PWA instalável, conteúdo científico offline | funcional |
| IA clínica com RAG (pgvector + busca híbrida, fontes citadas) | funcional |
| Curadoria editorial (fila de revisão, importação) | funcional |
| Editor Markdown no navegador | não implementado — Fase 3 |

Dados de paciente nunca são cacheados pelo service worker.
O round guarda apenas iniciais e número de prontuário.

## Subir o ambiente

    cp .env.example .env      # gere JWT_SECRET com: openssl rand -hex 32
    docker compose up --build

- Aplicação: http://localhost:8080
- API e documentação: http://localhost:8080/api/docs

O primeiro login usa `ADMIN_EMAIL` / `ADMIN_PASSWORD` do `.env`. Troque a senha antes do piloto.

## Carregar o conteúdo científico

Coloque os `.md` em `content/<tema>/` com front matter (veja o modelo em
`content/CDI/exemplo-estrutura.md`) e rode:

    docker compose exec backend python -m app.services.importer

Reimportar o mesmo documento cria uma revisão e incrementa a versão — nada é perdido.

## Apps móveis

O frontend já está construído para virar app sem reescrita: navegação em barra inferior,
áreas seguras (`env(safe-area-inset)`), alvos de toque grandes e manifest em modo standalone.

    cd frontend
    npm i @capacitor/core @capacitor/android @capacitor/ios
    npm i -D @capacitor/cli
    npx cap add android && npx cap add ios
    npm run sync:mobile

Publicação exige conta Google Play (Android) e Apple Developer + macOS com Xcode (iOS).

## Política de conteúdo

Nenhuma fórmula, dose ou referência entra no sistema sem origem verificável.
Escores sem coeficientes oficiais confirmados — GRACE, por exemplo — ficam com status
`verificacao_humana_necessaria` e são bloqueados na interface até validação.

## Identidade visual

Paleta derivada do brasão institucional: bordô `#6E1220`, dourado `#C4A15A`, branco e cinza claro.
`frontend/public/brasao.svg` é um marcador estrutural — substitua pelo vetor oficial antes do piloto.


## Migração do corpus 2.2.0

Os 225 arquivos do projeto anterior não eram Markdown limpo: cada um trazia um bloco
JSON com o conteúdo real, envolto em resíduo de conversa e artefatos do Perplexity
(marcadores `[web:NNN]`, spans ocultos, listas de notas de rodapé).

    python tools/migrar_corpus_legado.py <knowledge_do_projeto_antigo> -o content

Resultado: 225 lidos → 164 documentos únicos, 61 duplicatas resolvidas, nada descartado.
O script é idempotente — reexecutar reproduz exatamente o mesmo resultado.

### O que a migração revelou

- **61 dos 164 documentos (37%)** contêm a marcação `VERIFICAÇÃO HUMANA NECESSÁRIA`
  do próprio autor original. Ficam com `review_status=verificacao_humana_necessaria`,
  aparecem sinalizados na interface e a IA avisa ao usar essas informações.
- **13 documentos** não têm nenhuma referência bibliográfica.
- A desduplicação usa tamanho do texto como critério. Em alguns casos um arquivo
  chamado `...-parcial.md` era maior que o `...-completo.md` correspondente e venceu.
  Esses casos estão listados no relatório do script e merecem conferência manual.

## IA clínica

Recuperação híbrida: embeddings (pgvector, HNSW, distância de cosseno) fundidos com a
busca full-text em português por Reciprocal Rank Fusion. Sigla clínica vai mal em
embedding e bem em busca léxica — por isso os dois sinais.

Cada resposta devolve as fontes efetivamente usadas, com slug clicável para o documento.
Consultas ficam em `audit_logs` com modelo, fontes e tokens.

    docker compose exec backend python -c \
      "from app.core.db import SessionLocal; from app.services import rag; \
       print(rag.indexar_tudo(SessionLocal()))"

Indexar os 164 documentos gera ~855 trechos, custo aproximado de US$ 0,002 em embeddings.

### Trocar OpenAI por Claude

`app/services/ia/provedor.py` isola o provedor. A troca é `AI_PROVIDER=anthropic` no
`.env`. Um detalhe: a Anthropic não oferece endpoint de embeddings, então ao migrar
mantenha os embeddings em um serviço dedicado e use Claude só para a geração — a
interface já separa `embeddings()` de `responder()` justamente por isso.

## Identidade visual

Logotipos oficiais em `frontend/public/` (brasão, horizontal e vertical), aproveitados
do projeto 2.2.0. Ícones de PWA gerados a partir do brasão em 192/512 e maskable.
São PNG com fundo transparente em boa resolução (brasão 1012×981) — suficiente para web
e app. Um vetor só será necessário para impressão em grande formato.
