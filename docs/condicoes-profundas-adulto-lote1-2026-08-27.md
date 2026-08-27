# Condições profundas do adulto — lote 1

Data da produção: 27/08/2026  
Estado editorial: `pendente_revisao`  
Responsável pela produção inicial: ChatGPT  
Publicação automática: bloqueada

## Problema observado

Na base deste lote, 57 de 88 doenças estavam classificadas como `basico` e
apenas uma condição da área `geral` estava disponível. Além disso, a API já
entregava `diagnostic_approach`, `related_document_slugs` e
`patient_material_slug`, mas a tela de detalhe não exibia a abordagem
diagnóstica nem os vínculos explícitos. Assim, parte da superficialidade era de
conteúdo e parte era de apresentação.

## Escopo entregue

Quatro verbetes adultos completos, sem substituir registros especializados:

- hipertensão arterial sistêmica;
- fibrilação atrial;
- insuficiência cardíaca;
- síndrome coronariana crônica.

Cada verbete contém apresentação, abordagem diagnóstica estruturada,
diferenciais, exames, red flags, fluxos ambulatorial e de emergência,
tratamento, monitorização, populações especiais e assistente determinístico.

## Relações clínicas diretas

Os campos `related_document_slugs` e `patient_material_slug` apontam somente
para registros existentes e diretamente dedicados à condição. O teste do lote
resolve todos os slugs antes de permitir a integração.

O casamento exato e não ambíguo de diferenciais de triagem produz vínculos
diretos somente entre insuficiência cardíaca e as triagens `dispneia`, `edema`,
`fadiga-e-intolerancia-ao-esforco`,
`queda-ou-delirium-no-idoso-cardiopata` e
`sintomas-cardiovasculares-no-paciente-oncologico`.

## Proximidade temática preservada como não relação

- `pressao-arterial-alterada` não foi ligada à HAS: seus diferenciais são
  estados mais específicos (`Hipertensão crônica descontrolada` e
  `Emergência hipertensiva`), não sinônimos exatos do verbete.
- `palpitacoes` não foi ligada à FA: o diferencial agregado
  `Fibrilação/flutter atrial` não equivale a uma entidade única.
- `dor-toracica` não foi ligada à síndrome coronariana crônica: a triagem cita
  síndrome coronariana aguda, que é uma condição clínica distinta.
- Não foram criados vínculos novos com medicamentos, exames, evidências,
  estudos, calculadoras, casos, checklists, trilhas ou emergência sem um campo
  canônico explícito que os sustente.

## Fontes primárias

- AHA/ACC 2025 para hipertensão arterial — DOI
  `10.1161/CIR.0000000000001356`;
- ESC 2024 e SBC/SOBRAC 2025 para fibrilação atrial — DOI
  `10.1093/eurheartj/ehae176` e `10.36660/abc.20250618`;
- AHA/ACC/HFSA 2022 e atualização ESC 2023 para insuficiência cardíaca — DOI
  `10.1161/CIR.0000000000001063` e `10.1093/eurheartj/ehad195`;
- ESC 2024 e AHA/ACC 2023 para síndrome coronariana crônica — DOI
  `10.1093/eurheartj/ehae177` e `10.1016/j.jacc.2023.04.003`.

## Gates obrigatórios

- validação JSON e das regras determinísticas;
- resolução de documentos e materiais relacionados;
- inventário estrito e auditoria Tudo com Tudo;
- testes editoriais e de catálogo;
- build de produção do frontend;
- revisão clínica humana antes de alterar `review_status`.

