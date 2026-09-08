# PR #833 — revisão final de sinalizadores CLTI/AAA

08/09/2026. Revisão clínica/editorial e auditoria adversarial própria por Codex, autorizadas pelo responsável nesta tarefa. Não se declara revisão humana independente.

Base sincronizada: `e7b7c35def95831f2745f5e5810f477de6a6da28` (`main`). Head original: `db373c46ba8497d70ea1d4688bae30ee00acc0fe`. Integração da main por merge, preservando histórico e permitindo push sem força. Nenhum merge do PR nem deploy.

## Resultado clínico/editorial

Somente os três documentos novos passam de `pendente_revisao` para `revisado`, após revisão e verificações. A aprovação `editorial-approvals/pr833-aorta-dap-final-20260908.json` identifica os três slugs e SHA-256 finais. Preservado o slug antigo de CLTI para compatibilidade; título corrigido para isquemia **crônica** ameaçadora de membro.

Resolvidos os cinco achados automáticos: categoria `fluxograma`; porta de AAA com dor nova mesmo estável; ALI sem exigir os seis Ps; claudicação a poucos passos sem classificação automática como CLTI; referências YAML entre aspas. Tratados os 11 pontos editoriais: perfusão objetiva, infecção isolada, destino hospitalar versus vascular urgente, palpação sem valor excludente, fatores de risco sem gate por sexo/idade e claudicação sem prazo automático para intervenção.

## Fontes verificadas

- [ESC PAAD 2024, página oficial](https://www.escardio.org/guidelines/clinical-practice-guidelines/all-esc-practice-guidelines/peripheral-arterial-and-aortic-diseases/), [DOI ehae179](https://doi.org/10.1093/eurheartj/ehae179), [PMID 39210722](https://pubmed.ncbi.nlm.nih.gov/39210722/). Conferido o texto integral: 8.1.1/8.1.2 (fenótipos, CLTI, perfusão/WIfI, pp. 3574/3585), 8.1.3 (ALI, pp. 3588–3590), 9.2.3 (AAA, apresentação e rotura contida, p. 3607), 9.2.5.5/tabela 41 (reparo, pp. 3613–3615).
- [ESVS AAA 2024, PDF oficial](https://esvs.org/wp-content/uploads/2024/02/ESVS-2024-AAA-Guidelines.pdf), [DOI 10.1016/j.ejvs.2023.11.002](https://doi.org/10.1016/j.ejvs.2023.11.002), [PMID 38307694](https://pubmed.ncbi.nlm.nih.gov/38307694/). Complementa a distinção de AAA sintomático sem rotura: avaliação/otimização breve seguida de reparo urgente, sem ordem automática de cirurgia imediata em todo estável.

“Mesmo dia”, contato direto e alternativa pelo PS são operacionalização editorial de destino seguro, não prazo numérico atribuído literalmente à ESC. Duas semanas caracterizam cronicidade e nunca autorizam esperar diante de membro ameaçado. Sem doses ou classes de recomendação inventadas.

## Auditoria adversarial manual

Confrontados os protocolos e o fluxograma; destinos consistentes após correção:

| Cenário | Destino/guarda |
|---|---|
| Dor abrupta e parestesia, sem palidez e pulso apenas reduzido | ALI suspeita → PS agora, sem conjunto completo |
| Novo déficit motor em DAP crônica | Via aguda imediata, sem esperar ITB/WIfI |
| Pé ameaçado com pouca dor por neuropatia | Dor intensa não é requisito |
| Dor isquêmica de repouso persistente com DAP e estabilidade | Vascular urgente com acesso rápido acordado |
| CLTI sem acesso rápido, dor intratável ou piora | PS/hospital |
| Gangrena seca estável | Vascular urgente, sem ALI automática |
| Gangrena úmida, abscesso em pé isquêmico ou sinais sistêmicos | Hospital imediato, controle infeccioso e vascular |
| Celulite isolada sem isquemia | Não diagnosticar CLTI; gravidade infecciosa define cuidado próprio |
| Claudicação a poucos passos, estável e sem ameaça | Tratamento/exercício; eletivo se limitação persistente |
| Queda da distância percorrida sem outros sinais | Reavaliar; não diagnosticar ALI/CLTI automaticamente |
| AAA e dor lombar nova com PA normal | Hospital no mesmo dia; PS se acesso direto não garantido |
| Massa pulsátil dolorosa sem hipotensão | PS imediato |
| Síncope/choque em contexto de AAA suspeito | Emergência, sem exigir dor ou tríade completa |
| Mulher/não fumante sem massa palpável e suspeita aórtica | Ausências não excluem; aplicar via urgente |
| AAA incidental e lombalgia crônica inalterada de outra causa estabelecida | Sem emergência automática; dúvida/mudança → urgente |
| AAA assintomático com critério de reparo | Vascular prioritário; sem PS por diâmetro isolado |

## Links, taxonomia e anti-colisão

Inspecionado `backend/app/api/library.py`: `_library_document_links` converte `[rótulo](arquivo.md)` para `/biblioteca/<nome-do-arquivo>`. Os nomes entre crases foram convertidos em links reais. Os testes executam a função de produção extraída da árvore sintática, verificam arquivo, filename/slug, unicidade e status. Destinos externos ao lote já revisados na main; três documentos internos aprovados juntos. Não há referência runtime-only `corvia-intelligence-*`.

Busca GitHub por CLTI identificou #833, #868 (carótida/AIT), #901 (SAA), #474 (DAP/ALI canônico) e #578 (hub DAP). Mantidos os três slugs do PR, sem novo hub, score ou fluxo SAA/carótida concorrente. Inventário e auditorias validam colisões e links. Nenhuma aresta JSON inventada: infecção não equivale a CLTI e dor de AAA não equivale a rotura.

## Verificação e limites

Comandos: testes novos de PR833, testes existentes de frontmatter, links canônicos, status editorial e gate Tudo-com-Tudo; `content_inventory.py --strict`; `audit_tudo_com_tudo.py`; `audit_tudo_com_tudo_semantics.py --require-actual-mechanisms --json`; auditoria `--approval-manifest` do lote.

Testes de corpus executados com `pytest --noconftest`, sem carregar o conftest global de aplicação/banco, do qual não dependem. No Windows, caminhos estendidos evitam a limitação de nomes longos. Nenhuma lógica de gate foi relaxada. F1 semântico se refere aos casos versionados com mecanismos reais; não certifica toda a medicina do corpus.

O manifesto global `full-corpus-*` permanece idêntico à main. Mudanças já presentes na main vieram apenas da sincronização. A release integrada precisa consolidar total/fingerprints e verificar publicação no banco. Este PR não certifica banco/produção, não faz merge e não faz deploy.

## Resultados finais

- 12 testes de PR833/frontmatter/links/status editorial aprovados.
- 25 testes do gate Tudo-com-Tudo e 4 subtestes aprovados.
- Inventário estrito: 11.584 registros, 2.886 arquivos; invalid/missing vazios. A contagem usa caminhos estendidos do Windows, incluindo os arquivos com nomes longos.
- Tudo-com-Tudo: zero bloqueios, zero links Markdown quebrados, 11.584 revisados.
- Aprovação específica dos três documentos: gate aprovado, zero bloqueios.
- Semântica com mecanismos reais: F1 após correção = 1,00; zero resíduos/invariantes.
- Bloqueio de release preservado: manifesto full-corpus precisa de consolidação única após integração do lote; banco e UI publicada não foram testados neste PR.
