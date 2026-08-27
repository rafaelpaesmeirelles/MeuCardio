# Tudo com Tudo — Pericardite / Doença Pericárdica (verbete-hub adulto), 27/08/2026

## Lacuna identificada

Segundo ciclo independente Tudo com Tudo do dia (o primeiro produziu o PR #553, verbete-hub de endocardite infecciosa). Auditoria do corpus mostrou, de novo, o mesmo padrão: `content/Pericárdio/` reúne **26 documentos narrativos já revisados** (diretriz unificada ESC 2025 — framework IMPS de síndromes inflamatórias miocárdicas e pericárdicas —, diretriz ESC 2015 de doenças pericárdicas, pericardite recorrente/refratária com inibidores de IL-1, constritiva, efusivo-constritiva, purulenta bacteriana, tuberculosa, urêmica/dialítica, pós-infarto/Dressler, actínica), mais **10 materiais ao paciente** já publicados e **2 protocolos de emergência** de tamponamento cardíaco — mas `doencas/metadados.json` só tinha `doenca-pericardica-oncologia` (escopo específico oncológico), sem nenhum verbete geral adulto.

Dois outros candidatos foram avaliados e descartados: cardiomiopatia hipertrófica (base de conexão menor, 5 documentos dedicados) e miocardite aguda do adulto (base fragmentada entre pastas, apenas 6-8 documentos diretos, e já parcialmente ancorada por `miocardite-pediatrica` e `miocardite-por-inibidor-checkpoint`).

## PRs abertos evitados

Confirmado via `gh pr list --state open` que nenhum PR aberto toca `doencas/metadados.json` com verbete de pericardite. PRs antigos de checklists/material-paciente sobre pericárdio (#234, #292, #351, #388, #429/#440) propõem conteúdo em coleções diferentes, sem sobreposição. Também evitados: #543/#544/#545/#536/#535/#534 (Codex), #540/#542/#551/#553 (já meus, hoje).

## Escopo e cuidado com duplicação

O verbete geral **não duplica** `doenca-pericardica-oncologia`: detalhamento de causa oncológica/actínica sistêmica é citado apenas de passagem, remetendo ao verbete próprio. Miocardite/sarcoidose cardíaca (tema irmão, não pericárdico) foram avaliadas e excluídas do `related_document_slugs` por proximidade temática, não vínculo direto.

## Conteúdo produzido

Um único registro novo em `doencas/metadados.json`:

- **slug**: `pericardite` — **name**: Pericardite aguda e doença pericárdica — **area**: geral — **category**: pericardio — **subtype**: inflamatoria_e_infecciosa — **completeness**: completo — **fonte_producao**: claude — **review_status**: pendente_revisao — **version**: 1

Campos: epidemiologia, apresentação (7 itens), abordagem diagnóstica (critérios ESC 2015/2025), diferenciais (7), exames (6), red flags (8, com HRs da ESC 2025), tratamento, fluxo ambulatorial (5) e de emergência (5), monitorização (5), **10 populações especiais/subtipos** (recorrente/refratária, constritiva, efusivo-constritiva, purulenta, tuberculosa, urêmica/diálise, pós-infarto, actínica, derrame crônico idiopático, achados incidentais anatômicos, miopericardite pós-vacina mRNA), assistente determinístico (5 perguntas, 5 regras validadas), tags, 18 `source_refs`.

Nenhum documento, checklist, trilha, material ou protocolo de emergência novo foi criado.

## Fontes primárias

- Adler Y, Charron P, Imazio M, et al. 2015 ESC Guidelines for the diagnosis and management of pericardial diseases. Eur Heart J. 2015;36(42):2921-2964. PMID 26320112.
- Schulz-Menger J, Collini V, Gröschel J, et al. 2025 ESC Guidelines for the management of myocarditis and pericarditis. Eur Heart J. 2025;46(40):3952-4041. PMID 40878297.
- Imazio M et al. ICAP trial (colchicina). NEJM 2013. PMID 23992557.
- Brucato A et al. AIRTRIP (anakinra). JAMA 2016. PMID 27825009.
- Klein AL et al. RHAPSODY (rilonacepte). NEJM 2021. PMID 33200890.
- Sagristà-Sauleda J et al. Derrame pericárdico crônico idiopático — história natural. NEJM 1999. PMID 10615077.
- Mais 12 fontes de populações especiais (constritiva, purulenta, tuberculosa, urêmica, pós-infarto, actínica, agenesia de pericárdio, vacina mRNA) — ver `source_refs` completo no registro.

## Relações Tudo com Tudo

**22 vínculos diretos**, verificados por script (existem, são documento narrativo, não medicamento/exame/calculadora) e por teste automatizado (mencionam "pericárdio"/"pericardite" no próprio texto). **1 material ao paciente** já publicado (`pericardite-aguda`).

**4 relações avaliadas e recusadas** (proximidade temática, documentadas no relatório do agente de pesquisa): `sarcoidose-cardiaca...`, `miocardite-de-celulas-gigantes...`, `miocardite-diagnostico-estratificacao-de-risco...` (miocardite/sarcoidose são tema irmão, não pericárdico) e `pericardiotomia-posterior-esquerda-na-prevencao-de-fibrilacao-atrial-pos-operatoria-o-ensaio-palacs` (é uma técnica cirúrgica de prevenção de arritmia, não um protocolo de doença pericárdica).

## Riscos e limitações declarados

- Números de mortalidade/associação com pneumonia da pericardite purulenta vêm de séries históricas convergentes na literatura secundária, tratados como faixa estimada — o próprio documento-fonte já sinalizava isso.
- Papel do corticoide adjuvante na pericardite tuberculosa permanece incerto quanto à redução de mortalidade/constrição de forma geral.
- Escopo deliberadamente restrito: causa oncológica/actínica sistêmica remete ao verbete próprio, sem duplicar detalhe.

## Gates

- `audit_tudo_com_tudo.py`: 9.467 → 9.468 itens (+1), zero referência quebrada, `SpecialtyDisease.related_document_slugs` 76/76 → 98/98.
- `content_inventory.py --minimum-records 9468 --minimum-files 2187 --strict`: exit 0, 93 doenças (+1), 2.187 arquivos inalterados.
- Novo `backend/tests/test_tudo_com_tudo_pericardite.py` (6 testes) + conjunto ampliado (7 arquivos que iteram sobre toda a coleção `doencas/`, 59 testes): **58 passaram, 1 falha** — confirmada como pré-existente (mesma falha de frontend já identificada no ciclo da endocardite, `test_condicoes_profundas_adulto.py`).
- `python -c "import app.main"`: OK.

## Branch e PR

Branch: `claude/tudo-com-tudo-lacuna-2-20260827`, criada a partir de `origin/main` (commit `d3aad9d6`) via `git worktree`, independente de todas as outras branches em andamento. Sem merge, sem deploy, sem publicação automática. Revisão clínica humana obrigatória antes de `review_status: revisado`.
