---
title: "Intoxicação por betabloqueador ou antagonista de cálcio"
slug: fluxograma-intoxicacao-por-betabloqueador-ou-antagonista-de-calcio
theme: "Terapia intensiva"
kind: fluxograma
summary: "Fluxo AHA 2025 para hipotensão, bradicardia ou choque com risco de vida por betabloqueador ou bloqueador de canal de cálcio: separa glucagon e o timing da insulina no betabloqueador, cálcio e insulina precoce no bloqueador de cálcio, e VA-ECMO no choque cardiogênico refratário."
review_status: revisado
source_refs: ["Cao D, Arens AM, Chow SL, et al. Part 10: Adult and Pediatric Special Circumstances of Resuscitation: 2025 American Heart Association Guidelines for Cardiopulmonary Resuscitation and Emergency Cardiovascular Care. Circulation. 2025;152(16_suppl_2):S578-S672. DOI: 10.1161/CIR.0000000000001380. PMID: 41122889 — recomendações separadas e graduadas para betabloqueador e bloqueador de canal de cálcio, incluindo insulina, vasopressor, glucagon, cálcio, emulsão lipídica e ECLS", "St-Onge M, Anseeuw K, Cantrell FL, et al. Experts Consensus Recommendations for the Management of Calcium Channel Blocker Poisoning in Adults. Crit Care Med. 2017;45(3):e306-e315. DOI: 10.1097/CCM.0000000000002087. PMID: 27749343. PMCID: PMC5312725 — consenso específico de BCC, evidência de qualidade muito baixa; detalha cálcio, insulina em alta dose, vasopressor e escalonamento", "Engebretsen KM, Kaczmarek KM, Morgan J, Holger JS. High-dose insulin therapy in beta-blocker and calcium channel-blocker poisoning. Clin Toxicol (Phila). 2011;49(4):277-283. DOI: 10.3109/15563650.2011.582471. PMID: 21563902 — revisão histórica da base pré-AHA 2025; não usada para igualar as duas intoxicações"]
review_note: "Revisão de 26/08/2026: removidos os dois marcadores humanos mediante confronto com a diretriz oficial AHA 2025. O fluxo anterior tratava atropina, glucagon e cálcio como bloco indiferenciado, colocava insulina antes do vasopressor em ambas as intoxicações e apresentava emulsão lipídica com dose fixa como resgate padrão. A AHA distingue: no betabloqueador, vasopressor é recomendado, glucagon é razoável e insulina em alta dose entra quando a hipotensão é refratária ao vasopressor; no bloqueador de canal de cálcio, insulina em alta dose e vasopressor são recomendados para hipotensão, cálcio é razoável e a utilidade do glucagon é incerta. Emulsão lipídica tem utilidade incerta nos dois cenários. Doses foram retiradas deste fluxograma e remetidas ao protocolo institucional/toxicologia em tempo real."
---

# Intoxicação por betabloqueador ou antagonista de cálcio

Este fluxo é para **hipotensão, bradicardia sintomática, choque ou parada com
risco de vida** após exposição a betabloqueador ou bloqueador de canal de cálcio
(BCC). Suporte básico/avançado, ventilação, monitorização, acesso vascular e
contato imediato com centro de informação toxicológica devem ocorrer em
paralelo. Atropina e marca-passo podem ser tentados conforme o algoritmo de
bradicardia, mas têm resposta variável e não devem atrasar a terapia dirigida.

## Árvore de decisão

```mermaid
flowchart TD
  R["Hipotensão, bradicardia sintomática,<br/>choque ou parada após possível<br/>betabloqueador ou BCC"]
  P0["Suporte padrão sem atraso; ECG, glicemia,<br/>eletrólitos, função ventricular/vasoplegia;<br/>acionar centro toxicológico e UTI"]
  D0{"Exposição predominante?"}

  BB1["BETABLOQUEADOR com hipotensão:<br/>iniciar vasopressor; glucagon em bólus<br/>seguido de infusão é razoável se houver<br/>bradicardia sintomática ou hipotensão"]
  BBD{"Hipotensão persiste apesar<br/>do vasopressor?"}
  BB2["Administrar insulina em alta dose<br/>com manutenção da euglicemia;<br/>cálcio também pode ser considerado"]

  CCB1["BCC com hipotensão:<br/>administrar insulina em alta dose<br/>e vasopressor; cálcio IV é razoável"]
  CCB2["Glucagon no BCC tem utilidade incerta;<br/>não substituir insulina, vasopressor<br/>e cálcio por resposta imprevisível"]

  D1{"Choque cardiogênico persiste<br/>apesar das intervenções farmacológicas?"}
  C1["Continuar terapia específica e monitorar<br/>glicemia, potássio, sobrecarga de volume,<br/>perfusão e resposta hemodinâmica"]
  C2["Mobilizar precocemente ECLS/VA-ECMO<br/>em centro experiente; é razoável no choque<br/>cardiogênico refratário ou parada por intoxicação"]
  C3["Emulsão lipídica IV não é resgate automático:<br/>utilidade incerta em BB e BCC; considerar apenas<br/>com toxicologista em caso altamente selecionado"]

  R --> P0 --> D0
  D0 -->|"Betabloqueador"| BB1 --> BBD
  BBD -->|"Não"| C1
  BBD -->|"Sim"| BB2 --> D1
  D0 -->|"BCC"| CCB1 --> CCB2 --> D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| C2
  C2 -. "decisão individualizada" .-> C3

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## Por que os ramos não podem ser fundidos

Na intoxicação por **betabloqueador**, a AHA 2025 recomenda vasopressor para
hipotensão (Classe 1, C-EO), considera razoável glucagon em bólus seguido de
infusão para bradicardia sintomática ou hipotensão (Classe 2a, C-LD) e posiciona
insulina em alta dose quando a hipotensão permanece refratária ao vasopressor
(Classe 1, C-LD). Cálcio pode ser considerado, mas seu apoio vem de casos
confundidos por tratamentos simultâneos (Classe 2b, C-EO).

Na intoxicação por **BCC**, insulina em alta dose (Classe 1, B-NR) e vasopressor
(Classe 1, C-LD) são recomendados para hipotensão; cálcio é razoável (Classe 2a,
C-EO). A utilidade de glucagon em bólus seguido de infusão é **incerta**
(Classe 2b, C-EO). Portanto, escrever que “glucagon e cálcio frequentemente
falham” em ambas as intoxicações apaga diferenças que mudam a sequência.

## Insulina em alta dose: controles inseparáveis

Insulina em alta dose exige protocolo com dextrose e monitorização frequente de
glicemia e potássio. Hipoglicemia, hipocalemia e sobrecarga de volume são riscos
explicitamente apontados pela AHA. O potássio pode cair por deslocamento
intracelular; reposição e velocidade de correção dependem de concentração,
arritmia e protocolo, não de um reflexo automático.

Este fluxograma deliberadamente não replica dose, concentração ou velocidade de
infusão. A prescrição deve ser conferida no protocolo institucional e com o
centro toxicológico, porque envolve insulina em ordem de grandeza muito superior
ao uso metabólico habitual, dextrose titulada e diferentes sais de cálcio. O
documento específico de intoxicação por BCC do acervo contém a tabela
farmacológica e a graduação do consenso de 2017.

## Resgate e limites

- ECLS/VA-ECMO é razoável quando o choque cardiogênico permanece refratário às
  intervenções farmacológicas: Classe 2a, C-LD no betabloqueador adulto e
  Classe 2a, B-NR no BCC adulto. A mobilização deve começar antes do colapso
  irreversível.
- A utilidade da emulsão lipídica intravenosa é incerta tanto no betabloqueador
  quanto no BCC (Classe 2b, C-EO). A AHA registra relatos de parada abrupta após
  sua administração; ela não deve ocupar automaticamente um degrau obrigatório
  antes da ECMO.
- Atenolol, nadolol e sotalol podem ser dialisáveis em intoxicação grave; essa
  possibilidade depende do agente e não se aplica à classe inteira.
- Propranolol pode causar bloqueio de canal de sódio e QRS largo; sotalol pode
  prolongar repolarização. Esses fenótipos exigem terapias elétricas/toxicológicas
  adicionais e não cabem no ramo hemodinâmico genérico.
- Reposição volêmica deve ser guiada por responsividade e congestão. Insistir em
  salina como medida “essencial” contínua pode piorar sobrecarga sem corrigir a
  depressão miocárdica.

## Tudo com Tudo

- [Diretriz AHA 2025 de intoxicações cardiotóxicas graves](../Farmacologia/diretriz-aha-2025-intoxicacoes-cardiotoxicas-graves.md)
- [Intoxicação grave por bloqueador de canal de cálcio: insulina e suporte mecânico](intoxicacao-grave-por-bloqueador-de-canal-de-calcio-insulina-em-dose-alta-euglicemica-e-escalonamento-para-suporte-mecanico.md)
- [Hipercalemia grave e intoxicação por betabloqueador/BCC](hipercalemia-grave-e-intoxicacao-por-betabloqueador-ou-bloqueador-de-canal-de-calcio.md)
- [Choque misto: componente cardiogênico e vasodilatador](choque-misto-componente-cardiogenico-e-vasodilatador-simultaneos-titulacao-dupla.md)
- [Síndrome BRASH: diferenciar sinergia terapêutica de superdose](../Farmacologia/sindrome-brash-bradicardia-insuficiencia-renal-bloqueio-av-choque-e-hipercalemia.md)
