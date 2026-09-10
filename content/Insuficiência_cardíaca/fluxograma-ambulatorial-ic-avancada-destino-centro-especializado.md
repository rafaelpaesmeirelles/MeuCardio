---
slug: fluxograma-ambulatorial-ic-avancada-destino-centro-especializado
title: 'Fluxograma ambulatorial: IC avançada — destino (centro agora vs. reavaliar)'
kind: fluxograma
theme: Insuficiência cardíaca
summary: Reconhecimento de trajetória de IC avançada e referência oportuna com I-NEED-HELP contextualizado; urgência
  na instabilidade, avaliação especializada e decisão compartilhada sem esperar múltiplas reinternações.
tags: []
source_refs:
- 'McDonagh TA, Metra M, Adamo M, et al. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic
  heart failure. Eur Heart J. 2021;42(36):3599-3726. DOI: 10.1093/eurheartj/ehab368. PMID: 34447992'
- 'Baumwol J. "I Need Help"-A mnemonic to aid timely referral in advanced heart failure. J Heart Lung Transplant.
  2017;36(5):593-594. DOI: 10.1016/j.healun.2017.02.010. PMID: 28258792'
- 'Pagnesi M, Ghiraldin D, Vizzardi E, et al. Detailed Assessment of the "I Need Help" Criteria in Patients With
  Heart Failure: Insights From the HELP-HF Registry. Circ Heart Fail. 2023;16(12):e011003. DOI: 10.1161/CIRCHEARTFAILURE.123.011003.
  PMID: 37909222'
- 'Morris AA, Khazanie P, Drazner MH, et al. Guidance for Timely and Appropriate Referral of Patients With Advanced
  Heart Failure: A Scientific Statement From the American Heart Association. Circulation. 2021;144(15):e238-e250.
  DOI: 10.1161/CIR.0000000000001016. PMID: 34503343'
- 'Baudry G, et al. Identifying and overcoming barriers to referral in advanced heart failure. A scientific statement
  of the Heart Failure Association (HFA) of the ESC. Eur J Heart Fail. 2025. DOI: 10.1002/ejhf.70003. PMID: 40819957'
- 'Peled Y, Ducharme A, Kittleson M, et al. ISHLT Guidelines for the Evaluation and Care of Cardiac Transplant Candidates—2024.
  J Heart Lung Transplant. 2024;43(10):1529-1628.e54. DOI: 10.1016/j.healun.2024.05.010. PMID: 39115488'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: true
---

# Fluxograma ambulatorial: IC avançada — destino ao centro especializado

Prosa: [`sinalizadores-ambulatoriais-de-ic-avancada-quando-encaminhar-centro-lvad-transplante`](/biblioteca/sinalizadores-ambulatoriais-de-ic-avancada-quando-encaminhar-centro-lvad-transplante). Checklist: [`checklist-ambulatorial-i-need-help-encaminhamento-ic-avancada`](/biblioteca/checklist-ambulatorial-i-need-help-encaminhamento-ic-avancada). Árvore técnica / TCPE: [`fluxograma-encaminhamento-ic-avancada-lvad-transplante`](/biblioteca/fluxograma-encaminhamento-ic-avancada-lvad-transplante). Descompensação aguda: [`sinalizadores-ambulatoriais-de-descompensacao-de-ic-quando-encaminhar`](/biblioteca/sinalizadores-ambulatoriais-de-descompensacao-de-ic-quando-encaminhar).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial<br/>IC crônica em seguimento"] --> D1{"Alarme de descompensação aguda?<br/>dispneia em repouso nova ou rapidamente pior / hipoxemia<br/>hipoperfusão / síncope<br/>dor anginosa / arritmia instável"}

  D1 -->|"Sim ou dúvida fundamentada"| C1(["PS / emergência AGORA<br/>Após estabilizar: retomar<br/>avaliação de IC avançada"])

  D1 -->|"Não"| D2{"Há ≥1 critério I-NEED-HELP?<br/>inotrópico · NYHA III–IV / NP altos<br/>órgão-alvo · FEVE <20% ou VD importante<br/>choques CDI · ≥2 intern. IC/ano<br/>edema/escalada diurética<br/>PA baixa · intolerância a GDMT"}

  D2 -->|"Não"| C2(["Manter plano ambulatorial usual<br/>Educar alarmes de piora <br/>Reavaliar I-NEED-HELP a cada visita"])

  D2 -->|"Sim"| D3{"Prioridade alta?<br/>inotrópico atual/recente<br/>episódios prévios de baixo débito · choques recorrentes<br/>≥2 hospitalizações IC no ano<br/>intolerância progressiva a GDMT"}

  D3 -->|"Sim"| C3(["Encaminhar URGENTE a centro<br/>de IC avançada<br/>Não adiar por 'mais uma otimização'<br/>Ver fluxograma-encaminhamento-ic-avancada"])

  D3 -->|"Não (critério isolado mais brando)"| C4(["Encaminhar a centro de IC avançada<br/>em agenda prioritária ambulatorial<br/>Plano escrito de alarmes + retorno precoce<br/>se congestão evoluir"])

  C4 --> D4{"Barreira aparente<br/>(idade, comorbidade, adesão)?"}
  D4 -->|"Sim"| C5(["Discutir com centro e paciente<br/>Não excluir automaticamente por idade/comorbidade<br/>(ISHLT / fluxo técnico)"])
  D4 -->|"Não"| C6(["Manter encaminhamento + vigilância<br/>Não titular GDMT neste fluxograma<br/>Não cobrir cardiorrenal aqui"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C1,C3 alerta;
  class C2,C4,C5,C6 conduta;
```

## Notas

- **D1** = gate de segurança (descompensação aguda).
- **D2** = triagem I-NEED-HELP (Baumwol / HELP-HF / AHA / HFA-ESC).
- **D3** = priorização de urgência de encaminhamento (não decide LVAD vs. transplante).
- **D4** = barreira aparente não fecha a porta ao centro.
- Não decide doses de GDMT, diurético IV, ultrafiltração, listagem nem manejo cardiorrenal.

## Interpretação do reconhecimento

I-NEED-HELP é triagem para referência, não diagnóstico formal nem elegibilidade LVAD/transplante. Um item contextualizado pode motivar contato com programa de IC avançada; não esperar completar critérios HFA ou obter TCPE/RHC/escores. O centro considera otimização, valvas/arritmias/dispositivos, terapias avançadas e cuidados de suporte/paliativos. Idade, fragilidade e comorbidades não bloqueiam automaticamente a referência.

NP varia com idade, FA, DRC e obesidade; rim/fígado exigem atribuição e tendência, separando doença prévia. FEVE baixa isolada não define IC avançada. PAS 90–100 é faixa de alerta contextual, não corte diagnóstico. Contar internações realmente por IC; distinguir intolerância a GDMT de subutilização/adesão. Choque único estável de CDI pede via de dispositivo/EP; recorrência, IC importante ou instabilidade aumentam urgência.
### Variações entre documentos

Os limiares do mnemônico variam: o statementAHA2021 apresenta FEVE≤25% e pelo menos uma internação porIC nos12meses anteriores; versões usadas peloHELP-HF/HFA destacam FEVE<20% e mais de uma internação. Os critérios da tabela são sinalizadores operacionais, não barreiras obrigatórias. Não esperar a segunda internação nem FEVE<20% diante de trajetória preocupante. A referência deve considerar objetivos do paciente; doença não cardíaca terminal ou recusa informada de terapias complexas pede decisão compartilhada e suporte/paliação, sem abandono de cuidado.
