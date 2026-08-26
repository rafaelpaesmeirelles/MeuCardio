---
title: "Fluxograma: Choque inapropriado de CDI — investigação e manejo"
slug: fluxograma-choque-inapropriado-de-cdi-investigacao-e-manejo
theme: "Dispositivos"
kind: fluxograma
fonte_producao: chatgpt
summary: "Manejo do choque de CDI com triagem imediata de instabilidade e choques recorrentes, proteção para desfibrilação externa e, após estabilização, interrogação do dispositivo para distinguir terapia apropriada de causas de choque inapropriado."
review_status: revisado
review_note: "PMIDs conferidos individualmente no PubMed via E-utilities (esummary) nesta sessão: 36017572 (ESC 2022 VA/SCD, Zeppenfeld K, Eur Heart J 43(40):3997-4126 — corrige um PMID citado incorretamente em rodada anterior deste projeto, 36017553, que na verdade é a diretriz de avaliação perioperatória), 26949427 (consenso HRS/EHRA/APHRS/SOLAECE 2015 de programação de CDI, Wilkoff BL, J Arrhythm 32(1):1-28) e 23131066 (MADIT-RIT, Moss AJ, NEJM 367(24):2275-2283) — título, revista, volume/página e autor conferidos contra o registro oficial antes de citar. Pendente revisão médica independente antes de uso assistencial."
source_refs: ["2022 ESC Guidelines for the management of patients with ventricular arrhythmias and the prevention of sudden cardiac death · European Heart Journal · 2022 · 43(40):3997-4126 · https://pubmed.ncbi.nlm.nih.gov/36017572/", "2015 HRS/EHRA/APHRS/SOLAECE expert consensus statement on optimal implantable cardioverter-defibrillator programming and testing · Journal of Arrhythmia · 2016 · 32(1):1-28 · https://pubmed.ncbi.nlm.nih.gov/26949427/", "Reduction in inappropriate therapy and mortality through ICD programming (MADIT-RIT) · New England Journal of Medicine · 2012 · 367(24):2275-2283 · https://pubmed.ncbi.nlm.nih.gov/23131066/"]
---

# Fluxograma: Choque inapropriado de CDI — investigação e manejo

Todo choque de CDI exige primeiro **triagem clínica imediata**. Instabilidade
hemodinâmica, arritmia sustentada ou choques recorrentes são manejados como
emergência, com monitorização e capacidade de desfibrilação externa, sem
esperar a interrogação. Depois de estabilizar e proteger o paciente, revisar o
eletrograma armazenado evita presumir a causa pelo relato ou pela frequência
cardíaca isolada. A árvore então segue as quatro causas mais frequentes de
terapia inapropriada — taquicardia
supraventricular mal discriminada, falha de integridade do sistema de
eletrodo, ruído/miopotencial e sobredetecção de onda T —, cada uma com conduta
própria.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Choque(s) do CDI"] --> D0{"Instabilidade hemodinâmica,<br/>arritmia sustentada ou<br/>choques recorrentes?"}

  D0 -->|"Sim"| C0(["ABC/ACLS conforme o ritmo, monitorização<br/>contínua e pás de desfibrilação externa<br/>instaladas; tratar TV/FV ou tempestade elétrica<br/>sem aguardar interrogação"])
  D0 -->|"Não — paciente estável,<br/>episódio isolado"| C00(["Monitorização e avaliação clínica;<br/>providenciar interrogação urgente<br/>do dispositivo"])

  C0 --> R1["Após estabilização e proteção<br/>para desfibrilação externa:<br/>interrogar o dispositivo"]
  C00 --> R1
  R1 --> D1{"Eletrograma armazenado:<br/>a terapia foi apropriada?"}

  D1 -->|"Sim, para TV/FV real"| C1(["Choque apropriado: investigar gatilhos<br/>reversíveis, isquemia e descompensação;<br/>reavaliar programação, antiarrítmico<br/>e indicação de ablação conforme<br/>a arritmia clínica"])

  D1 -->|"Não, ou permanece incerta"| D2{"Causa do choque inapropriado"}

  D2 -->|"Taquicardia supraventricular<br/>na zona de detecção"| D3{"Discriminadores SVT/VT<br/>já estão otimizados?"}
  D3 -->|"Não"| C2(["Reprogramar discriminadores e zonas<br/>conforme o consenso HRS/EHRA/APHRS/<br/>SOLAECE 2015; ampliar a janela de<br/>monitorização antes da terapia"])
  D3 -->|"Sim, mesmo assim recorrente"| C3(["Tratar a taquiarritmia atrial<br/>(controle de frequência/ritmo ou<br/>ablação) e reavaliar limites, duração<br/>e discriminadores da zona de VT;<br/>não baixar o limiar reflexamente"])

  D2 -->|"Sobredetecção não fisiológica<br/>(ruído/miopotencial/interferência)"| D4{"Integridade do sistema confirmada<br/>por eletrograma, tendências de<br/>impedância, manobras provocativas<br/>e imagem quando indicada?"}
  D4 -->|"Não — fratura, deslocamento<br/>ou dano de isolamento"| C4(["Reprogramar em modo de segurança<br/>temporário e planejar reintervenção<br/>ou troca do eletrodo"])
  D4 -->|"Sim — sistema íntegro"| C5(["Identificar interferência externa ou<br/>miopotencial; eliminar o gatilho e<br/>ajustar sensibilidade, filtro e vetor<br/>de sensing por especialista"])

  D2 -->|"Sobredetecção de onda T"| C6(["Reprogramar vetor/polaridade de<br/>sensing e sensibilidade dinâmica<br/>conforme o consenso de programação"])

  D2 -->|"Causa não identificada<br/>na interrogação"| C7(["Intensificar a monitorização remota,<br/>reavaliar em consulta próxima e<br/>considerar Holter/monitor externo"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C00,C1,C2,C3,C4,C5,C6,C7 conduta;
```

## O que a árvore não mostra

**Choques repetidos ou causa ainda incerta exigem avaliação urgente.** Antes
de suspender terapias, instalar monitorização contínua e proteção com
desfibrilação externa. Se os choques forem recorrentes e houver forte suspeita
de terapia inapropriada, a suspensão temporária por programação ou ímã pode
ser considerada apenas com capacidade imediata de tratar TV/FV externamente;
o ímã não corrige a causa. Se os choques tratarem TV/FV real, conduzir a
tempestade elétrica e não atrasar desfibrilação para interrogar o CDI.

**A reprogramação de discriminadores segue princípios do consenso de 2015, não
uma regra única.** O documento recomenda, entre outras medidas, ampliar o
número de intervalos exigidos antes da terapia e usar zonas de detecção mais
altas quando clinicamente seguro — a escolha exata depende da arritmia clínica
de base, não é um ajuste padronizado para todo paciente.

**MADIT-RIT é a evidência de que reprogramar reduz terapia inapropriada e
mortalidade, não só desconforto.** O braço com detecção retardada/zona alta
teve redução de 79% na primeira terapia inapropriada e também menor
mortalidade por todas as causas em relação à programação convencional — é por
isso que a árvore trata reprogramação como conduta ativa, não como medida
paliativa.

**Fratura de eletrodo pode coexistir com terapia apropriada prévia.** Um
sistema que já tratou VT real corretamente no passado não está isento de
desenvolver falha de integridade depois — a checagem de impedância e imagem
vale mesmo quando o histórico do dispositivo é bom. Impedância pontual normal
também não exclui fratura intermitente; tendências e eletrograma importam.

**O suporte psicológico ao choque, apropriado ou não, não está na árvore** por
não ser um ramo de decisão clínica sobre a programação, mas é parte
recomendada do seguimento — choque de CDI é evento com impacto relatado sobre
qualidade de vida e ansiedade, independentemente da causa identificada.
