---
title: "Sinalizadores ambulatoriais para adiar cirurgia eletiva não cardíaca"
slug: sinalizadores-ambulatoriais-para-adiar-cirurgia-eletiva-nao-cardiaca
theme: "Perioperatório"
kind: protocolo
fonte_producao: grok
summary: "Checklist de consultório: quais condições cardiovasculares agudas ou instáveis pedem adiamento de cirurgia eletiva não cardíaca antes de qualquer escore (RCRI/Gupta), e o que documentar na decisão compartilhada."
review_status: pendente_revisao
review_note: "Pacote Tudo-com-Tudo Perioperatório 07/09/2026. Lacuna ambulatorial: RCRI/algoritmos já densos; foco em quando ADIAR eletiva. Fontes: AHA/ACC 2024 PMID 39316661; ESC 2022 PMID 36017553; SBC 2024 DOI 10.36660/abc.20240590; CCS 2017 PMID 27865641. Sem doses."
source_refs:
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. Circulation. 2024;150:e351-e442. DOI: 10.1161/CIR.0000000000001285. PMID: 39316661"
  - "Halvorsen S, Mehilli J, Cassese S, et al; ESC Scientific Document Group. 2022 ESC Guidelines on cardiovascular assessment and management of patients undergoing non-cardiac surgery. Eur Heart J. 2022;43(39):3826-3924. DOI: 10.1093/eurheartj/ehac270. PMID: 36017553"
  - "Gualandro DM, Fornari LS, Caramelli B, et al. Diretriz de Avaliação Cardiovascular Perioperatória da Sociedade Brasileira de Cardiologia – 2024. Arq Bras Cardiol. 2024;121(9):e20240590. DOI: 10.36660/abc.20240590"
  - "Duceppe E, Parlow J, MacDonald P, et al. Canadian Cardiovascular Society Guidelines on Perioperative Cardiac Risk Assessment and Management for Patients Who Undergo Noncardiac Surgery. Can J Cardiol. 2017;33(1):17-32. DOI: 10.1016/j.cjca.2016.09.008. PMID: 27865641"
---

# Sinalizadores ambulatoriais para adiar cirurgia eletiva não cardíaca

Este protocolo responde à pergunta de **consultório pré-operatório**: diante de cirurgia **eletiva** não cardíaca, **quais sinalizadores cardiovasculares pedem adiamento** (ou estabilização) **antes** de calcular RCRI/Gupta ou pedir prova funcional?

Não substitui:
- árvore de condições agudas/modificadores — [`condicoes-cardiacas-agudas-e-modificadores-de-risco-aha-acc-2024-arvore`](condicoes-cardiacas-agudas-e-modificadores-de-risco-aha-acc-2024-arvore.md);
- estratificação por escores — [`fluxograma-rcri-estratificacao-risco-cirurgico`](fluxograma-rcri-estratificacao-risco-cirurgico.md), [`arvore-decisao-rcri-lee`](arvore-decisao-rcri-lee.md);
- algoritmo SBC 2024 — [`diretriz-sbc-2024-algoritmo-avaliacao-cardiovascular-perioperatoria`](diretriz-sbc-2024-algoritmo-avaliacao-cardiovascular-perioperatoria.md);
- timing pós-stent — [`pci-stent-dapt-timing-cirurgia-nao-cardiaca-arvore-aha-acc-2024`](pci-stent-dapt-timing-cirurgia-nao-cardiaca-arvore-aha-acc-2024.md) e [`stent-coronario-recente-e-cirurgia-eletiva-janela-de-risco-ambulatorial`](stent-coronario-recente-e-cirurgia-eletiva-janela-de-risco-ambulatorial.md).

Árvore irmã: [`fluxograma-ambulatorial-risco-cardiovascular-preoperatorio-quando-escalar`](fluxograma-ambulatorial-risco-cardiovascular-preoperatorio-quando-escalar.md).

## Princípio

**Primeiro urgência e instabilidade; depois escore.** Cirurgia de emergência/urgência real não entra neste protocolo — prosseguir com proteção cardiovascular proporcional (AHA/ACC 2024; SBC 2024).

## Sinalizadores → considerar adiamento da eletiva

| Domínio | Sinalizador ambulatorial |
|---|---|
| Coronário agudo | SCA em curso ou recente não estabilizada; angina CCS III/IV nova ou progressiva |
| Insuficiência cardíaca | IC descompensada; edema pulmonar recente; NYHA III/IV sintomática não otimizada |
| Arrhythmia | Arritmia instável; FA com alta resposta ventricular sintomática; bradiarritmia grave / BAV avançado sintomático |
| Valva / aorta | Valvopatia grave sintomática; doença instável da aorta torácica |
| Pressão | PA muito elevada com sintoma de lesão aguda; limiar operacional SBC (PA >180×110 mmHg) como marcador de otimização — ver também sinalizadores de Hipertensão |
| Neurológico | AVC/AIT muito recente (modificador AHA/ACC 2024) |
| Dispositivo / stent | Timing inadequado pós-PCI/stent se a eletiva exigiria interromper antiagregação |
| Fragilidade / reserva | Fragilidade severa ou capacidade funcional muito limitada em cirurgia de risco intermediário/alto — não “adiar automaticamente”, mas reavaliar indicação, pré-habilitação e local |

Fontes-quadro: AHA/ACC 2024 (condições agudas e modificadores); SBC 2024 Tabela 2 (condições graves/instáveis); ESC 2022 (avaliação escalonada); CCS 2017 (biomarcadores e estratificação quando a eletiva segue).

## O que NÃO é sinalizador isolado de adiamento

- RCRI ≥2 ou Gupta elevado **sem** instabilidade — indica otimização/investigação, não cancelamento automático.
- Hipertensão crônica controlada.
- FA estável anticoagulação planejada — cruzar com [`anticoagulacao-ponte-heparina-preoperatorio-arvore-aha-acc-2024`](anticoagulacao-ponte-heparina-preoperatorio-arvore-aha-acc-2024.md) sem inventar doses aqui.
- CIED estável — planejar EMI, não adiar por rotina ([`fluxograma-manejo-perioperatorio-marcapasso-cdi-cied`](fluxograma-manejo-perioperatorio-marcapasso-cdi-cied.md)).

## Conduta ambulatorial em 5 passos

1. **Classificar urgência** da cirurgia (emergência / tempo-sensível / eletiva pura).
2. **Checklist de instabilidade** da tabela — se positivo, documentar motivo do adiamento e plano de estabilização.
3. **Discussão multidisciplinar** (cirurgia + anestesia + cardiologia) quando o adiamento compete com risco oncológico ou perda de janela terapêutica.
4. **Só então** estimar risco com ferramenta validada e capacidade funcional ([`dasi-capacidade-funcional-pre-operatoria`](dasi-capacidade-funcional-pre-operatoria.md)).
5. **Registrar** data-alvo de reavaliação e o que precisa estar estável para liberar a eletiva.

## Tudo com Tudo (cruzamentos)

- IC pré-op — [`insuficiencia-cardiaca-preoperatorio-eco-gdmt-sglt2-arvore-aha-acc-2024`](insuficiencia-cardiaca-preoperatorio-eco-gdmt-sglt2-arvore-aha-acc-2024.md)
- PA perioperatória — [`pressao-arterial-perioperatoria-limiares-e-arvore-aha-acc-2024`](pressao-arterial-perioperatoria-limiares-e-arvore-aha-acc-2024.md)
- Valvopatia — [`valvopatia-grave-cirurgia-nao-cardiaca-arvore-aha-acc-2024`](valvopatia-grave-cirurgia-nao-cardiaca-arvore-aha-acc-2024.md)
- Fragilidade — [`fragilidade-no-idoso-avaliacao-pre-operatoria-sbc-2024`](fragilidade-no-idoso-avaliacao-pre-operatoria-sbc-2024.md)
- Biomarcadores — [`biomarcadores-preoperatorios-bnp-ntprobnp-troponina-arvore-de-decisao`](biomarcadores-preoperatorios-bnp-ntprobnp-troponina-arvore-de-decisao.md)

## Limite da evidência

Os limiares (ex.: PA >180×110 mmHg na SBC) são **marcadores operacionais** de otimização, não substitutos do julgamento clínico nem indicação automática de cancelamento em cirurgia tempo-sensível.
