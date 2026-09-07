---
title: "Sinalizadores ambulatoriais no TEV associado ao câncer: PS agora vs oncologia/hematologia"
slug: sinalizadores-ambulatoriais-tev-associado-ao-cancer-destino-ps-vs-oncologia
theme: "Tromboembolismo"
kind: protocolo
fonte_producao: grok
summary: "Consultório: câncer ativo + suspeita ou TEV conhecido — quando escalar ao PS (TEP/instabilidade/sangramento/isquemia), quando articular oncologia/hematologia ambulatorial (escolha de anticoagulação, trombocitopenia, mucosa GI/GU, interação), sem doses e sem duplicar #837/#871 nem ensaios DOAC vs HBPM."
review_status: pendente_revisao
review_note: "PIVOT 07/09/2026: lacuna DESTINO ambulatorial CAT além de #837 (pós-TEP) e #871 (TVP genérica). Não reescreve Caravaggio/Hokusai/AVERT/CASSINI. Fontes: ASH 2021 PMID 33570602; ASCO 2023 PMID 37075273; ITAC 2022 PMID 35772465; ESC/ERS 2019 PMID 31504429; ASH 2020 PMID 33007077. Sem doses; sem PMID inventado."
source_refs:
  - "Lyman GH, Carrier M, Ay C, et al. American Society of Hematology 2021 guidelines for management of venous thromboembolism: prevention and treatment in patients with cancer. Blood Adv. 2021;5(4):927-974. DOI: 10.1182/bloodadvances.2020003442. PMID: 33570602"
  - "Key NS, Khorana AA, Kuderer NM, et al. Venous Thromboembolism Prophylaxis and Treatment in Patients With Cancer: ASCO Guideline Update. J Clin Oncol. 2023;41(16):3063-3071. DOI: 10.1200/JCO.23.00294. PMID: 37075273"
  - "Farge D, Frere C, Connors JM, et al. 2022 international clinical practice guidelines for the treatment and prophylaxis of venous thromboembolism in patients with cancer, including patients with COVID-19. Lancet Oncol. 2022;23(7):e334-e347. DOI: 10.1016/S1470-2045(22)00160-7. PMID: 35772465"
  - "Konstantinides SV, Meyer G, Becattini C, et al; ESC Scientific Document Group. 2019 ESC Guidelines for the diagnosis and management of acute pulmonary embolism developed in collaboration with the European Respiratory Society (ERS). Eur Heart J. 2020;41(4):543-603. DOI: 10.1093/eurheartj/ehz405. PMID: 31504429"
  - "Ortel TL, Neumann I, Ageno W, et al. American Society of Hematology 2020 guidelines for management of venous thromboembolism: treatment of deep vein thrombosis and pulmonary embolism. Blood Adv. 2020;4(19):4693-4738. DOI: 10.1182/bloodadvances.2020001830. PMID: 33007077"
---

# Sinalizadores ambulatoriais no TEV associado ao câncer: PS agora vs oncologia/hematologia

Pergunta de **consultório**: paciente com **câncer ativo** (ou tratamento sistêmico recente) e **suspeita** ou **TEV já conhecido** — o que exige **pronto-socorro agora**, o que pede **articulação ambulatorial com oncologia/hematologia**, e o que **não** é alarme isolado?

**Fora de escopo deliberado:**
- pós-alta de TEP genérico → [`sinalizadores-ambulatoriais-pos-tep-quando-reencaminhar-urgencia`](sinalizadores-ambulatoriais-pos-tep-quando-reencaminhar-urgencia.md) e [#837](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/837);
- destino TVP sem pivô oncológico → [`sinalizadores-ambulatoriais-tvp-quando-escalar-urgencia`](sinalizadores-ambulatoriais-tvp-quando-escalar-urgencia.md) e [#871](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/871);
- escolha DOAC vs HBPM / ensaios → [`caravaggio-apixabana-versus-dalteparina-no-tev-do-cancer`](caravaggio-apixabana-versus-dalteparina-no-tev-do-cancer.md), [`hokusai-vte-cancer-edoxabana-versus-dalteparina`](hokusai-vte-cancer-edoxabana-versus-dalteparina.md), [`fluxograma-doac-versus-dalteparina-no-tev-do-cancer`](fluxograma-doac-versus-dalteparina-no-tev-do-cancer.md);
- profilaxia primária Khorana/AVERT/CASSINI → docs dedicados nesta pasta;
- TEP agudo + trombocitopenia (via cardio-oncologia) → pasta `Cardio-oncologia`.

Árvore: [`fluxograma-destino-ambulatorial-tev-associado-ao-cancer`](fluxograma-destino-ambulatorial-tev-associado-ao-cancer.md). Braço specialty: [`tev-associado-ao-cancer-quando-escalar-hematologia-oncologia-vs-urgencia`](tev-associado-ao-cancer-quando-escalar-hematologia-oncologia-vs-urgencia.md).

**Sem doses de anticoagulante, trombolítico ou antídoto neste documento.**

## Princípio

ASH 2021 (PMID 33570602), ASCO 2023 (PMID 37075273) e ITAC 2022 (PMID 35772465) organizam prevenção/tratamento do TEV no câncer — mas o **gate ambulatorial de destino** (PS × specialty × retorno) é o conteúdo deste pacote. O câncer eleva risco de recorrência **e** de sangramento; trombocitopenia, mucosa GI/GU e interações medicamentosa mudam o plano — não o limiar de emergência cardiorrespiratória.

## Encaminhar AGORA à urgência / PS

| Domínio | Sinalizadores |
|---|---|
| TEP / embolia | Dispneia súbita ou piora abrupta; dor torácica pleurítica nova; hemoptise; síncope/pré-síncope; hipoxemia sintomática nova (ESC/ERS 2019, PMID 31504429) |
| Instabilidade | Hipotensão nova, sudorese fria, confusão, má perfusão |
| Isquemia / extensão crítica de membro | Dor intensa desproporcional; cianose/palidez/frialdade distal; déficit sensitivo-motor; suspeita de flegmasia |
| Sangramento maior sob anticoagulação | GI visível; hematúria franca; epistaxe/gingivorragia incoercível; hematoma em expansão; cefaleia súbita / déficit neurológico (suspeita ICH) |
| Falha crítica | Suspensão abrupta da anticoagulação + sintoma cardiorrespiratório ou de membro; incapacidade de obter o fármaco nas próximas horas com TEV proximal/TEP recente ativo |
| Trombocitopenia + sintoma agudo | Contagem muito baixa **com** sangramento ativo ou TEV sintomático novo — ambiente seguro (não “ajustar em casa”) |

**Conduta:** não observar em casa se houver dúvida fundamentada. Encaminhar; imagem avançada, reperfusão e reversão ficam no PS.

## Articular oncologia / hematologia (ambulatorial ou retorno curto) — sem PS imediato

Usar só se **não** houver item da tabela acima:

1. **TEV confirmado estável** em câncer ativo — iniciar/continuar anticoagulação conforme docs de escolha; articular oncologia para plano oncológico + risco de sangramento mucosa (ASCO/ASH/ITAC).
2. **Trombocitopenia sem sangramento ativo** e sem TEP/instabilidade — decidir via com hematologia/oncologia (ver braço specialty); não inventar limiar/dose aqui.
3. **Câncer GI/GU ou alto risco mucoso** — preferir discussão de HBPM vs DOAC com a equipe oncológica (ITAC/ASH), sem doses neste hub.
4. **Interação potencial** com terapia sistêmica (inibidores/indutores fortes) — hematologia/oncologia/farmacologia clínica; não improvisar troca no consultório isolado.
5. **TEV incidental** em TC de estadiamento, estável — ver [`fluxograma-tev-incidental-em-exame-de-imagem`](fluxograma-tev-incidental-em-exame-de-imagem.md) + contato oncológico; PS só se alarme da tabela.
6. **Recorrência sob anticoagulação plena sem instabilidade** — ambiente seguro + [`tev-recorrente-sob-anticoagulacao-em-dose-terapeutica-conduta`](tev-recorrente-sob-anticoagulacao-em-dose-terapeutica-conduta.md); muitas vezes PS/observação, não só “retorno em 1 semana”.

**Prazo operacional:** retorno/contato com oncologia-hematologia em **24–72 h** se estável com dúvida de escolha/adesão/plaquetas; **até 7 dias** se estável, rede segura e plano já definido. Antecipar se fragilidade, metástase visceral, IRA ou suporte social frágil.

## Três perguntas em 60 segundos

1. **TEP / instabilidade / isquemia / sangramento maior?** → PS agora.
2. **Plaquetas baixas, mucosa GI/GU, interação ou escolha DOAC vs HBPM?** → articular hematologia/oncologia (braço specialty), sem doses aqui.
3. **Só residual / logístico / incidental estável?** → retorno curto + orientação escrita + rede oncológica.

## Orientação escrita mínima

Levar ao PS se: falta de ar súbita; dor no peito nova; desmaio; tosse com sangue; perna azul/fria/muito dolorosa; sangramento que não para; fezes pretas/vermelhas; cefaleia súbita / fraqueza de um lado; sangramento vaginal intenso fora do esperado.

## Armadilhas

- Tratar todo edema de perna em quimioterapia como “só celularite” sem gate de TEP/isquemia.
- Liberar CAT proximal sem garantir fármaco + retorno + contato oncológico.
- Duplicar aqui Caravaggio/Hokusai/ADAM ou AVERT/CASSINI.
- Confundir com #837 (pós-TEP genérico) ou #871 (TVP sem pivô câncer).
- Inventar doses ou limiar plaquetário numérico neste protocolo de destino.

## Limite da evidência

ASH/ASCO/ITAC definem prevenção e tratamento; o **roteamento ambulatorial** (PS × specialty × retorno) é operacional e depende de rede local. Este doc é o gate de destino, não a monografia do anticoagulante nem o protocolo de trombocitopenia da cardio-oncologia.

## Slugs relacionados (existentes)

- `sinalizadores-ambulatoriais-pos-tep-quando-reencaminhar-urgencia` (#837)
- `sinalizadores-ambulatoriais-tvp-quando-escalar-urgencia` (#871)
- `fluxograma-doac-versus-dalteparina-no-tev-do-cancer`
- `caravaggio-apixabana-versus-dalteparina-no-tev-do-cancer`
- `hokusai-vte-cancer-edoxabana-versus-dalteparina`
- `fluxograma-tev-incidental-em-exame-de-imagem`
- `fluxograma-sangramento-maior-em-paciente-anticoagulado`
- `tev-recorrente-sob-anticoagulacao-em-dose-terapeutica-conduta`
