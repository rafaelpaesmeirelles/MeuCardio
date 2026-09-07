---
title: "Sinalizadores ambulatoriais de AINE no paciente cardiológico"
slug: sinalizadores-ambulatoriais-de-aine-no-paciente-cardiologico
theme: "Farmacologia"
kind: protocolo
fonte_producao: grok
summary: "Consultório: quando o anti-inflamatório de uso livre (ibuprofeno, diclofenaco, naproxeno, coxibe) vira alarme CV — quem não deve usar, o que perguntar no retorno, e quando escalar por IC/HAS/síndrome coronariana — sem doses e sem reescrever a metanálise CNT."
review_status: pendente_revisao
review_note: "Pacote Tudo-com-Tudo AINE ambulatorial (07/09/2026). Lacuna: ensaio CNT revisado em Geral cobre magnitude de risco; PRECISION e statement AHA existem no corpus de forma pontual; nenhum PR open de sinalizadores AINE. Este pacote é filtro de consultório (evitar / substituir / escalar). Fontes: CNT PMID 23726390; PRECISION PMID 27752637; AHA NSAID statement PMID 17325246; ESC HF 2021 DOI 10.1093/eurheartj/ehab368. Sem doses."
source_refs:
  - "Coxib and traditional NSAID Trialists' (CNT) Collaboration, Bhala N, Emberson J, Merhi A, et al. Vascular and upper gastrointestinal effects of non-steroidal anti-inflammatory drugs: meta-analyses of individual participant data from randomised trials. Lancet. 2013;382(9894):769-779. DOI: 10.1016/S0140-6736(13)60900-9. PMID: 23726390"
  - "Nissen SE, Yeomans ND, Solomon DH, et al. Cardiovascular Safety of Celecoxib, Naproxen, or Ibuprofen for Arthritis (PRECISION). N Engl J Med. 2016;375(26):2519-2529. DOI: 10.1056/NEJMoa1611593. PMID: 27752637"
  - "Antman EM, Bennett JS, Daugherty A, Furberg C, Roberts H, Taubert KA. Use of nonsteroidal antiinflammatory drugs: an update for clinicians: a scientific statement from the American Heart Association. Circulation. 2007;115(12):1634-1642. DOI: 10.1161/CIRCULATIONAHA.106.181646. PMID: 17325246"
  - "McDonagh TA, Metra M, Adamo M, et al. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726. DOI: 10.1093/eurheartj/ehab368"
---

# Sinalizadores ambulatoriais de AINE no paciente cardiológico

Pergunta de **consultório**: o paciente (ou familiar) compra ibuprofeno/diclofenaco “para a dor das costas” — **quando isso muda o plano cardiovascular**, e o que não dá para deixar para o próximo retorno.

Não substitui:
- magnitude e comparação entre moléculas — [`anti-inflamatorios-nao-esteroidais-aines-e-risco-cardiovascular-metanalise-cnt`](../Geral/anti-inflamatorios-nao-esteroidais-aines-e-risco-cardiovascular-metanalise-cnt.md);
- descompensação de IC em geral — pacote [#842](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/842);
- HAS / sinalizadores de crise — [#828](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/828);
- sangramento sob DOAC — [#860](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/860).

Árvore: [`fluxograma-ambulatorial-aine-quando-evitar-e-escalar`](fluxograma-ambulatorial-aine-quando-evitar-e-escalar.md). Checklist: [`checklist-ambulatorial-aine-no-retorno-cardiologico`](checklist-ambulatorial-aine-no-retorno-cardiologico.md).

## Princípio

AINEs (incluindo coxibes) elevam risco vascular e de IC por retenção de sódio/volume e efeitos pró-trombóticos (CNT Collaboration, PMID 23726390). A ESC 2021 de IC lista AINEs entre fármacos a **evitar** em insuficiência cardíaca. O statement AHA 2007 (PMID 17325246) propõe escada: não farmacológico → paracetamol → AINE na menor dose/tempo → preferência relativa ao naproxeno quando AINE for inevitável em alto risco — sem “AINE seguro” em IC.

PRECISION (PMID 27752637) comparou celecoxibe vs ibuprofeno vs naproxeno em artrite com estratificação de risco CV; não autoriza uso liberal em IC descompensada nem apaga o sinal de classe sobre IC da CNT.

## Quem NÃO deve receber AINE (filtro duro no retorno)

| Contexto | Por quê (âncora) | Alternativa prática (sem dose) |
|---|---|---|
| IC conhecida (qualquer FE) ou descompensação recente | Risco de IC ≈ dobrado em **todas** as classes (CNT); ESC 2021: evitar | Analgesia não-AINE; fisioterapia; revisar causa da dor |
| SCA / stent recente / angina instável | AHA 2007: evitar AINE no peri-SCA; risco trombótico | Escala dor + anti-isquêmico; articular ortopedia/dor |
| HAS descontrolada / crise hipertensiva ambulatorial | Retenção Na+/efeito sobre PA | Ver [#828](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/828); suspender AINE |
| DRC avançada / cardiorrenal ativo | Isquemia renal relativa + interação com IECA/BRA/diurético | [#829](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/829) / hub [#692](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/692) |
| Anticoagulado com sangramento recente ou alto risco GI | AINE ↑ sangramento GI (CNT) + anticoagulação | [#860](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/860); gastroproteção se AINE inevitável sob reumatologia |

## Quem merece pergunta explícita neste retorno

1. **Dor musculoesquelética “resolvida com comprimido da farmácia”** — nomear molécula (diclofenaco ≠ naproxeno ≠ ibuprofeno).
2. **Ganho de peso / edema / ortopneia** novos sob AINE — tratar como descompensação até prova em contrário ([#842](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/842)).
3. **PA que “subiu sem mudar o anti-hipertensivo”** — perguntar AINE OTC antes de rotular falha de adesão.
4. **Idoso frágil / polifarmácia** — alto uso OTC; cruzar com [#851](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/851).
5. **Pós-IAM / pós-PCI** em reabilitação — reafirmar “sem AINE” no teach-back ([#832](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/832), [#874](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/874)).

## Encaminhar / agir agora (não “continuar o anti-inflamatório até a reumato”)

1. **Edema + dispneia + AINE** → suspender AINE; manejar como IC; destino conforme [#842](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/842).
2. **Dor torácica / equivalente isquêmico sob AINE** → via SCA; não atribuir à “dor muscular”.
3. **Hemorragia digestiva / anemia aguda sob AINE ± anticoagulante** → emergência + [#860](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/860).
4. **AINE contínuo prescrito por outra especialidade em paciente com IC/SCA** → carta/contato coordenado; não só “anotar no prontuário”.

## Pode permanecer no plano habitual (com pergunta explícita)

- Uso **único/esporádico** em paciente sem IC/SCA/DRC grave, PA controlada, após tentativa de não-AINE — ainda assim educar sobre OTC.
- Indicação reumatológica forte sob especialista, com plano escrito de menor dose/menor duração e gastroproteção quando indicada (PRECISION não apaga CNT para IC).

## Conduta ambulatorial mínima (sem doses)

1. Perguntar AINE OTC **pelo nome** em todo retorno de IC, HAS, DAC, anticoagulado, idoso.
2. Se positivo → classificar: evitar absoluto vs reduzir exposição vs coordenar com prescritor.
3. Preferência relativa (quando AINE inevitável e **sem** IC): naproxeno costuma ser citado como perfil trombótico menos desfavorável na CNT — **não** isento de IC/GI (CNT; AHA 2007).
4. Evitar diclofenaco/coxibe “por costume” em alto risco vascular sem indicação forte (CNT).
5. Documentar orientação de suspensão e alternativa analgésica.

## Checklist de 90 segundos

1. IC / SCA recente / HAS descontrolada / DRC / anticoagulado de alto risco? → **não AINE**.
2. Edema/dispneia sob AINE? → suspender + via IC.
3. Diclofenaco OTC sem indicação? → educar (CNT).
4. Sem doses neste documento.

## Armadilhas

- Achar que “coxibe é gástrico-seguro, logo cardíaco-seguro”.
- Liberar ibuprofeno porque “é de farmácia”.
- Trocar só a molécula em quem tem IC — a CNT mostrou IC de **classe**.
- Ignorar interação com IECA/BRA/diurético (triplo whammy renal).

## Limite da evidência

Filtro ambulatorial. Escolha de esquema anti-inflamatório reumatológico, doses e duração ficam com a especialidade prescritora; este texto ancora o freio cardiovascular.
