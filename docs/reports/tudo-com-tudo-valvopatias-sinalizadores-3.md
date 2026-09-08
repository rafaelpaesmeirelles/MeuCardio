# Tudo-com-Tudo — Valvopatias: VAB/aortopatia + EA grave assintomática — revisão final 2026-09-08

## Escopo

Pacote de vigilância/encaminhamento com **dois eixos independentes**:

1. VAB/aortopatia — SAA vs avaliação prioritária da equipe de aorta vs vigilância;
2. EA grave assintomática — sintomas desmascarados, queda pressórica isolada, FEVE e demais critérios ESC/EACTS 2025 de intervenção/vigilância.

## Conteúdos

| Arquivo | Status final |
|---|---|
| `content/Valvopatias/sinalizadores-ambulatoriais-de-aortopatia-em-valva-aortica-bicuspide-quando-escalar.md` | `revisado` |
| `content/Valvopatias/sinalizadores-ambulatoriais-de-estenose-aortica-assintomatica-grave-vigilancia.md` | `revisado` |
| `content/Valvopatias/fluxograma-ambulatorial-bicuspide-aortopatia-e-ea-assintomatica-quando-escalar.md` | `revisado` |

## Correções adversariais incorporadas

### VAB/aortopatia
- removidos prazos fixos de encaminhamento e limiares cirúrgicos simplificados;
- prioridade passou a depender de fenótipo, diâmetro/indexação, crescimento, história familiar, coarctação, gestação, cirurgia valvar e qualidade de imagem;
- assimetria de pulsos/PA isolada foi contextualizada e deixou de ser tratada como diagnóstico;
- suspeita de síndrome aórtica aguda permanece **emergência independentemente do diâmetro previamente conhecido**;
- handoff usa `fluxograma-sindrome-aortica-aguda-esc-2024` já presente no corpus.

### EA grave assintomática
- atualizado para a **ESC/EACTS 2025** já revisada no corpus (PMID 40878295);
- sintomas provocados no esforço foram separados de queda sustentada de PA >20 mmHg sem sintomas;
- queda pressórica isolada permanece IIa/C e não é rotulada como sintomática/Classe I;
- FEVE **<50%** preservada como Classe I/B; FEVE **<55%** permanece fator IIa/B distinto;
- incluída coorte de EA grave de alto gradiente, FEVE ≥50%, baixo risco e teste normal para discussão de intervenção precoce como alternativa à vigilância (IIa/A);
- critérios de progressão, BNP e gravidade permanecem modificadores distintos dentro da árvore formal;
- removidos links dependentes de #840 que ainda não existem na árvore desta PR.

## Tudo com Tudo

VAB/aortopatia e EA grave podem compartilhar exames, anatomia valvar e Heart Team em situações específicas, mas **não devem receber relações clínicas fortes entre si apenas por compartilharem o tema Valvopatias**.

## Fontes principais

- ESC 2024 PAAD — PMID **39210722**
- ESC/EACTS Valvular Heart Disease 2025 — PMID **40878295**
- Consenso VAB/aortopatia — PMID **34505060**

## Governança

Pacote preparado para release consolidado. **Sem merge e sem deploy isolado.** A autorização global será recalculada uma única vez após congelamento de todos os lotes revisados.
