---
title: "Fluxograma: Timing cirúrgico na endocardite infecciosa por vegetação grande e risco embólico (ESC 2023)"
slug: fluxograma-endocardite-timing-cirurgico-vegetacao-grande-risco-embolico-esc-2023
theme: "Endocardite"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída a partir de duas fontes já conferidas nesta sessão via PubMed E-utilities (esearch/esummary/efetch, título e revista batendo exatamente): (1) o resumo de recomendações Classe I/IIb da ESC 2023 sobre cirurgia para prevenção de embolia, já verificado e publicado no documento 'indicacoes-e-timing-cirurgico-na-endocardite-infecciosa.md' desta mesma pasta (fonte primária ESC 2023, PMID 37622656, e a revisão do CTSNet sobre as implicações cirúrgicas dessa diretriz) — reaproveitado como fonte secundária já auditada em sessão anterior, sem reler o texto integral da diretriz (bloqueado por 403 no Oxford Academic, mesmo obstáculo já documentado à exaustão neste projeto); (2) dois estudos primários lidos integralmente nesta sessão para o corpo do texto e para as ressalvas: Thuny F et al., Circulation 2005 (PMID 15983252, n=384, preditores ecocardiográficos de embolia) e Kang DH et al./EASE trial, N Engl J Med 2012 (PMID 22738096, n=76, cirurgia precoce vs. convencional em endocardite com vegetação grande e doença valvar grave). O desenho da árvore separa deliberadamente os dois ramos da Classe I (evento embólico prévio, nível B, versus outra indicação cirúrgica associada, nível C) e isola o ramo Classe IIb (vegetação isolada em valva aórtica ou mitral, sem disfunção grave e sem embolia prévia) — nenhuma classe/nível foi extrapolada além do que o documento-fonte já registrava como verificado."
source_refs: ["Delgado V, Ajmone Marsan N, de Waha S, et al.; ESC Scientific Document Group. 2023 ESC Guidelines for the management of endocarditis. Eur Heart J. 2023;44(39):3948-4042. DOI: 10.1093/eurheartj/ehad193. PMID: 37622656 — recomendações de cirurgia para prevenção de embolia, conforme já resumidas e citadas no documento 'indicacoes-e-timing-cirurgico-na-endocardite-infecciosa.md' desta pasta, a partir da revisão 'Surgical Implications of the 2023 ESC Endocarditis Guidelines Endorsed by EACTS', CTSNet.", "Thuny F, Di Salvo G, Belliard O, et al. Risk of embolism and death in infective endocarditis: prognostic value of echocardiography: a prospective multicenter study. Circulation. 2005;112(1):69-75. DOI: 10.1161/CIRCULATIONAHA.104.493155. PMID: 15983252 — texto integral do abstract lido via PubMed E-utilities nesta sessão.", "Kang DH, Kim YJ, Kim SH, et al. Early surgery versus conventional treatment for infective endocarditis (EASE trial). N Engl J Med. 2012;366(26):2466-2473. DOI: 10.1056/NEJMoa1112843. PMID: 22738096 — texto integral do abstract lido via PubMed E-utilities nesta sessão.", "Anantha Narayanan M, Mahfood Haddad T, Kalil AC, et al. Association of Vegetation Size With Embolic Risk in Patients With Infective Endocarditis: A Systematic Review and Meta-analysis. JAMA Intern Med. 2018;178(4):502-510. DOI: 10.1001/jamainternmed.2017.8653. PMID: 29459947 — já citada e verificada no documento 'indicacoes-e-timing-cirurgico-na-endocardite-infecciosa.md' desta pasta, reaproveitada aqui só como contexto de risco de complicação neurológica por tamanho de vegetação, não como base de nenhuma classe/nível da árvore."]
---

# Fluxograma: Timing cirúrgico na endocardite infecciosa por vegetação grande e risco embólico (ESC 2023)

Esta pasta já tem um fluxograma para o timing cirúrgico **depois** de uma complicação
neurológica já ocorrida (AVC isquêmico ou hemorrágico) e um documento em prosa com a visão
geral das três indicações cirúrgicas — insuficiência cardíaca, infecção não controlada e
risco embólico. Este fluxograma isola a pergunta que fica no meio desses dois: **antes** de
qualquer evento neurológico, o tamanho da vegetação e a ocorrência (ou não) de um episódio
embólico prévio já mudam a indicação e a urgência da cirurgia cardíaca. É a decisão que a
diretriz ESC 2023 reformulou de forma mais explícita em relação à versão anterior,
introduzindo o corte de 10 mm como novidade Classe I quando associado a outra indicação, e
um novo Classe IIb para vegetação isolada em posição aórtica ou mitral.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Endocardite infecciosa confirmada,<br/>vegetação identificada ao ecocardiograma,<br/>valva nativa ou protética — ESC 2023"] --> D1{"Já existe indicação cirúrgica por<br/>insuficiência cardíaca refratária ou<br/>infecção não controlada abscesso,<br/>fístula ou deiscência protética?"}
  D1 -->|"Sim"| C1(["Cirurgia indicada pela insuficiência<br/>cardíaca ou infecção não controlada;<br/>o timing emergencial ou urgente segue<br/>essas indicações, não o tamanho da<br/>vegetação isoladamente — ver documento<br/>geral de indicação e timing cirúrgico<br/>desta pasta"])
  D1 -->|"Não, ausência dessas<br/>duas indicações clássicas"| D2{"Vegetação maior ou igual a 10 mm<br/>ao ecocardiograma transesofágico?"}
  D2 -->|"Não, vegetação<br/>menor que 10 mm"| C2(["Sem indicação cirúrgica por risco<br/>embólico neste momento; manter<br/>antibioticoterapia otimizada e repetir<br/>ecocardiograma para monitorar<br/>crescimento ou mudança de mobilidade<br/>da vegetação"])
  D2 -->|"Sim, vegetação maior<br/>ou igual a 10 mm"| D3{"Já ocorreu evento embólico sistêmico<br/>ou pulmonar documentado, apesar de<br/>antibioticoterapia adequada?"}
  D3 -->|"Sim, evento embólico<br/>prévio confirmado"| C3(["Cirurgia urgente indicada, dentro de<br/>3 a 5 dias — vegetação ≥10 mm associada<br/>a evento embólico prévio<br/>Classe I, Nível B — ESC 2023"])
  D3 -->|"Não, sem evento<br/>embólico documentado"| D4{"Paciente com baixo risco cirúrgico<br/>estimado pela equipe de endocardite?"}
  D4 -->|"Não, risco cirúrgico<br/>elevado ou proibitivo"| C4(["Manter tratamento clínico otimizado;<br/>reavaliação por ecocardiograma seriado<br/>e discussão multidisciplinar periódica<br/>da equipe de endocardite sobre<br/>reconsiderar cirurgia se o risco mudar"])
  D4 -->|"Sim, baixo<br/>risco cirúrgico"| D5{"Há disfunção valvar grave,<br/>regurgitação importante, associada<br/>à vegetação?"}
  D5 -->|"Sim, disfunção<br/>valvar grave presente"| C5(["Cirurgia urgente indicada, dentro de<br/>3 a 5 dias — vegetação ≥10 mm associada<br/>a outra indicação cirúrgica disfunção<br/>valvar grave<br/>Classe I, Nível C — ESC 2023"])
  D5 -->|"Não, sem disfunção<br/>valvar grave"| D6{"Vegetação em valva<br/>aórtica ou mitral?"}
  D6 -->|"Sim, posição<br/>aórtica ou mitral"| C6(["Considerar cirurgia urgente por<br/>risco embólico isolado, mesmo sem<br/>disfunção valvar grave e sem evento<br/>embólico prévio<br/>Classe IIb — ESC 2023"])
  D6 -->|"Não, valva<br/>tricúspide ou pulmonar"| C7(["Indicação cirúrgica isolada por<br/>tamanho de vegetação não está<br/>estabelecida para valvas direitas nesta<br/>diretriz; manter antibioticoterapia e<br/>ecocardiograma seriado — ver documento<br/>de endocardite de câmaras direitas<br/>desta pasta para conduta específica"])
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## O que a árvore não mostra

- **Mobilidade da vegetação é preditor independente, e a árvore só usa tamanho.** No estudo
  de Thuny et al. (n=384, 34,1% de embolia total, 7,3% de embolia nova sob antibioticoterapia),
  o comprimento da vegetação **acima de 10 mm** e a **mobilidade acentuada** foram preditores
  independentes de embolia nova, mesmo após ajuste para *Staphylococcus aureus* e
  *Streptococcus bovis* (dois microrganismos que, isoladamente, já se associaram a embolia em
  qualquer momento da doença). Vegetação **acima de 15 mm** foi preditor independente de
  mortalidade em 1 ano (risco relativo ajustado 1,8; IC95% 1,10–2,82; p=0,02). A árvore não
  ramifica por mobilidade nem incorpora esse segundo corte de 15 mm — são informações
  contextuais que pesam na decisão da equipe de endocardite, não critérios formais e
  independentes na diretriz.
- **O ensaio EASE apoia diretamente o ramo de disfunção valvar grave, não o ramo isolado por
  tamanho.** O EASE (Kang et al., N Engl J Med 2012) randomizou 76 pacientes com endocardite
  de **valva nativa esquerda, doença valvar grave E vegetação grande** — as duas condições
  juntas, não vegetação isolada — para cirurgia precoce (dentro de 48 horas) ou tratamento
  convencional. O desfecho composto de óbito hospitalar e evento embólico em 6 semanas ocorreu
  em 1 paciente (3%) no grupo de cirurgia precoce contra 9 (23%) no convencional (razão de risco
  0,10; IC95% 0,01–0,82; p=0,03), sem diferença de mortalidade por qualquer causa em 6 meses.
  Este resultado sustenta com mais força o ramo **C5** (vegetação associada a disfunção valvar
  grave) do que o ramo **C6** (vegetação isolada, sem disfunção grave) — a evidência randomizada
  para cirurgia por tamanho **isolado**, sem outro critério associado, é mais fraca, e é por
  isso que a diretriz classifica esse cenário como IIb, não como I.
- **O corte de 30 mm da literatura é sobre risco de complicação neurológica, não é um critério
  formal de indicação cirúrgica isolada.** A metanálise já citada no documento geral desta
  pasta (PMID 29459947) associa vegetação acima de 10 mm, e sobretudo acima de 30 mm, a maior
  risco de complicação neurológica — mas esse número não aparece como corte na recomendação
  Classe IIb da ESC 2023, que usa apenas o limiar de 10 mm. Por isso a árvore não usa 30 mm como
  ramo de decisão, para não atribuir à diretriz um corte que pertence a outra fonte.
- **A decisão de operar corre em paralelo ao esquema antibiótico**, não depois dele — os
  esquemas por agente e o esquema empírico têm fluxograma próprio nesta pasta.
- **Se sobrevier AVC ou outra complicação neurológica no meio deste algoritmo**, a decisão de
  timing muda de árvore — ver o fluxograma de timing cirúrgico após complicação neurológica
  desta mesma pasta, que trata especificamente da presença de coma e da exclusão de hemorragia
  por imagem.
- **Endocardite de câmaras direitas tem racional próprio**, incluindo aspiração mecânica
  percutânea como alternativa à cirurgia aberta em casos selecionados — ver o documento
  dedicado a endocardite de câmaras direitas desta pasta.
- **"Baixo risco cirúrgico" não é definido numericamente nesta árvore.** A diretriz remete à
  avaliação da equipe de endocardite (heart team), que pondera idade, comorbidade, escore de
  risco cirúrgico e fragilidade — não há um corte único de escore citado nas fontes usadas aqui.
