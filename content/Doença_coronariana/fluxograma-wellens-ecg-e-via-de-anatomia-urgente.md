---
title: "Fluxograma: Wellens — do ECG à via de anatomia urgente"
slug: fluxograma-wellens-ecg-e-via-de-anatomia-urgente
theme: "Doença coronariana"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de beira de leito: T bifásica (tipo A) ou T precordial profunda (tipo B) no intervalo livre de dor → não é esteira, é SCA até a anatomia. Mapeia o tempo do cateterismo nas vias ESC 2023 de risco muito alto e alto risco, sem criar classe para a síndrome nomeada."
review_status: revisado
review_note: "Árvore original. Não duplica o fluxograma geral de SCA nem o de timing da NSTE-ACS: entra quando o plantão reconhece o padrão de T e precisa de um caminho que impeça o ramo seletivo/ergométrico. Classes: invasiva imediata no risco muito alto (I C) e invasiva na internação no alto risco / alta suspeita de angina instável (I A), precoce < 24 h (IIa A) — conferidas no fluxograma-sca-sem-supra-timing-da-estrategia-invasiva-esc-2023 (Recommendation Table 4). A ESC 2023 cita Wellens’ sign na narrativa, não na tabela. SBC 2024: angina instável = contraindicação absoluta de ergometria (sem classe numerada no documento transcrito). Eco é opcional e não atrasa a sala."
source_refs:
  - "de Zwaan C, Bär FW, Wellens HJ. Am Heart J. 1982;103(4 Pt 2):730-736. DOI: 10.1016/0002-8703(82)90480-x. PMID: 6121481."
  - "de Zwaan C, Bär FW, Janssen JH, et al. Am Heart J. 1989;117(3):657-665. DOI: 10.1016/0002-8703(89)90742-4. PMID: 2784024."
  - "Rhinehardt J, Brady WJ, Perron AD, Mattu A. Electrocardiographic manifestations of Wellens' syndrome. Am J Emerg Med. 2002;20(7):638-643. DOI: 10.1053/ajem.2002.34800. PMID: 12442245."
  - "Byrne RA, Rossello X, Coughlan JJ, et al. 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2023;44(38):3720-3826. DOI: 10.1093/eurheartj/ehad191. PMID: 37622654. Narrativa (Wellens’ sign); timing na Recommendation Table 4."
  - "Diretriz Brasileira de Ergometria em População Adulta – 2024. Arq Bras Cardiol. 2024. Angina instável = contraindicação absoluta. Documento CorVIA: teste-ergometrico-seguranca-contraindicacoes-e-criterios-de-interrupcao-sbc-2024."
  - "Alexander J, Rizzolo D. Wellens syndrome: An important consideration in patients with chest pain. JAAPA. 2023;36(2):25-29. PMID: 36701576."
---

# Fluxograma: Wellens — do ECG à via de anatomia urgente

Esta árvore começa **depois** do ECG de 12 derivações, quando há T bifásica ou T profundamente invertida em precordiais e a pergunta do plantão é “esteira amanhã ou hemodinâmica?”. Não substitui o fluxograma geral de SCA nem o de timing da NSTE-ACS. Desvia para eles quando o caso deixa de ser o padrão de Wellens e vira oclusão em curso, outro diagnóstico ou NSTE-ACS sem o epônimo.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Dor torácica recente, agora ausente ou mínima,<br/>e ECG com T bifásica ou T profundamente invertida<br/>em V2–V3 (pode ir até V1–V6)"] --> D1{"Dor em curso com supra persistente<br/>ou equivalente de oclusão?"}

  D1 -->|"Sim"| C1(["Sair: via STEMI / oclusão.<br/>Não rotular Wellens. Não fibrinolisar<br/>por 'equivalente de Wellens'"])

  D1 -->|"Não"| D2{"O padrão está no intervalo LIVRE de dor?<br/>ST isoelétrico ou <1 mm, sem Q precordial,<br/>progressão de R preservada,<br/>história de angina recente?"}

  D2 -->|"Não — T isolada, com dor,<br/>ou faltam critérios"| C2(["Não fechar o epônimo.<br/>Seguir fluxograma de SCA / diagnóstico alternativo.<br/>Ainda assim: não mandar à esteira<br/>enquanto a NSTE-ACS não estiver afastada"])

  D2 -->|"Sim — conjunto de Wellens"| D3{"Tipo A (T bifásica, + inicial / − terminal)<br/>ou tipo B (T profunda simétrica)?<br/>Descrever a morfologia; a conduta é a mesma"}

  D3 -->|"Tipo A ou tipo B"| P1["NÃO pedir teste ergométrico, eco de estresse<br/>nem cintilografia. Internar monitorizado.<br/>AAS + P2Y12 e anticoagulante parenteral<br/>como SCA até a anatomia.<br/>Troponina seriada. Eco só se não atrasar a sala"]

  P1 --> D4{"Dor recorrente/refratária, T que 'normaliza'<br/>na crise, supra intermitente, instabilidade,<br/>IC isquêmica ou arritmia grave?"}

  D4 -->|"Sim — risco muito alto"| C3(["Angiografia de emergência<br/>o mais rápido possível<br/>Classe I C — ESC 2023, critério de NSTE-ACS,<br/>não classe da síndrome nomeada"])

  D4 -->|"Não"| D5{"IAMSSST pelo algoritmo de troponina<br/>ou T dinâmica em território anterior?"}

  D5 -->|"Sim — alto risco"| C4(["Invasiva durante a internação Classe I A;<br/>precoce <24 h deve ser considerada Classe IIa A.<br/>Não ramo seletivo"])

  D5 -->|"Não — troponina ainda negativa,<br/>padrão típico"| C5(["Alta suspeita de angina instável:<br/>invasiva nesta internação Classe I A.<br/>Não alta. Não esteira. Não angio-TC<br/>como substituto da anatomia no conjunto clássico"])

  C4 --> D6{"Anatomia: DA proximal/ostial crítica?"}
  C5 --> D6
  C3 --> D6

  D6 -->|"Sim"| C6(["Revascularizar a DA (ICP ou CRM<br/>conforme anatomia e Heart Team).<br/>Não tratar só clinicamente o padrão clássico"])

  D6 -->|"Não — outro vaso, ponte, espasmo,<br/>coronárias sem obstrução"| C7(["O ECG era o padrão; o mecanismo pode não ser DA ostial.<br/>Tratar o que a sala mostrou. Se sem obstrução:<br/>via MINOCA / espasmo / takotsubo — não 'alta, era Wellens'"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Como ler cada desvio

**C1 — supra persistente não é Wellens.** O epônimo descreve T no intervalo *sem* dor. Dor + supra é oclusão até a angiografia. Fibrinolisar “porque é equivalente de Wellens” mistura duas entidades. Equivalentes de supra (SBC 2025, Classe I B para *procurá-los*) são outra lista.

**C2 — critério incompleto não libera esteira.** Faltou história de angina, ou a T é só V1 em mulher jovem, ou o paciente ainda tem dor e o ST não foi serializado. Não fechar o nome. Também não enviar à ergometria “para ver se é isquemia”: se a NSTE-ACS não foi afastada, a esteira continua contraindicada (angina instável = absoluta na SBC 2024).

**D3 — tipo A e tipo B não ramificam conduta.** A bifurcação existe só para obrigar o plantão a *olhar* a morfologia. Tipo A (~25%, bifásica) não é forma menor. A literatura às vezes inverte tipo 1/tipo 2: descreva a onda.

**P1 — a frase que o fluxograma existe para gravar.** Pedido de teste ergométrico e laudo de Wellens não convivem. Internação, DAPT e heparina (ou o anticoagulante do protocolo local) são da via de SCA, não de uma classe inventada para o epônimo. Doses: documento de posologia já publicado.

**C3 versus C4/C5 — o tempo vem da ESC de NSTE-ACS.** Recorrência de dor ou ST/T dinâmico recorrente (sobretudo supra intermitente, ou T que pseudonormaliza) = imediata, Classe I C. IAMSSST ou T dinâmica sem instabilidade = internar para anatomia, visando < 24 h (IIa A) mas de qualquer modo antes da alta (I A). Troponina negativa com conjunto clássico = ainda assim alta suspeita de angina instável → anatomia nesta internação (I A). Nenhum desses três ramos é “Wellens Classe X”.

**C5 — o ramo que a porta mais erra.** Paciente conversando, enzima normal, vaga na esteira amanhã. É exatamente a série de 1982. A ESC reserva o teste não invasivo ao *baixo* índice de suspeita. Este não é o caso.

**C7 — a sala manda no mecanismo.** Wellens clássico é DA proximal. Nem todo padrão de T anterior é ostial, e nem toda DA crítica desenha o padrão. Espasmo, ponte, takotsubo e MINOCA saem para os protocolos próprios. O que não volta é a esteira.

## O que a árvore não mostra

**Percentual de “quantos vão para infarto se não cateterizar”.** A série de 1982 é pré-ICP e pequena. Revisões repetem que a maior parte dos não revascularizados teve infarto anterior em dias. Não usar isso como incidência 2026.

**Especificidade 99% / 97%** citada em algumas revisões. Não conferida em artigo primário nesta revisão editorial. Não entra no diagrama.

**Eco com alteração segmentar.** Apoia, não decide, não atrasa. Por isso ficou em P1 como opcional.

**Qual P2Y12, qual heparina, qual alvo de LDL.** Fora do recorte. Ver posologia e o playbook de alta.

**Classe ESC da síndrome nomeada.** Não existe na tabela. A narrativa cita Wellens’ sign (T bifásica ou T negativa proeminente, DA proximal grave). Fim.

## Tudo com Tudo

- [Protocolo: síndrome de Wellens — reconhecimento e por que não fazer teste ergométrico](sindrome-de-wellens-reconhecimento-e-por-que-nao-fazer-teste-ergometrico.md)
- [Fluxograma: SCA sem supra — timing da estratégia invasiva (ESC 2023)](fluxograma-sca-sem-supra-timing-da-estrategia-invasiva-esc-2023.md)
- [Fluxograma: Síndrome Coronariana Aguda (ESC 2023)](fluxograma-sindrome-coronariana-aguda-esc-2023.md)
- [Protocolo de Dor Torácica na Emergência (SBC 2025)](protocolo-de-dor-toracica-na-emergencia-escore-heart-e-tempo-porta-ecg-sbc-2025.md)
- [Teste Ergométrico — Segurança (SBC 2024)](teste-ergometrico-seguranca-contraindicacoes-e-criterios-de-interrupcao-sbc-2024.md)
- [Posologia de antiagregantes e anticoagulantes na SCA](posologia-de-antiagregantes-e-anticoagulantes-na-sindrome-coronariana-aguda-esc-2023.md)
- [Fluxograma MINOCA](fluxograma-minoca-investigacao-diagnostica.md)
- [Takotsubo](../Saúde_mental_e_cardiologia/fluxograma-cardiomiopatia-takotsubo-reconhecimento-manejo-agudo.md)
- [Cocaína](../Geral/cocaina-e-risco-cardiovascular-vasoespasmo-coronariano-e-infarto.md)
