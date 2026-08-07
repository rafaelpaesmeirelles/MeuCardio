---
title: "Endocardite infecciosa — ESC 2023: ecocardiograma, CT, PET/CT e árvore de imagem multimodal"
slug: endocardite-esc-2023-imagem-multimodal-tte-tee-ct-pet-e-arvore-diagnostica
theme: "Endocardite"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
---

# Endocardite infecciosa — estratégia de imagem multimodal pela ESC 2023

## A mudança prática

TTE e TEE/TOE continuam sendo as técnicas centrais na suspeita de endocardite infecciosa (EI), mas a ESC 2023 incorpora formalmente **CT, imagem nuclear e MRI** quando o ecocardiograma não responde completamente a pergunta — especialmente em próteses, material protético, dispositivos e suspeita de complicação perivalvar ou extracardíaca.

A regra não é “pedir todos os exames”. É usar cada modalidade para resolver a incerteza que permanece após clínica, microbiologia e ecocardiografia.

## Antes da imagem: microbiologia é parte do diagnóstico

Quando a situação clínica permite colher antes de antibiótico, a ESC orienta **pelo menos três conjuntos de hemoculturas**, com intervalo aproximado de 30 minutos, de veia periférica e antes da antibioticoterapia.

Uma única cultura positiva deve ser interpretada com cautela; bacteremia da EI costuma ser contínua, portanto não é necessário esperar pico febril para colher.

## Árvore diagnóstica inicial

```mermaid
flowchart TD
    A["Febre/sepsis sem foco ou fenômeno embólico + fatores de risco para EI"] --> B["Hemoculturas antes do antibiótico quando clinicamente possível + avaliação clínica"]
    B --> C["TTE como imagem inicial"]
    C --> D{"TTE confirma vegetação/complicação e responde a questão clínica?"}
    D -->|Sim| E["Integrar critérios diagnósticos + Endocarditis Team + definir extensão/complicações"]
    D -->|Não ou janela limitada| F{"Suspeita clínica continua alta, prótese ou CIED?"}
    F -->|Sim| G["TEE/TOE"]
    F -->|Não| H["Reavaliar probabilidade clínica, microbiologia e diagnósticos alternativos"]
    G --> I{"Diagnóstico/ extensão ainda incertos?"}
    I -->|Não| E
    I -->|Sim| J["Imagem multimodal dirigida: CT cardíaca ± FDG-PET/CT ± WBC SPECT/CT conforme cenário"]
    J --> E
```

## Quando CT cardíaca agrega valor

CT é particularmente útil para caracterizar **complicações perivalvares/periprotéticas** e anatomia quando há dúvida ou limitação ecocardiográfica, incluindo:

- abscesso;
- pseudoaneurisma;
- fístula;
- extensão paravalvar;
- planejamento anatômico pré-operatório em situações selecionadas.

A escolha deve considerar função renal, necessidade de contraste, artefatos e o quanto o resultado mudará manejo.

## Quando PET/CT entra

A imagem metabólica com **18F-FDG PET/CT** pode aumentar a capacidade diagnóstica em cenários com material protético e dispositivos, nos quais o eco isolado pode falhar. Além do foco cardíaco, PET/CT pode ajudar a identificar:

- embolizações sépticas;
- aneurismas infecciosos;
- focos metastáticos de infecção;
- possíveis portas de entrada/focos extracardíacos.

A interpretação precisa considerar o contexto temporal após cirurgia/procedimento e padrões de captação inespecíficos.

## CIED: não olhar apenas o pocket

Em paciente com marca-passo/CDI e bacteremia ou suspeita de EI, deve-se avaliar:

- pocket/gerador;
- eletrodos;
- valvas;
- embolização pulmonar/sistêmica conforme anatomia;
- possibilidade de infecção concomitante sem sinais locais exuberantes.

## Árvore: prótese valvar ou CIED com suspeita persistente

```mermaid
flowchart TD
    A["Prótese/material protético ou CIED + suspeita de EI"] --> B["TTE + TEE/TOE + hemoculturas"]
    B --> C{"Achado definitivo?"}
    C -->|Sim| D["Endocarditis Team: antibiótico dirigido + avaliar indicação/timing de cirurgia ou extração"]
    C -->|Não| E{"Probabilidade clínica/microbiológica ainda alta?"}
    E -->|Não| F["Reavaliar diagnóstico e repetir investigação se evolução mudar"]
    E -->|Sim| G["CT cardíaca para anatomia/perivalvar + PET/CT ou outra imagem nuclear conforme material e disponibilidade"]
    G --> H{"Complicação local ou foco extracardíaco encontrado?"}
    H -->|Sim| D
    H -->|Não| I["Reavaliar critérios; considerar repetição de eco/imagem conforme evolução"]
```

## Endocarditis Team cedo, não apenas quando a cirurgia já está decidida

A ESC 2023 recomenda envolvimento precoce da **Endocarditis Team**. Isso é especialmente relevante quando existem:

- insuficiência cardíaca;
- infecção não controlada;
- complicação perivalvar;
- eventos embólicos;
- prótese/dispositivo;
- necessidade potencial de cirurgia;
- incerteza entre continuar investigação e intervir.

## Biomarcadores não diagnosticam EI

PCR, procalcitonina, leucograma, troponina, peptídeos natriuréticos, creatinina e outros marcadores podem ajudar a avaliar gravidade e resposta, mas **nenhum biomarcador tem especificidade suficiente para diagnosticar endocardite**.

## Armadilhas

1. Não excluir EI porque TTE inicial foi negativo quando a probabilidade clínica é alta.
2. Não atrasar hemoculturas esperando febre subir.
3. Não interpretar uma única hemocultura positiva fora do contexto clínico como diagnóstico automático.
4. Não usar PET/CT como substituto de microbiologia e ecocardiografia; é ferramenta complementar.
5. Não esquecer embolização/focos extracardíacos quando sintomas sistêmicos persistem.

## Fonte verificada

Delgado V, Ajmone Marsan N, de Waha S, et al. 2023 ESC Guidelines for the management of endocarditis. *Eur Heart J.* 2023;44(39):3948-4042. PMID **37622656**. DOI **10.1093/eurheartj/ehad193**.

## Status de revisão

`VERIFICAÇÃO HUMANA NECESSÁRIA`: antes de transformar esta árvore em protocolo institucional automatizado, conferir diretamente as Recommendation Tables da ESC 2023 para classe/nível e critérios formais de PET/CT, WBC SPECT/CT e CT em cada subtipo de prótese/dispositivo.
