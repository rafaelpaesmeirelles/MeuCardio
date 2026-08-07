# Comparador de metodologias e resolvedor de discordância — risco perioperatório

> Metadados de produção: `{"fonte_producao":"chatgpt","frente":"documento_biblioteca","tema":"Perioperatório","revisado_por_voce":false}`
>
> Documento de síntese clínica. Não substitui as diretrizes nem transforma uma combinação de scores em um novo escore validado.

## Por que este documento existe

RCRI, Gupta MICA, DASI, AUB-HAS2, VSG-CRI, GSCRI, fragilidade e biomarcadores **não medem a mesma coisa**. Portanto, resultados discordantes são esperados e não devem ser “resolvidos” por média aritmética, votação ou escolha do score que produziu o menor risco.

A função deste documento é mostrar **qual dimensão do risco está puxando o resultado** e qual pergunta clínica vem depois.

---

## 1. O mapa mental

```mermaid
flowchart TD
    A[Resultados perioperatórios disponíveis] --> B[Risco clínico/procedimental]
    A --> C[Reserva funcional]
    A --> D[Vulnerabilidade biológica]
    A --> E[Fragilidade/contexto]

    B --> B1[RCRI / Gupta / AUB-HAS2 / VSG-CRI / GSCRI]
    C --> C1[DASI / status funcional]
    D --> D1[BNP ou NT-proBNP / troponina]
    E --> E1[Fragilidade / cognição / multimorbidade / urgência]

    B1 --> F[Integração clínica]
    C1 --> F
    D1 --> F
    E1 --> F

    F --> G{Existe achado acionável?}
    G -- Não --> H[Mitigar risco + plano perioperatório]
    G -- Sim --> I[Exame/tratamento/adiamento apenas se mudar manejo]
```

---

## 2. Quando RCRI e Gupta MICA discordam

### Cenário A — RCRI baixo, Gupta MICA elevado

Possíveis razões:

- idade aumenta risco no Gupta e não existe no RCRI;
- dependência funcional entra no Gupta e não no RCRI;
- classe ASA entra no Gupta;
- o tipo específico de procedimento exerce peso maior no Gupta.

```mermaid
flowchart TD
    A[RCRI baixo + Gupta ≥1%] --> B[Não escolher o menor score]
    B --> C[Identificar o que elevou Gupta:<br/>idade, ASA, dependência ou cirurgia]
    C --> D[Aplicar DASI / avaliar fragilidade]
    D --> E{Sintomas ou reserva ruim?}
    E -- Não --> F[Risco ainda pode ser elevado pelo procedimento;<br/>planejar perioperatório]
    E -- Sim --> G[Considerar biomarcadores/teste seletivo se mudar manejo]
```

**Leitura prática:** o RCRI baixo não “anula” um Gupta elevado. Ele apenas diz que os seis fatores clássicos de Lee são poucos.

---

### Cenário B — RCRI elevado, Gupta MICA baixo

Possíveis razões:

- história de DAC, AVC ou uso de insulina pode aumentar RCRI mesmo em um procedimento atual de menor estresse;
- o paciente pode ser independente, ASA mais baixo e ter categoria cirúrgica de menor risco no Gupta.

```mermaid
flowchart TD
    A[RCRI >1 + Gupta <1%] --> B[Não fazer média dos percentuais]
    B --> C[Revisar quais critérios elevaram o RCRI]
    C --> D{Doença está ativa ou descompensada?}
    D -- Sim --> E[A condição clínica prevalece sobre o score]
    D -- Não --> F[DASI + procedimento + modificadores]
    F --> G{Capacidade funcional adequada?}
    G -- Sim --> H[Evitar teste isquêmico rotineiro apenas pelo RCRI]
    G -- Não --> I[Considerar biomarcador/teste se acionável]
```

---

## 3. Score baixo, DASI ruim

Este é um dos cenários mais importantes para evitar dois erros opostos: ignorar baixa reserva ou pedir teste de isquemia automaticamente.

```mermaid
flowchart TD
    A[Risco calculado baixo + DASI ≤34] --> B[Confirmar por que a função é baixa]
    B --> C{Limitação parece cardiovascular?}
    C -- Sim --> D[Avaliar sintoma/doença específica]
    C -- Não --> E[Considerar fragilidade, doença pulmonar,<br/>musculoesquelética, anemia, descondicionamento]
    D --> F{Há indicação clínica independente de exame?}
    E --> F
    F -- Não --> G[Não transformar DASI ruim isolado em teste de isquemia]
    F -- Sim --> H[Investigar conforme a hipótese clínica]
```

**Atualização 2026:** o DASI acrescenta informação prognóstica, mas sua interpretação é dependente de idade, RCRI e biomarcadores; o mesmo valor de DASI não corresponde ao mesmo risco em todos os pacientes.

---

## 4. Score elevado, DASI bom

```mermaid
flowchart TD
    A[Risco calculado elevado + DASI >34] --> B[Capacidade funcional adequada reduz a necessidade de rastreamento isquêmico rotineiro]
    B --> C[Mas não apaga o risco do procedimento/comorbidades]
    C --> D[Planejar hemodinâmica, medicações e pós-operatório]
    D --> E{Há sintoma ativo ou outra indicação independente?}
    E -- Não --> F[Em geral, prosseguir sem stress de rotina]
    E -- Sim --> G[Investigar a condição clínica]
```

**Ponto central:** “bom DASI” e “baixo risco” não são sinônimos.

---

## 5. Score baixo, biomarcador anormal

```mermaid
flowchart TD
    A[Score clínico baixo + BNP/NT-proBNP ou troponina anormal] --> B[Revisar causa do marcador]
    B --> C{Há síndrome clínica ativa?}
    C -- Sim --> D[Tratar/investigar a síndrome]
    C -- Não --> E[Reconhecer risco biológico não capturado pelo score]
    E --> F[Rever DASI, IC subclínica, função renal e procedimento]
    F --> G[Planejar vigilância e decidir se investigação adicional é acionável]
```

Um biomarcador alterado não deve ser descartado apenas porque o RCRI é 0 ou 1.

---

## 6. Score elevado, biomarcador normal

```mermaid
flowchart TD
    A[Score elevado + biomarcador normal] --> B[Sinal biológico favorável]
    B --> C[Não reclassificar automaticamente para risco baixo]
    C --> D[DASI + sintomas + procedimento]
    D --> E{Teste adicional mudaria manejo?}
    E -- Não --> F[Prosseguir com mitigação e monitorização apropriadas]
    E -- Sim --> G[Teste seletivo]
```

Biomarcador normal é informação adicional; não é uma “autorização cirúrgica”.

---

## 7. Idoso: RCRI/Gupta versus GSCRI e fragilidade

Em pacientes ≥65 anos, a avaliação fica especialmente vulnerável à subestimação quando se olha apenas para cardiopatia conhecida.

O GSCRI foi construído especificamente para essa população e, na validação publicada, discriminou MICA melhor que RCRI e Gupta na coorte geriátrica.

```mermaid
flowchart TD
    A[Paciente ≥65 anos] --> B[RCRI/Gupta]
    A --> C[Fragilidade]
    A --> D[DASI/status funcional]
    A --> E[GSCRI quando disponível/validado no produto]
    B --> F[Integração geriátrica]
    C --> F
    D --> F
    E --> F
    F --> G[Definir não só risco cardíaco,<br/>mas destino pós-operatório e reserva para complicações]
```

---

## 8. Cirurgia vascular: não usar escore genérico como se fosse específico

O VSG-CRI foi desenvolvido para cirurgia vascular arterial. Nesse contexto, ele pode acrescentar estratificação específica que um score geral não captura da mesma forma.

```mermaid
flowchart TD
    A[Cirurgia vascular arterial] --> B[VSG-CRI]
    A --> C[RCRI/Gupta como contexto geral]
    B --> D{Resultados concordantes?}
    C --> D
    D -- Sim --> E[Planejamento guiado pela faixa de risco]
    D -- Não --> F[Priorizar validade do método para a população/procedimento<br/>e revisar o fator que gera a discordância]
```

Não extrapolar VSG-CRI para cirurgia geral.

---

## 9. Regra de precedência clínica

Quando dados discordam, a ordem de prioridade não deve ser “qual score é mais famoso”.

```mermaid
flowchart TD
    A[Discordância] --> B{Existe doença cardiovascular aguda/instável?}
    B -- Sim --> C[Tratar condição aguda primeiro]
    B -- Não --> D{O método foi validado para este tipo de paciente/procedimento?}
    D -- Não --> E[Reduzir peso desse método]
    D -- Sim --> F{Qual dimensão ele mede?}
    F --> G[Evento cardíaco]
    F --> H[Capacidade funcional]
    F --> I[Mortalidade global]
    F --> J[Fragilidade]
    G --> K[Integrar dimensões sem somar scores]
    H --> K
    I --> K
    J --> K
    K --> L{Há ação que pode reduzir risco ou mudar estratégia?}
    L -- Não --> M[Não ampliar investigação apenas por ansiedade diagnóstica]
    L -- Sim --> N[Executar investigação/otimização dirigida]
```

---

## 10. Matriz de interpretação rápida

| Combinação | Leitura mais provável | Próximo passo racional |
|---|---|---|
| RCRI baixo + Gupta baixo + DASI bom | baixo sinal clínico e boa reserva | evitar investigação cardíaca rotineira se assintomático/estável |
| RCRI alto + Gupta alto | risco clínico consistente | abrir camadas DASI/biomarcadores/modificadores |
| RCRI baixo + Gupta alto | idade/ASA/procedimento/funcionalidade provavelmente puxam risco | identificar driver; não escolher RCRI por conveniência |
| RCRI alto + Gupta baixo | comorbidade clássica pesa mais que contexto atual do Gupta | revisar atividade da doença e reserva funcional |
| score baixo + DASI ruim | baixa reserva não explicada pelo score | esclarecer causa funcional; fragilidade/sintomas |
| score alto + DASI bom | boa reserva não elimina risco estrutural/procedimental | normalmente evita stress rotineiro se estável, mas exige plano |
| score baixo + biomarcador alto | risco biológico não capturado | procurar causa e reavaliar estratégia/vigilância |
| score alto + biomarcador normal | sinal biológico favorável sem zerar risco | integrar demais dimensões, sem “downgrade” automático |

---

## 11. O que NÃO fazer

- **Não somar** pontos de RCRI + AUB-HAS2 + VSG-CRI.
- **Não fazer média** entre percentuais de Gupta, GSCRI e ACS-NSQIP.
- **Não escolher retrospectivamente** o score que produz o resultado mais conveniente.
- **Não pedir teste de isquemia** apenas porque dois scores discordaram.
- **Não interpretar DASI ≤34 como diagnóstico de DAC.**
- **Não interpretar BNP/NT-proBNP elevado como indicação automática de coronariografia.**
- **Não usar VSG-CRI fora de cirurgia vascular arterial.**

---

## 12. Sugestão para o frontend da Corvia

Em vez de cinco cards independentes, mostrar uma síntese em camadas:

```text
RISCO CALCULADO
RCRI: ... | Gupta: ... | método específico: ...

RESERVA
DASI: ... | Fragilidade: ...

SINAL BIOLÓGICO
BNP/NT-proBNP: ... | Troponina: ...

DISCORDÂNCIA
[explicação automática do principal driver]

PRÓXIMO PASSO
[prosseguir / otimizar / investigar sintoma / considerar biomarcador / considerar teste se mudar manejo]
```

A mensagem automática deve explicar **por que** os métodos discordam, não decretar “apto” ou “inapto”.

---

## Fontes principais

- Thompson A et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. *Circulation*. 2024. DOI 10.1161/CIR.0000000000001285.
- Halvorsen S et al. 2022 ESC Guidelines on cardiovascular assessment and management of patients undergoing non-cardiac surgery. *Eur Heart J*. 2022;43:3826-3924. PMID 36017553. DOI 10.1093/eurheartj/ehac270.
- Lee TH et al. *Circulation*. 1999;100:1043-1049. PMID 10477528. DOI 10.1161/01.CIR.100.10.1043.
- Gupta PK et al. *Circulation*. 2011;124:381-387. PMID 21730309. DOI 10.1161/CIRCULATIONAHA.110.015701.
- Hlatky MA et al. *Am J Cardiol*. 1989;64:651-654. PMID 2782256. DOI 10.1016/0002-9149(89)90496-7.
- Alrezk R et al. *J Am Heart Assoc*. 2017;6:e006648. PMID 29146612. PMCID PMC5721761. DOI 10.1161/JAHA.117.006648.
- Wijeysundera DN et al. *EClinicalMedicine*. 2026;96:104015. PMID 42326382. PMCID PMC13276150. DOI 10.1016/j.eclinm.2026.104015.
