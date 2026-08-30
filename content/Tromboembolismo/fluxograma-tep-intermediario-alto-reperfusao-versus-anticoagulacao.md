---
title: "Fluxograma: TEP de risco intermediário-alto — reperfusão versus anticoagulação"
slug: fluxograma-tep-intermediario-alto-reperfusao-versus-anticoagulacao
theme: "Tromboembolismo"
kind: fluxograma
summary: "Árvore da decisão de reperfusão depois de o TEP já estar classificado como intermediário-alto: reconfirmar se não é alto risco, anticoagular e vigiar, resgatar só na deterioração hemodinâmica, e não trombolisar por sela, VD dilatado ou troponina isoladamente — o PEITHO é exatamente este perfil."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica assistida em 29/08/2026. Árvore de decisão estrita (raiz única, um pai por nó, conduta só em folha). Recorte: classe intermediário-alto já conhecida. Não substitui fluxograma-tep-agudo-estratificacao-de-risco-e-decisao-de-trombolise (árvore das quatro classes) nem fluxograma-tromboembolismo-pulmonar-diagnostico-esc-2019. PEITHO PMID 24716681 conferido no PubMed nesta revisão editorial. Classe da via por cateter não atribuída. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Meyer G, Vicaut E, Danays T, et al; PEITHO Investigators. Fibrinolysis for patients with intermediate-risk pulmonary embolism. N Engl J Med. 2014;370(15):1402-1411. DOI: 10.1056/NEJMoa1302097. PMID: 24716681."
  - "Konstantinides SV, Vicaut E, Danays T, et al. Impact of Thrombolytic Therapy on the Long-Term Outcome of Intermediate-Risk Pulmonary Embolism. J Am Coll Cardiol. 2017;69:1536-1544. DOI: 10.1016/j.jacc.2016.12.039. PMID: 28335835."
  - "Konstantinides SV, Meyer G, Becattini C, et al. 2019 ESC Guidelines for the diagnosis and management of acute pulmonary embolism. Eur Heart J. 2020;41(4):543-603. DOI: 10.1093/eurheartj/ehz405. PMID: 31504429. Texto narrativo ERS lido nesta revisão editorial; classe/nível da tabela de reperfusão: LIMITE DA EVIDÊNCIA DISPONÍVEL."
  - "Amado VM, Fernandes CJCDS, Salibe-Filho W, et al. Brazilian guidelines for the pharmacological treatment of pulmonary embolism. J Bras Pneumol. 2025;51(2):e20240314. DOI: 10.36416/1806-3756/e20240314. PMID: 40531728."
  - "Creager MA, Barnes GD, Giri J, et al. 2026 AHA/ACC multisociety guideline for acute pulmonary embolism. J Am Coll Cardiol. 2026;87(13):1626-1710. DOI: 10.1016/j.jacc.2025.11.005. PMID: 41712898."
---

# Fluxograma: TEP de risco intermediário-alto — reperfusão versus anticoagulação

Árvore da **decisão de reperfusão** no adulto com TEP agudo **já classificado** como risco intermediário-alto: disfunção de ventrículo direito na imagem **e** troponina elevada, **sem** choque, parada ou hipotensão persistente. Não diagnostica TEP. Não calcula PESI. Não percorre as quatro classes da ESC — isso está em `fluxograma-tep-agudo-estratificacao-de-risco-e-decisao-de-trombolise`. As folhas são próximos caminhos, não atestados.

O PEITHO (tenecteplase vs. placebo, ambos com heparina; 1.005 pacientes na ITT) é o ensaio deste recorte: o lítico reduz morte ou descompensação em 7 dias (2,6% vs. 5,6%) sem reduzir morte isolada e com mais sangramento extracraniano (6,3% vs. 1,2%) e mais AVC (2,4% vs. 0,2%). Por isso a árvore só autoriza reperfusão **depois** da deterioração, ou se a reavaliação mostrar que o rótulo intermediário-alto estava errado.

## Árvore de decisão

```mermaid
flowchart TD
  R0["TEP agudo de risco intermediário-alto<br/>já classificado: disfunção de VD<br/>e troponina, sem choque nem parada"] --> D1{"Reavaliação imediata: há choque<br/>obstrutivo, hipotensão persistente<br/>ou PCR?"}
  D1 -->|"Sim — é alto risco agora"| C1(["Reclassificar como alto risco e<br/>reperfundir agora: trombólise sistêmica<br/>se não houver contraindicação absoluta"])
  D1 -->|"Não — permanece intermediário-alto"| P1["Anticoagulação parenteral imediata<br/>e internação em unidade com<br/>monitorização contínua"]
  P1 --> D2{"Há sangramento ativo grave ou<br/>outra contraindicação absoluta<br/>à anticoagulação?"}
  D2 -->|"Sim"| C2(["Filtro de veia cava inferior só neste<br/>cenário; não é indicação de trombólise<br/>e não substitui reperfusão se houver choque"])
  D2 -->|"Não"| D3{"Sob anticoagulação, ocorreu deterioração<br/>hemodinâmica — choque, hipotensão<br/>persistente ou vasopressor?"}
  D3 -->|"Sim"| D4{"Há contraindicação absoluta<br/>à trombólise sistêmica?"}
  D4 -->|"Não"| C3(["Trombólise de resgate agora;<br/>não esperar outro biomarcador<br/>nem a tomografia de controle"])
  D4 -->|"Sim"| C4(["Embolectomia cirúrgica ou tratamento<br/>por cateter se houver expertise no local;<br/>classe da via por cateter não atribuída aqui"])
  D3 -->|"Não"| D5{"A indicação de lítico está sendo justificada<br/>só por trombo em sela, relação VD/VE,<br/>síncope já resolvida ou lactato isolado?"}
  D5 -->|"Sim — anatomia ou marcador isolado"| C5(["Não trombolisar: esses achados não<br/>equivalem a instabilidade; o PEITHO<br/>randomizou exatamente este perfil"])
  D5 -->|"Não — estável sob vigilância"| C6(["Manter anticoagulação e vigilância;<br/>não adotar dose reduzida nem cateter<br/>como rotina a partir de MOPETT ou STORM-PE"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Como ler a árvore

- **A raiz já pressupõe a classe.** Se o PESI ainda não foi cruzado com VD e troponina, esta não é a árvore certa — volte à estratificação completa.
- **Oxigênio, suporte de VD e PERT** valem em qualquer ramo e por isso ficam fora do diagrama. PERT organiza a decisão; não é, por si, indicação de lítico.
- **C1** existe porque o rótulo intermediário-alto é dinâmico: a primeira medição de pressão pode estar desatualizada. Alto risco não espera o eco de 4 da manhã.
- **C3** é o resgate do PEITHO e da ESC 2019 (no corpus: Classe I, B — **LIMITE DA EVIDÊNCIA DISPONÍVEL** contra a tabela original). O tempo médio até descompensação no braço placebo, no texto ESC/ERS, é da ordem de 1,8 dia: a vigilância das primeiras 48 h não é teatro.
- **C4** não inventa classe para cateter nem para cirurgia. O texto narrativo da ESC 2019 trata as duas como alternativas quando o lítico é contraindicado ou falhou, **se houver expertise**. STORM-PE e PEERLESS/HI-PEITHO não tornam C4 a folha do paciente estável.
- **C5** é a folha do erro mais comum deste recorte: sela, carga trombótica e VD dilatado **já estavam** nos critérios de inclusão do PEITHO.
- **C6** recusa MOPETT (dose reduzida, ensaio pequeno e aberto) e STORM-PE (desfecho de imagem em 100 pacientes) como padrão. PEITHO-3 segue em andamento.

## O que a árvore não decide

- Qual heparina (não fracionada vs. baixo peso) e quando passar a DOAC — documentos de anticoagulação desta pasta.
- Contraindicações absolutas e relativas à fibrinólise, listadas na Table 10 da ESC (AVC hemorrágico prévio, AVC isquêmico em 6 meses, neoplasia de SNC, trauma/cirurgia/TCE em 3 semanas, diátese, sangramento ativo; relativas no protocolo).
- Categoria AHA/ACC D1–D2: hipotensão transitória ± hipoperfusão pode justificar **considerar** terapia avançada em decisão multidisciplinar, sem mandato de trombólise sistêmica plena. Não ganhou nó próprio para não fundir duas linguagens de gravidade no mesmo losango.
- Idade, sexo feminino e >75 anos aumentam o risco hemorrágico (SBPT 2025 cita mulheres >75). Isso pesa na conversa do resgate; não muda C5 nem C6 para “lítico preventivo”.
