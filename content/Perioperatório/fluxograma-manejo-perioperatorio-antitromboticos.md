---
title: "Fluxograma: manejo perioperatório de antiagregantes (DAPT/stent) e anticoagulantes orais"
slug: fluxograma-manejo-perioperatorio-antitromboticos
theme: "Perioperatório"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
source_refs:
  - "2022 ESC Guidelines on cardiovascular assessment and management of patients undergoing non-cardiac surgery. European Heart Journal. 2022;43(39):3826-3924. DOI: 10.1093/eurheartj/ehac270."
  - "Dual antiplatelet management in the perioperative period: updated and expanded systematic review. PMC. https://pmc.ncbi.nlm.nih.gov/articles/PMC10576385/"
  - "Perioperative Anticoagulation Management. StatPearls (NCBI Bookshelf). https://www.ncbi.nlm.nih.gov/books/NBK557590/"
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. Circulation. 2024;150:e351-e442. PMID: 39316661. DOI: 10.1161/CIR.0000000000001285."
  - "Derivado dos documentos já publicados no acervo 'Manejo Perioperatório de Antitrombóticos: DAPT e Anticoagulantes Orais' e 'Anticoagulação e ponte com heparina no perioperatório — AHA/ACC 2024' (content/Perioperatório/), que citam as mesmas fontes acima."
---

# Fluxograma: manejo perioperatório de antiagregantes (DAPT/stent) e anticoagulantes orais

Duas perguntas diferentes se escondem sob "o que fazer com o sangue fino antes da cirurgia": uma é sobre **dupla antiagregação plaquetária depois de stent coronariano**, onde o prazo mínimo protege contra trombose de stent; a outra é sobre **anticoagulante oral crônico**, onde a decisão central não é *se* suspender, mas *se vale a pena fazer ponte* com heparina durante a suspensão. As duas exigem árvores próprias, porque misturá-las nivela riscos que não são comparáveis.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente em uso de antiagregante ou anticoagulante, candidato a cirurgia/procedimento"] --> D1{"Qual classe de antitrombótico está em uso?"}

  D1 -->|"Dupla antiagregação plaquetária (DAPT) após stent coronariano"| D2{"Tempo desde o implante e tipo de stent"}
  D2 -->|"Stent metálico (BMS) implantado há menos de 1 mês"| C1(["Adiar a cirurgia eletiva até completar pelo menos 1 mês de DAPT"])
  D2 -->|"Stent farmacológico (DES) implantado há menos de 3 meses"| C2(["Adiar a cirurgia eletiva; aguardar pelo menos 6 meses de DAPT quando possível"])
  D2 -->|"DES entre 3 e 6 meses, e a cirurgia não pode aguardar até 6 meses"| C3(["Individualizar: considerar prosseguir a partir de 3 meses se o risco de adiar a cirurgia superar o risco de trombose de stent"])
  D2 -->|"Tempo mínimo já cumprido (BMS 1 mês ou mais, ou DES 6 meses ou mais)"| D3{"O risco de sangramento do procedimento permite manter a DAPT completa?"}
  D3 -->|"Sim"| C4(["Manter aspirina e inibidor de P2Y12 durante todo o perioperatório"])
  D3 -->|"Não, o procedimento exige suspender o inibidor de P2Y12"| P1["Suspender o inibidor de P2Y12 conforme o fármaco: clopidogrel/ticagrelor 5 dias antes, prasugrel 7 dias antes; manter a aspirina"]
  P1 --> C5(["Reiniciar o inibidor de P2Y12 em até 24 horas após a cirurgia, quando a hemostasia estiver adequada"])

  D1 -->|"Anticoagulante oral (DOAC ou varfarina)"| D4{"O procedimento pode ser realizado sem interromper a anticoagulação?"}
  D4 -->|"Sim (risco hemorrágico mínimo)"| C6(["Manter o anticoagulante, conforme o protocolo do procedimento e a estratégia anestésica"])
  D4 -->|"Não"| D5{"O risco trombótico do paciente é muito alto?"}
  D5 -->|"Não"| C7(["Interromper temporariamente o anticoagulante pelo tempo determinado pelo fármaco e pela função renal; não fazer ponte com heparina de rotina"])
  D5 -->|"Sim, prótese valvar mecânica mitral"| C8(["Considerar ponte individualizada com heparina, ajustada à hemostasia e à função renal, em decisão multidisciplinar"])
  D5 -->|"Sim, trombo de ventrículo esquerdo há menos de 3 meses"| C9(["Considerar ponte individualizada com heparina, ajustada à hemostasia e à função renal, em decisão multidisciplinar"])
  D5 -->|"Sim, fibrilação atrial com AVC ou AIT recente"| C10(["Considerar ponte individualizada com heparina, ajustada à hemostasia e à função renal, em decisão multidisciplinar"])
  D5 -->|"Sim, outra situação excepcional de alto risco trombótico"| C11(["Discussão especializada multidisciplinar; não presumir benefício automático da ponte"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11 conduta;
```

## O que a árvore não mostra

**Ponte com heparina não é sinônimo de segurança — na maioria dos pacientes ela soma sangramento sem reduzir tromboembolismo proporcionalmente.** A pergunta correta diante de um anticoagulante suspenso não é "o paciente usa anticoagulante, então precisa de ponte?", e sim se o risco trombótico durante os poucos dias sem cobertura é alto o bastante para justificar o risco hemorrágico adicional da heparina — na maioria dos pacientes comuns, a resposta é não.

**DOAC e varfarina não seguem o mesmo cronograma.** DOACs têm meia-vida relativamente curta e, em geral, não precisam de ponte em nenhum cenário; varfarina exige mais tempo para redução e recuperação do efeito. A função renal pesa sobretudo na duração do efeito de alguns DOACs, e procedimentos com anestesia neuraxial ou risco hemorrágico muito alto exigem cronograma específico — não existe uma janela universal aplicável a todos os anticoagulantes.

**Reinício pós-operatório depende sempre da hemostasia, em qualquer ramo desta árvore**: se a hemostasia não estiver adequada, adiar o reinício e reavaliar o sangramento antes de retomar qualquer antitrombótico.