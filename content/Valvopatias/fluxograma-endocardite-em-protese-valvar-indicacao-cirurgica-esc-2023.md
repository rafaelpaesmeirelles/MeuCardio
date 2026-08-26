---
title: "Fluxograma: Endocardite Infecciosa em Prótese Valvar — Indicação e Timing de Cirurgia (ESC 2023)"
slug: fluxograma-endocardite-em-protese-valvar-indicacao-cirurgica-esc-2023
theme: "Valvopatias"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Antes de produzir, conferi o corpus completo da pasta content/Valvopatias/ (comando ls) para evitar duplicação: já existem fluxogramas publicados sobre estenose aórtica (TAVI vs SAVR, timing na forma assintomática), estenose mitral reumática (comissurotomia vs cirurgia), regurgitação mitral, insuficiência tricúspide secundária, escolha de prótese mecânica vs biológica e trombose de prótese valvar — nenhum aborda endocardite infecciosa, então este é um recorte novo, sem sobreposição. Fonte primária localizada via PubMed E-utilities: esearch com o termo exato do título do documento retornou PMID 37622656 (Delgado V et al., '2023 ESC Guidelines for the management of endocarditis', Eur Heart J. 2023;44(39):3948-4042, DOI 10.1093/eurheartj/ehad193), confirmado por esummary (título, revista, volume/página e ano batem). O texto integral do artigo é pago na Oxford Academic (Europe PMC confirma 'Subscription required' para o link do editor); localizei uma cópia de acesso aberto do PDF publicado (versão do editor, 95 páginas) via repositório institucional da Universidade de Leiden, referenciada pelo Unpaywall a partir do mesmo DOI, e extraí o texto com pdftotext para conferência linha a linha. A árvore reproduz integralmente, sem adicionar classe/nível não presentes na fonte: (1) a Recommendation Table 19 (Seção 12.1, página 4000), que traz a única recomendação específica para PVE precoce — cirurgia com nova troca valvar e desbridamento completo, Classe I Nível C; e (2) a Recommendation Table 12 (Seção 8, página 3991), que cobre indicações de cirurgia em endocardite de valva nativa E de prótese valvar (PVE é citada explicitamente em quase todas as linhas), incluindo a linha específica de PVE por S. aureus ou Gram-negativo não-HACEK (Classe IIa, Nível C). As definições de urgência cirúrgica (emergência: até 24h; urgente: 3–5 dias; não urgente: mesma internação) vêm da nota de rodapé 'd' da própria Tabela 12. O texto da Seção 12.1.3 (prognóstico e tratamento da PVE) fundamenta o desfecho final da árvore — PVE tardia não complicada e não estafilocócica pode ser tratada clinicamente, com seguimento próximo pelo risco de recidiva. Há três errata publicadas para este artigo (PMID 37738322, 38086544 e 39824219) que não foram lidas nesta sessão; nenhuma delas, pelos metadados do PubMed, incide sobre as Tabelas 12 ou 19 (títulos genéricos de correção), mas fica registrado que não foram revisadas integralmente."
source_refs: ["Delgado V, Ajmone Marsan N, de Waha S, Bonaros N, Brida M, Burri H, et al.; ESC Scientific Document Group. 2023 ESC Guidelines for the management of endocarditis. Eur Heart J. 2023;44(39):3948-4042. DOI: 10.1093/eurheartj/ehad193. PMID: 37622656 — Seção 8 (Recommendation Table 12, indicações de cirurgia em endocardite de valva nativa e protética) e Seção 12.1 (Recommendation Table 19, indicações específicas para endocardite protética precoce), texto integral obtido via cópia de acesso aberto (repositório institucional, Universidade de Leiden) referenciada pelo Unpaywall a partir do mesmo DOI, e conferido nesta sessão."]
---

# Fluxograma: Endocardite Infecciosa em Prótese Valvar — Indicação e Timing de Cirurgia (ESC 2023)

A endocardite infecciosa em prótese valvar (PVE, do inglês *prosthetic
valve endocarditis*) é a forma mais grave de endocardite infecciosa,
respondendo por 20 a 30% de todos os casos e com mortalidade
hospitalar de 20 a 40%. A decisão entre tratamento clínico e cirurgia —
e, quando cirúrgica, o *timing* dessa cirurgia — é o determinante mais
importante do prognóstico: nos registros observacionais citados pela
diretriz, o principal fator associado a recidiva e morte é justamente
**deixar de operar apesar de uma indicação clara**. Este fluxograma
organiza essa decisão a partir das duas tabelas de recomendação da
diretriz ESC 2023 para o manejo da endocardite: a recomendação
específica para PVE precoce (Tabela 19) e as indicações gerais de
cirurgia por insuficiência cardíaca, infecção não controlada e
prevenção de embolia (Tabela 12), que se aplicam tanto à valva nativa
quanto à prótese. O ponto de partida é sempre um diagnóstico já
confirmado de PVE, com decisão tomada em conjunto pelo Heart Team/
Endocarditis Team.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Endocardite infecciosa em<br/>prótese valvar (PVE) confirmada<br/>— critérios de Duke modificados,<br/>avaliação pelo Endocarditis Team"] --> D1{"PVE precoce — até 6 meses<br/>após a cirurgia de implante<br/>ou troca da prótese?"}

  D1 -->|"Sim"| C1(["Cirurgia recomendada: nova<br/>troca valvar com desbridamento<br/>completo do material infectado<br/>(prótese, suturas, pledgets) —<br/>Classe I, Nível C"])

  D1 -->|"Não (PVE tardia)"| D2{"Regurgitação ou obstrução<br/>protética aguda grave, ou<br/>fístula, causando edema<br/>pulmonar refratário ou<br/>choque cardiogênico?"}

  D2 -->|"Sim"| C2(["Cirurgia de EMERGÊNCIA —<br/>em até 24 horas —<br/>Classe I, Nível B"])

  D2 -->|"Não"| D3{"Regurgitação ou obstrução<br/>protética aguda grave causando<br/>sintomas de insuficiência<br/>cardíaca, ou sinais<br/>ecocardiográficos de má<br/>tolerância hemodinâmica?"}

  D3 -->|"Sim"| C3(["Cirurgia URGENTE —<br/>em 3 a 5 dias —<br/>Classe I, Nível B"])

  D3 -->|"Não"| D4{"Infecção localmente não<br/>controlada — abscesso,<br/>pseudoaneurisma, fístula,<br/>vegetação em crescimento,<br/>deiscência protética nova,<br/>ou novo bloqueio<br/>atrioventricular?"}

  D4 -->|"Sim"| C4(["Cirurgia URGENTE —<br/>em 3 a 5 dias —<br/>Classe I, Nível B"])

  D4 -->|"Não"| D5{"Infecção por fungos ou por<br/>organismo multirresistente<br/>(ex.: Staphylococcus aureus<br/>resistente à meticilina,<br/>enterococo resistente à<br/>vancomicina)?"}

  D5 -->|"Sim"| C5(["Cirurgia urgente ou não<br/>urgente, conforme a condição<br/>hemodinâmica do paciente —<br/>Classe I, Nível C"])

  D5 -->|"Não"| D6{"Hemoculturas persistentemente<br/>positivas por mais de 1 semana,<br/>ou sepse persistente, apesar de<br/>antibioticoterapia apropriada e<br/>controle adequado dos focos<br/>metastáticos?"}

  D6 -->|"Sim"| C6(["Cirurgia urgente deve ser<br/>considerada —<br/>Classe IIa, Nível B"])

  D6 -->|"Não"| D7{"PVE causada por Staphylococcus<br/>aureus ou por bacilo Gram-negativo<br/>não pertencente ao grupo HACEK?"}

  D7 -->|"Sim"| C7(["Cirurgia urgente deve ser<br/>considerada —<br/>Classe IIa, Nível C"])

  D7 -->|"Não"| D8{"Vegetação ≥10 mm com um ou<br/>mais episódios embólicos prévios,<br/>apesar de antibioticoterapia<br/>apropriada?"}

  D8 -->|"Sim"| C8(["Cirurgia URGENTE recomendada<br/>para prevenção de novo<br/>episódio embólico —<br/>Classe I, Nível B"])

  D8 -->|"Não"| D9{"Vegetação ≥10 mm associada a<br/>alguma outra indicação cirúrgica<br/>já identificada acima (insuficiência<br/>cardíaca ou infecção não<br/>controlada)?"}

  D9 -->|"Sim"| C9(["Cirurgia URGENTE recomendada —<br/>Classe I, Nível C"])

  D9 -->|"Não"| D10{"Vegetação ≥10 mm isolada, sem<br/>disfunção valvar grave e sem<br/>evidência clínica de embolia,<br/>em paciente de baixo risco<br/>cirúrgico?"}

  D10 -->|"Sim"| C10(["Cirurgia urgente PODE ser<br/>considerada —<br/>Classe IIb, Nível B"])

  D10 -->|"Não"| C11(["PVE tardia não complicada,<br/>tipicamente não estafilocócica,<br/>sem nenhum dos critérios acima<br/>— tratamento clínico com<br/>antibioticoterapia prolongada;<br/>seguimento clínico e<br/>ecocardiográfico próximo, pelo<br/>maior risco de recidiva ou<br/>disfunção valvar tardia"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11 conduta;
```

## Notas de leitura

- **PVE precoce vs. tardia**: o corte de 6 meses após a cirurgia
  valvar não é apenas cronológico — reflete um perfil microbiológico e
  prognóstico distinto. A PVE de início peri-operatório é dominada por
  *S. aureus*, *Staphylococcus epidermidis* e micro-organismos
  nosocomiais (Gram-negativos, fungos), com alta mortalidade e resposta
  ruim a antibiótico isolado; por isso a diretriz recomenda reoperação
  já na Tabela 19, independentemente dos demais critérios.
- **As três famílias de indicação cirúrgica** (insuficiência cardíaca,
  infecção não controlada, prevenção de embolia) da Tabela 12 valem
  igualmente para valva nativa e protética — a única linha
  explicitamente redigida para PVE dentro dessa tabela é a de cirurgia
  por *S. aureus* ou Gram-negativo não-HACEK (D7 nesta árvore).
- **Definições de urgência** (nota de rodapé da Tabela 12): emergência
  = até 24 horas; urgente = 3 a 5 dias; não urgente = ainda na mesma
  internação.
- Este fluxograma cobre a PVE **pós-cirúrgica clássica**; a endocardite
  em prótese valvar aórtica transcateter (pós-TAVI) tem perfil de risco
  cirúrgico e taxas de reoperação bem diferentes (cirurgia realizada em
  apenas ~20% dos casos, segundo a mesma diretriz) e não está
  representada nesta árvore.
