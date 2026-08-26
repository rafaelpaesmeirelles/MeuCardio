---
title: "Fluxograma: Recusa de Transfusão Sanguínea em Cirurgia Cardíaca"
slug: fluxograma-recusa-transfusao-sanguinea-cirurgia-cardiaca
theme: "Comunicação clínica"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: a árvore deriva do documento já publicado no acervo (mesmo tema), que teve PMIDs conferidos por E-utilities do PubMed e a tese do STF conferida no PDF oficial do Tema 952 (mesma tese vale para o Tema 1069, julgado em conjunto). Nenhum dado novo foi introduzido nesta árvore além do que já está verificado no documento-fonte; a Resolução CFM 2.232/2019 já estava sinalizada naquele documento como verificada por três fontes secundárias convergentes, não pelo PDF oficial linha a linha — mesma ressalva reproduzida aqui."
source_refs:
  - "Documento já publicado no acervo (tema Comunicação clínica): 'Recusa de Transfusão Sanguínea em Cirurgia Cardíaca: Comunicação, Consentimento e Conservação de Sangue em Testemunhas de Jeová' (slug: recusa-de-transfusao-sanguinea-em-cirurgia-cardiaca-testemunhas-de-jeova-e-conservacao-de-sangue), de onde vêm a sequência de verificação de capacidade, o levantamento item a item do que o paciente aceita/recusa, a exigência de programa de conservação de sangue, o limite de idade e a distinção entre objeção de consciência do médico e recusa terapêutica do paciente."
  - "Supremo Tribunal Federal. RE 979.742 (Tema 952 da Repercussão Geral) e RE 1.212.272 (Tema 1069 da Repercussão Geral), Relator Min. Luís Roberto Barroso (Tema 952), julgamento conjunto em Plenário, 25/09/2024, por unanimidade (10x0). Tese fixada: 'Testemunhas de Jeová, quando maiores e capazes, têm o direito de recusar procedimento médico que envolva transfusão de sangue, com base na autonomia individual e na liberdade religiosa. Como consequência, em respeito ao direito à vida e à saúde, fazem jus aos procedimentos alternativos disponíveis no Sistema Único de Saúde – SUS, podendo, se necessário, recorrer a tratamento fora de seu domicílio.'"
  - "Conselho Federal de Medicina. Resolução CFM nº 2.232, de 17 de julho de 2019. Estabelece normas éticas para a recusa terapêutica por pacientes e objeção de consciência na relação médico-paciente."
  - "Pattakos G, Koch CG, Brizzio ME, Batizy LH, Sabik JF 3rd, Blackstone EH, Lauer MS. Outcome of patients who refuse transfusion after cardiac surgery: a natural experiment with severe blood conservation. Arch Intern Med. 2012;172(15):1154-1160. DOI: 10.1001/archinternmed.2012.2449. PMID: 22751620"
---

# Fluxograma: Recusa de Transfusão Sanguínea em Cirurgia Cardíaca

Esta árvore organiza, em sequência de decisão, a conduta diante do paciente que recusa
hemoderivados por convicção religiosa antes de procedimento cardíaco — a situação de maior
probabilidade histórica de necessidade de hemoderivados na prática da especialidade. Ela segue
a mesma lógica do documento-fonte já publicado neste acervo: a recusa não é tratada como
obstáculo à conduta correta, mas como um dado da história clínica que redesenha o plano
cirúrgico, dentro dos limites que a tese do STF (Temas 952 e 1069, julgamento conjunto de
25/09/2024) e a Resolução CFM 2.232/2019 estabelecem.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente com indicação de procedimento cardíaco recusa transfusão de hemoderivados por convicção religiosa"] --> D1{"Paciente é maior de idade e capaz (lúcido, orientado, consciente)?"}

  D1 -->|"Não, é menor de idade"| N1["Autonomia religiosa não se aplica ao menor — prevalece o melhor interesse da criança/adolescente (tese do STF, Temas 952/1069)"]
  N1 --> C1(["Não aceitar a recusa dos pais como decisão válida em nome do menor; acionar bioética/serviço social e, se necessário, via judicial — sem aguardar a urgência quando a cirurgia for eletiva com data programável"])

  D1 -->|"Sim, maior de idade e capaz"| N2["Verificar com o próprio paciente, sem intermediário, o que ele aceita (hemodiluição autóloga em circuito fechado, recuperador celular/cell saver, frações de plasma) e o que recusa (hemocomponentes alogênicos)"]
  N2 --> D2{"A equipe/instituição tem programa estruturado de conservação de sangue disponível?"}

  D2 -->|"Não"| C2(["Não operar sem protocolo por falta de alternativa percebida; encaminhar a centro com programa de conservação de sangue, como determina a tese do STF"])
  D2 -->|"Sim"| N3["Explicar o que a equipe PODE oferecer (eritropoetina pré-operatória, hemodiluição normovolêmica, recuperador celular, antifibrinolíticos, hipotermia controlada) antes de discutir o que não pode"]
  N3 --> D3{"O procedimento é eletivo ou de urgência/emergência com risco iminente de vida?"}

  D3 -->|"Eletivo"| D4{"O médico/cirurgião se sente confortável em operar sem possibilidade de transfusão?"}
  D4 -->|"Sim"| N4["Documentar a recusa como consentimento informado positivo: registrar que o paciente compreende o risco concreto de sangramento não corrigido por transfusão, não apenas que assinou termo"]
  N4 --> C3(["Prosseguir com o procedimento sob protocolo de conservação de sangue, com consentimento informado documentado item a item"])
  D4 -->|"Não, objeção de consciência"| C4(["Exercer objeção de consciência comunicando ao diretor técnico do estabelecimento, garantindo encaminhamento a outro profissional que assuma o caso — nunca recusar atendimento sem alternativa"])

  D3 -->|"Urgência/emergência com risco iminente de vida"| N5["A recusa livre, consciente e informada do paciente adulto e capaz permanece válida mesmo em risco de vida (tese do STF); o direito de objeção de consciência do médico não pode ser exercido aqui se não houver outro profissional disponível"]
  N5 --> C5(["Aplicar o protocolo de conservação de sangue já pactuado e prosseguir respeitando a recusa documentada; se não houver outro médico disponível, o profissional presente não pode recusar o atendimento"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Sobre os critérios usados nesta árvore

A primeira bifurcação (maioridade e capacidade) é o limite que a própria tese do STF
constitucionaliza e que não se negocia: a autonomia religiosa não se estende a filhos menores
de idade, prevalecendo o melhor interesse da criança e do adolescente quando há tratamento
eficaz e seguro disponível. É por isso que essa pergunta abre a árvore, antes de qualquer
outra consideração clínica.

A verificação item a item do que o paciente aceita — hemodiluição autóloga em circuito
fechado, recuperador celular intraoperatório, determinadas frações de plasma — reflete o
achado do documento-fonte de que "recusar hemoderivados" não é categoria única: muitas
Testemunhas de Jeová aceitam técnicas que mantêm o sangue em circuito contínuo com o corpo do
paciente e recusam apenas a transfusão alogênica. Essa distinção muda o plano cirúrgico
inteiro, e só o próprio paciente pode defini-la.

A bifurcação entre eletivo e urgência/emergência com risco iminente de vida reproduz a
distinção que a Resolução CFM 2.232/2019 traça para o direito de objeção de consciência do
médico — que tem limite explícito em situação de urgência/emergência sem outro profissional
disponível — sem que isso autorize, em nenhum dos dois ramos, transfundir contra a vontade do
paciente adulto e capaz: a tese do STF garante essa autonomia mesmo diante de risco de morte,
que foi exatamente o cenário do caso concreto julgado no Tema 1069 (cirurgia de troca de valva
aórtica).
