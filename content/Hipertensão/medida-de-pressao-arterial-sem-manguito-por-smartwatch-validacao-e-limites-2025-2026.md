---
title: "Medida de Pressão Arterial Sem Manguito por Smartwatch: o Que a Validação de 2025-2026 Mostra — e Por Que Ainda Não Deve Guiar Decisão Clínica"
slug: medida-de-pressao-arterial-sem-manguito-por-smartwatch-validacao-e-limites-2025-2026
theme: "Hipertensão"
kind: documento
review_status: revisado
source_refs: ["Parati G, Ochoa JE, Abreu A, et al. Cuffless Blood Pressure Monitoring Devices: Technical Foundations and Clinical Implications. Eur J Prev Cardiol. 2026;33(7):1058-1071. DOI: 10.1093/eurjpc/zwag058. PMID: 41739846", "Choi KH, Park CS, Kang D, et al. Feasibility and performance evaluation of PPG on a Galaxy Watch in continuous central blood pressure monitoring. Eur Heart J Digit Health. 2026;7(2):ztag008. DOI: 10.1093/ehjdh/ztag008. PMID: 41716935. PMCID: PMC12912915", "Walzel S, Sebestova H, Rafl-Huttova V, Rozanek M, Rafl J. Long-term accuracy and stability of blood pressure measurements from a smartwatch: Prospective validation study. Digit Health. 2026;12:20552076261415923. DOI: 10.1177/20552076261415923. PMID: 41602947. PMCID: PMC12833194. ClinicalTrials.gov NCT06098092"]
review_note: "Os três PMIDs conferidos via PubMed E-utilities (esearch/efetch/esummary) em 09/09/2026 — título, revista, ano e achado numérico principal conferidos linha a linha contra o abstract, nenhum de memória. O documento central (Parati et al. 2026) é um scientific statement da European Society of Cardiology publicado no Eur J Prev Cardiol, com posição institucional explícita contra o uso destes dispositivos em decisão clínica — citado como tal, não como recomendação de uso. Os dois estudos de validação (Choi et al., Walzel et al.) são citados como evidência primária que sustenta essa posição, não como endosso de uso clínico. Nenhum número de acurácia foi extrapolado além do que consta no abstract/resumo estruturado de cada artigo. Checado contra `content/Hipertensão/` inteiro antes de escrever: não havia nenhum documento sobre medida de PA sem manguito/cuffless/smartwatch nesta pasta — é lacuna nova, não duplicata."
---

# Medida de Pressão Arterial Sem Manguito por Smartwatch: o Que a Validação de 2025-2026 Mostra — e Por Que Ainda Não Deve Guiar Decisão Clínica

## Por que este documento existe agora
Relógios inteligentes e outros dispositivos "cuffless" (sem manguito) que estimam a pressão arterial (PA) a partir de fotopletismografia (PPG) ou de tempo de trânsito de onda de pulso já são vendidos e usados por pacientes, muitas vezes sem que o cardiologista saiba. A pergunta que chega ao consultório não é mais "essa tecnologia existe?", e sim "posso confiar no número que meu paciente me mostra na tela do relógio?". Em 2026, pela primeira vez, existe uma resposta institucional explícita da cardiologia europeia a essa pergunta, publicada como *scientific statement* — e ela é mais cautelosa do que o entusiasmo comercial em torno do tema sugere.

## O que são, tecnicamente, os dispositivos "cuffless"
Pela revisão técnica de Parati G et al. (European Society of Cardiology, *Eur J Prev Cardiol*, 2026;33(7):1058-1071, PMID 41739846), os dispositivos sem manguito formam um **grupo tecnologicamente heterogêneo**, não uma categoria única — o que já é o primeiro ponto de cautela: validar um modelo específico não valida a classe inteira. Eles se dividem por:
- **Princípio de medida**: tempo de trânsito de onda de pulso (pulse transit time) ou análise de forma de onda, captados por sensor de contato (PPG no pulso) ou sem contato.
- **Modo de operação**: contínuo ou intermitente; automatizado ou manual.
- **Necessidade de calibração**: alguns não exigem calibração, outros exigem calibração inicial contra um manguito convencional (e, como visto adiante, essa calibração se degrada com o tempo).
- **Forma física**: vestível (relógio, anel, faixa) ou estacionário.

Essa diversidade técnica é, segundo o próprio documento, a razão pela qual **os protocolos de validação usados para monitores oscilométricos convencionais (ISO 81060-2) não se aplicam diretamente** a esta classe de dispositivos — cada categoria exige requisito de validação próprio, ainda em desenvolvimento.

## A posição institucional: potencial reconhecido, uso clínico não recomendado
O texto de Parati et al. é explícito ao separar **potencial de aplicação** de **prontidão para uso clínico**. Do próprio resumo estruturado do documento:

> *"Devido à validação de acurácia insuficiente, este scientific statement não recomenda seu uso em decisões clínicas, apesar do interesse potencial, em linha com as diretrizes internacionais que não recomendam seu uso no manejo da hipertensão."*

Isso não é rejeição da tecnologia — o documento lista aplicações clínicas potenciais genuínas e relevantes: monitorização ambulatorial ampliada fora do consultório, avaliação não enviesada do padrão circadiano de PA e de sua variabilidade, melhor detecção de hipertensão noturna, potencial de melhorar adesão e controle pressórico de longo prazo por facilitar a medida repetida, monitorização contínua em ambiente hospitalar, e — pelo menor custo frente à tecnologia convencional — possível ampliação do rastreio de hipertensão em cenários de recursos limitados. O documento também nomeia os desafios que faltam resolver antes que esse potencial vire prática: protocolos de validação padronizados por categoria de dispositivo, dados normativos de PA específicos para essas tecnologias, o volume de dados gerado (que sobrecarrega o clínico se não for filtrado), e o amadurecimento de sensores, modelos matemáticos e algoritmos.

## Dois estudos de 2026 que ilustram exatamente esse recado — o dispositivo funciona, e ainda tem limite real

### Rastreamento de mudança de pressão em tempo real (Galaxy Watch, cateterismo como padrão-ouro)
Choi KH et al. (Samsung Medical Center, *Eur Heart J Digit Health*, 2026;7(2):ztag008, PMID 41716935, PMCID PMC12912915) desenvolveram um algoritmo baseado em PPG do Samsung Galaxy Watch 6 para detectar **mudanças** na pressão arterial média (PAM), usando pressão aórtica central invasiva (via cateter durante cateterismo cardíaco) como referência — o padrão mais rigoroso possível de comparação.

- **Calibração**: 6.117 medidas em 440 participantes.
- **Validação externa prospectiva**: 114 participantes submetidos a cateterismo cardíaco esquerdo e/ou direito, com PA aórtica central registrada a intervalos de 1 minuto por cateter *pigtail*, comparada em tempo real ao sinal PPG do relógio.
- **Desfecho primário**: detecção de um aumento ≥15% na PAM em relação ao basal.
- **Resultado**: correlação forte entre a estimativa do relógio e a medida invasiva (r=0,92; p<0,001), viés médio de **0,51mmHg** (Bland-Altman). Acurácia diagnóstica para detectar aumento ≥15% da PAM: AUC 0,85 (IC95% 0,80-0,91), com desempenho robusto mesmo em conjunto de dados não calibrado. Defasagem temporal entre a mudança de PA invasiva e a detectada pelo relógio: mediana de **1,0 minuto**.

Os próprios autores emolduram o achado com a mesma cautela institucional: **"desde que nosso protocolo não atendeu aos requisitos de validação relevantes, mais estudos são necessários para confirmar sua aplicabilidade clínica potencial"** — ou seja, mesmo o estudo com o padrão-ouro mais rigoroso disponível (PA aórtica invasiva) se descreve como viabilidade preliminar, não como validação suficiente para uso clínico.

### Estabilidade da calibração ao longo de 28 dias — o achado mais prático para o consultório
Walzel S et al. (Czech Technical University, *Digit Health*, 2026;12:20552076261415923, PMID 41602947, PMCID PMC12833194) testaram algo diferente e clinicamente mais relevante para o dia a dia: **quanto tempo a calibração inicial de um smartwatch continua confiável?** A maioria dos estudos de validação de dispositivos cuffless mede acurácia em um único momento; este mediu estabilidade ao longo do intervalo de recalibração recomendado pelo fabricante.

- **Desenho**: estudo prospectivo de braço único, 37 participantes, protocolo de 28 dias — calibração inicial no dia 0 (Samsung Galaxy Watch 5 contra esfigmomanômetro validado Omron M4) seguida de 27 dias de medidas pareadas diárias.
- **Resultado agregado**: diferença média desprezível entre relógio e referência ao longo de todo o período — **-0,34mmHg** para PA sistólica e **0,62mmHg** para PA diastólica (Bland-Altman), com drift mínimo ao longo da janela de calibração (-0,19mmHg sistólica; 1,02mmHg diastólica). Pelos critérios ISO/IEEE de acurácia, o dispositivo passou em todos os quesitos, menos um.
- **O achado que mais importa na prática**: quando a PA de referência estava **10mmHg distante do ponto de calibração**, a diferença média subiu para **3,4mmHg na sistólica e 5,1mmHg na diastólica** — ou seja, a acurácia é boa perto do valor calibrado e se deteriora à medida que a PA real do paciente se afasta desse ponto.

Conclusão dos próprios autores, praticamente idêntica em espírito à posição da ESC: o dispositivo demonstrou estabilidade e acurácia de longo prazo aceitáveis para monitorização de tendência, **"mas a acurácia diminuiu conforme os valores se afastaram do ponto de calibração. Confirmação por manguito é recomendada quando a PA flutua substancialmente ou quando decisões diagnósticas ou terapêuticas estão planejadas."**

## Síntese para a prática clínica
Os três documentos, lidos juntos, convergem para uma mensagem consistente, não contraditória entre si:

1. **A tecnologia funciona razoavelmente bem para o que ela foi desenhada — detectar tendência e mudança relativa de PA**, não para substituir a medida absoluta que orienta diagnóstico e ajuste de dose. A correlação com padrão-ouro invasivo (r=0,92) e o viés médio baixo (<1mmHg) em condições próximas à calibração são dados reais e favoráveis.
2. **A acurácia depende de calibração recente e de a PA atual não se afastar muito do valor calibrado.** Um paciente hipertenso que descompensa — exatamente o cenário em que a medida mais importa — é também o cenário em que o erro do dispositivo cresce (até ~5mmHg na diastólica, no estudo de Walzel), porque a PA real se afasta do ponto de calibração.
3. **Nenhuma das três fontes recomenda decisão clínica — diagnóstico, início ou ajuste de anti-hipertensivo — baseada nesses dispositivos.** A posição da ESC é explícita, e os dois estudos de validação, mesmo favoráveis aos seus próprios dispositivos, reforçam a mesma cautela nas próprias conclusões.
4. **O uso apropriado hoje é complementar e informal**: apoiar o paciente a perceber padrão e variabilidade de PA no dia a dia (por exemplo, sinalizar quando procurar aferição com manguito), nunca substituir MAPA/MRPA validados para diagnóstico de hipertensão mascarada, do avental branco ou para ajuste terapêutico — que continuam sendo os métodos recomendados pelas diretrizes vigentes (SBC 2020, ESC 2024) para medida fora do consultório.
5. **Pergunta a fazer na anamnese, na prática**: se o paciente relatar valores de um relógio inteligente muito diferentes dos aferidos no consultório ou por MAPA/MRPA validados, **o valor confiável é o do método validado** — a diferença não indica necessariamente descompensação real, pode ser deriva de calibração do dispositivo vestível, especialmente se a calibração inicial for antiga ou a PA atual estiver longe do valor calibrado.

## VERIFICAÇÃO HUMANA NECESSÁRIA
O *scientific statement* de Parati et al. (2026) refere-se a "diretrizes internacionais" que já não recomendam o uso desses dispositivos em manejo da hipertensão, sem nomear individualmente cada diretriz nem citar o trecho exato de recomendação (classe/nível) de cada uma no resumo estruturado disponível. Não foi possível, dentro desta verificação, localizar e confirmar o texto integral do artigo (bloqueado por acesso restrito na Oxford Academic) para extrair a citação literal dessas diretrizes internacionais — o achado central relatado aqui (posição de não recomendação) está confirmado pelo próprio resumo/abstract do artigo, mas a lista específica de diretrizes que ele referencia nesse ponto não foi verificada linha a linha e não deve ser citada como se tivesse sido.
