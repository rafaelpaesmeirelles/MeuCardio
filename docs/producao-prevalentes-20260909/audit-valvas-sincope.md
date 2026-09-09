# Auditoria e produção — valvopatias e síncope, 09/09/2026

Base: árvore GitHub main 64796aa973316c94b47dcf8dc75a474415ecba34. Quatro documentos centrais foram lidos diretamente via github_fetch_file: resumo canônico valvar, atualização ESC 2025, síncope ESC 2018 e fluxograma de sopro incidental adulto. Inventário completo de paths consultado; não se afirma leitura integral de todos os documentos de ambas as pastas.

## Entregas

Três novos complementos de consulta/imagem e uma correção pontual real:

- content/Valvopatias/estenose-aortica-do-laudo-discordante-a-consulta-longitudinal.md: interpretação básica dos parâmetros, discordância, revisão técnica, seguimento documentado, caso fictício e vínculos reais.
- content/Valvopatias/insuficiencia-mitral-leitura-critica-do-laudo-e-preparo-da-decisao.md: diferenciação por mecanismo, armadilhas de quantificação, ficha de encaminhamento, caso fictício e vínculos reais.
- content/Síncope/sincope-recorrente-apos-marca-passo-interpretacao-do-tilt-e-reavaliacao.md: complemento à lacuna de interpretação longitudinal e à inversão encontrada no nó canônico.
- content/Síncope/sincope-diagnostico-e-manejo-esc-2018.md: versão atual preservada, com correção do parágrafo que atribuía maior recorrência pós-MP ao tilt NEGATIVO; subanálise ISSUE-3 demonstra associação com tilt POSITIVO. Acrescentadas referências e nota de escopo; status legado revisado preservado sem alegação de revisão humana integral.

## Evidência acessada e limites

Fontes primárias abertas: EACVI/ASE 2017 estenose (DOI 10.1016/j.echo.2017.02.009), BSE 2021 estenose (DOI 10.1530/ERP-20-0035), ASE 2017 regurgitação (DOI 10.1016/j.echo.2017.01.007); abstracts originais ISSUE-3 subanálise (PMID 24336948) e BIOSync CLS (PMID 33279955). Links completos em source_refs de cada documento. Sínteses breves, sem tradução extensa ou reprodução de tabelas/figuras das fontes. Casos e fichas são originais e explicitamente identificados.

Portais oficiais ESC 2025 valvas e ESC 2018 síncope acessados. O texto integral OUP e slides não retornaram conteúdo utilizável nesta sessão; por isso não reproduzidas novas classes de intervenção 2025 nem afirmada conferência integral das tabelas. Os documentos novos remetem aos fluxos atuais já existentes para indicação definitiva. Novos textos em pendente_revisao, não falsamente revisados por humano.

A subanálise ISSUE-3 não deve ser extrapolada para contraindicar estimulação em todo tilt positivo: BIOSync CLS demonstrou benefício em população selecionada com assistolia induzida e síncope reflexa recorrente grave. O patch canônico contempla a distinção.

## Proposta de relações centrais (slugs verificados nos metadados atuais)

Documento estenose-aortica-do-laudo-discordante-a-consulta-longitudinal:
- doença estenose-aortica-tavi-idoso; fragmento adicional existente estenose-aortica.json, conferir slug interno antes da relação.
- exames ecocardiograma-de-estresse-com-dobutamina-em-baixa-dose-na-estenose-aortica-de-baixo-fluxo-baixo-gradiente-com-fe-reduzida; escore-de-calcio-da-valva-aortica-na-estenose-aortica-de-baixo-fluxo-baixo-gradiente; ergometria-na-estenose-aortica-assintomatica-grave (apenas como aprendizagem do cenário correto, não pedido reflexo em sintomático).
- fluxos de estenose grave sintomática e assintomática ESC/EACTS 2025, ambos ligados no corpo.

Documento insuficiencia-mitral-leitura-critica-do-laudo-e-preparo-da-decisao:
- fragmento existente doencas/fragmentos/insuficiencia-mitral.json; conferir slug interno para relação.
- fluxo regurgitacao-mitral-esc-eacts-2025, COAPT/MITRA-FR, prolapso/disjunção anular, imagens de ETE/3D/Doppler, já ligados no corpo.

Documento sincope-recorrente-apos-marca-passo-interpretacao-do-tilt-e-reavaliacao:
- doença sincope.
- exames teste-de-inclinacao-tilt-test; holter-e-monitor-de-eventos-externo-na-sincope; monitor-de-eventos-implantavel-ilr-na-sincope (vínculo temático condicionado à indicação individual; ILR não é automaticamente necessário em portador de MP com registros úteis).
- artigo canônico síncope e artigo estimulação CLS com relações recíprocas propostas.

Não há calculadora validada inventada para quantificação integrada, ficha de consulta ou recorrência pós-MP. Checklist original não tem validação prognóstica. Não foram modificadas relações centrais, exames ou trilhas; integração reservada ao coordenador.

## Verificação

Links relativos dos quatro arquivos conferidos contra current-paths.txt mais novos arquivos: nenhum destino ausente. Nenhum commit, push, PR ou deploy realizado por esta frente. Uma rodada não fecha todas as lacunas de cardiologia prevalente; material entregue é complemento incremental, com limites explicitados.
