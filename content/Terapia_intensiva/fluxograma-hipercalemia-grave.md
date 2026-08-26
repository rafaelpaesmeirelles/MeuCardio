---
title: "Fluxograma: hipercalemia aguda no adulto"
slug: fluxograma-hipercalemia-grave
theme: "Terapia intensiva"
kind: fluxograma
summary: "Conduta adulta na hipercalemia moderada ou grave: confirma o resultado, separa alteração eletrocardiográfica de parada, estabiliza a membrana com dose equivalente de cálcio, desloca potássio e organiza remoção definitiva."
review_status: revisado
review_note: "Reescrito em 26/08/2026 contra ERC/RCUK 2025 e UK Kidney Association 2023. Corrigida dose potencialmente insuficiente: 10 mL de gluconato de cálcio a 10% foi substituído pela dose equivalente do algoritmo 2025 (30 mL a 10% em 10 min quando o cloreto não estiver disponível; cloreto 10 mL a 10% em 5 min é a opção preferida no algoritmo). Removidos patiromer e combinação automática de diurético/quelante/diálise dos ramos de emergência. O regime de correção com ciclossilicato de sódio e zircônio foi explicitado como 10 g VO três vezes ao dia, por até 48–72 horas conforme resposta e protocolo, com potássio seriado; não é dose única. O fluxo é adulto e não deve ser extrapolado à pediatria, cujas recomendações de cálcio na parada diferem."
source_refs: ["Lott C, Karageorgos V, Abelairas-Gomez C, et al. European Resuscitation Council Guidelines 2025 Special Circumstances in Resuscitation. Resuscitation. 2025;215 Suppl 1:110753. DOI: 10.1016/j.resuscitation.2025.110753. PMID: 41117569.", "Resuscitation Council UK. Special circumstances guidelines: hyper/hypokalaemia and other electrolyte disorders. Publicado em 27/10/2025. Recomendações e doses conferidas em 26/08/2026. https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/special-circumstances-guidelines", "Alfonzo A, Harrison A, Baines R, Chu A, Mann S, MacRury M. UK Kidney Association Clinical Practice Guideline: Management of Hyperkalaemia in Adults. Publicada em 19/12/2023; revisão programada para 19/10/2026. https://www.ukkidney.org/health-professionals/guidelines/treatment-acute-hyperkalaemia-adults-0"]
---

# Hipercalemia aguda no adulto

Usar este fluxo no **adulto** com potássio confirmado de 6,0 mmol/L ou mais,
ou com alteração eletrocardiográfica compatível e forte suspeita clínica. Repetir
imediatamente uma amostra possivelmente hemolisada, mas não atrasar tratamento se
há instabilidade, alteração de condução ou parada. Suspender fontes de potássio,
obter ECG de 12 derivações e iniciar monitorização contínua.

## Árvore de decisão

```mermaid
flowchart TD
  A["K ≥6,0 mmol/L ou suspeita forte<br/>com alteração eletrocardiográfica"]
  B["Confirmar amostra sem hemólise; ECG contínuo;<br/>glicemia, função renal e causa; suspender K"]
  C{"Parada cardiorrespiratória<br/>atribuída à hipercalemia?"}
  D["ALS padrão + cloreto de cálcio 10% 10 mL IV<br/>+ bicarbonato de sódio 50 mmol IV;<br/>usar linhas separadas ou lavar a linha entre ambos"]
  E{"Alteração eletrocardiográfica<br/>na hipercalemia grave?"}
  F["Cloreto de cálcio 10% 10 mL IV em 5 min;<br/>se indisponível, gluconato de cálcio 10%<br/>30 mL IV em 10 min"]
  G{"K 6,0–6,4 mmol/L<br/>ou ≥6,5 mmol/L?"}
  H["Insulina solúvel 10 U + glicose 25 g IV;<br/>salbutamol nebulizado 10–20 mg como adjuvante"]
  N["Insulina solúvel 10 U + glicose 25 g IV;<br/>monitorar glicemia e potássio durante a RCP"]
  I["Se glicemia prévia <7 mmol/L:<br/>glicose 10% a 50 mL/h por 5 h"]
  J["Ciclossilicato de sódio e zircônio 10 g VO<br/>3 vezes ao dia na correção, por até 48–72 h;<br/>ajustar/interromper pelo K seriado e discutir<br/>diálise se hipercalemia grave refratária"]
  K["Repetir K, glicemia e ECG; monitorar rebote;<br/>tratar causa e rever fármacos"]
  L["Reavaliar diagnóstico e tendência;<br/>tratar causa sem aplicar automaticamente<br/>o pacote de hipercalemia moderada/grave"]
  M["Na parada refratária: considerar diálise/ECPR<br/>conforme recursos e protocolo local"]

  A --> B --> C
  C -->|"Sim"| D --> N --> M
  C -->|"Não"| E
  E -->|"Sim"| F --> H
  E -->|"Não"| G
  G -->|"Sim"| H
  G -->|"Não"| L
  H --> I --> J --> K

  classDef action fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class D,F,H,I,J,K,L,M,N action;
```

## O que cada etapa faz

- **Cálcio estabiliza a membrana; não remove potássio.** Na hipercalemia grave
  com alteração eletrocardiográfica, o algoritmo ERC/RCUK 2025 prefere 10 mL de
  cloreto de cálcio a 10% em 5 minutos. Quando o cloreto não está disponível,
  a dose alternativa é 30 mL de gluconato a 10% em 10 minutos. Não tratar os
  dois volumes como equivalentes frasco a frasco.
- **Insulina/glicose desloca potássio para dentro da célula.** Salbutamol é
  adjuvante e não substitui insulina/glicose. Verificar glicemia repetidamente;
  a infusão de glicose após o bólus é indicada pelo algoritmo quando a glicemia
  pré-tratamento é inferior a 7 mmol/L.
- **Remoção é necessária para evitar rebote.** O algoritmo 2025 inclui
  ciclossilicato de sódio e zircônio no regime de correção de **10 g por via
  oral três vezes ao dia**, por até 48–72 horas conforme resposta e protocolo,
  com potássio seriado para ajustar ou interromper após a correção; não se trata
  de uma dose única. Recomenda-se considerar diálise na hipercalemia grave
  refratária. Diurético só é pertinente quando há
  diurese e contexto volêmico apropriado; não é um degrau obrigatório.
- **Patiromer não pertence ao resgate imediato.** Seu início de ação é tardio e
  a bula não o indica como tratamento emergencial da hipercalemia com risco de
  vida. Poliestirenossulfonato também não substitui as intervenções de ação
  rápida nem a diálise quando esta é necessária.

## Limites de segurança

Este fluxo não autoriza repetir cálcio indefinidamente nem prescrever insulina
sem monitorização de glicose e potássio. Alterações eletrocardiográficas são
insensíveis: um ECG aparentemente normal não torna seguro observar um paciente
com potássio muito elevado. A decisão de diálise considera refratariedade,
função renal, acidose, sobrecarga, catabolismo e possibilidade de rebote.

Na intoxicação digitálica, hiperpotassemia pode indicar fragmentos Fab; seguir o
fluxo específico e acionar toxicologia, em vez de transportar automaticamente
toda esta sequência. Em criança, usar protocolo pediátrico próprio; as doses e
as recomendações da parada adulta acima não devem ser convertidas por peso.

## Tudo com Tudo

- [Fluxograma de parada cardiorrespiratória no adulto](/biblioteca/fluxograma-parada-cardiorrespiratoria-ritmo-inicial)
- [Fluxograma de intoxicação digitálica](/biblioteca/fluxograma-intoxicacao-digitalica)
- [Síndrome BRASH](/biblioteca/sindrome-brash-bradicardia-insuficiencia-renal-bloqueio-av-choque-e-hipercalemia)
- [Ciclossilicato de sódio e zircônio na hipercalemia](/biblioteca/ciclossilicato-de-sodio-e-zirconio-szc-na-hipercalemia-o-ensaio-harmonize)
- [Patiromer e bloqueio do SRAA no DIAMOND](/biblioteca/hipercalemia-como-barreira-ao-bloqueio-do-sraa-o-ensaio-diamond-com-patiromer)
- [Hipercalemia e intoxicação por betabloqueador/BCC](/biblioteca/hipercalemia-grave-e-intoxicacao-por-betabloqueador-ou-bloqueador-de-canal-de-calcio)
