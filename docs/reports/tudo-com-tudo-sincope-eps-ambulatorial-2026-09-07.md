# Tudo-com-Tudo — Síncope: EPS / ILR / CDI ambulatorial — revisão final 2026-09-08

## Escopo

Pacote ambulatorial para três decisões distintas:

1. identificar paciente de **alto risco** que não deve entrar em fila eletiva;
2. selecionar quando **EPS** pode acrescentar informação versus monitorização/ILR;
3. reconhecer quando a síncope deve **reabrir estratificação específica de morte súbita/CDI**, sem transformar síncope em indicação de implante.

## Arquivos

| Arquivo | Status final |
|---|---|
| `content/Síncope/sinalizadores-ambulatoriais-sincope-recorrente-inexplicada-quando-referir-eletrofisiologia.md` | `revisado` |
| `content/Síncope/fluxograma-ambulatorial-sincope-recorrente-eps-versus-ilr-destino.md` | `revisado` |
| `content/Síncope/candidatos-ambulatoriais-avaliacao-cdi-apos-sincope-quando-encaminhar.md` | `revisado` |

## Correções adversariais incorporadas

- síncope **sem pródromos** passou a ser marcador de alto risco independente de trauma;
- história familiar de morte súbita em idade jovem é checada antes do ramo de baixo risco;
- EPS de maior força ficou restrito a **IAM prévio/outra condição relacionada a cicatriz**, sem extrapolar para toda cardiopatia estrutural;
- links para documentos de #859 ausentes da árvore desta PR foram removidos;
- “FE reduzida” deixou de ser atalho para CDI; FEVE levemente reduzida isoladamente não define elegibilidade;
- síncope isolada ficou explicitamente definida como **não indicação de CDI**;
- MCH, Brugada, QT longo, CPVT e outras doenças de risco devem seguir critérios próprios;
- incorporada referência contemporânea ESC 2022 de arritmias ventriculares/morte súbita (PMID **36017572**).

## Fontes principais

- ESC 2018 Syncope — PMID **29562304**
- Practical Instructions ESC 2018 — DOI 10.1093/eurheartj/ehy071
- ACC/AHA/HRS 2017 Syncope — PMID **28280231**
- ESC 2022 Ventricular Arrhythmias/SCD — PMID **36017572**

## Governança

Conteúdo preparado para o release consolidado. **Sem merge e sem deploy isolado.** A autorização global do corpus será recalculada uma única vez após congelamento de todos os lotes revisados.
