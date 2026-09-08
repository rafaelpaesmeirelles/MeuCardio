---
title: "Sinalizadores ambulatoriais de SVT recorrente: quando escalar"
slug: sinalizadores-ambulatoriais-de-svt-recorrente-quando-escalar
theme: "Arritmias"
kind: protocolo
fonte_producao: grok
summary: "TSV paroxística recorrente no consultório: quais sinais pedem PS/eletrofisiologia urgente, quais permitem discussão eletiva de ablação e como não confundir com FA pré-excitada ou taquicardiomiopatia."
review_status: revisado
review_note: "Revisão científica e adversarial 08/09/2026: reconstruídos findings PR864, urgência contextual, referências e navegação; fonte grok preservada."
source_refs:
  - "Brugada J, Katritsis DG, Arbelo E, et al. 2019 ESC Guidelines for the management of patients with supraventricular tachycardia. Eur Heart J. 2020;41(5):655-720. DOI: 10.1093/eurheartj/ehz467. PMID: 31504425"
  - "Page RL, Joglar JA, Caldwell MA, et al. 2015 ACC/AHA/HRS Guideline for the Management of Adult Patients With Supraventricular Tachycardia. Circulation. 2016;133(14):e506-e574. DOI: 10.1161/CIR.0000000000000311. PMID: 26399663"
---

# Sinalizadores ambulatoriais de SVT recorrente: quando escalar

Pergunta de **consultório**: diante de taquicardia supraventricular (TSV/SVT) paroxística **recorrente** documentada ou altamente sugestiva, **quando encaminhar agora** (PS / eletrofisiologia urgente) e quando oferecer **via eletiva** (documentar + discutir ablação)?

Não substitui:
- manejo agudo de TSV de QRS estreito — [`fluxograma-taquicardia-supraventricular-qrs-estreito-esc-2019`](/biblioteca/fluxograma-taquicardia-supraventricular-qrs-estreito-esc-2019) e [`taquicardia-supraventricular-diagnostico-e-manejo-esc-2019`](/biblioteca/taquicardia-supraventricular-diagnostico-e-manejo-esc-2019);
- pré-excitação / WPW no consultório → PS — [`pre-excitacao-wpw-no-consultorio-sinais-vermelhos-quando-ir-ao-ps`](/biblioteca/pre-excitacao-wpw-no-consultorio-sinais-vermelhos-quando-ir-ao-ps);
- TVNS ambulatorial — `sinalizadores-ambulatoriais-de-taquicardia-ventricular-nao-sustentada-quando-escalar` (PR #839, se mergeado).

## Princípio

Padrão de pré-excitação no ECG não equivale à síndrome de WPW, que associa substrato a taquiarritmia clínica. Síncope remota, explicada e com recuperação completa pede avaliação do contexto e encaminhamento prioritário se suspeita arrítmica; não PS automático. TSV atual persistente/refratária requer cuidado agudo monitorado mesmo sem hipotensão, antes da via eletiva.


**A maior parte das TSV paroxísticas sintomáticas tem ablação por cateter como opção de primeira linha após discussão de riscos/benefícios (ESC 2019).** O consultório decide o **tempo**: alarme hemodinâmico/estrutural → agora; recorrência sem alarme → eletivo com ECG documentado.

- ESC 2019 (PMID 31504425): ablação Classe I (LOE A/B) para a maioria das TSV sintomáticas (AVNRT, AVRT, flutter típico, taquicardia atrial focal sintomática selecionada); farmacoterapia crônica tem papel menor e sem “receita ambulatorial” inventada aqui.
- ACC/AHA/HRS 2015 (PMID 26399663): pacientes com TSV recorrente sintomática devem ser avaliados para estratégia definitiva (incluindo ablação); síncope ou intolerância hemodinâmica elevam a urgência da estratificação.

## Sinalizadores → escalar agora (PS ou EP urgente)

| Domínio | Sinalizador |
|---|---|
| Hemodinâmico / neurológico | Síncope, pré-síncope recorrente com TSV, dor torácica isquêmica, dispneia aguda, confusão nova, hipotensão sintomática |
| Elétrico de alto risco | QRS largo irregular muito rápido (suspeita de FA pré-excitada), pré-excitação manifesta + taquicardia sustentada, degeneração documentada para FV |
| Estrutural / miocárdio | Suspeita de taquicardiomiopatia (FEVE reduzida nova com TSV frequente/incessante), IC descompensada |
| Frequência / refratariedade | Crises muito frequentes com inviabilidade de alta segura, falha de manobras vagais **e** necessidade de ambiente monitorado |
| Gestação / puerpério | TSV com instabilidade ou dúvida diagnóstica — não “ajustar em casa” |
| Pós-ablação recente | Recorrência precoce com sintomas graves ou complicação suspeita |

**Conduta:** não liberar “só com retorno em semanas” se há linha da tabela. Documentar traçado de 12 derivações (sinusal e, se possível, durante a crise). Taquicardia de QRS largo irregular + pré-excitação = via de emergência — ver protocolo irmão de WPW.

## Sem sinalizador de alarme → via eletiva

1. **Confirmar o diagnóstico** (ECG/Holter/monitor de eventos): TSV de QRS estreito vs. sinusal vs. FA/flutter vs. aberrância.
2. **ECG de 12 derivações em ritmo sinusal** — procurar pré-excitação manifesta intermitente no histórico (delta, PR curto); via oculta conduz apenas retrogradamente e não produz delta, portanto ECG normal não a exclui.
3. **Excluir gatilhos reversíveis** óbvios (tireotoxicose clínica, estimulantes, anemia grave) sem atrasar a oferta de ablação se a TSV já é recorrente e tipicamente reentrante.
4. **Discutir ablação** como opção de primeira linha (ESC 2019) — encaminhar à eletrofisiologia **eletiva**.
5. **Ecocardiograma** se sintomas de IC, TSV frequente/incessante ou suspeita de cardiopatia estrutural.
6. Evitar inventar esquema antiarrítmico ambulatorial sem diagnóstico elétrico claro e sem seguir a diretriz do tipo de TSV.

## Checklist de 90 segundos no consultório

1. Há síncope recente associada à crise atual, instabilidade, QRS largo irregular ou pré-excitação + crise? → **PS agora**.
2. Há FEVE nova/baixa ou TSV incessante? → **escalar (urgente/EP)** — suspeita de taquicardiomiopatia.
3. TSV recorrente, ECG/eco sem alarme, paciente estável? → **via eletiva** (documentar + discutir ablação).
4. Pré-excitação manifesta no ECG basal? → usar o protocolo de WPW; não tratar como “TSV comum”.

## Armadilhas

- Tratar toda TSV recorrente como “ansiedade” sem traçado.
- Liberar após síncope só porque “passou sozinha”.
- Confundir FA pré-excitada com TSV de QRS estreito e usar bloqueio nodal no consultório.
- Atrasar EP eletiva indefinidamente em TSV típica recorrente sintomática quando a ablação já é Classe I.
- Inventar doses de adenosina/antiarrítmicos orais neste protocolo.

## Limite da evidência

ESC 2019 e ACC/AHA/HRS 2015 definem **indicação e papel da ablação**, não um limiar único de “número de crises/mês” que separe sempre urgente de eletivo. A decisão de escalar combina sintoma de alarme, morfologia (estreito vs. largo/irregular), pré-excitação e impacto estrutural — não o Holter isolado.
