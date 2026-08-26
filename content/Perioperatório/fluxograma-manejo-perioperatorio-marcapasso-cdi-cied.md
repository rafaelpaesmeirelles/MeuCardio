---
title: "Fluxograma: Manejo perioperatório de marca-passo, CDI e outros dispositivos cardíacos eletrônicos implantáveis (CIED)"
slug: fluxograma-manejo-perioperatorio-marcapasso-cdi-cied
theme: "Perioperatório"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fontes primárias conferidas via PubMed E-utilities (esearch/esummary/efetch). Achado relevante corrigido aqui: o PMID citado nos documentos já publicados do acervo para a Practice Advisory da ASA 2020 (32032098) resolve, na verdade, para a ERRATA da revista (Anesthesiology. 2020;132(4):938), não para o artigo original (132(2):225-252) — corrigido para o PMID correto do artigo original, 31939838, confirmado por esearch (Anesthesiology[ta] AND 132[volume] AND 225[page]) e esummary (mesmo DOI 10.1097/ALN.0000000000002821 já citado no acervo, PMID diferente). PMID 39316661 (AHA/ACC 2024) conferido e correto, batendo título/revista/volume/páginas/DOI com o que já constava no acervo. Conteúdo derivado dos dois documentos já publicados nesta mesma pasta, reestruturado em árvore de decisão estrita (cada nó não-raiz com um único pai, sem convergência) — a árvore mermaid do documento de origem (marcapasso-cdi-cied-cirurgia-nao-cardiaca-emi-arvore-aha-acc-2024.md) tinha múltiplos nós convergindo para os mesmos nós finais, formato não permitido para kind: fluxograma."
source_refs: ["American Society of Anesthesiologists Task Force on Perioperative Management of Patients with Cardiac Implantable Electronic Devices. Practice Advisory for the Perioperative Management of Patients with Cardiac Implantable Electronic Devices: Pacemakers and Implantable Cardioverter-Defibrillators 2020 — An Updated Report. Anesthesiology. 2020;132(2):225-252. DOI: 10.1097/ALN.0000000000002821. PMID: 31939838.", "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. Circulation. 2024;150(19):e351-e442. DOI: 10.1161/CIR.0000000000001285. PMID: 39316661.", "Derivado dos documentos já publicados no acervo 'Manejo Perioperatório de Marca-passo e CDI em Cirurgia Não Cardíaca' (content/Perioperatório/manejo-perioperatorio-de-marca-passo-e-cdi-em-cirurgia-nao-cardiaca.md) e 'Marcapasso, CDI e outros CIEDs na cirurgia não cardíaca — árvore AHA/ACC 2024' (content/Perioperatório/marcapasso-cdi-cied-cirurgia-nao-cardiaca-emi-arvore-aha-acc-2024.md), que citam as mesmas fontes acima."]
---

# Fluxograma: Manejo perioperatório de marca-passo, CDI e outros dispositivos cardíacos eletrônicos implantáveis (CIED)

Paciente com dispositivo cardíaco eletrônico implantável (DCEI/CIED — marca-passo, cardiodesfibrilador implantável, ressincronizador, marca-passo sem eletrodo ou CDI subcutâneo) precisa de um **plano do dispositivo** antes de cirurgia não cardíaca, não apenas de uma anotação "portador de MP/CDI". A principal ameaça não é o dispositivo falhar sozinho — é a interferência eletromagnética (IEM) gerada pelo próprio procedimento, sobretudo pelo eletrocautério monopolar, interagir com ele de forma imprevisível. A *Practice Advisory* 2020 da ASA detalha o preparo pré-operatório, a monitorização intraoperatória e a reavaliação pós-operatória; a diretriz AHA/ACC 2024 fecha o algoritmo de decisão por tipo de dispositivo e dependência de estimulação. A árvore abaixo integra as duas fontes.

## Árvore de decisão

```mermaid
flowchart TD
  R["Paciente portador de CIED (marca-passo, CDI, ressincronizador,<br/>marca-passo sem eletrodo ou CDI subcutâneo) candidato a cirurgia não cardíaca"] --> D1{"O dispositivo já foi identificado (tipo, fabricante/modelo), a dependência<br/>de estimulação está definida, e há interrogação nos últimos 3-6 meses<br/>ou relatório da interrogação mais recente disponível?"}
  D1 -->|"Não"| C1(["Interrogar o dispositivo (ou obter o relatório da interrogação<br/>mais recente) e definir a dependência de estimulação<br/>antes de prosseguir com o planejamento do procedimento"])
  D1 -->|"Sim"| D2{"Há risco de interferência eletromagnética (IEM) prevista no<br/>procedimento — sobretudo eletrocautério monopolar ou ablação<br/>por radiofrequência — próxima ao gerador/eletrodos?"}
  D2 -->|"Não"| C2(["Nenhuma reprogramação nem uso de ímã são necessários;<br/>manter a monitorização cardíaca padrão do CIED"])
  D2 -->|"Sim"| D3{"Qual é o tipo de dispositivo e a dependência de estimulação do paciente?"}
  D3 -->|"Marca-passo transvenoso, paciente DEPENDENTE de estimulação"| D4{"A resposta ao ímã deste modelo específico é conhecida e confiável,<br/>e a fonte de IEM não está muito próxima do gerador/eletrodos?"}
  D4 -->|"Sim"| C3(["Aplicar ímã durante o procedimento (gera estimulação assíncrona)<br/>OU reprogramar para modo assíncrono; suspender o sensor de frequência<br/>adaptativa; manter pacing e desfibrilação externos disponíveis"])
  D4 -->|"Não — resposta ao ímã desconhecida/não confiável,<br/>ou IEM muito próxima ao gerador"| C4(["Reprogramar para modo assíncrono antes da cirurgia (não confiar<br/>no ímã); suspender o sensor de frequência adaptativa; manter<br/>pacing e desfibrilação externos disponíveis"])
  D3 -->|"Marca-passo transvenoso, paciente NÃO dependente de estimulação"| C5(["Suspender o sensor de frequência adaptativa; reprogramação para<br/>modo assíncrono não é obrigatória; manter pacing externo<br/>disponível se a IEM prevista for extensa"])
  D3 -->|"CDI transvenoso, paciente DEPENDENTE de estimulação"| C6(["Desabilitar a função antitaquicardia do CDI E garantir pacing<br/>assíncrono — sempre por reprogramação, nunca só por ímã — em<br/>ambiente monitorizado, com desfibrilador externo imediato"])
  D3 -->|"CDI transvenoso, paciente NÃO dependente de estimulação"| C7(["Desabilitar a função antitaquicardia por reprogramação (ou por<br/>ímã, somente se a resposta for conhecida e confiável), com<br/>desfibrilador externo imediatamente disponível"])
  D3 -->|"Marca-passo sem eletrodo (leadless), paciente DEPENDENTE"| C8(["Reprogramar para modo assíncrono; não presumir resposta ao<br/>ímã neste tipo de dispositivo — pode simplesmente não haver resposta"])
  D3 -->|"CDI subcutâneo"| C9(["Reprogramar ou usar ímã, se a resposta for conhecida, para<br/>suspender temporariamente as terapias de choque; desfibrilador<br/>externo imediatamente disponível — o ímã pode falhar em paciente<br/>obeso ou com gerador implantado profundo"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8,C9 conduta;
```

## A regra que mais gera erro na prática: ímã em marca-passo não é o mesmo que ímã em CDI

- **Marca-passo**: a aplicação do ímã costuma iniciar estimulação assíncrona numa frequência fixa, com intervalo atrioventricular fixo — mas a resposta ao ímã é **programável**, e alguns marca-passos (inclusive alguns modelos sem eletrodo/leadless) têm resposta ao ímã diferente do esperado, ou nenhuma resposta. Não presumir a resposta sem confirmar contra o modelo específico.
- **CDI**: a aplicação do ímã **nunca** altera o modo de estimulação de um CDI — isso só acontece por reprogramação. O que o ímã faz num CDI, quando funciona, é suspender a terapia antitaquicardia (choque), não mudar o modo de estimulação. Em muitos CDIs não há forma confiável de confirmar que o ímã de fato suspendeu a terapia; em paciente obeso ou com gerador implantado profundo (CDI subcutâneo), a aplicação pode simplesmente falhar em provocar qualquer resposta.

## Monitorização, enquanto a alteração estiver em vigor

Monitorização e exibição contínua do eletrocardiograma do início da anestesia até a transferência do paciente para fora da sala, sem interrupção; oximetria de pulso e pulso periférico contínuos; equipamento de reserva (pacing e desfibrilação externos) imediatamente disponível antes, durante e depois de qualquer procedimento com potencial de IEM. Diante de interação inesperada e inexplicada entre o procedimento e o dispositivo, a conduta é **interromper o procedimento** até que a fonte de interferência seja eliminada ou controlada.

## Passo pós-operatório que vale para todo ramo em que houve reprogramação ou desabilitação de terapia

Qualquer alteração feita para o procedimento — modo assíncrono, terapia antitaquicardia desabilitada, sensor de frequência adaptativa suspenso — precisa ser **restaurada antes de o paciente sair para um ambiente sem monitorização contínua**. A ASA 2020 trata reprogramação pré-operatória e pós-operatória como duas pontas do mesmo processo, não etapas independentes; a falha em reativar a terapia de um CDI após a cirurgia já foi associada a mortes evitáveis. Reinterrogar o dispositivo é recomendado quando há indicação clínica — os gatilhos mais citados são cirurgia de urgência sem interrogação pré-operatória disponível, suspeita de alteração permanente causada pelo ímã ou de mau funcionamento do dispositivo, e IEM ocorrida em proximidade próxima ao gerador durante o procedimento.

## O que este documento não cobre

Ressonância magnética e radioterapia em portador de CIED têm corpo de evidência e recomendação próprios, fora do escopo deste fluxograma, que é estritamente sobre cirurgia não cardíaca com eletrocautério/ablação como principal fonte de interferência. A evidência de segurança de RM (registro MagnaSafe) está em documento próprio desta mesma pasta, `ressonancia-magnetica-em-portador-de-marca-passo-e-cdi-o-registro-magnasafe.md`.

## Regra prática

O magneto não é uma solução universal. O plano seguro depende de três perguntas — o paciente depende de pacing? haverá IEM relevante? o que exatamente este dispositivo faz quando recebe um magneto? — e de uma quarta, obrigatória depois: quem vai restaurar a programação antes da alta para ambiente não monitorizado?
