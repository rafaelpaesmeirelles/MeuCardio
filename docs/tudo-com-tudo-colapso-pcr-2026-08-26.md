# Lote Tudo com Tudo — colapso súbito e suspeita de PCR no adulto

Data da auditoria: 26/08/2026.

## Lacuna priorizada

A `main` continha protocolo de suporte avançado, fluxograma por ritmo, protocolo
de emergência, evidências, estudos e trilha de cuidado pós-parada. Faltava,
porém, a porta de entrada operacional para reconhecer o adulto não responsivo
com respiração ausente ou anormal — inclusive gasping — e acionar a cadeia de
sobrevivência sem uma checagem leiga de pulso. A omissão foi priorizada pela
gravidade, dependência temporal e capacidade de conectar conteúdo já publicado.

## Conteúdo novo

- triagem: `colapso-subito-inconsciencia-e-respiracao-anormal`;
- doença: `parada-cardiorrespiratoria-e-morte-subita-abortada`;
- checklist: `resposta-imediata-ao-colapso-subito-e-suspeita-de-parada-no-adulto`;
- material ao paciente: `colapso-subito-como-reconhecer-parada-e-usar-o-dea`.

Os quatro registros permanecem como `pendente_revisao`. Nenhuma decisão de
revisão clínica humana foi presumida.

## Relações diretas e bidirecionais na consulta

| Origem | Relação estruturada | Destino | Natureza |
|---|---|---|---|
| doença | `differential_for` por coincidência exata | triagem | direta, derivada de metadado |
| doença | `mentioned_in` | protocolo, fluxograma, DEA e pós-parada | direta, derivada de slug explícito |
| material | `patient_education_for` | doença | direta, derivada de slug explícito |
| material/checklist | `derived_from` | protocolo canônico de PCR | direta, derivada de slug explícito |
| emergência | `derived_from` / `uses_flowchart` | protocolo / fluxograma de PCR | direta, já existente |
| documento/fluxograma | `supported_by` | nove evidências de PCR | direta, já existente |
| trilha | `contains` | protocolo, fluxograma e pós-parada | direta, já existente |

O armazenamento da aresta é dirigido, mas a API do grafo consulta entrada e
saída; a navegação resultante é bidirecional. A prova de contrato está em
`backend/tests/test_tudo_com_tudo_colapso_pcr.py`.

## Proximidade temática, sem promoção a vínculo clínico

Estudos como TTM2 e PARAMEDIC2 pertencem ao tema `Terapia intensiva` e podem
ser recuperados pela camada taxonômica. Eles não receberam relação direta com a
nova doença porque o schema atual não contém um campo editorial estudo↔doença.
Medicamentos, exames, calculadoras e casos também não receberam arestas novas:
proximidade textual ou participação possível na ressuscitação não basta para
criar uma afirmação clínica específica.

## Fontes primárias e nível de evidência

- AHA 2025, Adult Basic Life Support, DOI `10.1161/CIR.0000000000001369`:
  reconhecimento de adulto inconsciente/não responsivo com respiração ausente
  ou anormal como parada presumida; leigo e profissional, Classe 1, LOE C-LD;
  compressões pelo leigo, Classe 1, LOE B-NR.
- AHA 2025, Systems of Care, DOI `10.1161/CIR.0000000000001378`:
  cadeia de sobrevivência, papéis de equipe, debriefing e melhoria de qualidade.
- AHA 2025, Adult Advanced Life Support, DOI
  `10.1161/CIR.0000000000001376`: cuidado avançado e pós-retorno.
- SBC 2019, DOI `10.5935/abc.20190203`: diretriz nacional canônica já publicada
  no corpus para execução de RCP, desfibrilação, fármacos e causas reversíveis.

URLs oficiais estão registradas nos próprios itens. Não foram usadas fontes
secundárias para sustentar as recomendações novas.

## Riscos e limites declarados

- escopo principal: adulto; pediatria, gestação, afogamento, trauma e intoxicação
  exigem algoritmos próprios e são apenas sinalizados como situações especiais;
- a triagem não substitui treinamento prático, regulação do SAMU ou protocolo
  institucional;
- doses e procedimentos avançados não foram duplicados no material leigo;
- o número epidemiológico de 356 mil eventos/ano refere-se aos Estados Unidos e
  não foi extrapolado ao Brasil;
- revisão clínica final é obrigatória antes de mudar os quatro registros para
  `revisado`.

## Gates esperados

- inventário: 9.452 → 9.456 registros, sem arquivo científico físico novo;
- revisão: 9.452 `revisado` + 4 `pendente_revisao`;
- referências canônicas quebradas: zero;
- cobertura temática explícita: 9.456/9.456;
- JSON, testes editoriais/integração, build e QA do grafo devem permanecer verdes.

