---
title: "Eletrodos de CIED — HRS 2026: abandonar, revisar ou extrair e árvore de decisão"
slug: eletrodos-cied-extracao-hrs-2026-abandonar-remover-e-arvore-de-decisao
theme: "Dispositivos"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
---

# Manejo e extração de eletrodos de CIED — consenso HRS 2026

## Por que a atualização de 2026 é importante

A atualização conjunta HRS/AHA/APHRS/EHRA/IDSA/LAHRS/PACES/STS publicada em abril de 2026 substitui a lógica simplista de “eletrodo velho = extrair” por uma decisão individualizada que compara **risco atual, risco futuro, benefício clínico e complexidade da extração**.

O documento incorpora novas tecnologias que não estavam maduras em 2017, como:

- pacing sem eletrodo;
- sistemas de desfibrilação fora do sistema vascular;
- novos eletrodos lumenless;
- novas ferramentas e técnicas de extração;
- interação entre eletrodos transvalvares e intervenções tricúspides transcateter.

## Princípio central

A decisão entre **manter, abandonar ou extrair** um eletrodo deve ser feita por decisão compartilhada, levando em conta:

- indicação clínica atual;
- risco de infecção;
- mau funcionamento;
- acesso vascular;
- necessidade de upgrade;
- idade e expectativa de vida;
- tempo de permanência do eletrodo;
- futuras necessidades de acesso venoso/MRI/intervenção estrutural;
- risco procedural e experiência do centro.

## Árvore de decisão: manter, abandonar ou extrair

```mermaid
flowchart TD
    A["Paciente com eletrodo de CIED que precisa decisão de manejo"] --> B{"Infecção do sistema ou indicação infecciosa formal?"}
    B -->|Sim| C["Via de manejo de infecção do CIED + avaliação para remoção completa conforme indicação"]
    B -->|Não| D{"Eletrodo com falha, complicação vascular, interferência mecânica ou necessidade de upgrade?"}
    D -->|Não| E["Manter e acompanhar se benefício da extração não supera risco"]
    D -->|Sim| F["Avaliar necessidade de novo acesso, carga de hardware e alternativas tecnológicas"]
    F --> G{"Extração oferece benefício clínico/futuro relevante com risco aceitável?"}
    G -->|Sim| H["Encaminhar para centro experiente de extração com planejamento estruturado"]
    G -->|Não| I["Considerar abandono seguro + nova estratégia de pacing/ICD quando apropriado"]
    H --> J["Plano de complicações, backup cirúrgico e cuidado pós-extração"]
    I --> K["Documentar hardware abandonado e implicações futuras"]
```

## Extração é procedimento de alto impacto, não simples “troca de cabo”

O consenso enfatiza que extração transvenosa pode produzir complicações ameaçadoras à vida. Portanto, deve ser realizada em estrutura apropriada, com:

- operador e equipe experientes;
- protocolo institucional padronizado;
- ferramentas adequadas;
- planejamento por imagem quando indicado;
- capacidade de resposta imediata a complicações;
- **backup cirúrgico** e recursos compatíveis com o risco do procedimento.

## Quando a infecção muda a lógica

Infecção de CIED não deve ser abordada apenas com antibiótico e observação do pocket. O documento de 2026 atualiza evidências sobre diagnóstico, tratamento e prevenção de infecção de dispositivos e mantém a necessidade de considerar **remoção do sistema quando existe indicação infecciosa**, acompanhada de antibioticoterapia e estratégia adequada de reimplante.

A decisão de reimplantar deve responder:

1. o paciente ainda precisa de dispositivo?
2. qual tipo de dispositivo oferece menor risco futuro?
3. o sítio e o momento do reimplante são seguros?
4. alternativas sem eletrodo transvenoso podem reduzir risco?

## Árvore: após extração por infecção

```mermaid
flowchart TD
    A["Sistema removido por infecção"] --> B["Tratar infecção e documentar controle microbiológico/clínico"]
    B --> C{"Indicação original de pacing/ICD ainda existe?"}
    C -->|Não| D["Não reimplantar automaticamente; acompanhamento"]
    C -->|Sim| E["Reavaliar tipo de sistema e risco de nova infecção"]
    E --> F{"Sistema transvenoso continua melhor opção?"}
    F -->|Sim| G["Planejar reimplante no momento/sítio apropriado conforme controle da infecção"]
    F -->|Não| H["Considerar leadless pacing, ICD extravascular/subcutâneo ou outra estratégia conforme necessidade"]
```

## Valva tricúspide: uma nova interface crítica

O consenso aborda especificamente pacientes com eletrodos atravessando a tricúspide e indicação de **substituição tricúspide transcateter**.

Esses pacientes devem ser avaliados por **Heart Team multidisciplinar**, incluindo eletrofisiologista com experiência em manejo/extração de eletrodos, porque aprisionar um eletrodo entre prótese e tecido pode comprometer futuras intervenções, funcionamento do eletrodo e possibilidade de extração.

## Árvore: CIED antes de intervenção tricúspide transcateter

```mermaid
flowchart TD
    A["CIED com eletrodo atravessando tricúspide + indicação de intervenção transcateter"] --> B["Heart Team estrutural + eletrofisiologia/extração"]
    B --> C["Definir dependência de pacing, função do eletrodo, idade do lead e anatomia"]
    C --> D{"Risco de aprisionamento/comprometimento futuro clinicamente relevante?"}
    D -->|Sim| E["Planejar manejo do eletrodo antes da prótese: extração/revisão/estratégia alternativa conforme risco"]
    D -->|Não| F["Pode ser possível preservar o sistema com plano de contingência"]
    E --> G["Considerar pacing sem eletrodo ou outra solução que evite novo lead transvalvar quando apropriado"]
```

## Eletrodo abandonado: o custo futuro também conta

Abandono evita o risco imediato da extração, mas pode aumentar:

- quantidade de hardware intravascular;
- complexidade de futura extração;
- risco de obstrução venosa e interação entre eletrodos;
- dificuldade de upgrades;
- questões relacionadas a futuras intervenções estruturais.

Por outro lado, extrair preventivamente um eletrodo antigo e aderido em paciente de alto risco pode causar dano desproporcional. Por isso, o consenso insiste em **decisão individualizada e compartilhada**.

## Armadilhas

1. Não indicar extração apenas pela idade cronológica do eletrodo.
2. Não minimizar risco de extração porque o procedimento é “percutâneo”.
3. Não abandonar lead sem documentar implicações para acesso venoso e futuras intervenções.
4. Não planejar TTVR ignorando eletrodo transvalvar.
5. Não presumir que todo paciente removido por infecção precisa do mesmo tipo de dispositivo novamente.

## Fonte verificada

Cha YM, El-Chami MF, Liu CF, et al. 2026 HRS/AHA/APHRS/EHRA/IDSA/LAHRS/PACES/STS Expert Consensus Statement Update on Cardiovascular Implantable Electronic Device Lead Management and Extraction. *Heart Rhythm.* Published online April 23, 2026. PMID **42034327**. DOI **10.1016/j.hrthm.2026.04.015**.

## Status de revisão

`VERIFICAÇÃO HUMANA NECESSÁRIA`: antes de converter qualquer indicação específica de extração em regra automática, conferir classe, força e texto integral da recomendação no consenso final de 2026.
