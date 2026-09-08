# Tudo com Tudo — Dispositivos: pacote ambulatorial pré-RM em CIED (2026-09-07)

## Pivô (anti-duplicação)

**Alvo original da leva:** densificar `content/Dispositivos` com gap ambulatorial **além do PR #835** (disfunção de eletrodo + choque CDI).

**Achado em #835:** já cobre triagem pós-choque e sinalizadores de eletrodo.

**Corpus main:** já existe o estudo revisado MagnaSafe/Nazarian (`ressonancia-magnetica-em-pacientes-com-marcapasso-ou-cdi-nao-condicional-o-registro-magnasafe`) — evidência, não checklist de destino de consultório.

**Alternativas avaliadas e evitadas:**
- Infecção de bolsa ambulatorial → colisão temática com fluxogramas existentes + PR **#711** (triagem-sintomas).
- CRT não-respondedor / alerta remoto “quando ligar” → candidatos futuros; MRI ambulatorial era lacuna mais limpa e clinicamente frequente.

**Escolha:** checklist + fluxograma + braço urgente de **pré-RM em portador de CIED** (PS/hospital com protocolo vs especialidade vs retorno curto).

## Anti-colisão

- Não toca arquivos do PR **#835**.
- Não altera o estudo MagnaSafe já `revisado`.
- Não entra em `triagem-sintomas/metadados.json` (#711).
- PRs abertos #826–#868: único Dispositivos Tudo-com-Tudo recente é #835; demais temas são outros hubs.

## Arquivos

| Arquivo | Slug | Kind |
|---|---|---|
| `content/Dispositivos/checklist-ambulatorial-pre-rm-em-portador-de-cied-destino.md` | `checklist-ambulatorial-pre-rm-em-portador-de-cied-destino` | protocolo |
| `content/Dispositivos/fluxograma-pre-rm-com-cied-destino-ambulatorial.md` | `fluxograma-pre-rm-com-cied-destino-ambulatorial` | fluxograma |
| `content/Dispositivos/rm-urgente-em-portador-de-cied-quando-nao-esperar-o-centro.md` | `rm-urgente-em-portador-de-cied-quando-nao-esperar-o-centro` | protocolo |

Todos com `review_status: pendente_revisao`, `fonte_producao: grok`. Sem doses. Sem auto-merge.

## Slugs relacionados (existentes)

`ressonancia-magnetica-em-pacientes-com-marcapasso-ou-cdi-nao-condicional-o-registro-magnasafe`, `manejo-de-marcapasso-e-cdi-durante-radioterapia-oncologica`, `fluxograma-disfuncao-de-eletrodo-fratura-e-falha-de-isolamento-conduta`, `fluxograma-choque-inapropriado-de-cdi-investigacao-e-manejo`.

## Fontes (PMIDs reais, alinhados ao documento revisado do catálogo)

- MagnaSafe — Russo et al. NEJM 2017 — PMID **28225684**
- Nazarian et al. NEJM 2017 — PMID **29281579**
- HRS 2017 MRI and radiation exposure in CIEDs — PMID **28502708**

## Branch

`feat/tudo-com-tudo-dispositivos-pre-rm-ambulatorial-20260907-0509` → `main`
