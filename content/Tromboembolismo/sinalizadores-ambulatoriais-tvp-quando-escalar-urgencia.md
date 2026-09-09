---
title: "Sinalizadores ambulatoriais na TVP: quando escalar à urgência (além do pós-TEP)"
slug: sinalizadores-ambulatoriais-tvp-quando-escalar-urgencia
theme: "Tromboembolismo"
kind: protocolo
fonte_producao: grok
summary: "Consultório: suspeita ou TVP já conhecida — quais sinais exigem PS agora (TEP associado, isquemia de membro, sangramento, falha crítica), quais pedem imagem/retorno precoce, e o que não é alarme — sem doses e sem duplicar o pacote pós-TEP (#837) nem o algoritmo Wells/D-dímero/US."
review_status: revisado
review_note: "Revisão científica/adversarial 08/09/2026: findings PR871 reconstruídos; urgência, bibliografia e limites revistos. Fonte grok preservada."
source_refs:
  - "NICE NG158. Venous thromboembolic diseases: diagnosis, management and thrombophilia testing. Updated 2023. https://www.nice.org.uk/guidance/ng158/chapter/recommendations"
  - "Lim W, Le Gal G, Bates SM, et al. American Society of Hematology 2018 guidelines for management of venous thromboembolism: diagnosis of venous thromboembolism. Blood Adv. 2018;2(22):3226-3256. DOI: 10.1182/bloodadvances.2018024828. PMID: 30482764"
  - "Ortel TL, Neumann I, Ageno W, et al. American Society of Hematology 2020 guidelines for management of venous thromboembolism: treatment of deep vein thrombosis and pulmonary embolism. Blood Adv. 2020;4(19):4693-4738. DOI: 10.1182/bloodadvances.2020001830. PMID: 33007077"
  - "Stevens SM, Woller SC, Kreuziger LB, et al. Antithrombotic Therapy for VTE Disease: Second Update of the CHEST Guideline and Expert Panel Report. Chest. 2021;160(6):e545-e608. DOI: 10.1016/j.chest.2021.07.055. PMID: 34352278"
  - "Konstantinides SV, Meyer G, Becattini C, et al; ESC Scientific Document Group. 2019 ESC Guidelines for the diagnosis and management of acute pulmonary embolism developed in collaboration with the European Respiratory Society (ERS). Eur Heart J. 2020;41(4):543-603. DOI: 10.1093/eurheartj/ehz405. PMID: 31504429"
---

# Sinalizadores ambulatoriais na TVP: quando escalar à urgência

Pergunta de **consultório**: diante de **suspeita** de trombose venosa profunda (TVP) ou de **TVP já diagnosticada** em seguimento, o que exige **pronto-socorro agora**, o que pede **imagem/retorno precoce**, e o que pode ficar no plano ambulatorial?

**Fora de escopo deliberado:**
- pós-alta de TEP (recurrence / sangramento / sobrecarga de VD) → [`sinalizadores-ambulatoriais-pos-tep-quando-reencaminhar-urgencia`](/biblioteca/sinalizadores-ambulatoriais-pos-tep-quando-reencaminhar-urgencia) e [#837](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/837);
- algoritmo diagnóstico Wells → D-dímero → US → [`fluxograma-trombose-venosa-profunda-suspeita-wells-d-dimero-e-ultrassom`](/biblioteca/fluxograma-trombose-venosa-profunda-suspeita-wells-d-dimero-e-ultrassom);
- escolha do anticoagulante / doses → [`fluxograma-escolha-do-anticoagulante-no-tev-doac-varfarina-ou-hbpm`](/biblioteca/fluxograma-escolha-do-anticoagulante-no-tev-doac-varfarina-ou-hbpm);
- TEV do câncer (escolha DOAC vs HBPM) — docs dedicados nesta pasta.

Árvore: [`fluxograma-sinalizadores-ambulatoriais-tvp-destino`](/biblioteca/fluxograma-sinalizadores-ambulatoriais-tvp-destino). Braço TVP confirmada: [`tvp-confirmada-no-consultorio-ambulatorial-versus-internacao`](/biblioteca/tvp-confirmada-no-consultorio-ambulatorial-versus-internacao).

**Sem doses de anticoagulante, trombolítico ou antídoto neste documento.**

## Princípio

O Wells/D-dímero deste braço aplica-se a primeiro episódio de membro inferior em não gestantes. Recorrência ipsilateral, gestação e membro superior seguem algoritmos próprios. US antigo positivo não confirma novo episódio; comparar imagem se suspeita de recorrência. Edema residual não é falha terapêutica: confirmar progressão/recorrência e exposição, adesão/interação/absorção.


ASH 2020 (PMID 33007077) sugere tratamento **domiciliar** para TVP não complicada quando o contexto for seguro. ASH 2018 (PMID 30482764) e CHEST 2021 (PMID 34352278) organizam diagnóstico e fase inicial. O gate ambulatorial não é “toda perna inchada vai ao PS” — é **alarme de embolia, isquemia, sangramento ou falha logística crítica** versus **caminho diagnóstico/seguimento ambulatorial**.

## Encaminhar AGORA à urgência / PS

| Domínio | Sinalizadores |
|---|---|
| TEP associado / embolia | Dispneia súbita ou piora abrupta; dor torácica pleurítica nova; hemoptise; síncope/pré-síncope; hipoxemia sintomática nova (ESC/ERS 2019, PMID 31504429) |
| Instabilidade | Hipotensão nova, sudorese fria, confusão, taquicardia com má perfusão |
| Isquemia / extensão crítica de membro | Dor intensa desproporcional; cianose / palidez / frialdade distal; déficit sensitivo-motor; suspeita de flegmasia (cerulea/alba) |
| Sangramento sob anticoagulação | Sangramento gastrointestinal visível; hematúria franca; epistaxe/gingivorragia incoercível; hematoma em expansão; cefaleia súbita / déficit neurológico (suspeita ICH) |
| Falha / má adesão crítica | Suspensão abrupta da anticoagulação + sintomas cardiorrespiratórios ou de membro; incapacidade de obter o fármaco nas próximas horas com sintoma ativo / TVP proximal recente |
| Diagnóstico sem rede segura | TVP proximal confirmada **sem** acesso a anticoagulante, sem retorno garantido e sem suporte domiciliar — não “liberar e ver” |

**Conduta:** não observar em casa se houver dúvida fundamentada de TEP, isquemia de membro ou sangramento maior. Encaminhar; imagem avançada, reperfusão e reversão ficam no ambiente de urgência.

## Retorno ambulatorial precoce / imagem no próprio fluxo (sem PS imediato)

Usar só se **não** houver item da tabela acima:

1. Edema/dor de membro com Wells improvável → D-dímero de alta sensibilidade (ASH 2018); se positivo → ultrassom no fluxo ambulatorial.
2. Wells provável → ultrassom **direto** (não atrasar para “esperar D-dímero”); se US proximal negativo sem diagnóstico alternativo → repetir em ~1 semana (ASH 2018).
3. Equimose pequena / hematomas puntiformes sem expansão sob anticoagulação — orientar; antecipar retorno se piorar.
4. Edema residual em resolução lenta após TVP conhecida, sem piora súbita nem sintomas cardiorrespiratórios.
5. Dúvida de adesão **sem** sintoma agudo — reorganizar acesso ao fármaco e retorno curto (24–72 h).

**Atraso de imagem:** suspeita provável exige US rápido. NG158 prevê US em até 4 h quando possível; se não disponível, avaliar anticoagulação terapêutica interina com risco hemorrágico aceitável e US em até 24 h. Sem capacidade de executar esse plano, encaminhar à urgência. Não aguardar 72 h sem proteção.

## Três perguntas em 60 segundos

1. **TEP / instabilidade / isquemia de membro?** → PS agora.
2. **Sangramento maior ou falha crítica de anticoagulação?** → PS agora (ver [`fluxograma-sangramento-maior-em-paciente-anticoagulado`](/biblioteca/fluxograma-sangramento-maior-em-paciente-anticoagulado)).
3. **Só suspeita de TVP ou residual / logístico?** → caminho Wells/US ou retorno precoce + orientação escrita.

## Orientação escrita mínima

Levar ao PS se: falta de ar que piora de repente; dor no peito nova; desmaio; tosse com sangue; perna que fica azul/fria/muito dolorosa; sangramento que não para; fezes pretas/vermelhas; dor de cabeça súbita forte ou fraqueza de um lado.

## Armadilhas

- Tratar toda panturrilha dolorosa como emergência sem checar TEP/isquemia/sangramento.
- Atrasar US em Wells **provável** para “pedir D-dímero primeiro”.
- Liberar TVP proximal confirmada sem plano de fármaco + retorno.
- Duplicar aqui o checklist pós-TEP (#837): sintomas cardiorrespiratórios pós-alta de TEP → pacote pós-TEP, não este doc.
- Inventar doses neste hub de doença.

## Limite da evidência

ASH 2020 recomenda home treatment para TVP **não complicada** com certeza baixa e condicional — a elegibilidade depende de estabilidade, sangramento, adesão e rede. Este protocolo é o **gate de destino**, não o algoritmo diagnóstico completo nem a monografia do anticoagulante.

## Slugs relacionados (existentes)

- `sinalizadores-ambulatoriais-pos-tep-quando-reencaminhar-urgencia` (#837)
- `fluxograma-trombose-venosa-profunda-suspeita-wells-d-dimero-e-ultrassom`
- `trombose-venosa-profunda-diagnostico-e-tratamento`
- `trombose-venosa-profunda-distal-isolada-duracao-da-anticoagulacao-e-vigilancia`
- `fluxograma-sangramento-maior-em-paciente-anticoagulado`
- `tratamento-ambulatorial-do-tep-de-baixo-risco-aujesky-e-hestia`

## Condições para plano domiciliar

Confirmar episódio atual e localização. Distal isolada de baixo risco pode seguir US seriado em vez de anticoagulação; proximal e distal com indicação precisam tratamento oportuno, sem aguardar consulta vascular. Avaliar dor, comorbidades, rim/fígado, gestação, câncer, risco hemorrágico, acesso ao fármaco, adesão e suporte. Phlegmasia, ameaça de membro ou TEP exigem urgência. Sangramento segue [classificação maior/CRNM/nuisance](/biblioteca/sinalizadores-ambulatoriais-doac-sangramento-quando-encaminhar).
