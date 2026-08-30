---
title: "Fluxograma: hiponatremia no adulto com insuficiência cardíaca"
slug: fluxograma-hiponatremia-na-ic
theme: "Insuficiência cardíaca"
kind: fluxograma
summary: "Árvore da hiponatremia (Na <135) na IC: cérebro primeiro, depois volume, depois congestão. Vaptano só no ramo estreito de correção do número, nunca como terapia de desfecho. Emergência neurológica sai para UTI/salina hipertônica sem reproduzir a tabela de bolus não relida."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada em SALT-1/2 (PMID 17105757), TACTICS-HF (PMID 27654854), EVEREST (PMID 17384437) e definição Spasovski (PMID 24569496). Tabela de salina a 3% e limites de correção NÃO relidos — o ramo de emergência aponta para UTI sem dose. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Schrier RW, et al.; SALT Investigators. N Engl J Med. 2006;355(20):2099-2112. PMID: 17105757."
  - "Felker GM, et al. TACTICS-HF. JACC. 2017. PMID: 27654854."
  - "Documento da casa tolvaptana-na-ic-descompensada-o-ensaio-everest-e-o-limite-de-tratar-a-congestao (PMID 17384437)."
  - "Documento da casa hiponatremia-na-insuficiencia-cardiaca-abordagem-pratica."
---

# Fluxograma: hiponatremia no adulto com insuficiência cardíaca

```mermaid
flowchart TD
  R0["Na sérico < 135 mmol/L<br/>no adulto com IC"] --> D1{"Sintomas neurológicos graves?<br/>(convulsão, coma, vômitos incoercíveis,<br/>rebaixamento)"}

  D1 -->|"Sim"| C0(["Emergência de sódio.<br/>UTI + salina hipertônica.<br/>Não usar vaptano como primeira linha.<br/>Tabela de bolus europeia: abrir a fonte<br/>(não reproduzida aqui)"])

  D1 -->|"Não"| D2{"Estado volêmico?"}

  D2 -->|"Hipovolêmico<br/>(diurético em excesso, perdas)"| C1(["Parar diurético. Repor volume.<br/>Não restringir água. Não vaptano"])

  D2 -->|"Euvolêmico"| C2(["Investigar SIADH, tiazídico, SSRI,<br/>carbamazepina, tireoide, adrenal.<br/>Não é o EVEREST"])

  D2 -->|"Hipervolêmico (o usual da IC)"| D3{"Há congestão clínica/imagem?"}

  D3 -->|"Sim"| C3(["Descongestionar: diurético de alça,<br/>bloqueio sequencial se resistente<br/>(ADVOR/CLOROTIC da casa).<br/>Reavaliar Na depois da água sair"])

  D3 -->|"Não, ou já descongestionado<br/>e Na persiste baixo com sintomas<br/>de hipo-osmolaridade"| D4{"A pergunta é prognóstico<br/>ou o número/sintoma osmolar?"}

  D4 -->|"Prognóstico"| C4(["Não prescrever tolvaptana.<br/>EVEREST: morte HR 0,98;<br/>morte CV/internação HR 1,04"])

  D4 -->|"Número / sintoma osmolar"| C5(["Ramo estreito: considerar tolvaptana<br/>curta (SALT sobe o Na; TACTICS<br/>não aumenta respondedores em 24 h).<br/>Monitorar Na, sede e diurese"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

**SODIUM-HF** restringe sódio **na dieta** e não trata hiponatremia. **Piora renal no TACTICS** não autoriza abandonar o diurético de alça — autoriza não somar vaptano achando que o congesto vai “responder” mais em 24 h.

## Mensagem prática

Cérebro primeiro. Volume depois. Congestão em seguida. Vaptano por último, e só para o número — nunca para a sobrevida.
