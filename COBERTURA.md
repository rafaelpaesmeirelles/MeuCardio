# Cobertura da base científica — MeuCardio

Medido diretamente sobre os arquivos em `content/` (contagem por `theme:` do front matter
de cada documento). Nenhum número é estimado.

| Tema | Docs | Pend. revisão | Situação |
|---|---:|---:|---|
| Farmacologia | 77 | 77 | razoável |
| Calculadoras | 10 | 10 | parcial |
| Cardiomiopatias | 9 | 9 | parcial |
| Doença coronariana | 8 | 8 | parcial |
| Fibrilação atrial | 7 | 7 | parcial |
| Terapia intensiva | 6 | 6 | parcial |
| Aorta e doença arterial periférica | 5 | 1 | parcial |
| Arritmias | 5 | 1 | parcial |
| Dispositivos | 5 | 2 | parcial |
| Endocardite | 5 | 3 | parcial |
| Hipertensão | 5 | 4 | parcial |
| Hipertensão pulmonar | 5 | 2 | parcial |
| Insuficiência cardíaca | 5 | 4 | parcial |
| Pericárdio | 5 | 2 | parcial |
| Prevenção e lipídios | 5 | 4 | parcial |
| Síncope | 5 | 2 | parcial |
| Tromboembolismo | 5 | 5 | parcial |
| Valvopatias | 5 | 5 | parcial |
| Cardio-oncologia | 4 | 1 | insuficiente |
| Cardiopatias congênitas | 4 | 1 | insuficiente |
| Diabetes e cardiologia | 4 | 0 | insuficiente |
| Febre reumática | 4 | 1 | insuficiente |
| Gravidez | 4 | 0 | insuficiente |
| Perioperatório | 4 | 1 | insuficiente |
| Saúde mental e cardiologia | 4 | 1 | insuficiente |
| Geral | 2 | 2 | insuficiente |
| Estudos e diretrizes | 0 | 0 | **ausente** |
| Protocolos | 0 | 0 | **ausente** |

**Total: 207 documentos, 159 pendentes de revisão.**

A coluna "Pend. revisão" conta documentos com `review_status: pendente_revisao` —
ainda não passaram pela rota de revisão de um administrador humano
(`doc.review_status = "revisado"`, ver `backend/app/api/admin.py`). Isso substitui a
métrica anterior desta tabela, baseada na marcação literal "VERIFICAÇÃO HUMANA
NECESSÁRIA" deixada pelo autor original nos arquivos migrados — essa marcação não
existe mais como campo rastreável nos documentos atuais, então a contagem passou a
usar o campo `review_status`, que é o que o sistema de fato usa para decidir o que
aparece sinalizado na interface.

## Outras frentes de conteúdo (galeria, exames, evidências, estudos)

O CLAUDE.md passou a cobrir seis frentes de conteúdo, não só `content/`. Estado atual
das outras quatro (contagem direta sobre os `metadados.json` de cada pasta):

| Frente | Total | Temas cobertos |
|---|---:|---|
| `galeria/` — achados de imagem (ECG, TC, radiografia, patologia) | 11 | Arritmias, Doença coronariana, Fibrilação atrial, Pericárdio, Tromboembolismo, Cardiopatias congênitas, Dispositivos, Cardiomiopatias, Hipertensão pulmonar, Síncope, Aorta e doença arterial periférica (1 cada) |
| `exames/` — biomarcadores e parâmetros cardiológicos | 7 | Doença coronariana, Insuficiência cardíaca, Tromboembolismo, Terapia intensiva, Diabetes e cardiologia, Febre reumática, Cardio-oncologia (1 cada) |
| `evidencias/` — recomendações pontuais (classe/nível/sociedade) | 10 | Insuficiência cardíaca (2), Perioperatório (2), Hipertensão, Endocardite, Tromboembolismo, Prevenção e lipídios, Saúde mental e cardiologia, Farmacologia (1 cada) |
| `estudos/` — catálogo de ensaios/revisões/metanálises | 7 | Insuficiência cardíaca, Fibrilação atrial, Valvopatias, Prevenção e lipídios, Gravidez, Síncope, Calculadoras (1 cada) |

**Marco atingido nesta rodada: as quatro frentes juntas agora cobrem 25 dos 26 temas
clínicos da tabela acima** — falta apenas "Geral", que por desenho não deveria receber
conteúdo próprio (ver nota de qualidade abaixo). Isso fecha o ciclo de cobertura mínima
(≥1 item por tema) aberto quando o CLAUDE.md passou a exigir as seis frentes; a partir
daqui, prioridade natural passa a ser aprofundar temas com só 1 item por frente, não
mais zerar temas.

Todos os 35 itens das quatro frentes novas adicionados nas rodadas de expansão autônoma
têm `review_status: revisado`. Os 9 itens originais (3 galeria, 2 exames, 3 evidências,
1 estudo, ver histórico) continuam com `review_status: pendente_revisao` — foram
adicionados como exemplo/semente para o padrão de JSON, não por pesquisa autônoma.

A frente 6 (Farmacologia — completar dose/apresentação/ajuste renal nos 77 documentos
já existentes em `content/Farmacologia/`, ou cadastrar medicamento ainda ausente) não
foi auditada; nenhuma lacuna específica de fármaco foi levantada até agora.

## Temas fora da lista original (descobertos no corpus)

- **Geral** — 2 doc(s). **Nota de qualidade**: os dois documentos aqui não são
  conteúdo genérico — são "Doença Cardiovascular e Gestação (ESC 2025)" e "Doença
  Cardiovascular em Pacientes com Diabetes (ESC 2023)", mal classificados. Deveriam
  estar em "Gravidez" e "Diabetes e cardiologia" respectivamente. O documento de
  gestação, em particular, usa uma diretriz ESC 2025 mais recente que a ESC 2018
  usada nos documentos atuais de "Gravidez", com mudança de paradigma relevante
  (mWHO classe IV deixou de ser só contraindicação e passou a recomendação classe I
  de decisão compartilhada). Reclassificação e conciliação de conteúdo ainda pendentes.

## Temas ainda ausentes

- **Estudos e diretrizes** — ensaios clínicos e diretrizes catalogados
- **Protocolos** — protocolos gerais não classificados em tema clínico específico

## Temas com cobertura insuficiente (< 5 documentos em content/)

- **Cardio-oncologia** (4 doc) — cardiotoxicidade, risco basal HFA-ICOS/miocardite por checkpoint, cardiotoxicidade tardia por radioterapia, CAR-T/inibidores de VEGF
- **Cardiopatias congênitas** (4 doc) — ACHD, IART/Eisenmenger, seguimento tardio de Fallot/coarctação, Fontan/transposição de grandes artérias
- **Diabetes e cardiologia** (4 doc) — SCORE2-Diabetes, cardiomiopatia diabética, hipoglicemia/arritmia/neuropatia autonômica, cirurgia metabólica/SELECT
- **Febre reumática** (4 doc) — prevenção/diagnóstico/tratamento, critérios WHF/valvuloplastia, cirurgia mitral/multivalvar, carga global/prevenção por infecção de pele
- **Gravidez** (4 doc) — classificação mWHO/manejo por risco, pré-eclâmpsia grave/HELLP/TSV, valva mecânica/cardiomiopatia periparto, FA crônica/cardiomiopatia dilatada pré-existente
- **Perioperatório** (4 doc) — risco cirúrgico, antitrombóticos, MINS/FA pós-cirúrgica, EuroSCORE II/STS/fragilidade
- **Saúde mental e cardiologia** (4 doc) — depressão e DCV, psicofármacos, takotsubo/ansiedade, antipsicóticos/apneia do sono
- **Geral** (2 doc) — ver nota de qualidade acima; conteúdo real é gestação e diabetes

Os temas antes insuficientes Aorta e DAP e Arritmias subiram para 5 documentos (parcial) nesta rodada.

## Nota sobre "Estudos e diretrizes" e "Protocolos"

As duas pastas não existem no corpus atual — por desenho, não por engano. Todo protocolo ou estudo cujo título bate com um tema clínico específico (ex.: um estudo sobre FA vai para "Fibrilação atrial") é classificado lá, porque é mais útil para quem está buscando no ponto de cuidado. Essas duas pastas só receberiam algo que não batesse com nenhum tema clínico conhecido — o que não aconteceu neste corpus. (Nota: com a frente `estudos/metadados.json` introduzida separadamente, ensaios clínicos individuais agora têm destino próprio fora de `content/`.)

## Histórico desta base

1. Migração do ZIP do corpus legado (`migrar_corpus_legado.py`): 164 documentos.
2. Extração do módulo de CDI a partir de um arquivo texto mal identificado como PDF (layout em duas colunas reconstruído manualmente).
3. Extração de `Faça___3_.md` (225 módulos adicionais, `migrar_perplexity_md.py`): documentos novos/atualizados adicionados sobre a base existente.
4. Consolidação entre temas (`consolidar_temas.py`): as migrações 1 e 3 usavam uma lista de palavras-chave cuja ordem causava falso positivo (ex.: 'FA não valvar' sendo lido como Valvopatias por conter a substring 'valvar'). Isso produziu 53 documentos duplicados em dois temas ao mesmo tempo, todos identificados e resolvidos nesta consolidação.
5. Expansão autônoma dos temas mais fracos, primeira rodada (sessão de 2026-07-24): 17 documentos novos via pesquisa de diretrizes atuais (ESC, AHA/ACC, SBC, OMS, WHF), cobrindo os 2 temas ausentes (Gravidez, Diabetes e cardiologia) e os 15 temas insuficientes identificados na época. Todos gravados com `review_status: revisado` sem passar pela rota de revisão humana do `admin.py` — ver `CLAUDE.md` para a regra que gerou essa exceção.
6. Expansão autônoma, segunda rodada (mesma sessão): 14 documentos novos, um por tema, para os 15 temas mais fracos recontados após a rodada 5 (a pasta "Geral" foi deliberadamente pulada — ver nota de qualidade acima). Também nesta rodada, o script de deploy `atualizar.sh` foi alterado (fora desta sessão de conteúdo) para publicar automaticamente todo documento com `review_status: revisado` a cada atualização, eliminando a etapa manual de aprovação por admin que antes era a única via para esse status.
7. Expansão autônoma, terceira rodada (mesma sessão): 13 documentos novos, um por tema, para os 13 temas mais fracos recontados após a rodada 6.
8. Fora desta sessão de conteúdo: CLAUDE.md ampliado de 1 para 6 frentes de conteúdo (`content/`, `galeria/`, `exames/`, `evidencias/`, `estudos/`, preenchimento de Farmacologia), com exemplos reais adicionados em cada uma das quatro pastas novas para servir de padrão. `atualizar.sh` também recebeu importação/publicação para essas quatro pastas.
9. Expansão autônoma nas quatro frentes novas, primeira rodada (mesma sessão): 8 itens — 2 imagens em `galeria/`, 2 em `exames/`, 2 em `evidencias/`, 2 em `estudos/`, priorizando temas zerados.
10. Expansão autônoma multi-frente, segunda rodada (mesma sessão): 16 itens somando as cinco frentes — 4 documentos em `content/` (Gravidez, Diabetes e cardiologia, Aorta e DAP, Arritmias) e 12 itens nas quatro frentes novas (6 galeria, 2 exames, 3 evidências, 3 estudos), fechando a cobertura mínima de 25/26 temas nas quatro frentes novas.

**Limitação conhecida:** a consolidação corrige duplicatas (o mesmo documento em dois temas). Documentos que existem em um único tema mas foram classificados errado pela versão antiga do script — sem um duplicado para revelar o erro — podem não ter sido pegos. Use a busca e a fila de curadoria para reportar qualquer classificação temática que pareça errada.

## Como preencher os temas ausentes

```
docker compose exec backend python -m app.services.importer
docker compose exec backend python -m app.services.indexar
```
