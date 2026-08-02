---
title: "Modulação da Contratilidade Cardíaca (CCM): o Ensaio FIX-HF-5C"
slug: modulacao-da-contratilidade-cardiaca-ccm-o-ensaio-fix-hf-5c
theme: "Dispositivos"
kind: estudo
review_status: revisado
source_refs: ["Abraham WT, Kuck KH, Goldsmith RL, et al. A Randomized Controlled Trial to Evaluate the Safety and Efficacy of Cardiac Contractility Modulation. JACC Heart Fail. 2018;6(10):874-883. DOI: 10.1016/j.jchf.2018.04.010. PMID: 29754812. Errata: Correction. JACC Heart Fail. 2023;11(1):132. DOI: 10.1016/j.jchf.2022.11.003. PMID: 36599543 — conteúdo da errata não pôde ser lido (ver nota no corpo do documento), VERIFICAÇÃO HUMANA NECESSÁRIA"]
legacy_source: "Documento novo — modulação da contratilidade cardíaca (dispositivo Optimizer) não tinha nenhum registro nesta biblioteca, apesar de ser terapia de dispositivo aprovada para uma população específica que não se qualifica para TRC (QRS estreito)."
---

# Modulação da Contratilidade Cardíaca (CCM): o Ensaio FIX-HF-5C

## Definicao
Terapia de dispositivo distinta da terapia de ressincronização cardíaca (TRC) já registrada nesta biblioteca — em vez de corrigir dissincronia elétrica por QRS alargado, a modulação da contratilidade cardíaca (CCM) entrega sinais elétricos **não excitatórios** ao coração durante o período refratário absoluto, buscando aumentar a força de contração por via de sinalização intracelular, não por ressincronização. Indicada especificamente para o paciente com **QRS estreito** (<130ms), que não se qualifica para TRC.

## O ensaio fix-hf-5c
Abraham WT et al., JACC Heart Fail. 2018;6(10):874-883 (PMID 29754812). Ensaio randomizado, controlado, não cego, confirmando análise de subgrupo do ensaio anterior FIX-HF-5:
- **160 pacientes** NYHA III ou IV, **QRS <130ms**, FEVE **entre 25% e 45%**, randomizados para terapia clínica otimizada isolada (controle, 86) ou terapia clínica + CCM (tratamento, 74), por 24 semanas
- **Desfecho primário** (diferença de pico de VO2 entre grupos, modelagem bayesiana com empréstimo de 30% do subgrupo do FIX-HF-5): **0,84 mL O2/kg/min** (intervalo de credibilidade bayesiano 95%: 0,123-1,552) — **critério de sucesso atingido**
- **Qualidade de vida** (questionário Minnesota Living With Heart Failure): melhor no grupo CCM (p<0,001)
- **Classe funcional NYHA**: melhor no grupo CCM (p<0,001)
- **Teste de caminhada de 6 minutos**: melhor no grupo CCM (p=0,02)
- **Segurança**: 7 eventos relacionados ao dispositivo, resultando em limite inferior de 80% de pacientes livres de evento — acima da meta pré-especificada de 70%, **critério de segurança atingido**
- **Composto de morte cardiovascular e hospitalização por IC**: reduzido de **10,8% para 2,9%** (p=0,048)

## Nota sobre a errata (JACC Heart Fail. 2023;11(1):132)
A errata citada em `source_refs` foi **lida nesta revisão** — antes, o documento só registrava que ela existia, sem ter sido consultada. Confirmação bibliográfica feita direto no XML do PubMed (`CommentsCorrectionsList` do registro PMID 29754812): a errata é o **PMID 36599543**, DOI **10.1016/j.jchf.2022.11.003**, título "Correction", classificada como *Published Erratum*, publicada em *JACC Heart Fail.* 2023 Jan;11(1):132, e o próprio registro da errata (`RefType="ErratumFor"`) confirma que ela corrige exatamente o artigo original (JACC Heart Fail. 2018 Oct;6(10):874-883, DOI 10.1016/j.jchf.2018.04.010, PMID 29754812) — não há ambiguidade de qual artigo é corrigido.

Antes disso, **todos os números citados neste documento foram reconferidos palavra por palavra contra o abstract estruturado do PubMed** (via E-utilities, texto completo do `<Abstract>`, não resumo de terceiro): 160 pacientes (controle 86, tratamento 74, não cego), desfecho primário de VO2 de pico com diferença de 0,84 mL O2/kg/min (intervalo de credibilidade bayesiano 95%: 0,123-1,552), Minnesota Living With Heart Failure p<0,001, classe funcional NYHA p<0,001, teste de caminhada de 6 minutos p=0,02, 7 eventos relacionados ao dispositivo com limite inferior de 80% de pacientes livres de evento (meta pré-especificada 70%), e composto de morte cardiovascular/hospitalização por IC reduzido de 10,8% para 2,9% (p=0,048). **Todos batem exatamente com o que já estava escrito neste documento — nenhuma divergência encontrada no corpo do abstract original.**

**O que não foi possível confirmar, apesar de tentativa real por múltiplas vias, em DUAS revisões independentes (a original e esta, mais recente):** o **conteúdo** da errata em si — isto é, qual valor ou afirmação específica do artigo de 2018 ela corrige — não pôde ser lido. Vias tentadas e todas fechadas na primeira revisão:
- PubMed direto (`pubmed.ncbi.nlm.nih.gov/36599543`): bloqueado por verificação de navegador (Cloudflare);
- Registro XML da própria errata no PubMed: tem só metadados bibliográficos, **sem `<AbstractText>`** — corrections curtas da Elsevier costumam não ter resumo indexado;
- PMC: **nenhum dos dois artigos (original e errata) tem depósito de texto completo** — conferido por `elink` com `linkname=pubmed_pmc` (só existe `pubmed_pmc_refs`, que são artigos que citam, não o texto do próprio artigo);
- Europe PMC: só metadados bibliográficos, sem `abstractText`;
- Crossref, OpenAlex, Semantic Scholar: só título ("Correction") e metadados; OpenAlex e Unpaywall classificam o item como aberto (licença CC BY-NC-ND) mas **sem PDF direto** — apontam de volta para a página do editor;
- `sciencedirect.com` e `jacc.org` (a página do editor, incluindo a via CDN de PDF `ars.els-cdn.com`/`pdf.sciencedirectassets.com`): **403 com desafio Cloudflare/CAPTCHA** em todas as tentativas, com e sem User-Agent de navegador;
- Wayback Machine: indisponível para fetch a partir deste ambiente.

**Vias adicionais tentadas nesta segunda revisão, todas também fechadas — não repetir:**
- Wayback Machine, desta vez com acesso real (a indisponibilidade anterior era do ambiente, não do arquivo): CDX API localizou **5 capturas** da página `sciencedirect.com/science/article/pii/S2213177922006552` (a errata). A captura HTML (20230114231049) é só o **shell da SPA da ScienceDirect** — sem JavaScript, o corpo do artigo não renderiza, e o snapshot arquivado não contém o texto; a captura do link de PDF (20230114231101) é uma **página intersticial "Preparing your download"**, não o PDF em si — o rastreador do Archive.org nunca chegou a capturar os bytes do PDF. Nenhuma captura de `els-cdn.com` ou `pdf.sciencedirectassets.com` existe no CDX;
- API de mineração de texto da Elsevier (`api.elsevier.com/content/article/PII:S2213177922006552`), sem chave: devolve XML de metadados confirmando **`openaccessArticle: true`, `openaccessType: Full`, licença CC BY-NC-ND, cobertura 2023-01-31** — mas **sem o corpo do texto**; pedir a `view=FULL` (que traria o corpo) devolve `AUTHENTICATION_ERROR: Invalid API Key` — a Elsevier expõe metadados sem chave, mas exige chave paga para o texto completo, mesmo em artigo rotulado open access;
- `linkinghub.elsevier.com/retrieve/pii/S2213177922006552`: mesmo redirecionamento para `jacc.org`, mesmo bloqueio Cloudflare;
- Crossref confirma via campo `update-to` que o registro do DOI 10.1016/j.jchf.2022.11.003 aponta especificamente para 10.1016/j.jchf.2018.04.010 como `type: erratum` — reforça (não acrescenta) a identificação já feita via `CommentsCorrectionsList` do PubMed.

**VERIFICAÇÃO HUMANA NECESSÁRIA**: não foi possível determinar se a errata de 2023 altera algum número citado neste documento (VO2 de pico, IC bayesiano, p-valores, taxa do composto de morte/hospitalização) ou se corrige outro ponto (ex.: afiliação de autor, erro tipográfico não numérico). Quem tiver acesso institucional a `https://doi.org/10.1016/j.jchf.2022.11.003` deve abrir e conferir — os números atuais deste documento são os do abstract original e **não foram alterados nesta revisão** por falta de confirmação de que a errata os afeta. **O artigo é rotulado open access (CC BY-NC-ND) pela própria Elsevier** — a barreira encontrada é técnica (Cloudflare/CAPTCHA na página, exigência de chave de API paga para o texto minerado), não uma questão de licença fechada; um humano abrindo `https://doi.org/10.1016/j.jchf.2022.11.003` num navegador comum, resolvendo o desafio do Cloudflare manualmente, provavelmente consegue o que nenhuma via automatizada conseguiu aqui.

## Sintese pratica
CCM é opção de dispositivo com evidência de melhora funcional (VO2 de pico, teste de caminhada, qualidade de vida, classe funcional) e redução do composto de morte cardiovascular/hospitalização, especificamente na população que a TRC não alcança — QRS estreito. Diferente de vários ensaios já registrados nesta biblioteca (onde o desfecho composto melhora sem que a mortalidade isolada atinja significância), aqui o desfecho primário já é funcional (VO2 de pico), não mortalidade — a leitura correta é "melhora capacidade funcional e qualidade de vida, com sinal favorável também no composto clínico", não "reduz mortalidade isolada comprovadamente".

## Armadilhas clinicas
- Confundir CCM com TRC — são terapias de dispositivo distintas, com mecanismo e população-alvo diferentes: TRC corrige dissincronia elétrica em QRS alargado, CCM atua por sinalização intracelular em QRS estreito
- Indicar CCM em paciente com QRS ≥130ms elegível para TRC — a população do FIX-HF-5C foi selecionada justamente por ter QRS estreito, cenário em que a TRC não se aplica
- Tratar o resultado do desfecho primário (VO2 de pico) como equivalente a redução de mortalidade comprovada — o desfecho primário do ensaio é funcional; o composto de morte cardiovascular/hospitalização foi desfecho secundário, com redução numérica relatada (10,8% para 2,9%, p=0,048) mas amostra pequena (160 pacientes) para desfecho duro
