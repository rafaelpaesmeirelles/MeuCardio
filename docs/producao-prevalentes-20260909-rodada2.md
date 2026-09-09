# Produção cardiovascular prevalente — rodada 2 — 09/09/2026

Continuação do PR #915, com seis frentes autorais e revisão cruzada entre agentes independentes da autoria. Os registros usam revisão assistida por IA de forma explícita. Não houve revisão humana, importação no banco ou publicação.

## Entrega integrada

| Frente | Casos fictícios | Material ao paciente | Checklist novo | Aplicação principal |
|---|---:|---:|---:|---|
| Hipertensão | 2 | 1 | 1 | Uso real, intolerância, hipocalemia e rastreio sob interferentes |
| Insuficiência cardíaca | 2 | 1 | 1 | Segurança do ARM, depleção pós-alta e continuidade após melhora da FEVE |
| FA e palpitações | 2 | 1 | 1 | Correlação parcial no Holter e preparo de cardioversão após omissões do DOAC |
| Doença coronariana | 2 | 1 | 1 | Teste inconclusivo e duplicação de P2Y12 no retorno |
| Prevenção/lipídios e DM2 | 2 | 1 | 1 | Validade do LDL calculado, resposta ao tratamento e declínio inicial da TFGe |
| Valvopatias e síncope | 2 | 1 | 1 | Laudos discordantes e correlação clínica/dispositivo após desmaio |
| **Total** | **12** | **6** | **6** | **24 recursos novos** |

Cada novo caso apresenta contexto fictício, quatro alternativas, resposta em índice base zero e justificativas. Casos não são modelos de prescrição individual. Os seis materiais não oferecem posologia; o detector do carregador real também foi executado nos dois materiais corrigidos.

## Correções de conteúdos existentes

Cinco registros estruturados corrigidos: caso ANOCA/INOCA, materiais DAPT e prótese valvar, checklists de resistência hipertensiva e estenose aórtica de baixo fluxo/baixo gradiente. Dois documentos de origem foram corrigidos para manter coerência entre páginas:

- HAS: causas secundárias podem exigir investigação paralela; resistência aparente não comprova pseudorresistência; diurético depende da função renal e da volemia. Jung passa a explicitar **40/76 (53%)**, sem extrapolar aos 375 encaminhados. Kallioinen descreve efeitos individuais de erros de medida, sem somá-los. Terminologia e limites de avaliação da adesão refinados na consolidação.
- DAPT: retiradas duração máxima universal, alegação de única classe I e faixas genéricas de NNT/NNH. Anticoagulação concomitante tem via própria. MASTER DAPT e OPT-BIRISK delimitados por população e momento; OPT-BIRISK corrigido para **Li et al.** e **HR 0,75**, preservando intervalo e seleção dos participantes.
- ANOCA: espasmo microvascular diferenciado de outros mecanismos de disfunção microvascular; bloqueador de canal de cálcio considerado inicialmente no endótipo espástico.
- Valvas: removida suspensão universal de antitrombóticos aos três meses; prótese mecânica especifica antagonista da vitamina K e controle de INR. DSE diagnóstica em baixa dose distinguida de teste de esforço.

Na revisão cruzada final, a monitorização de ALT/CK foi delimitada ao contexto da estatina, com acompanhamento específico de outros medicamentos; sinais de AVC e possível melena foram redigidos sem exigir sintomas simultâneos. Essas solicitações dos pareceres foram aplicadas no catálogo final. As notas autorais preservam o estado anterior à consolidação.

## Tudo com Tudo

Os **24 recursos** têm retorno ao documento correspondente por link no caso ou campo nativo do material/checklist. **14 documentos** receberam links de ida aos recursos. Foram acrescentadas **24 relações explícitas de doença** e **18 etapas** às oito trilhas da primeira rodada, que agora somam **67 etapas**. Materiais ao paciente são acessíveis pelo documento e grafo; não foram inseridos como tipo de etapa que o carregador não suporta.

A sequência inclui fundamentos, aplicação, intercorrências e seguimento. O checklist de FEVE melhorada foi colocado após a transição pós-alta. As relações de palpitações explicitam diagnóstico diferencial, sem pressupor FA confirmada. A associação a exames e medicamentos é contextual; não significa indicação automática ou uso conjunto.

Mapa verificável: [recursos, documentos, doenças e trilhas](producao-prevalentes-20260909-rodada2-mapa.json).

## Verificação e preservação

Validação estática sem erros: JSON, frontmatter, referências, gabaritos, IDs de checklist, detector nativo de posologia, fontes documentais, 431 links internos do conjunto e destinos do grafo/trilhas. A revisão independente confirmou ausência de recursos órfãos. Detalhes: [resultado de validação](producao-prevalentes-20260909-rodada2-validacao.json).

Preservados, sem mudança de valor, **914 casos, 471 checklists e 446 materiais** fora das cinco correções. Catálogos resultantes: **927 casos, 479 checklists e 454 materiais**. Preservadas as 3.135 relações da primeira rodada e as 555 trilhas anteriores a este trabalho.

Base de autoria: main `cb750689b94f7888b18133e68ff8293bff55d742`. Consolidação confrontada com main `1c8454d132bfc6ecedec802c731dbb26b4d1e6da`: sem colisões nos arquivos alterados; mudanças paralelas preservadas. A continuação foi salva em patch compacto na branch do PR; sua aplicação e integração com a main cabem ao responsável pelo deploy.

Fontes efetivamente consultadas, limitações de acesso, pareceres e decisões de integração estão em [registros de revisão](producao-prevalentes-20260909-rodada2/). Não há alegação de leitura integral de fontes cujo acesso falhou. O overlay de materiais foi simulado com a função real e não sobrepôs as correções. O fluxo Intelligence pode substituir notas de revisão dos checklists conforme vínculos no banco; esse estado não foi consultado e não afeta os itens clínicos nesta entrega.

## Situação para lançamento

Somando as duas rodadas, o PR entrega **18 documentos novos**, **nove documentos existentes corrigidos**, **24 recursos estruturados novos**, **cinco registros estruturados corrigidos**, **oito trilhas** e **105 relações explícitas novas**. Isso amplia a cobertura prática, mas não certifica completude de todas as patologias ou do acervo histórico.

O teste histórico de autorização do corpus já falhava na primeira rodada: o manifesto de 07/09 autoriza 11.581 registros e não acompanha automaticamente alterações posteriores. O arquivo de autorização e seu teste foram preservados; a nova produção não equivale a uma nova aprovação geral do corpus. A publicação continua sujeita ao fluxo editorial existente. Nenhum gate foi desabilitado, nenhuma autorização foi fabricada e nenhum `published: true` foi acrescentado.

Importação, promoção editorial, reconciliação em produção e navegação autenticada ainda não foram executadas. Antes de declarar os temas integralmente completos, permanece necessária a auditoria de cobertura de cada núcleo, incluindo urgências, populações especiais e consistência do acervo histórico.
