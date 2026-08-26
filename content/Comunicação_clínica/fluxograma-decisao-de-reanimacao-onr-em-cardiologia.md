---
title: "Fluxograma: Decisão sobre Status de Reanimação (ONR) no Cardiopata"
slug: fluxograma-decisao-de-reanimacao-onr-em-cardiologia
theme: "Comunicação clínica"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
source_refs:
  - "Documento já publicado no acervo (tema Comunicação clínica): 'Ordem de Não Ressuscitar (ONR): a Conversa sobre RCP no Cardiopata em Fase Terminal' (slug: ordem-de-nao-ressuscitar-onr-nao-ressuscitar-nao-e-nao-tratar), de onde vêm a estrutura de seis passos da conversa, a distinção entre ONR e suspensão de cuidado, e o achado de que a preferência de recusar RCP fica sistematicamente subdetectada quando não perguntada de forma direta."
  - "Documento já publicado no acervo (tema Comunicação clínica): 'Decisão Compartilhada em Discussões de Status de Reanimação' (slug: decisao-compartilhada-em-status-de-reanimacao-ensaio-randomizado), de onde vem a evidência de que uma discussão estruturada reduz conflito decisional e muda a escolha registrada."
  - "Wenger NS, Phillips RS, Teno JM, et al. Physician understanding of patient resuscitation preferences: insights and clinical implications. J Am Geriatr Soc. 2000;48(5 Suppl):S44-51. PMID: 10809456."
  - "Golin CE, Wenger NS, Liu H, et al. A prospective study of patient-physician communication about resuscitation. J Am Geriatr Soc. 2000;48(5 Suppl):S52-60. PMID: 10809457."
  - "Diem SJ, Lantos JD, Tulsky JA. Cardiopulmonary resuscitation on television. Miracles and misinformation. N Engl J Med. 1996;334(24):1578-1582. PMID: 8628340."
  - "Becker C, Gross S, Beck K, et al. A Randomized Trial of Shared Decision-Making in Code Status Discussions. NEJM Evid. 2025;4(5):EVIDoa2400422. DOI: 10.1056/EVIDoa2400422. PMID: 40261118."
---

# Fluxograma: Decisão sobre Status de Reanimação (ONR) no Cardiopata

Esta árvore segue a estrutura prática de seis passos do documento-fonte, organizada em torno do achado que a justifica: médicos que não perguntam diretamente presumem, por padrão, que o paciente quer reanimação — e acertam essa suposição em 86% dos casos, mas acertam apenas 46% das vezes quando o paciente na verdade não quer ser reanimado (Wenger et al., 2000). A árvore trata isso como o ponto de partida: perguntar de forma explícita, não presumir.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Cardiopata com indicação de discutir status de reanimação (doença grave, IC avançada terminal, ou rotina de admissão)"] --> D1{"O médico já conhece, de conversa prévia explícita, a preferência do paciente sobre RCP?"}

  D1 -->|"Não, preferência nunca foi perguntada diretamente"| N1["Abrir separando a ONR do resto do plano: 'quero conversar sobre o que fazer se o coração parar — isso não muda nada do resto do tratamento'"]
  N1 --> N2["Explicar o que a RCP tenta fazer, em termos concretos, sem eufemismo (compressão, choque, possível intubação)"]
  N2 --> N3["Dar o número real de sobrevida (ex.: ~15-20% na população geral internada, tendendo a ser menor em cardiopatia terminal), nomeando a distorção da TV"]
  N3 --> D2{"Qual a preferência manifestada pelo paciente, perguntada de forma direta?"}

  D2 -->|"Prefere tentar reanimação (código completo)"| C1(["Registrar código completo; reafirmar que a preferência será revisitada se o quadro clínico mudar"])
  D2 -->|"Prefere não ser reanimado (ONR)"| N4["Nomear explicitamente que 'sim para ONR' não é 'sim para desistir' — reafirmar tudo que continua (conforto, presença, tratamento de intercorrência tratável)"]
  N4 --> C2(["Documentar a ordem de não ressuscitar (ONR) e revisitar se houver internação nova, piora aguda ou pedido de reabertura da conversa"])

  D1 -->|"Sim, preferência já foi explicitamente conversada e registrada"| D3{"Houve mudança relevante no quadro clínico desde o registro (nova internação, piora aguda)?"}
  D3 -->|"Sim, mudança relevante"| C3(["Reabrir a conversa e reconfirmar ou atualizar a preferência antes de qualquer decisão"])
  D3 -->|"Não, quadro estável desde o último registro"| C4(["Manter a ordem já registrada; não presumir mudança de preferência sem perguntar"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Sobre os critérios usados nesta árvore

A distinção entre ONR e suspensão de cuidado, verbalizada como primeiro passo, é o ponto que o documento-fonte identifica como origem da resistência de muitas famílias: "a pergunta que ouvem não é 'querem que eu tente compressão torácica quando o coração parar', é, na cabeça delas, 'vocês querem que eu pare de cuidar dele'". Nomear a diferença antes de pedir a decisão evita recusa por um motivo que não é o que está de fato em jogo.

Os números de sobrevida citados vêm de duas coortes que o documento-fonte é explícito em não generalizar sem ressalva: Girotra et al. (N Engl J Med 2012, PMID 23150959) encontraram sobrevida até a alta subindo de 13,7% para 22,3% entre 2000 e 2009 em população geral internada, e Ehlenbach et al. (N Engl J Med 2009, PMID 19571280) encontraram 18,3% em pacientes de 65 anos ou mais — nenhuma das duas seleciona especificamente cardiopatia estrutural terminal, e o documento-fonte marca essa extrapolação como raciocínio clínico razoável, não dado medido (`VERIFICAÇÃO HUMANA NECESSÁRIA` para taxa específica por classe funcional NYHA).

A evidência de que a estruturação da conversa muda desfecho vem do ensaio suíço cluster-randomizado de Becker et al. (NEJM Evid 2025, PMID 40261118): 206 residentes cuidando de 2.663 pacientes, com a intervenção estruturada associada a mais escolhas de DNR (50,0% vs. 37,2%; RR ajustado 1,37) e menor conflito decisional (14,4 vs. 21,8 pontos na Decisional Conflict Scale) — achado que o próprio estudo interpreta não como objetivo de "aumentar DNR", mas como sinal de decisão mais esclarecida quando a conversa inclui prognóstico e verificação de compreensão, e não uma pergunta binária isolada.