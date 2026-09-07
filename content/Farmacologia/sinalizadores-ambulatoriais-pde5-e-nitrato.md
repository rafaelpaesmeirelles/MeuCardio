---
title: "Sinalizadores ambulatoriais: PDE5 e nitrato no paciente cardiológico"
slug: sinalizadores-ambulatoriais-pde5-e-nitrato
theme: "Farmacologia"
kind: protocolo
fonte_producao: grok
summary: "Consultório: quando inibidor de PDE5 (sildenafila, tadalafila, vardenafila) e nitrato (ou riociguate) não podem coexistir — quem perguntar, janelas de segurança, e quando hipotensão/sintoma vira emergência — sem doses de disfunção erétil."
review_status: pendente_revisao
review_note: "Pacote Tudo-com-Tudo PDE5+nitrato ambulatorial (07/09/2026). Lacuna: monografia sildenafila-citrato e ensaios RELAX/SIOVAC cobrem fármaco/HAP/ICFEp; nenhum PR open de sinalizadores ambulatoriais PDE5×nitrato/riociguate. Fontes: AHA sexual activity 2012 PMID 22267846; Princeton III PMID 22862865; ESC CCS 2019 DOI 10.1093/eurheartj/ehz425. Sem doses de DE."
source_refs:
  - "Levine GN, Steinke EE, Bakaeen FG, et al. Sexual activity and cardiovascular disease: a scientific statement from the American Heart Association. Circulation. 2012;125(8):1058-1072. DOI: 10.1161/CIR.0b013e3182447787. PMID: 22267846"
  - "Nehra A, Jackson G, Miner M, et al. The Princeton III Consensus recommendations for the management of erectile dysfunction and cardiovascular disease. Mayo Clin Proc. 2012;87(8):766-778. DOI: 10.1016/j.mayocp.2012.06.015. PMID: 22862865"
  - "Knuuti J, Wijns W, Saraste A, et al. 2019 ESC Guidelines for the diagnosis and management of chronic coronary syndromes. Eur Heart J. 2020;41(3):407-477. DOI: 10.1093/eurheartj/ehz425"
---

# Sinalizadores ambulatoriais: PDE5 e nitrato no paciente cardiológico

Pergunta de **consultório**: o paciente (DAC, IC, angina, pós-IAM/PCI) usa ou pede sildenafila/tadalafila — **quando o nitrato (ou riociguate) torna isso contraindicação absoluta**, e o que não dá para “deixar para o urologista”.

Não substitui:
- monografia e interações formais — [`sildenafila-citrato`](sildenafila-citrato.md);
- angina / sinalizadores coronarianos — pacotes [#843](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/843) / [#874](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/874);
- HAP grupo 2 (onde sildenafila **não** é o eixo) — [#841](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/841) / ensaio SIOVAC no corpus.

Árvore: [`fluxograma-ambulatorial-pde5-quando-evitar-e-escalar`](fluxograma-ambulatorial-pde5-quando-evitar-e-escalar.md). Checklist: [`checklist-ambulatorial-pde5-no-retorno-cardiologico`](checklist-ambulatorial-pde5-no-retorno-cardiologico.md).

## Princípio

Inibidores de PDE5 potencializam a via do óxido nítrico / GMPc. Uso **concomitante** com nitratos (orgânicos ou doadores de NO) é **contraindicação absoluta** por hipotensão grave potencialmente fatal (AHA 2012, PMID 22267846; bulas e monografia local). Riociguate (estimulador de guanilato ciclase) soma o mesmo risco — também CI absoluta com PDE5 ([`sildenafila-citrato`](sildenafila-citrato.md)).

Princeton III (PMID 22862865) e o statement AHA de atividade sexual estratificam risco cardiovascular da relação sexual e reforçam: estabilizar a doença cardíaca **antes** de liberar PDE5; nitrato contínuo ou de resgate frequente é barreira clínica, não detalhe de bula.

ESC CCS 2019 (DOI 10.1093/eurheartj/ehz425) mantém nitratos como antianginoso sintomático — o que torna a pergunta PDE5 obrigatória em quem tem frasco de isossorbida/nitroglicerina na bolsa.

## Quem NÃO deve receber PDE5 enquanto houver nitrato/riociguate (filtro duro)

| Contexto | Por quê (âncora) | Conduta ambulatorial (sem dose de DE) |
|---|---|---|
| Nitrato contínuo (isossorbida, mononitrato, adesivo) | CI absoluta PDE5×nitrato (AHA 2012) | Não iniciar PDE5; revisar se o nitrato ainda é necessário |
| Nitrato de resgate em uso recente | Mesma CI; janela de washout incompleta | Ver janelas abaixo; educar “não misturar” |
| Riociguate (CTEPH / HAP selecionada) | CI absoluta PDE5×riociguate (bula; monografia) | Não combinar; articular com HP [#841](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/841) |
| Angina instável / SCA recente não estabilizado | Princeton III / AHA: alto risco para atividade sexual e para vasodilatação empilhada | Estabilizar coronária primeiro ([#843](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/843)) |
| Hipotensão sintomática / choque / volume depleção grave | Risco de colapso com PDE5±nitrato | Tratar causa; não liberar PDE5 |

## Janelas de segurança (washout) — âncoras, não posologia de DE

Quando o paciente **já usou** PDE5 e precisa de nitrato de emergência (ou o inverso):

| PDE5 | Intervalo mínimo citado na prática/rotulagem refletida no statement AHA |
|---|---|
| Sildenafila / vardenafila | **≥ 24 h** antes de nitrato |
| Tadalafila | **≥ 48 h** antes de nitrato |

Se houver dor torácica **dentro** da janela pós-PDE5: **não dar nitrato**; oxigênio/analgesia/anti-isquêmico sem nitrato e via SCA — o nitrato clássico de “dor no peito” vira risco (AHA 2012).

## Quem merece pergunta explícita neste retorno

1. **DAC / angina / pós-IAM/PCI** com frasco de nitrato — “usa Viagra/Cialis/genérico?”.
2. **Pedido de “liberar o comprimido azul”** no retorno cardiológico — estratificar risco sexual (Princeton III) **e** mapa de nitratos/riociguate.
3. **IC com nitrato sintomático** — mesma CI; não “liberar porque a FE melhorou”.
4. **Polifarmácia / idoso** — PDE5 OTC/empréstimo de familiar; cruzar com [#851](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/851).
5. **HAP / CTEPH em riociguate** — pergunta PDE5 é filtro de segurança, não oferta de DE.

## Encaminhar / agir agora

1. **Síncope / hipotensão grave após PDE5 ± nitrato** → emergência; suspender ambos; suporte.
2. **Dor torácica após PDE5 com nitrato na bolsa** → via SCA **sem** nitrato até esgotar a janela.
3. **Nitrato contínuo + PDE5 crônico “escondido”** → suspender um dos eixos agora; documentar educação.
4. **Riociguate + PDE5** → suspender a combinação; articular HP.

## Pode permanecer no plano habitual (com pergunta explícita)

- Paciente **estável** (Princeton baixo/intermediário controlado), **sem** nitrato e **sem** riociguate, após discussão de risco da atividade sexual (AHA 2012).
- DE tratada por urologia com PDE5, cardiologista documentou ausência de nitrato/riociguate e estratificação.

## Conduta ambulatorial mínima (sem doses de DE)

1. Mapear nitratos (contínuo e resgate) e riociguate **antes** de qualquer PDE5.
2. Se nitrato necessário e frequente → PDE5 **não**; revisar anti-isquêmico/revascularização ([#843](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/843)).
3. Educar: dor no peito após PDE5 → **não** automedicar nitrato; procurar emergência.
4. Documentar washout se transição entre classes.
5. Teach-back da CI ([#832](https://github.com/rafaelpaesmeirelles/MeuCardio/pull/832)).

## Checklist de 90 segundos

1. Nitrato ou riociguate ativo? → **não PDE5**.
2. SCA/angina instável não estabilizada? → estabilizar primeiro.
3. Paciente sabe a janela 24 h / 48 h? → educar.
4. Sem doses de DE neste documento.

## Armadilhas

- Achar que “nitrato só de resgate” permite PDE5 no mesmo dia.
- Liberar tadalafila com washout de sildenafila (48 h ≠ 24 h).
- Esquecer riociguate na lista de CI (não é nitrato, mas mesma via GMPc).
- Tratar DE sem perguntar atividade sexual / risco isquêmico (Princeton III).

## Limite da evidência

Filtro ambulatorial de **segurança de interação** e estratificação. Dose/escolha de PDE5 para DE, esquema de HAP e manejo avançado de choque ficam fora de escopo.
