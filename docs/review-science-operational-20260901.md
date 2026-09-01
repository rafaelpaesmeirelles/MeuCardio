# Revisão científica operacional — 2026-09-01

## Escopo e decisão editorial

- Base exata: `8226e364aa140631b656226db9d2b0cf56ac8c1a`.
- Branch: `review/science-operational-20260901`.
- Escopo revisado: casos clínicos, checklists (incluindo o lote legado), materiais ao paciente, trilhas e os três registros de triagem previamente aprovados em `editorial-approvals/all-three-release-20260829.json`.
- Decisão: os registros descritos abaixo foram revisados, normalizados para `review_status: revisado` e `published: true`. O campo `published` permanece metadado editorial do corpus; os carregadores deliberadamente não o copiam diretamente para o banco, e a publicação efetiva continua condicionada à reconciliação de conteúdo revisado.
- Proveniência anterior foi preservada nos campos existentes e complementada por nota de conclusão datada. Não houve push, merge ou deploy.

## Método

1. Releitura dos registros e de suas relações, com foco em conduta, critérios, dose, contraindicação, monitorização, red flags e limites de evidência.
2. Conferência das referências já resolvidas na revisão de 31/08 (`74/74`, sem bloqueio remanescente) e reabertura dirigida de fontes primárias/diretrizes para os pontos de maior risco.
3. Validação estrutural dos manifestos e dos vínculos com documentos/itens canônicos existentes.
4. Verificação específica de linguagem leiga para impedir prescrição individual em material ao paciente.
5. Validação das perguntas e regras das três triagens com o mesmo contrato do motor clínico.

Fontes oficiais/primárias reabertas nesta passagem incluem:

- [AHA — insuficiência cardíaca direita](https://professional.heart.org/en/science-news/evaluation-and-management-of-right-sided-heart-failure/top-things-to-know)
- [ACC/AHA — diretriz de valvopatias](https://www.acc.org/Guidelines/Guidelines/2020/12/17/14/24/Valvular-Heart-Disease)
- [SAEM GRACE-3 — tontura e vertigem agudas](https://www.saem.org/publications/grace/grace-3)
- [AAO-HNS — BPPV](https://www.entnet.org/quality-practice/quality-products/clinical-practice-guidelines/bppv/)
- [ACOG/SMFM — aspirina e prevenção de pré-eclâmpsia](https://www.acog.org/clinical/clinical-guidance/practice-advisory/articles/2021/12/low-dose-aspirin-use-for-the-prevention-of-preeclampsia-and-related-morbidity-and-mortality)
- [FDA — estatinas na gestação e amamentação](https://www.fda.gov/drugs/drug-safety-and-availability/fda-requests-removal-strongest-warning-against-using-cholesterol-lowering-statins-during-pregnancy)
- [ESC 2025 — doença cardiovascular e gestação](https://www.escardio.org/guidelines/clinical-practice-guidelines/all-esc-practice-guidelines/cardiovascular-diseases-during-pregnancy-management-of/)

## Resultado quantitativo

| Frente | Registros | Unidades internas | Referências declaradas |
|---|---:|---:|---:|
| Casos clínicos | 28 | 112 alternativas | 112 `source_refs` |
| Checklists | 50 | 548 itens | 386 `source_refs` |
| Material ao paciente | 15 | 90 seções | 78 `fontes` preferidas pelo loader + 2 URLs no alias `source_refs` (80 entradas brutas) |
| Trilhas | 24 | 267 etapas | fontes herdadas dos alvos canônicos |
| Triagem | 3 | 45 perguntas / 34 regras | 19 `source_refs` |
| **Total** | **120** | — | **475 PMIDs únicos nas listas declaradas de referências** |

O escaneamento dos objetos completos encontra 478 PMIDs únicos: além dos 475
presentes em `source_refs`/`fontes`, os PMIDs `15320558`, `22735914` e
`23184102` são citados apenas no campo `resumo` do checklist
`acometimento-cardiaco-sindrome-antifosfolipide-catastrofica`. No material ao
paciente, a contagem bruta de 80 soma 78 entradas em `fontes`, campo preferido
pelo loader, e duas URLs mantidas no alias `source_refs` do material sobre
aspirina na gestação.

Todos os 120 registros ficaram `revisado` e `published: true`. As 267 etapas das trilhas resolvem para alvo existente, têm ordem contígua e possuem justificativa. As três triagens não têm pergunta ou regra inválida. Com esta inclusão, o conjunto submetido ao approval final totaliza 725 registros.

## Correções científicas e de segurança

### Casos clínicos

- Os 28 casos mantiveram suas respostas e explicações porque a releitura não encontrou regressão de conduta que justificasse alteração clínica.
- Todos preservam ao menos duas alternativas, índice de resposta válido e referências.
- Um rótulo residual `Corvia Clinical OS` em uma referência interna foi normalizado para `CorVIA`, sem alterar a fonte ou a conclusão clínica.

### Checklists

- Foram concluídos 50 checklists: 29 explicitamente não publicados no base, 46 alcançados pela marcação legada e 50 slugs únicos após deduplicação.
- Doses, ajustes renais, contraindicações, sequência terapêutica e necessidade de decisão multidisciplinar foram relidos. O texto de conclusão exige bula vigente e protocolo local quando a dose depende de produto/população.
- Em cinco checklists, a nota histórica foi reconciliada com o estado editorial final: nenhuma atestação clínica individual do Dr. Rafael Paes Meirelles foi presumida; a aprovação editorial do lote está registrada no manifesto versionado e a revisão científica independente está concluída. Nenhuma conduta foi alterada.
- Os `documento_origem` presentes resolvem para documento canônico existente. Dois vínculos removidos antes desta revisão continuaram ausentes porque seus slugs legados não são documentos do corpus:
  - `doenca-ateroembolica-cristais-colesterol-checklist` → o conceito existe como doença `ateroembolismo-por-colesterol`, mas não como documento compatível.
  - `nao-perder-hipertireoidismo-apatico-no-idoso` → o conceito existe como doença `hipertireoidismo-apatico-idoso`, mas não como documento compatível.
- Não foi criado vínculo artificial entre tipos diferentes apenas para preencher o campo.

### Material ao paciente

- Os 15 materiais agora têm fonte declarada; sete registros que dependiam apenas do documento associado receberam referências explícitas no próprio manifesto.
- O detector de posologia do carregador não encontra dose medicamentosa explícita nos 15 textos revisados.
- Correções materiais:
  - **Aspirina na gestação:** removido placeholder duplicado de dose; indicação restringida a alto risco ou combinação de fatores moderados; início/continuidade alinhados a ACOG/SMFM; alergia, sangramento e uso concomitante passaram a ser alertas explícitos. O texto não escolhe dose para a paciente.
  - **Hipolipemiantes na gestação/amamentação:** removidos placeholder de triglicerídeos e erro textual; retirada a afirmação obsoleta de contraindicação absoluta de estatina para toda gestante. A redação agora reflete FDA/ESC: a maioria pausa, exceções de risco muito alto exigem decisão especializada, e amamentação não é recomendada quando a estatina precisa continuar.
- O `documento_slug` legado removido de `hipertireoidismo-apatico-no-idoso-por-que-parece-so-cansaco` permaneceu ausente: há doença canônica relacionada, mas não documento com identidade compatível.

### Trilhas e alvos removidos

- Vinte e quatro trilhas foram revisadas, incluindo `trilha-aorta-mimetizadores-raros-igg4-erdheim-chester-behcet` e `trilha-tromboembolismo-pulmonar-risco-intermediario-alto-e-terapia-guiada-pelo-risco`.
- Na trilha de TEP intermediário-alto, a etapa PEITHO foi redirecionada do slug legado removido para o estudo canônico `peitho-tenecteplase-versus-placebo-tep-normotenso-vd-e-troponina`. As sete etapas foram relidas e preservam o nexo clínico: fibrinólise sistêmica, alternativa por cateter, filtro de veia cava, intervenção em TVP, prevenção de síndrome pós-trombótica e continuidade da anticoagulação.
- Oito ocorrências de etapa que existiam em `ce40e822` continuaram removidas. Há sete identidades clínicas correspondentes no manifesto de doenças, mas `carregar_trilhas.py` não aceita `doenca` como `item_type`; reintroduzi-las como `documento` recriaria link quebrado, e mudar o tipo sem suporte quebraria a carga.

| Ocorrência legada | Correspondente canônico existente | Decisão |
|---|---|---|
| LAL-D na trilha de depósito | `doencas:lal-d` | mantida removida |
| LAL-D na trilha de dislipidemias | `doencas:lal-d` | mantida removida |
| Abscesso hepático amebiano | `doencas:abscesso-hepatico-amebiano-ruptura-pericardica-tamponamento` | mantida removida |
| Granulomatose com poliangiite | `doencas:granulomatose-com-poliangiite-cardiovascular` | mantida removida |
| Deficiência de VLCAD | `doencas:deficiencia-de-vlcad` | mantida removida |
| Deficiência de CPT2 | `doencas:deficiencia-de-cpt2` | mantida removida |
| Pseudoxantoma elástico | `doencas:pseudoxantoma-elastico` | mantida removida |
| Osteogênese imperfeita | `doencas:osteogenese-imperfeita` | mantida removida |

- Títulos, objetivos, contagens implícitas, transições e justificativas das cinco trilhas afetadas foram reescritos para refletir somente as etapas publicáveis. Não há lacuna de ordem nem narrativa que prometa uma etapa ausente.

### Triagem

- Foram incorporados, em commit próprio, os três slugs aprovados: `distensao-abdominal-ascite-congestao-cardiaca`, `sopro-cardiaco-incidental` e `tontura-vertigem-persistente`.
- A triagem de ascite foi limitada: ajuste de diurético exige avaliação de pressão, perfusão, função renal e eletrólitos; creatinina isolada não determina automaticamente redução nem autoriza intensificação sem supervisão.
- A triagem de tontura recebeu GRACE-3 e AAO-HNS para sustentar o diferencial central/periférico e impedir classificação automática de quadro atípico como VPPB.
- O papel permanece de estratificação e encaminhamento; nenhum dos três fluxos confirma diagnóstico.

## Validações executadas

- `jq empty` nos cinco manifestos alterados: **passou**.
- `git diff --check`: **passou**.
- Contratos puros do motor de triagem para 45 perguntas e 34 regras: **passou**.
- Casos: 28/28 com pelo menos duas alternativas, resposta no intervalo e fonte: **passou**.
- Checklists: 50/50 com itens, IDs únicos, `origem_secao` e fonte: **passou**.
- Material ao paciente: 15/15 com fontes e sem match do detector canônico de posologia: **passou**.
- Trilhas: 24/24, 267/267 etapas resolvidas, ordem contígua e sem alvo legado removido na narrativa; auditoria transversal manteve 3.391/3.391 referências resolvidas: **passou**.
- Pytest do backend não foi reinstalado neste worktree: o ambiente não contém `sqlalchemy`, e a orientação operacional proíbe reinstalação pesada desnecessária. As validações independentes de banco diretamente ligadas aos manifestos foram executadas.

## Commits auditáveis

- `68922c61` — casos: conclusão da revisão operacional.
- `a3f44065` — checklists: conclusão da revisão clínica e legada.
- `4a759ed9` — material ao paciente: segurança, fontes e correções de gestação.
- `beca6b5c` — trilhas: sequência e alvos canônicos.
- `86399e4c` — triagem: três fluxos aprovados, em commit separado.
- `d81278b1` — casos: alinhamento do campo canônico `revisao`.
- `e9cdb59d` — trilhas: etapa PEITHO redirecionada para o estudo canônico.

## Limites preservados

- A revisão não transforma evidência observacional em recomendação graduada.
- Conteúdo raro ou de baixa certeza continua explicitando necessidade de centro especializado/decisão multidisciplinar.
- Nenhum vínculo inexistente foi inventado para recuperar cardinalidade anterior.
- A decisão clínica individual, a bula vigente, o protocolo local e a aprovação regulatória aplicável prevalecem sobre o conteúdo educacional.
