# CardioBene — API

FastAPI + PostgreSQL + Redis.

## Rodar

    cp ../.env.example ../.env   # e edite os segredos
    docker compose up --build

Documentação interativa: http://localhost:8080/api/docs

## Importar conteúdo científico

Coloque os arquivos `.md` em `../content/<tema>/` e execute:

    docker compose exec backend python -m app.services.importer

## Módulos

| Rota | Função |
|---|---|
| `/api/auth` | login JWT, perfil |
| `/api/library` | documentos científicos por tema, versionamento |
| `/api/search` | busca full-text em português (tsvector + pg_trgm) |
| `/api/calculators` | escores clínicos com fórmula, referência e limitações |
| `/api/drugs` | banco de medicamentos e comparador |
| `/api/round` | pacientes, problemas, evolução, resumo |

## Política de conteúdo

Fórmulas e doses só entram no sistema com referência verificável.
Itens sem coeficiente oficial confirmado ficam com status
`verificacao_humana_necessaria` e não são calculados.
