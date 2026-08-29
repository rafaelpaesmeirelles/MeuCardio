# Registro novo de triagem de sintomas — Sopro cardíaco identificado ao exame (achado incidental) — 29/08/2026

## Contexto

Missão dedicada: criar um registro **novo** em `triagem-sintomas/metadados.json`
(manifesto de Triagem de Sintomas — **não** confundir com `doencas/metadados.json`,
o Guia de Doenças, que tem schema totalmente diferente) para "Sopro cardíaco
identificado ao exame", cobrindo o achado **incidental em paciente
assintomático**, tanto adulto quanto criança. Slug: `sopro-cardiaco-incidental`.

O manifesto tinha 18 registros antes desta rodada; nenhum cobria sopro
cardíaco como queixa/triagem própria (o único registro pediátrico amplo,
`sintomas-cardiovasculares-na-crianca`, trata sopro como um entre vários
sintomas, sem árvore dedicada de timing/grau/manobra).

## Fontes usadas (todas lidas por completo)

- `content/Geral/fluxograma-sopro-cardiaco-incidental-no-adulto-assintomatico.md`
  — âncoras ACC/AHA 2020 valvopatia (PMID 33332150) e ESC/EACTS 2021
  valvopatia (PMID 34453165); achados semiológicos quantificados de Etchells,
  Bell, Robb (JAMA 1997, PMID 9032164).
- `content/Cardiopatias_congênitas/fluxograma-sopro-cardiaco-na-crianca-inocente-versus-patologico.md`
  — Frank & Jacobe (Am Fam Physician 2011, PMID 22010618) e atualização Ford,
  Lara, Park (Am Fam Physician 2022, PMID 35289571).
- `content/Cardiologia_pediátrica/sopros-cardiacos-na-infancia-diferenciacao-entre-sopro-inocente-e-sopro-patologico.md`
  (encontrado via `grep -ril "sopro cardiaco\|sopro inocente\|ausculta cardiaca" content/`,
  usado só para enriquecer perguntas/regras — este manifesto não tem campo de
  documentos relacionados) — trouxe PMID 40466724 (Mahawattege et al., Aust J
  Gen Pract 2025, sinais de alarme Box 3 e observação de que sopro inocente se
  acentua em vigência de febre) e PMID 30761241 (Doshi & Chikkabyrappa, Cureus
  2018, caracterização dos 4 sopros inocentes clássicos).

## Verificação de citações

Os 7 PMIDs citados em `source_refs` (33332150, 34453165, 9032164, 22010618,
35289571, 40466724, 30761241) foram conferidos nesta sessão via PubMed
E-utilities (`esummary`) — título, periódico, ano e primeiro autor batem com
o que está registrado.

## Estrutura do registro

- **11 perguntas**: idade (number), recém-nascido (<28 dias), instabilidade
  (obrigatória — gate de emergência), timing do sopro (sistólico/diastólico/
  contínuo), grau na escala de Levine (1–6), características de alerta à
  ausculta (multiselect: holossistólico/pico tardio, timbre áspero,
  irradiação, B2 anormal, clique sistólico, aumenta em pé), manobra postural/
  compressão jugular, sintomas associados (multiselect, obrigatória —
  dispneia, cianose, síncope, dor torácica, falha de crescimento/dificuldade
  alimentar), contexto febril/sinal de endocardite, história familiar de
  morte súbita/cardiomiopatia, fator de risco estrutural conhecido.
- **10 regras** (priority 100→15): instabilidade → emergência; lactente com
  falha de crescimento/cianose → emergência (red flag pediátrico grave);
  recém-nascido → urgente; sopro diastólico → sempre urgente (red flag
  incondicional); sopro sistólico grau ≥3 ou com característica de alerta/
  sintoma associado → urgente; contexto febril/endocardite → urgente;
  história familiar/fator de risco estrutural → prioritário; sopro contínuo
  que não desaparece com manobra → prioritário (diferencial: PCA, fístula
  arteriovenosa); zumbido venoso (desaparece com manobra) → informativo;
  sopro inocente clássico (sistólico suave, grau ≤2, sem nenhuma
  característica de alerta nem sintoma, sem fator de risco) → rotina, sem
  red flags.
- Nenhuma dose de fármaco em nenhum campo.
- `review_status: "pendente_revisao"`, `version: 1`.

## Validação

- JSON e ambos os validadores do motor de regras
  (`validate_question_definitions`/`validate_rule_definitions`) passam sem
  erro.
- `evaluate_rules` testado manualmente para os quatro cenários exigidos pela
  missão (diastólico, sistólico intenso/sintomático, lactente com falha de
  crescimento/cianose, sopro inocente clássico) — comportamento correto,
  incluindo `red_flags == []` no cenário de sopro inocente.
- Teste dedicado: `backend/tests/test_novo_sintoma_sopro_cardiaco_incidental.py`.
- Gate de review_status: como o registro é publicado como
  `pendente_revisao`, `test_canonical_content_review_status.py::
  test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc`
  **falha com 1 item esperado e documentado** — a allowlist
  `PENDENTES_LOTES_TUDO_COM_TUDO["triagem-sintomas/metadados.json"]` foi
  atualizada com um comentário explicando que essa allowlist só isenta
  registros já `revisado`, então o `pendente_revisao` novo continua
  aparecendo em `invalidos` até aval editorial explícito — mesmo padrão
  usado no PR #698 (branch
  `claude/novo-verbete-cardiomiopatia-de-takotsubo-20260829`) para
  `cardiomiopatia-de-takotsubo`.

## Risco de colisão sinalizado

O registro foi adicionado ao **final** do array JSON de
`triagem-sintomas/metadados.json` (era o item 19, após 18 registros
pré-existentes) para minimizar conflito de merge — vários outros agentes
estavam trabalhando em paralelo no mesmo arquivo, em branches distintas,
durante esta sessão (confirmado por processos de teste concorrentes de
outras worktrees rodando durante a validação).
