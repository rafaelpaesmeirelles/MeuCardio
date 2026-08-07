# Atlas visual — Avaliação Cardiológica Pré-Operatória de Risco Cirúrgico

> Metadados de produção: `{"fonte_producao":"chatgpt","frente":"documento_biblioteca","tema":"Perioperatório","revisado_por_voce":false}`
>
> **Status:** conteúdo científico produzido pelo ChatGPT a partir de fontes primárias consultadas; a decisão final de marcar como revisado/publicado pertence ao fluxo de validação da Corvia.

## Objetivo

Este documento transforma os principais métodos de avaliação cardiovascular perioperatória em **árvores de decisão clínicas**. A ideia central é impedir que um número isolado — RCRI, Gupta MICA, DASI ou qualquer outro — seja confundido com a avaliação pré-operatória inteira.

O modelo proposto para a Corvia é um **Risk Stack** em camadas:

1. urgência e doença cardiovascular ativa;
2. risco clínico/procedimental por ferramenta validada;
3. reserva funcional e fragilidade;
4. biomarcadores quando indicados;
5. exames adicionais apenas quando o resultado puder mudar conduta.

---

## 1. Risk Stack perioperatório — visão geral

```mermaid
flowchart TD
    A[Cirurgia não cardíaca planejada] --> B{Emergência?}
    B -- Sim --> C[Prosseguir para cirurgia<br/>com avaliação e mitigação possíveis no tempo disponível]
    B -- Não --> D{Condição cardiovascular aguda ou instável?}
    D -- Sim --> E[Pausar quando clinicamente possível<br/>tratar/definir síndrome aguda]
    D -- Não --> F[Estimar risco perioperatório<br/>RCRI / Gupta MICA / método apropriado]
    F --> G{Risco calculado baixo?}
    G -- Sim --> H[Em geral, seguir para cirurgia<br/>sem rastreamento cardíaco excessivo]
    G -- Não --> I[Pesquisar modificadores de risco<br/>e reserva fisiológica]
    I --> J[DASI + fragilidade quando aplicável]
    J --> K{Capacidade funcional adequada e sintomas estáveis?}
    K -- Sim --> L[Prosseguir, com plano perioperatório individualizado]
    K -- Não ou desconhecida --> M{Exame adicional mudará decisão ou tratamento?}
    M -- Não --> N[Prosseguir com mitigação de risco<br/>e vigilância apropriada]
    M -- Sim --> O[Biomarcadores e/ou teste cardíaco seletivo]
    O --> P{Achado de alto risco acionável?}
    P -- Não --> L
    P -- Sim --> Q[Discussão multidisciplinar<br/>otimização, estratégia alternativa ou adiamento]
```

### Como interpretar

- **Risco baixo** não significa risco zero; significa que a probabilidade estimada de MACE é suficientemente pequena para que rastreamento adicional rotineiro tenha baixo rendimento.
- **Risco elevado** não significa “pedir teste ergométrico”. Significa abrir as camadas seguintes do Risk Stack.
- **Exame pré-operatório só tem valor se puder alterar conduta** — princípio central da AHA/ACC 2024.

---

## 2. RCRI — Revised Cardiac Risk Index

### O que responde

“Quantos dos seis preditores clássicos de complicação cardíaca maior estão presentes?”

Preditores originais de Lee et al.:

- cirurgia de alto risco;
- doença isquêmica cardíaca;
- insuficiência cardíaca;
- doença cerebrovascular;
- diabetes tratado com insulina;
- creatinina sérica pré-operatória >2,0 mg/dL.

Na coorte de validação original, a taxa de complicação cardíaca maior foi 0,4%, 0,9%, 7% e 11% para 0, 1, 2 e ≥3 fatores, respectivamente.

### Árvore de decisão

```mermaid
flowchart TD
    A[Paciente candidato a cirurgia não cardíaca] --> B[Marcar os 6 critérios do RCRI]
    B --> C[Somar 1 ponto por critério]
    C --> D{RCRI >1?}
    D -- Não --> E[Risco tradicionalmente baixo pela AHA/ACC 2024]
    D -- Sim --> F[Risco cardiovascular calculado elevado]
    E --> G[Integrar tipo de cirurgia + sintomas + DASI]
    F --> H[Integrar DASI, fragilidade e modificadores de risco]
    H --> I{Capacidade funcional ruim/desconhecida?}
    I -- Não --> J[Em geral, seguir com estratégia perioperatória]
    I -- Sim --> K{Resultado de investigação adicional mudaria manejo?}
    K -- Não --> J
    K -- Sim --> L[Considerar biomarcadores e teste seletivo conforme diretriz]
```

### Armadilhas

- O RCRI **não contém idade nem capacidade funcional**.
- A definição histórica de “cirurgia de alto risco” do RCRI não é intercambiável com todas as classificações cirúrgicas contemporâneas.
- As taxas de 0,4/0,9/7/11% pertencem à **coorte de validação original**, não são uma promessa de risco absoluto para qualquer população moderna.

**Fonte primária:** Lee TH et al. *Circulation*. 1999;100(10):1043-1049. PMID 10477528. DOI 10.1161/01.CIR.100.10.1043.

---

## 3. Gupta MICA

### O que responde

“Qual é a probabilidade individual estimada de infarto do miocárdio ou parada cardíaca perioperatória?”

O modelo original deriva a estimativa de cinco domínios:

- idade;
- status funcional;
- classe ASA;
- creatinina anormal;
- tipo de cirurgia.

Na validação publicada, o modelo apresentou C-statistic 0,874; na mesma base, o RCRI apresentou C-statistic 0,747.

### Árvore de decisão

```mermaid
flowchart TD
    A[Paciente em cirurgia não cardíaca] --> B[Idade]
    B --> C[Status funcional]
    C --> D[Classe ASA]
    D --> E[Creatinina]
    E --> F[Categoria do procedimento]
    F --> G[Regressão Gupta MICA]
    G --> H[Probabilidade estimada de IAM/PCR em 30 dias]
    H --> I{Risco calculado ≥1%?}
    I -- Não --> J[Faixa tradicional de baixo risco perioperatório]
    I -- Sim --> K[Faixa de risco cardiovascular elevado]
    K --> L[DASI + modificadores + biomarcadores/teste apenas se acionáveis]
```

### Armadilhas

- É uma estimativa populacional; não elimina avaliação clínica.
- Procedimentos devem ser mapeados à categoria cirúrgica do modelo original com cautela.
- O corte de **1%** é utilizado pela abordagem AHA/ACC como limiar tradicional para distinguir risco baixo de risco elevado quando se usa uma calculadora perioperatória.

**Fonte primária:** Gupta PK et al. *Circulation*. 2011;124(4):381-387. PMID 21730309. DOI 10.1161/CIRCULATIONAHA.110.015701.

---

## 4. DASI — capacidade funcional estruturada

### O que responde

“Qual é a capacidade funcional autorreferida por um instrumento estruturado em vez de uma estimativa subjetiva do médico?”

O DASI contém 12 atividades ponderadas. A soma varia de **0 a 58,2**.

A AHA/ACC 2024 considera razoável usar avaliação estruturada como o DASI em cirurgia de risco elevado e usa **DASI ≤34** como definição operacional de capacidade funcional ruim no algoritmo de teste pré-operatório.

### Árvore de decisão

```mermaid
flowchart TD
    A[Cirurgia de risco elevado ou dúvida sobre capacidade funcional] --> B[Aplicar as 12 perguntas do DASI]
    B --> C[Somar os pesos das atividades que o paciente consegue realizar]
    C --> D[DASI 0–58,2]
    D --> E{DASI >34?}
    E -- Sim --> F[Capacidade funcional operacionalmente adequada]
    E -- Não --> G[Capacidade funcional operacionalmente ruim]
    F --> H[Se sintomas estáveis e sem outro gatilho,<br/>evitar teste cardíaco rotineiro]
    G --> I{Risco cardiovascular calculado também é elevado?}
    I -- Não --> J[Interpretar contexto; evitar transformar DASI isolado em indicação de teste]
    I -- Sim --> K{Teste adicional mudará decisão ou terapia?}
    K -- Não --> L[Plano perioperatório + vigilância]
    K -- Sim --> M[Biomarcador e/ou stress/CCTA seletivos]
```

### Atualização importante de 2026

Uma análise internacional agrupada de 3.485 pacientes mostrou que o DASI acrescenta informação prognóstica além de idade, RCRI e peptídeo natriurético, mas com ganho global modesto de discriminação. O risco associado ao mesmo valor de DASI varia conforme idade, RCRI e biomarcadores.

**Implicação para a Corvia:** manter o corte **≤34** porque ele é operacional na AHA/ACC 2024, mas exibir o **valor contínuo** e uma mensagem de contexto, evitando a falsa ideia de que 33 e 35 representam pacientes biologicamente distintos.

**Fontes:**

- Hlatky MA et al. *Am J Cardiol*. 1989;64(10):651-654. PMID 2782256. DOI 10.1016/0002-9149(89)90496-7.
- Thompson A et al. AHA/ACC et al. Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. *Circulation*. 2024. DOI 10.1161/CIR.0000000000001285.
- Wijeysundera DN et al. *EClinicalMedicine*. 2026;96:104015. PMID 42326382. PMCID PMC13276150. DOI 10.1016/j.eclinm.2026.104015.

---

## 5. GSCRI — paciente geriátrico

### Quando faz sentido

O Geriatric-Sensitive Cardiac Risk Index foi desenvolvido especificamente para pacientes **≥65 anos** submetidos a cirurgia não cardíaca.

Variáveis do modelo final:

- AVC prévio;
- ASA;
- categoria cirúrgica;
- status funcional;
- creatinina >1,5 mg/dL;
- história de insuficiência cardíaca;
- diabetes, distinguindo insulinodependência.

Na validação geriátrica publicada, a AUC foi 0,76, comparada com 0,63 para RCRI e 0,70 para Gupta MICA.

### Árvore de decisão

```mermaid
flowchart TD
    A[Paciente ≥65 anos] --> B{Cirurgia não cardíaca?}
    B -- Não --> C[Não aplicar GSCRI]
    B -- Sim --> D[Coletar AVC, ASA, cirurgia, funcionalidade,<br/>creatinina, IC e diabetes]
    D --> E[Calcular probabilidade pelo modelo GSCRI]
    E --> F[Interpretar risco absoluto em conjunto com DASI/frailty]
    F --> G{Risco elevado ou reserva fisiológica ruim?}
    G -- Não --> H[Prosseguir conforme contexto]
    G -- Sim --> I[Planejamento multidisciplinar e investigação seletiva]
```

**Nota de implementação:** os coeficientes do modelo estão disponíveis no texto completo de acesso aberto, portanto o GSCRI pode ser reproduzido localmente após validação técnica independente da fórmula.

**Fonte primária:** Alrezk R et al. *J Am Heart Assoc*. 2017;6(11):e006648. PMID 29146612. PMCID PMC5721761. DOI 10.1161/JAHA.117.006648.

---

## 6. Biomarcadores — quando acrescentam informação

A AHA/ACC 2024 considera razoável medir **BNP ou NT-proBNP** antes de cirurgia de risco elevado em pacientes com doença cardiovascular conhecida, idade ≥65 anos, ou idade ≥45 anos com sintomas sugestivos de doença cardiovascular. Troponina cardíaca pré-operatória pode ser considerada no mesmo cenário.

O algoritmo da diretriz usa como valores anormais:

- troponina acima do percentil 99 do ensaio;
- BNP >92 ng/L;
- NT-proBNP ≥300 ng/L.

### Árvore de decisão

```mermaid
flowchart TD
    A[Cirurgia de risco elevado] --> B{DCV conhecida, idade ≥65,<br/>ou idade ≥45 com sintomas de DCV?}
    B -- Não --> C[Biomarcador rotineiro não é automaticamente necessário]
    B -- Sim --> D[Considerar BNP ou NT-proBNP]
    D --> E[Considerar troponina cardíaca pré-operatória]
    E --> F{Biomarcador normal?}
    F -- Sim --> G[Menor sinal biológico de risco;<br/>integrar com score + DASI]
    F -- Não --> H[Maior risco biológico]
    H --> I{Investigação adicional mudará conduta?}
    I -- Não --> J[Planejar monitorização e mitigação de risco]
    I -- Sim --> K[Discussão multidisciplinar + teste seletivo]
```

**Importante:** biomarcador anormal **não equivale automaticamente** a indicação de coronariografia ou teste de isquemia.

**Fonte:** Thompson A et al. AHA/ACC et al. *Circulation*. 2024. DOI 10.1161/CIR.0000000000001285.

---

## 7. Quando pedir ECG

```mermaid
flowchart TD
    A[Pré-operatório] --> B{Cirurgia de risco elevado?}
    B -- Não --> C{Assintomático e procedimento de baixo risco?}
    C -- Sim --> D[Não solicitar ECG rotineiramente para melhorar desfechos]
    C -- Não --> E[Individualizar pela condição clínica]
    B -- Sim --> F{DAC conhecida, arritmia significativa, DAP,<br/>doença cerebrovascular, cardiopatia estrutural ou sintomas?}
    F -- Sim --> G[ECG de 12 derivações é razoável]
    F -- Não --> H[ECG pode ser considerado como baseline]
    G --> I{Nova anormalidade?}
    I -- Sim --> J[Avaliação adicional é razoável]
    I -- Não --> K[Prosseguir na árvore de risco]
```

A AHA/ACC 2024 lista como sintomas/sinais ativos relevantes dor torácica, dispneia, palpitações não diagnosticadas, taquicardia, síncope e sopro.

---

## 8. Quando pedir ecocardiograma para função ventricular

```mermaid
flowchart TD
    A[Paciente pré-operatório] --> B{Dispneia nova, sinais de IC<br/>ou suspeita de disfunção ventricular nova/pior?}
    B -- Sim --> C[Avaliar função ventricular antes da cirurgia]
    B -- Não --> D{IC conhecida com mudança clínica?}
    D -- Sim --> C
    D -- Não --> E[Paciente estável e assintomático]
    E --> F[Não solicitar avaliação rotineira de função ventricular]
```

O objetivo é reduzir ecocardiogramas “de liberação” sem pergunta clínica definida.

---

## 9. Quando considerar teste de isquemia ou CCTA

```mermaid
flowchart TD
    A[Cirurgia não cardíaca] --> B{Risco perioperatório calculado elevado?}
    B -- Não --> C[Não realizar teste de stress rotineiro]
    B -- Sim --> D{DASI ≤34 ou capacidade funcional desconhecida?}
    D -- Não --> C
    D -- Sim --> E{Resultado do teste mudaria decisão,<br/>tratamento ou estratégia cirúrgica?}
    E -- Não --> F[Não testar apenas para obter 'liberação']
    E -- Sim --> G[Considerar stress não invasivo ou CCTA]
    G --> H{Anatomia/isquemia de alto risco?}
    H -- Não --> I[Prosseguir com estratégia perioperatória]
    H -- Sim --> J[Discussão multidisciplinar;<br/>tratar DAC segundo indicações usuais, não só para 'liberar' cirurgia]
```

A AHA/ACC 2024 classifica teste de stress como opção **2b** em pacientes com cirurgia de risco elevado, capacidade funcional ruim/desconhecida e risco elevado por ferramenta validada. Em pacientes de baixo risco, com capacidade funcional adequada e sintomas estáveis, ou submetidos a procedimento de baixo risco, teste rotineiro não oferece benefício.

---

## 10. Fragilidade — não deixar o idoso ser reduzido a idade cronológica

A AHA/ACC 2024 considera útil avaliar fragilidade com ferramenta validada em todos os pacientes ≥65 anos — e em mais jovens com suspeita de fragilidade — quando submetidos a cirurgia de risco elevado.

### Árvore

```mermaid
flowchart TD
    A[Cirurgia de risco elevado] --> B{Idade ≥65 ou fragilidade percebida?}
    B -- Não --> C[Seguir avaliação padrão]
    B -- Sim --> D[Aplicar ferramenta validada de fragilidade]
    D --> E{Fragilidade relevante?}
    E -- Não --> C
    E -- Sim --> F[Adicionar risco de vulnerabilidade<br/>ao RCRI/Gupta/DASI]
    F --> G[Planejar prevenção de delirium, mobilização,<br/>nutrição, reabilitação e destino pós-operatório]
```

**Princípio:** fragilidade não é sinônimo de contraindicação cirúrgica; é um modificador de risco e de planejamento.

---

## 11. Como escolher o método — matriz prática

| Método | Pergunta que responde | Desfecho principal | Melhor uso | Limitação central |
|---|---|---|---|---|
| **RCRI** | Quantos fatores cardíacos clássicos estão presentes? | Complicação cardíaca maior | Triagem simples e transparente | Não inclui idade nem capacidade funcional |
| **Gupta MICA** | Qual a probabilidade individual de IAM/PCR? | IAM ou parada cardíaca em 30 dias | Risco contínuo e consentimento | Depende de categoria cirúrgica/ASA |
| **DASI** | Qual a reserva funcional autorreferida? | Capacidade funcional / prognóstico incremental | Evitar estimativa subjetiva de METs | Não deve ser usado isoladamente como “liberação” |
| **GSCRI** | Qual o risco cardíaco em ≥65 anos? | MICA | Idoso em cirurgia não cardíaca | Aplicação específica à população geriátrica |
| **AUB-HAS2** | Estratificação cardíaca perioperatória simplificada | MACE perioperatório | Alternativa validada em coortes próprias | Generalização depende da população |
| **VSG-CRI** | Risco cardíaco em cirurgia vascular | Eventos cardíacos | Cirurgia vascular | Não extrapolar para cirurgia geral |
| **ACS-NSQIP SRC** | Qual o risco global de múltiplos desfechos? | Mortalidade e complicações diversas | Planejamento cirúrgico global | Ferramenta externa; termos não permitem automação local |
| **POSPOM/SORT** | Qual o risco de mortalidade pós-operatória? | Mortalidade | Planejamento anestésico/cirúrgico global | Não são escores cardiovasculares específicos |

---

## 12. Regra de ouro da investigação pré-operatória

```mermaid
flowchart LR
    A[Exame considerado] --> B{Se vier anormal,<br/>eu faria algo diferente?}
    B -- Não --> C[Não pedir rotineiramente]
    B -- Sim --> D{A mudança de conduta<br/>melhora decisão/segurança?}
    D -- Não --> C
    D -- Sim --> E[Pedir exame com pergunta clínica explícita]
```

Essa regra reduz o ciclo “risco → exame → outro exame → atraso cirúrgico” sem benefício demonstrado.

---

## 13. Arquitetura recomendada para a Corvia

A tela de Avaliação Cardiológica Pré-Operatória pode exibir os resultados em cinco blocos, em vez de uma lista de scores:

### Camada 1 — Segurança imediata

- cirurgia de emergência/urgência;
- SCA;
- arritmia instável;
- insuficiência cardíaca descompensada;
- outra condição cardiovascular aguda que mude o timing.

### Camada 2 — Risco calculado

- RCRI;
- Gupta MICA;
- AUB-HAS2;
- VSG-CRI em cirurgia vascular;
- GSCRI em ≥65 anos quando implementado/validado no produto.

### Camada 3 — Reserva do paciente

- DASI contínuo;
- corte operacional DASI ≤34;
- fragilidade;
- status funcional.

### Camada 4 — Sinal biológico

- BNP/NT-proBNP;
- troponina quando indicada;
- função renal e hemoglobina como contexto.

### Camada 5 — Decisão acionável

- seguir para cirurgia;
- otimizar condição cardiovascular;
- solicitar eco;
- solicitar teste de isquemia/CCTA;
- discutir estratégia alternativa;
- planejar monitorização pós-operatória/troponina.

### Saída ideal do sistema

Em vez de “**RCRI = 2**”, a Corvia deve conseguir produzir algo como:

> **Risco cardiovascular calculado elevado + capacidade funcional reduzida.** O score isolado não determina investigação adicional. Verifique se biomarcador/teste cardíaco mudaria a estratégia cirúrgica ou o tratamento. Se não mudar, priorize otimização e plano perioperatório em vez de rastreamento indiscriminado.

Essa frase é uma síntese clínica original; não substitui recomendação formal da diretriz.

---

## 14. Fontes primárias consultadas

1. Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. *Circulation*. 2024. DOI: 10.1161/CIR.0000000000001285.
2. Halvorsen S, Mehilli J, Cassese S, et al. 2022 ESC Guidelines on cardiovascular assessment and management of patients undergoing non-cardiac surgery. *Eur Heart J*. 2022;43:3826-3924. PMID 36017553. DOI: 10.1093/eurheartj/ehac270.
3. Lee TH, Marcantonio ER, Mangione CM, et al. *Circulation*. 1999;100:1043-1049. PMID 10477528. DOI: 10.1161/01.CIR.100.10.1043.
4. Gupta PK, Gupta H, Sundaram A, et al. *Circulation*. 2011;124:381-387. PMID 21730309. DOI: 10.1161/CIRCULATIONAHA.110.015701.
5. Hlatky MA, Boineau RE, Higginbotham MB, et al. *Am J Cardiol*. 1989;64:651-654. PMID 2782256. DOI: 10.1016/0002-9149(89)90496-7.
6. Alrezk R, Jackson N, Al Rezk M, et al. *J Am Heart Assoc*. 2017;6:e006648. PMID 29146612. PMCID PMC5721761. DOI: 10.1161/JAHA.117.006648.
7. Wijeysundera DN, Cuthbertson BH, Duceppe E, et al. *EClinicalMedicine*. 2026;96:104015. PMID 42326382. PMCID PMC13276150. DOI: 10.1016/j.eclinm.2026.104015.

---

## 15. Governança

- Nenhum fluxograma deste documento deve converter recomendação **2a/2b** em obrigação automática.
- Nenhum score deve ser usado fora da população/desfecho para o qual foi desenvolvido sem aviso explícito.
- Valores não confirmados em fonte primária devem permanecer marcados como `VERIFICAÇÃO HUMANA NECESSÁRIA`.
- As árvores são **representações educacionais próprias da Corvia**, derivadas de recomendações e estudos citados; não são reprodução gráfica das figuras protegidas das diretrizes.
