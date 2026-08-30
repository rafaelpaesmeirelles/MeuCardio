---
title: "Quando usar ácido bempedoico depois do CLEAR Outcomes"
slug: quando-usar-acido-bempedoico-apos-clear-outcomes
theme: "Prevenção e lipídios"
kind: protocolo
summary: "Protocolo de decisão: ácido bempedoico 180 mg/dia entra no intolerante a estatina com ASCVD ou alto risco (CLEAR Outcomes reduz MACE de 4 pontos, não reduz morte CV nem morte total nem AVC). Não duplica o dump do ensaio nem a monografia; não compete com ezetimiba (IMPROVE-IT) nem com PCSK9; não trata inclisirana como se tivesse desfecho cardiovascular."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Números do CLEAR Outcomes conferidos no abstract (PMID 36876740; Nissen, NEJM 2023;388(15):1353-1364; DOI 10.1056/NEJMoa2215024; NCT02993406) e já transcritos no documento da casa hipolipemiantes-nao-estatinicos-improve-it-clear-outcomes-e-o-limite-do-orion. Este arquivo NÃO re-despeja o ensaio: é o 'quando usar'. Contraindicação de sinvastatina >40 mg e lactação lidas na monografia da casa acido-bempedoico (bula NUSTENDI). Não atribuir redução de mortalidade. Não promover inclisirana a desfecho CV (ORION-10/11 são LDL). Revisão científica concluída em 30/08/2026."
source_refs:
  - "Nissen SE, Lincoff AM, Brennan D, Ray KK, Mason D, Kastelein JJP, et al.; CLEAR Outcomes Investigators. Bempedoic Acid and Cardiovascular Outcomes in Statin-Intolerant Patients. N Engl J Med. 2023;388(15):1353-1364. DOI: 10.1056/NEJMoa2215024. PMID: 36876740. NCT02993406. Números conferidos no abstract nesta revisão editorial; dump completo na casa: hipolipemiantes-nao-estatinicos-improve-it-clear-outcomes-e-o-limite-do-orion."
  - "Documento da casa acido-bempedoico — monografia (dose 180 mg, gota, creatinina, contraindicação sinvastatina >40 mg/dia, lactação contraindicada na bula brasileira)."
  - "Documento da casa fluxograma-dislipidemia-meta-de-ldl-e-escalonamento-esc-eas-2025 e intolerancia-a-estatina-definicao-operacional-e-protocolo-de-reexposicao-eas-2015 — este protocolo entra depois da reexposição, não no lugar dela."
  - "Cannon CP, et al.; IMPROVE-IT. N Engl J Med. 2015. PMID: 26039521 — ezetimiba TEM desfecho CV, mas em quem JÁ toma estatina após SCA. Não é o CLEAR."
---

# Quando usar ácido bempedoico depois do CLEAR Outcomes

## Função deste protocolo

A casa já tem o dump do ensaio (IMPROVE-IT + CLEAR + o limite do ORION) e a monografia do fármaco. Faltava a pergunta do plantão e do ambulatório: **este paciente deve sair com ácido bempedoico hoje?**

A resposta curta: **sim, no intolerante a estatina com doença aterosclerótica ou alto risco, quando a reexposição falhou e o LDL continua acima da meta — com a reserva explícita de que o ensaio não reduziu morte cardiovascular, morte total nem AVC.**

## O que o CLEAR mostrou — só o que muda a prescrição

- **13.970** intolerantes a estatina (incapazes ou não dispostos por efeito adverso inaceitável), com ASCVD ou alto risco.
- Ácido bempedoico **180 mg/dia** versus placebo. Seguimento mediano **40,6 meses**.
- LDL basal **139 mg/dL**; diferença adicional de **−29,2 mg/dL** em 6 meses (21,1 pontos percentuais).
- Primário (morte CV + IAM não fatal + AVC não fatal + revascularização coronariana): **11,7% versus 13,3%**; **HR 0,87 (0,79–0,96); P=0,004**.
- **Sem efeito significativo** sobre AVC fatal/não fatal, **morte cardiovascular** e **morte por qualquer causa**.
- Mais **gota (3,1% vs 2,1%)** e **colelitíase (2,2% vs 1,2%)**; pequenos aumentos de creatinina, ácido úrico e enzimas hepáticas.

Quem prescreve ácido bempedoico como se fosse “estatina sem músculo que reduz mortalidade” está lendo o ensaio errado.

## Árvore de decisão

```mermaid
flowchart TD
  R0["LDL acima da meta em prevenção<br/>secundária ou alto/muito alto risco"] --> D1{"Toma estatina em dose máxima tolerada?"}

  D1 -->|"Sim"| C1(["Não é a pergunta do CLEAR.<br/>Escalonar ezetimiba (IMPROVE-IT) e/ou<br/>PCSK9. Bempedoico é adição, não substituto"])

  D1 -->|"Não — não toma estatina"| D2{"Reexposição a estatina já foi tentada<br/>(dose baixa, estatina alternativa,<br/>protocolo EAS da casa)?"}

  D2 -->|"Não"| C2(["Primeiro: documentar intolerância e<br/>reexpor. Ver protocolo de intolerância.<br/>CLEAR não dispensa essa etapa"])

  D2 -->|"Sim — intolerância verdadeira<br/>ou recusa documentada"| D3{"ASCVD ou alto risco no sentido do CLEAR?"}

  D3 -->|"Não — só prevenção primária<br/>de baixo risco"| C3(["CLEAR não responde.<br/>Não prescrever para 'melhorar o LDL'<br/>em baixo risco sem evidência de desfecho"])

  D3 -->|"Sim"| D4{"Gota ativa, colelitíase sintomática,<br/>gravidez, lactação, ou sinvastatina >40 mg?"}

  D4 -->|"Sim"| C4(["Não iniciar agora.<br/>Gota/cálculo: tratar e reavaliar.<br/>Gravidez/lactação/sinvastatina alta: contraindicado"])

  D4 -->|"Não"| C5(["Ácido bempedoico 180 mg/dia.<br/>Expectativa: menos MACE de 4 pontos,<br/>NÃO menos morte. Combinar ezetimiba<br/>se ainda fora da meta. Vigiar urato e GOT"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Onde o bempedoico NÃO entra

- **No lugar da estatina** em quem tolera estatina. O CLEAR é um ensaio de intolerantes contra placebo, não contra atorvastatina.
- **Como se reduzisse mortalidade.** O primário é um composto de 4 pontos puxado por IAM e revascularização.
- **Como se fosse inclisirana.** ORION-10/11 medem LDL, não MACE. CVOT de inclisirana não lido / não publicado como desfecho nesta revisão editorial — não antecipar.
- **Na gestação ou na lactação.** Bula brasileira do Nustendi contraindica lactação (monografia da casa).
- **Com sinvastatina acima de 40 mg/dia.** Interação de exposição; contraindicação de prescrição.

## Vigilância prática

- Ácido úrico e crises de gota — avisar o paciente antes da primeira caixa.
- Colelitíase.
- Creatinina e transaminases — aumentos pequenos no ensaio; não transformar isso em “nefrotóxico” sem contexto.
- LDL em 8–12 semanas para decidir se entra ezetimiba (se ainda não estiver) ou PCSK9.

## Mensagem prática

**Ácido bempedoico 180 mg/dia é a opção com desfecho cardiovascular medido para quem não toma estatina de verdade — depois da reexposição, em ASCVD ou alto risco, sem pretender redução de morte.** Ezetimiba continua a primeira adição em quem já está em estatina.
