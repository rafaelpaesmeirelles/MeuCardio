# Lote Tudo com Tudo — suspeita de AVC agudo e primeira hora

Data da auditoria: 26/08/2026.

## Lacuna priorizada

A `main` tinha prevenção de AVC, anticoagulação na fibrilação atrial, estudos de
reperfusão, medicamentos trombolíticos e investigação etiológica pós-evento.
Não havia, porém, triagem sindrômica nem protocolo de emergência para reconhecer
um déficit neurológico focal súbito, acionar o sistema de emergência e preservar
o último horário sabidamente bem. A lacuna foi priorizada por gravidade,
dependência temporal e conexão clínica direta com FA, hipertensão, carótidas e
antitrombóticos.

## Conteúdo novo

- documentos: protocolo e fluxograma de reconhecimento/primeira hora;
- triagem: `deficit-neurologico-focal-subito`;
- doença: `acidente-vascular-cerebral-agudo`;
- emergência: `suspeita-de-avc-agudo`;
- checklist: `primeira-hora-na-suspeita-de-avc-agudo`;
- material ao paciente: `sinais-de-avc-como-agir-sem-perder-tempo`;
- evidências: acionamento imediato, FAST/Cincinnati e glicemia sem atraso;
- trilha: da identificação à decisão especializada de reperfusão.

Os 11 registros permanecem como `pendente_revisao`, com
`fonte_producao=chatgpt`. Nenhuma decisão de revisão clínica humana foi
presumida.

## Relações clínicas diretas

| Origem | Campo estruturado | Destino | Justificativa |
|---|---|---|---|
| doença | `differential_for` por nome exato | triagem | déficit focal súbito é porta de entrada do AVC agudo |
| doença | `related_document_slugs` | protocolo e fluxograma | ambos descrevem a mesma primeira hora |
| material | `patient_education_for` | doença | sinais e acionamento do SAMU 192 |
| material/checklist | `derived_from` | protocolo | derivação explícita, com slug canônico |
| emergência | `derived_from` / `uses_flowchart` | protocolo / fluxograma | execução operacional da mesma suspeita |
| evidências | `supported_by` | protocolo / fluxograma | recomendações pontuais AHA/Red Cross 2024 |
| trilha | `contains` | documentos, evidências, checklist, ECASS III, alteplase e tenecteplase | sequência explícita da identificação à decisão de reperfusão |
| documentos | links Markdown | protocolo, fluxograma, alteplase e tenecteplase | navegação bidirecional pela API do grafo |

O armazenamento das arestas é dirigido, mas a API consulta relações de entrada
e saída. Os nós pendentes continuam fora da publicação até revisão humana.

## Proximidade temática sem promoção a vínculo direto

- CHA₂DS₂-VASc estima risco embólico em FA; não diagnostica AVC agudo nem decide
  reperfusão, portanto não entrou na trilha;
- casos de ELAN, FOP e monitorização pós-AVC tratam prevenção secundária ou
  etiologia, não reconhecimento/primeira hora;
- OCEANIC-STROKE e INTERSTROKE são relevantes à prevenção, não à execução deste
  protocolo;
- exames cardiovasculares do corpus não substituem neuroimagem cerebral, e não
  foi fabricado um vínculo com eles;
- não existe verbete canônico de TC/RM de crânio na coleção `exames`; a lacuna é
  declarada, não preenchida por aproximação.

## Fontes primárias e atuais

- AHA/Red Cross First Aid 2024, DOI `10.1161/CIR.0000000000001281`:
  acionamento imediato e FAST/Cincinnati, Classe I, LOE B-NR; glicemia sem
  atrasar o acionamento, Classe IIa, LOE C-EO; oxigênio rotineiro sem benefício
  em AVC, Classe III, LOE B-R.
- AHA/ASA Acute Ischemic Stroke 2026, DOI
  `10.1161/STR.0000000000000513`, com correção DOI
  `10.1161/STR.0000000000000530`: sistema pré-hospitalar, neuroimagem,
  trombólise com alteplase/tenecteplase e seleção de terapia endovascular.
- Ministério da Saúde, página oficial AVC e SAMU 192, consultadas em
  26/08/2026, para adaptação do acionamento ao Brasil.
- ECASS III, DOI `10.1056/NEJMoa0804656`, já verificado no corpus, usado somente
  na trilha como estudo original da janela de 3 a 4,5 horas da alteplase.

## Riscos e limites

- o fluxo não substitui neurologia, neuroimagem, regulação do SAMU ou protocolo
  institucional;
- não contém critérios completos de trombólise/trombectomia nem prescrição
  automática;
- não orienta AAS ou anticoagulante antes de excluir hemorragia;
- FAST ajuda a reconhecer adultos, mas não exclui apresentações posteriores e
  não deve ser usado isoladamente em pediatria;
- rotulagem local e protocolo de diretriz podem divergir para tenecteplase; a
  decisão cabe à equipe de AVC e à regulação aplicável;
- revisão clínica e técnica final é obrigatória antes de qualquer item mudar
  para `revisado`.

## Gates esperados

- inventário: 9.452 → 9.463 itens; arquivos físicos: 2.185 → 2.187;
- revisão: 9.452 `revisado` + 11 `pendente_revisao`;
- referências canônicas quebradas: zero;
- cobertura temática explícita: 9.463/9.463;
- JSON, frontmatter, regras de triagem, inventário, grafo, testes e build devem
  permanecer verdes.

