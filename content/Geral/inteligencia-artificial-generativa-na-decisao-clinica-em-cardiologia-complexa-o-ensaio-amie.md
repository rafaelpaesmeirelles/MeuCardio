---
title: 'Inteligência Artificial Generativa na Decisão Clínica em Cardiologia Complexa: o Ensaio Randomizado do AMIE'
slug: inteligencia-artificial-generativa-na-decisao-clinica-em-cardiologia-complexa-o-ensaio-amie
theme: Geral
kind: estudo
review_status: revisado
source_refs:
- 'A large language model for complex cardiology care. Nature medicine. PMID: 41652123. DOI: 10.1038/s41591-025-04190-9. PMCID:
  PMC12920087.'
review_note: 'Texto integral do ensaio AMIE conferido, PMC12920087. Corrigida alegação de entrada multimodal bruta no LLM:
  o AMIE recebeu texto; médicos acessaram exames originais. Incluídos 107 casos, julgamento por tarefa e erros persistentes;
  retiradas afirmações regulatórias gerais não verificadas e ausência absoluta de avaliações da IA isolada.'
summary: 'Os médicos tinham acesso a relatórios e dados originais de ECG, ecocardiografia, ressonância e teste cardiopulmonar
  quando disponíveis. O AMIE recebeu os relatórios em texto, não interpretou diretamente todos os exames brutos: a existência
  de modalidades distintas no prontuário não demonstra capacidade de leitura autônoma de imagens pelo sistema. Resultados
  de testes genéticos foram omitidos de ambos durante a avaliação.'
tags: []
source_tier: A
gaps: []
published: true
---

# Inteligência artificial no raciocínio cardiológico complexo: o estudo AMIE

## Desenho e população
O estudo publicado na Nature Medicine avaliou o AMIE, sistema experimental baseado em modelo de linguagem, como apoio a cardiologistas gerais. Nove médicos analisaram **107 casos retrospectivos** de uma prática subespecializada, com suspeita de doença cardiovascular genética. Cada caso foi avaliado por dois cardiologistas, um com assistência do AMIE e outro sem, em comparação randomizada.

Os médicos tinham acesso a relatórios e dados originais de ECG, ecocardiografia, ressonância e teste cardiopulmonar quando disponíveis. **O AMIE recebeu os relatórios em texto**, não interpretou diretamente todos os exames brutos: a existência de modalidades distintas no prontuário não demonstra capacidade de leitura autônoma de imagens pelo sistema. Resultados de testes genéticos foram omitidos de ambos durante a avaliação.

Três subespecialistas, cegos à origem das respostas, julgaram triagem, diagnóstico e manejo com uma rubrica de dez domínios. Foi um experimento sobre respostas clínicas a casos existentes, sem alocar pacientes a tratamentos prospectivos.

## Resultados
- Os avaliadores preferiram as respostas assistidas em **46,7%**, as não assistidas em **32,7%** e consideraram **20,6%** empatadas (p=0,02).
- Erros considerados clinicamente significativos ocorreram em **13,1%** das avaliações assistidas e **24,3%** das não assistidas (p=0,033).
- Conteúdo relevante ausente: **17,8% versus 37,4%** (p=0,0021), respectivamente.
- Houve preferência significativa por assistência nos domínios de plano de manejo e investigação diagnóstica; não houve vantagem demonstrada em todos os domínios.
- Os cardiologistas relataram ajuda em **57,0%** dos casos e economia de tempo em **50,5%**. Essa economia foi percebida pelos participantes, não uma demonstração de eficiência clínica prospectiva.

Mesmo com assistência, persistiram erros. Os comentários descreveram achados de imagem fabricados, interpretações equivocadas de medidas e exames recomendados apesar de já realizados. A supervisão médica permaneceu essencial no experimento.

## Interpretação e limites
A randomização fortalece a comparação de qualidade das avaliações nessa tarefa. Ela não demonstra redução de mortalidade, complicações ou tempo até diagnóstico em atendimento real. O número de médicos foi pequeno, os casos vieram de uma prática subespecializada e a qualidade foi julgada por rubrica, não por desfechos de pacientes.

O artigo inclui exemplos de avaliações produzidas pelo AMIE isoladamente; a comparação principal randomizada foi **cardiologista com versus sem assistência**, e não superioridade de uma IA autônoma sobre subespecialistas.

O financiamento e os vínculos dos autores com a empresa desenvolvedora exigem consideração na leitura e reforçam a utilidade de replicação independente. O estudo caracteriza o AMIE como experimental; não estabelece autorização de uso clínico no Brasil nem valida outros modelos comerciais. Tampouco sustenta extrapolação automática para urgências, outras doenças ou integração assistencial na CorVIA.

## Fonte
O'Sullivan e colaboradores. *A large language model for complex cardiology care*. Nature Medicine, 2026. PMID 41652123; DOI 10.1038/s41591-025-04190-9. Texto integral: https://pmc.ncbi.nlm.nih.gov/articles/PMC12920087/.

## Tudo com Tudo

- [Inteligência Artificial Generativa na Comunicação com o Paciente Cardiológico: o que a Evidência Mostra e Onde Ela Falha](/biblioteca/inteligencia-artificial-generativa-na-comunicacao-com-o-paciente-cardiologico) — Relaciona desempenho do AMIE à comunicação clínica por IA generativa, supervisão e limites de validação no cuidado ao paciente.
