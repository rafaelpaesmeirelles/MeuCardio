---
title: "Alteplase"
slug: alteplase
theme: "Farmacologia"
kind: farmacologia
review_status: revisado
source_refs: ["ACTIVASE (alteplase, Genentech) — rótulo aprovado pelo FDA, via DailyMed, SPL setid c669f77c-fa48-478b-a14b-80b20a0139c2, itens 1.1 e 2.1 · consultado em 29/07/2026", "Bula do profissional de saúde ACTILYSE (alteplase, Boehringer Ingelheim), versão 04/09/2012, item 4 (Contraindicações), via bulário saudedireta.com.br", "Hacke W, Kaste M, Bluhmki E, et al; ECASS Investigators. Thrombolysis with alteplase 3 to 4.5 hours after acute ischemic stroke (ECASS III). N Engl J Med. 2008;359(13):1317-1329. DOI: 10.1056/NEJMoa0804656. PMID: 18815396", "Byrne RA, Rossello X, Coughlan JJ, et al. 2023 ESC Guidelines for the management of acute coronary syndromes. Eur Heart J. 2023;44(38):3720-3826, Tabela S10 do material suplementar. DOI: 10.1093/eurheartj/ehad191. PMID: 37622654"]
---

# Alteplase

## Nome generico
Alteplase (ativador do plasminogênio tecidual recombinante, rt-PA)

## Classe
Trombolítico/fibrinolítico

## Mecanismo acao
Ativa a conversão de plasminogênio em plasmina de forma seletiva na superfície da fibrina, promovendo a lise do trombo já formado

## Indicacoes cardiologicas e neurologicas
Infarto agudo do miocárdio com supra de ST (IAMCSST) quando ICP primária não está disponível em tempo hábil, tromboembolismo pulmonar de alto risco, AVC isquêmico agudo dentro da janela terapêutica, e desobstrução de cateteres ocluídos

## Dose — IAMCSST (esquema acelerado, infusão de 90 minutos)
- **peso ≥65 kg**: bolus IV de 15 mg, seguido de 50 mg em 30 minutos, seguido de 35 mg em 60 minutos — dose total máxima de 100 mg
- **peso <65 kg**: bolus IV de 15 mg, seguido de 0,75 mg/kg em 30 minutos, seguido de 0,5 mg/kg em 60 minutos — dose total máxima de 100 mg
- **fonte**: diretriz ESC 2023 de síndromes coronarianas agudas, Tabela S10 do material suplementar (Byrne RA, Rossello X, Coughlan JJ, et al. Eur Heart J. 2023;44(38):3720-3826, PMID 37622654) — corte de peso alinhado ao registro estruturado de medicamentos (`medicamentos/metadados.json`), que usa a mesma fonte; StatPearls (fonte anterior) usava 67 kg

## Dose — AVC isquemico agudo
0,9 mg/kg, dose total máxima de 90 mg — 10% administrado em bolus IV em 1 minuto, restante infundido em 60 minutos; administrar o quanto antes, **dentro de 3 horas** do início dos sintomas.
- **fonte**: rótulo do ACTIVASE (alteplase, Genentech) aprovado pelo FDA, item 2.1, conferido em 29/07/2026 — confere com a bula brasileira do Actilyse quanto à dose e à janela

**A menção a "até 4,5 h conforme protocolo estendido" foi removida daqui em 29/07/2026, e o motivo importa.** Ela vinha do StatPearls, fonte terciária, sem indicar qual protocolo. Conferido nesta data: **as três rotulagens registradas convergem em 3 horas** — a bula brasileira do Actilyse (2012), o rótulo do Activase aprovado pelo FDA em sua versão vigente, e o rótulo do TNKase atualizado em 02/2025, que é explícito ao dizer que a alteplase "é aprovada para uso dentro de 0 a 3 horas". O que se afastou foi a prática, não o rótulo.

**Resolvido em 29/07/2026** com a leitura do ECASS III (Hacke W et al., N Engl J Med. 2008;359(13):1317-1329, PMID 18815396) — confirmado: a janela estendida de **3 a 4,5 horas** do início dos sintomas tem sustentação em ensaio clínico randomizado, duplo-cego, placebo-controlado. 821 pacientes com AVC isquêmico agudo (excluídos os com hemorragia ou grande infarto à TC), randomizados 1:1 para alteplase IV (0,9mg/kg) ou placebo, tempo mediano de administração de 3h59min. Desfecho favorável (Rankin modificado 0-1 aos 90 dias): **52,4% com alteplase vs. 45,2% com placebo** (OR 1,34; IC95% 1,02-1,76; p=0,04). Hemorragia intracraniana sintomática foi mais frequente com alteplase (2,4% vs. 0,2%; p=0,008), sem diferença significativa na mortalidade (7,7% vs. 8,4%; p=0,68). O campo `dosing` do verbete estruturado da alteplase deve ser atualizado com a mesma citação, para as duas telas não divergirem.

## Contraindicacoes
Segundo a bula do ACTILYSE (item 4), organizadas em blocos — lista bem mais extensa que a de fontes terciárias como StatPearls:

- **Hipersensibilidade**: ao princípio ativo, à gentamicina (resíduo do processo de fabricação) ou a qualquer componente da fórmula, em qualquer indicação
- **Geral, alto risco de hemorragia (todas as indicações)**: distúrbio hemorrágico significativo no momento ou nos últimos 6 meses, diátese hemorrágica conhecida; anticoagulação oral efetiva (ex.: varfarina, INR >1,3); histórico de dano ao SNC (neoplasia, aneurisma, cirurgia intracraniana/espinhal); histórico, evidência ou suspeita de hemorragia intracraniana (incluindo subaracnóidea); hipertensão arterial grave não controlada; cirurgia de grande porte ou trauma grave nos últimos 10 dias; RCP prolongada/traumática (>2min), parto nos últimos 10 dias, punção recente de vaso não compressível; hepatopatia grave (insuficiência hepática, cirrose, hipertensão portal com varizes esofágicas, hepatite ativa); endocardite bacteriana, pericardite; pancreatite aguda; doença ulcerativa gastrintestinal nos últimos 3 meses; aneurisma arterial, malformação arteriovenosa; neoplasia com alto risco de sangramento
- **Específico de IAM e embolia pulmonar**: AVC hemorrágico ou de origem desconhecida a qualquer momento; AVC isquêmico ou AIT nos 6 meses anteriores (exceto o próprio AVC isquêmico agudo corrente, dentro de 3 horas)
- **Específico de AVC isquêmico agudo**: início dos sintomas há mais de 3 horas antes da infusão, ou horário de início desconhecido; sintomas melhorando rapidamente ou apenas leves antes da infusão; AVC grave (ex.: NIHSS >25) clínico e/ou por imagem; convulsão no início do quadro; AVC prévio ou traumatismo craniano grave nos últimos 3 meses; combinação de AVC anterior e diabetes mellitus; heparina nas 48h anteriores com TTPa aumentado; plaquetas <100.000/mm³; PAS >185 mmHg, PAD >110 mmHg ou necessidade de terapia agressiva IV para atingir esses limites; glicemia <50 ou >400 mg/dL; idade <18 ou >80 anos

Lista alinhada ao registro estruturado de medicamentos, mesma fonte e mesma versão de bula.
