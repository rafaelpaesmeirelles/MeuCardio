# Guia de Doenças — adulto, lote 2

Data da produção: 27/08/2026

Estado editorial: `pendente_revisao`
Publicação automática: bloqueada

## Problemas priorizados

A auditoria encontrou duas falhas de maior impacto:

1. síndrome coronariana aguda (SCA) não existia como doença adulta, embora já
   houvesse triagem, emergência, documentos e conteúdo longitudinal dedicado;
2. a busca do Guia de Doenças não normalizava acentos nem consultava o slug,
   fazendo `hipertensao` retornar zero mesmo com o verbete publicado.

O lote adiciona um único verbete clínico completo e corrige a descoberta do
catálogo. Não altera o estado editorial do AVC nem dos lotes especializados.

## Verbete entregue

`sindrome-coronariana-aguda` contém apresentação, diagnóstico estruturado,
diferenciais, exames, sinais de alarme, fluxos ambulatorial e de emergência,
tratamento em alto nível, monitorização, populações especiais e assistente
determinístico. O assistente apenas eleva prioridade, evidencia dados ausentes
e encaminha ao protocolo; ele não interpreta ECG, escolhe reperfusão, calcula
dose ou autoriza alta.

## Relações clínicas diretas

- triagem `dor-toracica`, por correspondência nominal exata do diferencial;
- emergência `sindrome-coronariana-aguda`, pelo mesmo conceito clínico;
- sete documentos e fluxogramas nominalmente dedicados à SCA, ECG/troponina e
  estratégia invasiva ou de reperfusão;
- checklist `alta-pos-sindrome-coronariana-aguda` e trilha
  `trilha-sindrome-coronariana-aguda`, ambos nominalmente dedicados à SCA;
- material ao paciente `doenca-coronariana-e-infarto`.

As três arestas externas curadas (emergência, checklist e trilha) ficam no
manifesto `doencas/relacoes-explicitas.json`. O grafo só as publica quando os
dois extremos estiverem publicados na mesma reconciliação; como o novo verbete
está pendente, elas permanecem auditáveis sem aparecer para usuários.

Medicamentos, exames, evidências, estudos, calculadoras e casos podem aparecer
como conteúdo do mesmo tema. Eles não foram promovidos em bloco a relação
clínica direta: indicação, população, comparador e limites de cada registro
precisam permanecer explícitos.

## Correções funcionais do guia

- busca sem acento por slug, nome, aliases e tags, com `%` e `_` escapados;
- facetas condicionais para não oferecer combinações vazias;
- filtros sincronizados com a URL e navegação voltar/avançar;
- remoção de filtros invisíveis ao trocar de aba;
- rota da Biblioteca corrigida para `/doencas`;
- mensagens do assistente renderizadas;
- resultado do assistente limpo ao trocar ambulatório por emergência;
- resposta booleana vazia preservada como não respondida;
- rótulos legíveis para área e categoria no detalhe.

## Fontes primárias

- Rao SV, O'Donoghue ML, Ruel M, et al. 2025 ACC/AHA/ACEP/NAEMSP/SCAI
  Guideline for the Management of Patients With Acute Coronary Syndromes.
  DOI `10.1161/CIR.0000000000001309`, com correções oficiais DOI
  `10.1161/CIR.0000000000001328`, `10.1161/CIR.0000000000001346` e
  `10.1161/CIR.0000000000001397`.

Documentos ESC preexistentes permanecem apenas como navegação clínica. A ESC
declara que transformar suas diretrizes em software ou algoritmos exige acordo
formal de licença; nenhuma regra deste lote foi derivada da diretriz ESC.

## Gates

- resolução de todos os slugs de documentos e material;
- validação das perguntas e regras determinísticas;
- prova de que somente `dor-toracica` cria vínculo direto por diferencial;
- inventário e auditoria de referências Tudo com Tudo;
- testes focados de busca, facetas, navegação e assistente;
- testes editoriais/backend e build de produção;
- revisão clínica humana antes de alterar `review_status`.
