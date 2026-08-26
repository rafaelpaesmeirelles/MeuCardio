---
title: "Fluxograma: Profilaxia antibiótica de endocardite infecciosa antes de procedimento odontológico ou não odontológico (ESC 2023)"
slug: fluxograma-endocardite-profilaxia-antibiotica-procedimento-odontologico-invasivo-esc-2023
theme: "Endocardite"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída a partir de dois documentos já publicados e revisados nesta pasta — 'profilaxia-antibiotica-de-endocardite-infecciosa-em-procedimentos-odontologicos.md' (população de alto risco e esquema de dose única conferidos contra a Recommendation Table 1 e a Table 6 da diretriz ESC 2023, texto integral lido em sessão anterior) e 'profilaxia-antibiotica-de-endocardite-infecciosa-em-procedimentos-nao-odontologicos.md' (Seção 3.3.2 e Table 5 da mesma diretriz). Nenhuma fonte nova foi consultada; a árvore preserva a marcação VERIFICAÇÃO HUMANA NECESSÁRIA já registrada no documento de procedimentos não odontológicos, quanto à ausência de esquema padronizado de fármaco/dose para a recomendação Classe IIb — não foi inventado nenhum esquema para esse ramo."
source_refs: ["Delgado V, Ajmone Marsan N, de Waha S, et al.; ESC Scientific Document Group. 2023 ESC Guidelines for the management of endocarditis. Eur Heart J. 2023;44(39):3948-4042. DOI: 10.1093/eurheartj/ehad193. PMID: 37622656 — Recommendation Table 1 e Table 6 (profilaxia odontológica, população de alto risco e esquema por dose única), texto integral já citado no documento 'profilaxia-antibiotica-de-endocardite-infecciosa-em-procedimentos-odontologicos.md' desta pasta.", "Delgado V, Ajmone Marsan N, de Waha S, et al. 2023 ESC Guidelines for the management of endocarditis. Eur Heart J. 2023;44(39):3948-4042. DOI: 10.1093/eurheartj/ehad193. PMID: 37622656 — Seção 3.3.2 (Non-dental procedures) e Table 5 (General Prevention Measures), já citadas no documento 'profilaxia-antibiotica-de-endocardite-infecciosa-em-procedimentos-nao-odontologicos.md' desta pasta."]
---

# Fluxograma: Profilaxia antibiótica de endocardite infecciosa antes de procedimento odontológico ou não odontológico (ESC 2023)

Esta pasta já tem um documento dedicado à profilaxia em procedimento odontológico e outro à
profilaxia em procedimento não odontológico — e a diretriz chega a conclusões
estruturalmente diferentes nos dois casos, o erro mais comum sendo tratá-los como
equivalentes. Este fluxograma reúne as duas decisões numa única árvore, partindo sempre da
mesma primeira pergunta: o paciente pertence à população de alto risco de desfecho adverso
por endocardite.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente vai ser submetido a procedimento<br/>odontológico ou não odontológico invasivo —<br/>avaliar necessidade de profilaxia antibiótica<br/>para endocardite infecciosa"] --> D1{"Paciente pertence à população de alto risco?<br/>prótese valvar, incluindo transcateter, ou material<br/>protético em reparo valvar cirúrgico; endocardite<br/>infecciosa prévia; cardiopatia congênita cianótica<br/>não tratada, ou tratada com defeito residual ou<br/>prótese; dispositivo de assistência ventricular"}

  D1 -->|"Não, risco padrão"| C1(["Profilaxia antibiótica não indicada<br/>para prevenção de endocardite infecciosa"])

  D1 -->|"Sim"| D2{"O procedimento é odontológico, com<br/>manipulação de tecido gengival, região<br/>periapical dentária ou perfuração<br/>da mucosa oral?"}

  D2 -->|"Sim"| D3{"Paciente tem alergia a<br/>penicilina ou ampicilina?"}

  D3 -->|"Não"| C2(["Amoxicilina via oral 2g em dose única,<br/>30 a 60 minutos antes do procedimento<br/>Classe I — alternativa: ampicilina IM/IV 2g<br/>ou cefazolina/ceftriaxona IM/IV 1g"])

  D3 -->|"Sim, sem história de<br/>anafilaxia, angioedema<br/>ou urticária com penicilina"| C3(["Cefalexina via oral 2g em dose única —<br/>alternativa: azitromicina ou claritromicina<br/>500mg, ou doxiciclina 100mg via oral.<br/>Clindamicina não é recomendada pela<br/>ESC 2023 pelo risco de C. difficile"])

  D3 -->|"Sim, COM história de<br/>anafilaxia, angioedema ou<br/>urticária a penicilina —<br/>não usar cefalosporina"| C4(["Azitromicina ou claritromicina 500mg,<br/>ou doxiciclina 100mg, via oral em dose única —<br/>se via oral for impossível, considerar via<br/>IM/IV com apoio de infectologia"])

  D2 -->|"Não, procedimento não odontológico<br/>endoscopia digestiva, colonoscopia,<br/>cistoscopia, biópsia de próstata,<br/>procedimento dermatológico"| D4{"Há infecção ativa identificada em<br/>qualquer foco pele, urinário, dentário<br/>antes do procedimento eletivo?"}

  D4 -->|"Sim"| C5(["Tratar a infecção ativa com<br/>antibiótico curativo antes do<br/>procedimento eletivo — não é profilaxia,<br/>é tratamento de infecção já estabelecida"])

  D4 -->|"Não, sem infecção<br/>ativa identificada"| C6(["Garantir ambiente asséptico rigoroso<br/>durante o procedimento; profilaxia<br/>antibiótica pode ser considerada de forma<br/>individualizada Classe IIb, sem esquema<br/>padronizado de fármaco/dose na diretriz"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

- **A justificativa para a Classe IIb em procedimento não odontológico não é nova evidência
  de eficácia.** A própria diretriz é explícita: "nenhuma evidência convincente foi
  apresentada sobre a relação entre bacteremia resultante de um procedimento não
  odontológico e o risco de endocardite infecciosa subsequente". A elevação de Classe III
  (diretriz anterior) para Classe IIb (ESC 2023) refletiu maior sobrevida dos pacientes e
  maior complexidade cirúrgica ao longo do tempo, não uma demonstração direta de que a
  profilaxia previne esses casos.
- **Não existe esquema de fármaco/dose padronizado para o ramo Classe IIb** (procedimento
  não odontológico). Onde a decisão individualizada optar por profilaxia nesse cenário, a
  escolha deve ser discutida caso a caso, idealmente com infectologia — o documento de
  origem já registra essa lacuna como `VERIFICAÇÃO HUMANA NECESSÁRIA`, e esta árvore não
  inventa um esquema para preenchê-la.
- **Reparo transcateter de valva mitral ou tricúspide** (Classe IIa, "deve ser considerada")
  e **transplante cardíaco em geral, sem exigir valvopatia associada** (Classe IIb, "pode ser
  considerada") são populações com recomendação mais fraca que a população de alto risco
  Classe I usada no nó raiz — tratadas em detalhe no documento de profilaxia odontológica já
  publicado nesta pasta, não repetidas aqui para manter a árvore legível.
- **Planejamento pré-procedimento de médio prazo não é profilaxia do dia do procedimento.**
  A diretriz recomenda eliminar focos de sepse dentária pelo menos 2 semanas antes de
  implante de prótese valvar ou outro material intracardíaco/intravascular — medida de
  prevenção geral, distinta da dose única administrada antes do procedimento odontológico em
  si.
- **Revisão sistemática Cochrane (2022) não encontrou evidência conclusiva de ensaio clínico
  randomizado** comprovando eficácia da profilaxia antes de procedimento dentário — a
  decisão de profilaxiar continua apoiada em consenso de especialistas e plausibilidade
  biológica, não em ensaio controlado robusto. Isso não muda a recomendação vigente, mas
  contextualiza a força real da evidência por trás dela.
- **Cardiopatia congênita corrigida cirurgicamente só mantém indicação de profilaxia nos
  primeiros 6 meses após o reparo completo**, na ausência de defeito residual ou prótese —
  detalhe que não coube no rótulo do nó raiz e está descrito por extenso no documento de
  profilaxia odontológica já publicado nesta pasta.
