---
title: "Sinalizadores ambulatoriais pós-alta de UTI: infecção, dispositivo, IC e cognição"
slug: sinalizadores-ambulatoriais-pos-alta-uti-infeccao-dispositivo-ic-cognicao
theme: "Terapia intensiva"
kind: protocolo
fonte_producao: grok
summary: "Quatro eixos de alarme no consultório após UTI cardiológica: infecção (incluindo sítio/dispositivo), falha ou complicação de dispositivo, descompensação de IC, e piora cognitiva/PICS — com destino PS vs retorno precoce, sem doses."
review_status: pendente_revisao
review_note: "Irmão do protocolo pós-UTI/choque 07/09/2026. Lacuna fina: eixos infecção + dispositivo + IC + cognicao no pós-alta. Anti-colisão com #826–858 e com Dispositivos #835 (CDI/eletrodo — não reescreve). Fontes: HFA/ESC CS PMID 32469155; ESC HF 2021 PMID 34447992. Sem doses; sem PMID inventado."
source_refs:
  - "Chioncel O, Parissis J, Mebazaa A, et al. Epidemiology, pathophysiology and contemporary management of cardiogenic shock – a position statement from the Heart Failure Association of the European Society of Cardiology. Eur J Heart Fail. 2020;22(8):1315-1341. DOI: 10.1002/ejhf.1922. PMID: 32469155"
  - "McDonagh TA, Metra M, Adamo M, et al. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726. DOI: 10.1093/eurheartj/ehab368. PMID: 34447992"
---

# Sinalizadores ambulatoriais pós-alta de UTI: infecção, dispositivo, IC e cognição

Complemento operacional de [`sinalizadores-ambulatoriais-pos-uti-choque-cardiogenico-quando-escalar`](sinalizadores-ambulatoriais-pos-uti-choque-cardiogenico-quando-escalar.md). Foco nos **quatro motivos** mais frequentes de ligação/consultório pós-UTI cardiológica quando a clínica precisa **escalar**.

Não substitui o pacote de Dispositivos sobre eletrodo/CDI ambulatorial (PR [#835](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/835)); aqui o eixo “dispositivo” é **pós-UTI** (acesso vascular, MCS temporário recente, infecção de sítio, alarme geral que pede PS).

## 1. Infecção

| Destino | Sinais |
|---|---|
| **PS agora** | Febre alta + calafrios + hipotensão / confusão / oligúria; eritema expansivo / secreção purulenta em sítio de cateter/dispositivo; suspeita de sepse |
| **Retorno precoce** | Febre baixa sem instabilidade; dor local sem celulite expansiva; cultura pendente com dúvida clínica |
| **Plano** | Sem febre, sítio limpo, orientação de vigilância escrita |

Precipitante infeccioso agrava trajetória pós-choque (HFA/ESC PMID 32469155 — infecção como fator de deterioração). Não iniciar “antibiótico de consultório” neste documento.

## 2. Dispositivo / sítio vascular pós-UTI

| Destino | Sinais |
|---|---|
| **PS agora** | Sangramento ativo / hematoma expansivo; isquemia de membro; alarme crítico de dispositivo; choque CDI apropriado recente com sintomas; suspeita de falha mecânica |
| **Retorno precoce** | Dor em sítio sem expansão; edema assimétrico leve; dúvida de infecção local; interrogatório de dispositivo sem choque recente |
| **Plano** | Sítio cicatrizando, sem alarme, educação de sinais |

Para disfunção de eletrodo/choque CDI em seguimento crônico de dispositivo, preferir o pacote de Dispositivos — não duplicar aqui.

## 3. Insuficiência cardíaca / trajetória pós-choque

| Destino | Sinais |
|---|---|
| **PS agora** | Edema pulmonar, ortopneia grave, hipoperfusão, síncope, dor isquêmica em curso |
| **Retorno precoce** | Ganho de peso, edema progressivo, dispneia de esforço nova, intolerância sem hipoxemia — janela curta (ESC HF 2021 PMID 34447992: continuidade e reavaliação) |
| **Plano** | Compensado, adesão e alarmes escritos, retorno programado |

**Não protocolar doses** de diurético/GDMT neste texto.

## 4. Cognição / PICS (síndrome pós-cuidados intensivos)

| Destino | Sinais |
|---|---|
| **PS agora** | Déficit focal novo, rebaixamento, agitação com risco, convulsão, suspeita de AVC/AIT |
| **Retorno precoce** | Confusão flutuante, déficit de memória/atenção com impacto em adesão à terapia, humor grave com risco — acionar rede (neuro/geriatria/saúde mental/rehab) |
| **Plano** | Queixa cognitiva leve estável, cuidador presente, educação + retorno |

Cognição alterada aumenta risco de falha de adesão e atraso em reconhecer congestão/infecção — tratar como **fator de risco operacional**, não como “só cansaço”.

## Checklist rápido dos 4 eixos

1. Infecção com sepse ou sítio agressivo? → **PS**.
2. Dispositivo/sítio com sangramento, isquemia ou alarme crítico? → **PS**.
3. IC com congestão aguda ou hipoperfusão? → **PS**; congestão leve → **retorno precoce**.
4. Cognitivo: focal/agudo → **PS**; PICS com impacto → **retorno + rede**.
5. Sem alarme nos quatro? → plano escrito + data de retorno.

## Limite

Só define **destino**. Diagnóstico etiológico hospitalar, culturas, imagem de dispositivo e ajuste farmacológico ficam fora.
