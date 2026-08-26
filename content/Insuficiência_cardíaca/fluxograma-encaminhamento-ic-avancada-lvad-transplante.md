---
title: "Fluxograma: Quando Encaminhar para IC Avançada — LVAD e Transplante Cardíaco"
slug: fluxograma-encaminhamento-ic-avancada-lvad-transplante
theme: "Insuficiência cardíaca"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Construído a partir de referências já verificadas e publicadas nesta mesma pasta em sessões anteriores (PubMed E-utilities e leitura de texto integral registradas nos documentos de origem), sem PMID/DOI novo. Estágio D (IC avançada) reproduz a definição já publicada em 'segunda-definicao-universal-insuficiencia-cardiaca-2026.md' (PMID 42370864/42366997). Critérios de teste cardiopulmonar de exercício (VO2 pico ≤12 mL/kg/min em uso de betabloqueador, ≤14 mL/kg/min sem betabloqueador, RER >1,05) reproduzem literalmente os já conferidos e publicados em 'teste-cardiopulmonar-de-exercicio-na-selecao-do-candidato-a-transplante-cardiaco-vo2-pico-e-o-efeito-do-betabloqueador.md' (fontes primárias Mancini 1991 PMID 1999029, Peterson 2003 PMID 14550824, confirmados também na diretriz ISHLT 2024 PMID 39115488, texto integral lido por pdftotext -layout em sessão anterior). MOMENTUM 3 PMID 30883052 já verificado em 'lvad-de-fluxo-centrifugo-versus-axial-o-ensaio-momentum-3.md'. A árvore não distingue LVAD como ponte para transplante de LVAD como terapia de destino nem detalha critérios de elegibilidade a transplante além de sinalizar a existência de contraindicações — essa decisão fina é do centro especializado, não deste documento, e o texto diz isso explicitamente."
source_refs: ["Walsh MN, Kober L, Sliwa K, et al.; Joint AHA/ACC/ESC/WHF Task Force. AHA/ACC/ESC/WHF Expert Consensus Document: Second Universal Definition of Heart Failure (2026). J Am Coll Cardiol. 2026. DOI: 10.1016/j.jacc.2026.05.036. PMID: 42370864.", "Mancini DM, Eisen H, Kussmaul W, et al. Value of peak exercise oxygen consumption for optimal timing of cardiac transplantation in ambulatory patients with heart failure. Circulation. 1991;83(3):778-786. DOI: 10.1161/01.cir.83.3.778. PMID: 1999029", "Peterson LR, Schechtman KB, Ewald GA, et al. Timing of cardiac transplantation in patients with heart failure receiving beta-adrenergic blockers. J Heart Lung Transplant. 2003;22(10):1141-1148. DOI: 10.1016/s1053-2498(02)01225-1. PMID: 14550824", "Peled Y, Ducharme A, Kittleson M, et al.; International Society for Heart and Lung Transplantation. ISHLT Guidelines for the Evaluation and Care of Cardiac Transplant Candidates—2024. J Heart Lung Transplant. 2024;43(10):1529-1628.e54. DOI: 10.1016/j.healun.2024.05.010. PMID: 39115488", "Mehra MR, Uriel N, Naka Y, et al; MOMENTUM 3 Investigators. A Fully Magnetically Levitated Left Ventricular Assist Device - Final Report. N Engl J Med. 2019;380(17):1618-1627. DOI: 10.1056/NEJMoa1900486. PMID: 30883052", "Singh TP, Cherikh WS, Hsich E, et al.; ISHLT. Graft survival in primary thoracic organ transplant recipients: A special report from the ISHLT Registry. J Heart Lung Transplant. 2023;42(10):1321-1333. DOI: 10.1016/j.healun.2023.07.017. PMID: 37549773"]
---

# Fluxograma: Quando Encaminhar para IC Avançada — LVAD e Transplante Cardíaco

Encaminhar tarde demais é o erro mais caro na IC avançada: sobrevida e
elegibilidade a transplante caem quanto mais disfunção de outros órgãos o
paciente acumula esperando. Este fluxograma não decide entre LVAD e
transplante — essa é decisão do centro especializado, que pesa contraindicação,
suporte social e disponibilidade de órgão — mas organiza **quando encaminhar**,
a partir dos sinais de estágio D já reconhecidos pela Segunda Definição
Universal de IC (2026). O teste cardiopulmonar de exercício refina a seleção
de candidatos ambulatoriais, mas não é requisito para iniciar o encaminhamento.

## Árvore de decisão

```mermaid
flowchart TD
  R0["IC crônica de qualquer fenótipo de FEVE<br/>(ICFEr, ICFEi ou ICFEp), em tratamento<br/>orientado por diretriz e máximo tolerado<br/>para o fenótipo, com sintomas persistentes"]
  D1{"Sinal de alerta de estágio D (IC<br/>avançada) presente — hospitalizações<br/>recorrentes por IC apesar de GDMT<br/>otimizada, necessidade crescente de<br/>diurético, intolerância a GDMT por<br/>hipotensão/disfunção renal,<br/>hipoperfusão persistente, caquexia<br/>cardíaca ou NYHA III-IV persistente?"}
  C1(["Manter o tratamento ambulatorial<br/>orientado pelo fenótipo de IC e a<br/>reavaliação periódica — sem critério de<br/>encaminhamento a IC avançada neste<br/>momento"])
  D2{"Já em inotrópico intravenoso<br/>contínuo, suporte circulatório mecânico<br/>temporário, ou internações repetidas<br/>por descompensação nos últimos 12<br/>meses?"}
  C2(["Encaminhamento URGENTE a centro de IC<br/>avançada — avaliação para transplante<br/>cardíaco e/ou dispositivo de assistência<br/>ventricular, sem adiar por otimização<br/>ambulatorial adicional"])
  D3{"Capacidade funcional objetivamente<br/>reduzida confirmada por teste<br/>cardiopulmonar de exercício — VO2 pico ≤<br/>12 mL/kg/min em uso de betabloqueador<br/>ou ≤ 14 mL/kg/min sem betabloqueador,<br/>com teste máximo (RER > 1,05)?"}
  C3(["Encaminhar a centro de IC avançada<br/>para avaliação formal de transplante<br/>cardíaco e/ou LVAD — o TCPE apoia o<br/>encaminhamento e a avaliação integrada,<br/>mas não determina isoladamente a<br/>listagem (ISHLT 2024)"])
  D4{"Possível barreira a transplante ou<br/>LVAD (neoplasia ativa, disfunção grave<br/>de outro órgão, fragilidade, barreira<br/>psicossocial/adesão) presente?"}
  C4(["Encaminhar mesmo assim ao centro de IC<br/>avançada para avaliar reversibilidade e<br/>elegibilidade a cada estratégia — uma<br/>barreira ao transplante não torna o<br/>paciente automaticamente elegível a<br/>LVAD como terapia de destino"])
  C5(["Encaminhar a centro de IC avançada<br/>para avaliação completa — incluindo TCPE<br/>se ainda não realizado e reavaliação de<br/>contraindicações; a decisão entre<br/>transplante e LVAD, e entre ponte e<br/>terapia de destino, é do centro<br/>especializado"])

  R0 --> D1
  D1 -->|"Não"| C1
  D1 -->|"Sim — sinal de alerta de estágio D<br/>presente"| D2
  D2 -->|"Sim"| C2
  D2 -->|"Não"| D3
  D3 -->|"Sim — critério de TCPE atingido"| C3
  D3 -->|"Não, ou TCPE ainda não realizado"| D4
  D4 -->|"Sim — possível barreira"| C4
  D4 -->|"Não"| C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

**IC avançada não é sinônimo de ICFEr.** Sintomas refratários, eventos
recorrentes, hipoperfusão ou intolerância ao tratamento podem justificar o
encaminhamento em ICFEr, ICFEi ou ICFEp. A elegibilidade posterior para LVAD
depende da anatomia e da fisiologia de cada paciente, mas essa seleção não
deve restringir a porta de entrada no centro de IC avançada.

**Critérios completos de listagem para transplante** (gradiente transpulmonar,
resistência vascular pulmonar, Seattle Heart Failure Model, idade) não são
repetidos aqui — estão detalhados, com a fonte primária de 2016 e a diretriz
sucessora de 2024, em
`transplante-cardiaco-sobrevida-do-enxerto-retransplante-e-fatores-de-risco-registro-ishlt.md`,
nesta mesma pasta.

**Escolha entre LVAD de ponte para transplante e LVAD como terapia de
destino** depende de elegibilidade a transplante, idade, comorbidade e
preferência do paciente — decisão do centro especializado, não representada
como ramo desta árvore.

**Escolha entre modelos de LVAD** (fluxo centrífugo versus axial) não é objeto
deste fluxograma — ver `lvad-de-fluxo-centrifugo-versus-axial-o-ensaio-momentum-3.md`.

**Sobrevida do enxerto e risco de retransplante pós-operatórios** também não
estão aqui — são desfechos posteriores à decisão de encaminhar, cobertos no
documento do Registro ISHLT já citado acima.
