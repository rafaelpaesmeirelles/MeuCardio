# Tudo-com-Tudo — Pericárdio: suspeita ambulatorial de constrição (2026-09-07)

## Escopo

Lacuna fina: **reconhecimento ambulatorial** de pistas de pericardite constritiva e **destino** (PS agora vs. eco precoce + referência). Não densifica doses, não reescreve DD imagem constrição×restrição, nem tamponamento agudo.

## Anti-colisão

- Não toca pacote pericardite ambulatorial (**#846**).
- Não toca pacote miocardite ambulatorial (**#857**).
- Não reescreve `fluxograma-pericardite-constritiva-versus-cardiomiopatia-restritiva`, critérios numéricos 2024, efusivo-constritiva nem `fluxograma-tamponamento-cardiaco`.
- Evita hubs/PRs densificação overnight (#826–#879+: Diabetes, FA, Hipertensão, Cardiorrenal, Reabilitação, Teach-back, Aorta/DAP, Cardio-oncologia, Dispositivos, Perioperatório, Tromboembolismo, Farmacologia, Arritmias, Valvopatias, HAP, IC, Doença coronariana, Cardiomiopatias, Esporte, Congênitas, etc.).
- Busca: zero `sinalizadores-ambulatoriais-suspeita-constricao*` / checklist ambulatorial de constrição pré-existente.
- Skip Endocardite/Síncope (já densos); skip “quando escalonar recorrente” (já coberto por #846 + fluxograma de escalonamento); skip PPS ambulatorial nesta leva (arquivo diagnóstico/prevenção já existe; pode ser leva futura).

## Arquivos

| Arquivo | Kind |
|---|---|
| `content/Pericárdio/sinalizadores-ambulatoriais-suspeita-constricao-pericardica-quando-encaminhar.md` | protocolo |
| `content/Pericárdio/fluxograma-ambulatorial-suspeita-constricao-destino.md` | fluxograma |
| `content/Pericárdio/constricao-pericardica-checklist-ambulatorial-de-alarme.md` | protocolo |

Todos: `review_status: pendente_revisao`, `fonte_producao: grok`, PT, sem doses.

## Fontes (conferidas no corpus)

- ESC 2025 myocarditis/pericarditis — PMID 40878297
- Klein et al. JACC Cardiovasc Imaging 2024 — PMID 39111992
- Feng et al. Circulation 2011 — PMID 21969014

Sem PMID inventado.

## Branch

`feat/tudo-com-tudo-pericardio-constricao-suspeita-20260907-0226` → `main`
