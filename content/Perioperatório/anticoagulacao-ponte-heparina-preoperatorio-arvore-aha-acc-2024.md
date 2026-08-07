---
title: "Anticoagulação e ponte com heparina no perioperatório — AHA/ACC 2024"
slug: anticoagulacao-ponte-heparina-preoperatorio-arvore-aha-acc-2024
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
revisado_por_voce: false
summary: "Árvore para decidir interrupção de anticoagulante e quando evitar ou considerar ponte com heparina no pré-operatório."
source_refs:
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. Circulation. 2024;150:e351-e442. PMID: 39316661. DOI: 10.1161/CIR.0000000000001285."
---

# Anticoagulação perioperatória: interromper não significa fazer ponte

A decisão perioperatória em paciente anticoagulado envolve dois riscos concorrentes:

- **tromboembolismo** quando a anticoagulação é interrompida;
- **sangramento** quando ela é mantida ou substituída por heparina durante o intervalo.

A AHA/ACC 2024 enfatiza que, para a maioria dos pacientes em anticoagulação terapêutica, a estratégia correta é **interromper temporariamente o anticoagulante quando o procedimento exigir e não realizar ponte rotineira**.

## Regra central da diretriz

Para a maioria dos pacientes em uso de DOAC ou varfarina, a ponte com heparina parenteral durante a interrupção **pode causar dano por aumentar sangramento** e não deve ser usada rotineiramente.

A exceção é o paciente com **risco trombótico muito alto**, em quem o risco da interrupção sem cobertura pode superar o risco hemorrágico.

A AHA/ACC 2024 cita explicitamente como exemplos de alto risco:

- **prótese valvar mecânica mitral**;
- **trombo de ventrículo esquerdo nos últimos 3 meses**;
- **fibrilação atrial com AVC recente**.

Nesses cenários, ponte com heparina não fracionada ou heparina de baixo peso molecular **pode reduzir risco tromboembólico** e deve ser individualizada.

## Árvore de decisão

```mermaid
flowchart TD
    A["Paciente anticoagulado candidato a cirurgia/procedimento"] --> B["Identificar anticoagulante, indicação,<br/>função renal, risco hemorrágico e urgência"]
    B --> C{"Procedimento pode ser realizado<br/>sem interromper anticoagulação?"}
    C -->|"Sim"| D["Manter conforme protocolo do procedimento<br/>e estratégia anestésica"]
    C -->|"Não"| E["Planejar interrupção pelo fármaco,<br/>função renal e risco de sangramento"]
    E --> F{"Risco trombótico é muito alto?"}
    F -->|"Não"| G["Não fazer ponte de rotina;<br/>interrupção temporária sem heparina"]
    F -->|"Sim"| H{"Qual situação de alto risco?"}
    H -->|"Prótese mecânica mitral"| I["Considerar ponte individualizada"]
    H -->|"Trombo de VE <3 meses"| I
    H -->|"FA + AVC recente"| I
    H -->|"Outra situação excepcional"| J["Discussão especializada;<br/>não presumir benefício da ponte"]
    I --> K["Escolher HNF/HBPM e janela conforme anticoagulante,<br/>hemostasia e função renal"]
    G --> L["Realizar procedimento"]
    K --> L
    J --> L
    D --> L
    L --> M{"Hemostasia pós-operatória adequada?"}
    M -->|"Não"| N["Adiar reinício terapêutico e reavaliar sangramento"]
    M -->|"Sim"| O["Reiniciar anticoagulação em momento apropriado<br/>ao risco hemorrágico do procedimento"]
```

## Por que a ponte rotineira é problemática

A ponte substitui um anticoagulante oral interrompido por anticoagulação parenteral de curta ação. Embora pareça intuitivamente protetora, em pacientes de risco trombótico baixo ou moderado ela tende a acrescentar **sangramento** sem benefício tromboembólico proporcional.

Por isso, a pergunta correta não é “o paciente usa anticoagulante, então precisa de ponte?”, mas:

> **o risco trombótico durante poucos dias sem anticoagulação é alto o suficiente para justificar o risco hemorrágico adicional da heparina?**

Na maioria dos pacientes, a resposta é não.

## DOAC versus varfarina

A estratégia de interrupção não é idêntica:

- DOACs têm meia-vida relativamente curta e, em geral, **não necessitam ponte**;
- varfarina exige tempo maior para redução e recuperação do efeito anticoagulante;
- função renal é especialmente relevante para a duração do efeito de alguns DOACs;
- procedimentos com anestesia neuraxial ou risco de sangramento de consequência grave exigem cronograma específico.

Os intervalos exatos devem ser definidos pelo fármaco, clearance renal e risco hemorrágico do procedimento; não se deve aplicar uma única janela universal a todos os anticoagulantes.

## Situações que merecem especialista/equipe multidisciplinar

- prótese mecânica;
- trombo intracardíaco recente;
- AVC/tromboembolismo recente;
- múltiplos fatores de alto risco trombótico;
- insuficiência renal avançada em DOAC;
- cirurgia com risco hemorrágico muito alto;
- anestesia neuraxial;
- cirurgia urgente que não permite aguardar eliminação do anticoagulante.

## Regra prática

**Interromper anticoagulante não cria automaticamente indicação de ponte.** A ponte deve ser reservada para risco trombótico realmente alto, porque em pacientes comuns ela acrescenta sangramento e pode piorar o balanço benefício–risco.
