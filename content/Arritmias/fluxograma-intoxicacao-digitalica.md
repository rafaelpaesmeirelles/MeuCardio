---
title: "Fluxograma: intoxicação digitálica com risco de vida"
slug: fluxograma-intoxicacao-digitalica
theme: "Arritmias"
kind: fluxograma
summary: "Conduta na suspeita de toxicidade por digoxina: reconhecer arritmia, bloqueio ou hiperpotassemia de risco, administrar fragmentos Fab sem atraso e calcular a neutralização conforme quantidade ingerida ou concentração sérica."
review_status: revisado
review_note: "Reescrito em 26/08/2026 contra AHA 2025 e o rótulo FDA/DailyMed vigente do DigiFab. Corrigido erro de dose potencialmente grave: na ingestão aguda de quantidade desconhecida, o rótulo indica 20 frascos (podendo iniciar 10 e completar mais 10), não 10 no adulto/5 na criança. Separada a dose empírica da toxicidade crônica sem nível (6 frascos se ≥20 kg; 1 se <20 kg). Removida a árvore baseada no temor histórico de 'coração de pedra': a fonte primária prioriza Fab e orientação toxicológica, sem sustentar uma proibição universal de cálcio neste fluxo."
source_refs: ["Cao D, Arens AM, Chow SL, et al. Part 10: Adult and Pediatric Special Circumstances of Resuscitation: 2025 American Heart Association Guidelines for Cardiopulmonary Resuscitation and Emergency Cardiovascular Care. Circulation. 2025;152(16 Suppl 2):S578-S672. DOI: 10.1161/CIR.0000000000001380. PMID: 41122889.", "DigiFab (Digoxin Immune Fab [Ovine]). Prescribing Information aprovado pelo FDA, DailyMed SPL setid c05ee6a5-c98b-45f4-83fd-40781639d653. Seções 1, 2.1 e 5.3 conferidas em 26/08/2026. https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=c05ee6a5-c98b-45f4-83fd-40781639d653"]
---

# Intoxicação digitálica com risco de vida

Suspeitar diante de náusea/vômitos, alteração visual, confusão, bradicardia,
bloqueio atrioventricular ou arritmia ventricular em pessoa exposta a digoxina.
Suspender o fármaco, obter ECG contínuo, potássio, função renal e concentração
sérica, sem esperar o resultado para tratar manifestação de risco de vida.

## Árvore de decisão

```mermaid
flowchart TD
  A["Suspeita de toxicidade por digoxina"] --> B["ECG contínuo + potássio + função renal<br/>+ concentração sérica; suspender digoxina;<br/>acionar toxicologia/centro de informação toxicológica"]
  B --> C{"Há manifestação de risco de vida?<br/>Arritmia ventricular grave, bradicardia progressiva,<br/>BAV de 2º/3º grau refratário à atropina ou<br/>K >5,5 mEq/L no adulto / >6 mEq/L na criança<br/>com sinais rapidamente progressivos"}
  C -->|"Sim"| D(["Administrar DigiFab sem esperar nova dosagem;<br/>calcular neutralização quando os dados forem conhecidos;<br/>manter suporte do ritmo e da perfusão"])
  C -->|"Não"| E{"Ingestão aguda potencialmente fatal ou<br/>concentração no limiar do rótulo?<br/>≥10 mg no adulto; ≥4 mg ou >0,1 mg/kg na criança;<br/>nível de equilíbrio ≥10 ng/mL;<br/>toxicidade crônica >6 ng/mL no adulto<br/>ou >4 ng/mL na criança"}
  E -->|"Sim"| D
  E -->|"Não"| F(["Monitorização contínua e reavaliação seriada;<br/>tratar causas associadas; administrar Fab se surgir<br/>critério clínico, eletrolítico ou de exposição"])
  D --> G["Monitorar ECG, pressão e potássio de perto:<br/>o K pode cair rapidamente após a neutralização"]

  classDef action fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class D,F action;
```

## Como calcular os frascos de DigiFab

Cada frasco contém 40 mg de Fab e neutraliza aproximadamente **0,5 mg de
digoxina**. Arredondar o resultado para o frasco inteiro seguinte.

- **Quantidade corporal conhecida:** frascos = carga corporal de digoxina (mg)
  ÷ 0,5. Para comprimidos de digoxina, o rótulo estima carga corporal como
  quantidade ingerida × 0,8; cápsulas e digitoxina têm biodisponibilidade
  diferente e não devem receber automaticamente o fator 0,8.
- **Toxicidade crônica com concentração sérica conhecida:** frascos =
  concentração (ng/mL) × peso (kg) ÷ 100.
- **Ingestão aguda de quantidade desconhecida, sem nível disponível:**
  **20 frascos**. O rótulo permite iniciar 10 e administrar os 10 restantes se
  necessário para reduzir risco de reação febril; em criança <20 kg, monitorar
  sobrecarga de volume.
- **Toxicidade crônica sem concentração sérica:** **6 frascos** em adultos e
  crianças ≥20 kg; **1 frasco** em lactentes e crianças <20 kg.

Na emergência com risco de vida, a estimativa imperfeita não deve atrasar o
antídoto. Falta de resposta ao Fab deve levar à reconsideração do diagnóstico,
da dose neutralizante e de causas concomitantes.

## Hiperpotassemia e suporte do ritmo

Hiperpotassemia na intoxicação aguda é marcador de gravidade e indica Fab nos
limiares do rótulo. Medidas temporizadoras e estabilização de membrana devem ser
individualizadas com toxicologia e não podem atrasar o antídoto. Após o Fab, o
potássio pode entrar rapidamente na célula e produzir hipopotassemia; acompanhar
de perto nas primeiras horas e repor com cautela quando necessário.

Enquanto o Fab é obtido, executar suporte avançado compatível com o ritmo e a
perfusão. Desfibrilação continua indicada em FV/TV sem pulso. Atropina, pacing,
antiarrítmico ou cardioversão no paciente com pulso dependem do fenótipo e de
orientação toxicológica; nenhum deles substitui a neutralização. Hemodiálise,
hemofiltração, hemoperfusão e plasmaférese **não são recomendadas** para remover
digoxina/digitoxina na toxicidade grave (AHA 2025, Classe 3: sem benefício,
B-NR).

## Tudo com Tudo

- [Diretriz AHA 2025 de intoxicações cardiotóxicas graves](/biblioteca/diretriz-aha-2025-intoxicacoes-cardiotoxicas-graves)
- [Monografia do anticorpo antidigoxina Fab](/biblioteca/anticorpo-antidigoxina-fab-ovino-digifab)
- [Intoxicação digitálica: manejo agudo e Fab](/biblioteca/intoxicacao-digitalica-manejo-agudo-e-anticorpo-antidigoxina-fab)
- [Fluxograma de bradicardia sintomática no adulto](/biblioteca/fluxograma-bradicardia-sintomatica-manejo-agudo)
- [Fluxograma de parada cardiorrespiratória no adulto](/biblioteca/fluxograma-parada-cardiorrespiratoria-ritmo-inicial)
