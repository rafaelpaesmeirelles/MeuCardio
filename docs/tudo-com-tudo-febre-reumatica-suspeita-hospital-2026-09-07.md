---
title: "Tudo-com-Tudo — Febre_reumática: suspeita ambulatorial FRA → hospital (2026-09-07)"
slug: tudo-com-tudo-febre-reumatica-suspeita-hospital-2026-09-07
theme: "Febre reumática"
kind: nota
fonte_producao: grok
summary: "Relatório do pivô: lacuna fina além de #850 (benzatina/adesão) — destino ambulatorial na suspeita de febre reumática aguda para hospital/eco."
review_status: pendente_revisao
review_note: "Relatório operacional do pacote; não é conteúdo clínico prescritivo."
---

# Tudo-com-Tudo — Febre_reumática: suspeita ambulatorial de FRA → hospital (2026-09-07)

## Escopo

Lacuna fina **além de #850**: reconhecimento ambulatorial de **suspeita de febre reumática aguda** e **destino** (PS agora vs. hospital com eco Doppler). Não densifica doses, não reescreve Jones 2015, nem graduação SBC da cardite, nem adesão à benzatina.

## Anti-colisão

- Não toca pacote adesão/benzatina dose perdida (**#850**).
- Não toca sinalizadores Valvopatias / mitral (**#866**).
- Não reescreve `fluxograma-febre-reumatica-aguda-criterios-de-jones-2015`, `cardite-reumatica-aguda-graduacao-de-gravidade-e-tratamento-sbc-2022`, profilaxia duração/esquema, gestação RHDAustralia nem WHF staging.
- Evita hubs recentes #880 constrição, #881 QT, #882 HO e demais densificações overnight (#826–#879+).
- Busca: zero `sinalizadores-ambulatoriais-suspeita-febre-reumatica*` / checklist cardite suspeita FRA pré-existente no main.

## Arquivos

| Arquivo | Kind |
|---|---|
| `content/Febre_reumática/sinalizadores-ambulatoriais-suspeita-febre-reumatica-aguda-quando-encaminhar.md` | protocolo |
| `content/Febre_reumática/fluxograma-ambulatorial-suspeita-fra-destino-hospital.md` | fluxograma |
| `content/Febre_reumática/checklist-ambulatorial-alarme-cardite-suspeita-fra.md` | protocolo |

Todos: `review_status: pendente_revisao`, `fonte_producao: grok`, PT, sem doses.

## Fontes (PMIDs reais)

- Gewitz et al. Circulation 2015 (Jones + eco) — PMID **25908771**
- Ralph et al. Med J Aust 2021 (diretriz australiana 2020) — PMID **33190309**
- OMS 2024 FR/CR — PMID **39631006**
- WHF 2023 eco RHD — PMID **37914787**

Sem PMID inventado.

## Branch

`feat/tudo-com-tudo-febre-reumatica-suspeita-hospital-20260907` → `main`

Sem merge automático; revisão clínica humana antes de `revisado`.
