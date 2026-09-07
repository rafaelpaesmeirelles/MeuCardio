---
title: "Fluxograma: monitoramento ambulatorial da amiodarona"
slug: fluxograma-monitoramento-amiodarona-ambulatorial
theme: "Farmacologia"
kind: protocolo
review_status: pendente_revisao
summary: "Árvore prática do retorno ambulatorial em uso crônico de amiodarona — sintomas sentinela, eixos tireoide/fígado/pulmão/olho/ECG, e desfechos manter-com-reforço / pausar / referenciar. Complementa o protocolo textual de monitoramento."
source_refs:
  - "Hindricks G, et al. 2020 ESC Guidelines for the diagnosis and management of atrial fibrillation. Eur Heart J. 2021;42(5):373-498."
  - "Van Gelder IC, et al. 2024 ESC Guidelines for the management of atrial fibrillation. Eur Heart J. 2024;45(36):3314-3414."
  - "Joglar JA, et al. 2023 ACC/AHA/ACCP/HRS Guideline for the Diagnosis and Management of Atrial Fibrillation. Circulation. 2024;149(1):e1-e156."
  - "Corpus MeuCardio: monitoramento-ambulatorial-da-amiodarona-tireoide-figado-pulmao-e-olho.md; amiodarona-cloridrato.md."
---

# Fluxograma: monitoramento ambulatorial da amiodarona

Uso crônico de amiodarona exige vigilância multissistêmica. Este fluxograma traduz o protocolo textual irmão em árvore de decisão para o retorno ambulatorial. Intervalos de laboratório/imagem seguem a lógica qualitativa alinhada a diretrizes de FA (ESC/AHA) e ao mnemônico TRETA do corpus — **sem inventar cortes percentuais de ensaio**.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Retorno ambulatorial: paciente em uso crônico de amiodarona"]
  D0{"Há sintoma sentinela?<br/>dispneia/tosse nova · visual · tireoidiano ·<br/>icterícia/dor HD · síncope/bradicardia"}

  Dpulm{"Predomínio respiratório?"}
  Cpulm["Pausar amiodarona enquanto investiga;<br/>RX/TC ± PFR; referenciar pneumologia;<br/>diferenciar IC/infecção/TEP"]

  Dolho{"Predomínio visual grave<br/>ou suspeita de neuropatia óptica?"}
  Colho["Pausar; oftalmologia urgente"]

  Dtir{"Sinais de hipertireoidismo<br/>ou instabilidade arrítmica tireoidiana?"}
  Ctir["Laboratório tireoidiano urgente;<br/>endocrinologia; discutir pausa/troca<br/>com o responsável pelo ritmo"]

  Dhep{"Icterícia, sintomas hepáticos<br/>ou enzimas em alta progressiva?"}
  Chep["Pausar; repetir enzimas ± bilirrubina/INR;<br/>considerar hepatologia"]

  Decg{"Bradicardia sintomática, BAV alto grau<br/>ou QT muito prolongado com risco?"}
  Cecg["Pausar ou reduzir exposição;<br/>revisar interações; ECG; decidir MP/troca"]

  Dcal{"Calendário de vigilância em dia?<br/>TSH e enzimas hepáticas ~6 meses;<br/>RX tórax periódico; ECG nas revisões"}
  Catraso["Completar exames pendentes<br/>antes de reiniciar intervalo longo"]
  Cok["Manter amiodarona;<br/>reforçar educação de sintomas sentinela;<br/>revisar interações digoxina/varfarina/estatina;<br/>agendar próximo laboratório"]

  Dlab{"Achado laboratorial/imagem<br/>anormal no check de rotina?"}
  Cleve["Alteração leve, estável, assintomática<br/>ex.: enzimas levemente ↑ ou TSH limítrofe:<br/>manter com reforço — repetir em intervalo curto;<br/>hipotireoidismo: frequentemente manter + T4<br/>com endocrino"]
  Cgrave["Alteração progressiva/grave ou sintomática:<br/>pausar e referenciar o eixo correspondente"]

  R0 --> D0
  D0 -->|Sim| Dpulm
  Dpulm -->|Sim| Cpulm
  Dpulm -->|Não| Dolho
  Dolho -->|Sim| Colho
  Dolho -->|Não| Dtir
  Dtir -->|Sim| Ctir
  Dtir -->|Não| Dhep
  Dhep -->|Sim| Chep
  Dhep -->|Não| Decg
  Decg -->|Sim| Cecg
  Decg -->|Não — sintoma atípico| Dlab

  D0 -->|Não| Dcal
  Dcal -->|Não| Catraso
  Dcal -->|Sim| Dlab
  Dlab -->|Não — tudo ok| Cok
  Dlab -->|Sim — leve/estável| Cleve
  Dlab -->|Sim — progressivo/grave| Cgrave

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class Cpulm,Colho,Ctir,Chep,Cecg,Catraso,Cok,Cleve,Cgrave conduta;
```

## O que a árvore não mostra

- **Posologia** de ataque/manutenção — ver monografia e bulas.
- **Percentuais de incidência** — não são necessários para decidir pausar vs reforçar.
- **Toxicidade pulmonar** pode apresentar-se de forma subaguda; ausência de febre não afasta.
- **Após pausa**, a meia-vida longa implica que melhora clínica/laboratorial pode ser lenta.
- Interação **amiodarona–digoxina**: se houver sinalizadores de digitálico, seguir `sinalizadores-ambulatoriais-de-toxicidade-da-digoxina.md` em paralelo.
