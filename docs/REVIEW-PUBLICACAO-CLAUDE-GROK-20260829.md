# Revisão e preparação de publicação — Claude + Grok — 29/08/2026

## Estado

- Claude HEAD revisado: `84e376fb25c9faab0a8940b4a40506849b2c52e5`.
- Registros monolíticos Claude promovidos/corrigidos: **43**.
- Itens de checklist removidos por colisão/fonte não resolvida: **3**.
- Registros inteiros retidos: **0**.
- Fragmentos/correções de doença modificados pelo Claude: promovidos a `revisado` após correções dirigidas e gates estruturais.

## Correções clínicas dirigidas
- EAo no idoso: CGA/futilidade e manejo hemodinâmico reescritos sem proibições absolutas.
- Sarcoidose cardíaca: indicação de biópsia endomiocárdica tornada seletiva, não universal.
- Valvopatia no atleta: IAo e valva bicúspide corrigidas para evitar gatilho cirúrgico indevido.
- CIED perioperatório: dependência e magneto/reprogramação reescritos de forma dispositivo-específica.
- Endocardite protética: tempo pós-implante explicitamente removido como gatilho cirúrgico isolado.

## Itens removidos/retidos
- `recomendacoes-granulares-esc2020-ahaacc2018-ebstein-eisenmenger-cia-civ-fontan-tga-switch` / `eisenmenger-bosentana-breathe5` — sobreposição com documento BREATHE-5 já existente.
- `recomendacoes-granulares-esc2020-ahaacc2018-ebstein-eisenmenger-cia-civ-fontan-tga-switch` / `fontan-anticoagulacao-vigilancia-hepatica` — superado por documento de tromboprofilaxia em Fontan com síntese mais atual.
- `vigilancia-e-manejo-pos-transplante-cardiaco-rejeicao-e-vasculopatia-do-enxerto` / `rejeicao-celular-manejo-por-gravidade` — fonte não resolvida: não confirmados a partir de abstract.

- Gate de reconciliação do banco: campo `checklists.revisao` normalizado de objeto JSON para texto, compatível com `discharge_checklists.revisao`.

## Grok 67–75

- HEAD local informado no handoff: `8b00af0c…`.
- HEAD atualmente visível no GitHub: `8a013105beb5ab1d13f907c4e6eeed1783492047`.
- **Grok 67–75: BLOQUEADO / NÃO IMPORTADO.** O bundle/ZIP informado existe no host local do Grok, mas não está acessível neste runner nem no GitHub. A branch remota é antiga e não será usada como substituto silencioso.
- Para completar o release, importar o bundle/ZIP ou publicar o HEAD `8b00af0c…` no GitHub e repetir a mesma revisão independente antes do merge final.

## Gate de release

- Claude: **PRONTO PARA PUBLICAÇÃO** após a validação estrutural deste branch.
- Grok 67–75: **BLOQUEIO ATIVO** enquanto o HEAD local não estiver materializado no repositório/runner.
- Merge final para `main` e deploy: **não executar enquanto o bloqueio Grok estiver ativo**, para cumprir a solicitação de revisar todo o conteúdo antes da publicação consolidada.

## Deploy preparado

O workflow `deploy-reviewed-science.yml` fica preparado para execução manual após o merge final. Ele exige o SHA exato de `main` e recusa execução enquanto este relatório não contiver a marca `Grok 67–75: INTEGRADO E REVISADO`.
