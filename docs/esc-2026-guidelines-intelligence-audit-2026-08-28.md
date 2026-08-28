# ESC 2026 — integração de guidelines e expansão do CorVIA Intelligence

Data da auditoria: 28/08/2026.

## Escopo

Foram revisados quatro documentos oficiais fornecidos ao CorVIA e conferidas as fontes públicas oficiais ESC/Oxford Academic disponíveis durante o ESC Congress 2026.

Os PDFs oficiais contêm restrições explícitas a reprodução/tradução sem autorização. Por isso, o conteúdo clínico adicionado ao CorVIA é **síntese original em português**, e não tradução integral. Classes e níveis de evidência selecionados foram preservados quando necessários para uso clínico.

## Documentos oficiais incorporados ao conteúdo

1. **2026 ESC Guidelines for the management of cardiovascular disease and chronic kidney disease** — DOI `10.1093/eurheartj/ehag098`.
2. **2026 ESC Guidelines on cardiac rehabilitation** — DOI `10.1093/eurheartj/ehag099`.
3. **2026 ESC Guidelines for the management of heart failure** — DOI `10.1093/eurheartj/ehag100`.
4. **Fifth Universal Definition of Myocardial Infarction (2026)** — DOI `10.1093/eurheartj/ehag101`.

A coleção oficial Oxford Academic/ESC de 2026 lista exatamente esses quatro documentos em 28/08/2026:
`https://academic.oup.com/eurheartj/pages/esc_guidelines`.

## Novos documentos oficiais identificados pelo radar

Além dos quatro documentos acima, a verificação pública identificou itens de alto valor que devem entrar como **detected** e permanecer aguardando revisão antes de alterar conteúdo clínico:

- **European Society of Cardiology (ESC) Core Curriculum for the Cardiologist: 2026 update** — publicado em 27/08/2026 — DOI `10.1093/eurheartj/ehag521`.
- **Ventricular free-wall rupture, ventricular pseudoaneurysm, and papillary muscle rupture complicating acute myocardial infarction: a clinical consensus statement** — 14/08/2026 — DOI `10.1093/eurheartj/ehag164`.
- **Pathophysiology, prevention, and management of coronary microvascular obstruction: a clinical consensus statement** — 14/08/2026 — DOI `10.1093/eurheartj/ehag334`.
- **Workup and Management of Rhythm Disorders in Myocarditis and Inflammatory Cardiomyopathy: a clinical consensus statement** — listado para 28/08/2026 no hub oficial do Congresso — DOI `10.1093/europace/euag153`.
- **Diagnosis and Management of Very Rare Primary Arrhythmia Syndromes in Children and Adults: a clinical consensus statement** — listado para 28/08/2026 — DOI `10.1093/europace/euag184`.

O hub oficial usado para acompanhamento contínuo é:
`https://academic.oup.com/esc/pages/2026-simultaneous-publications`.

Esse hub informa que é atualizado ao longo do ESC Congress 2026 e organiza publicações simultâneas/Hot Line de 28 a 31 de agosto. Ele contém, além de consensos, estudos, registros, ensaios randomizados, meta-análises e outras publicações cardiovasculares lançadas em associação com o congresso.

## Correção de classificação

Uma hipótese anterior de “guideline ESC 2026 de saúde mental e doença cardiovascular” foi descartada após conferência da coleção oficial. O documento correspondente é **2025 ESC Clinical Consensus Statement on mental health and cardiovascular disease**, classificado na coleção de 2025; portanto não deve ser semeado como lançamento ESC 2026.

## Mudanças no CorVIA Intelligence

O radar passa a combinar:

- portal oficial ESC de guidelines;
- coleção oficial ESC Guidelines no Oxford Academic;
- hub `ESC Congress 2026 Simultaneous Publications`;
- `European Heart Journal — Advance Articles` para statements/curriculum de alto sinal;
- fontes já existentes ACC, AHA e SBC.

A descoberta agora:

- extrai DOI quando disponível;
- deduplica prioritariamente por DOI, evitando duplicar a mesma publicação encontrada no ESC e no OUP;
- usa janela móvel de 45 dias, com piso inicial em 10/08/2026;
- não alerta publicações com data futura, mesmo que já apareçam pré-listadas no hub do Congresso;
- aceita todos os artigos do hub curado do ESC Congress, mas mantém filtro de alto sinal nas demais fontes;
- cria achados como `detected`;
- envia alerta factual, sem alterar automaticamente recomendações clínicas;
- contém bootstrap auditável dos lançamentos já confirmados para evitar perda de itens que saiam da primeira tela de coleções dinâmicas.

## Execução contínua

Foi adicionado workflow agendado para executar o radar no backend de produção a cada 4 horas. A rotina é idempotente e a mesma publicação não deve gerar duplicidade por DOI/fingerprint/URL e por restrições de entrega de notificação.

## Regra editorial

**Descoberta não é publicação clínica.** Um item detectado deve passar por leitura, síntese, revisão de segurança, integração Tudo com Tudo e revisão editorial antes de ser promovido a conteúdo clínico.