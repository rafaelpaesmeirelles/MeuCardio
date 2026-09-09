# Rodada 2 — prevenção/lipídios e DM2 — 09/09/2026

## Entrega e escopo

Listas novas, sem modificar produção1 ou catálogos existentes:

- `round2/prevencao/casos-clinicos.json`: 2 casos fictícios, 4 alternativas, índice correto base 0, explicação A/B/C/D.
- `round2/prevencao/material-paciente.json`: 1 roteiro prático de preparo ao retorno.
- `round2/prevencao/checklists.json`: 1 checklist de retorno com 12 itens.

Todos `pendente_revisao`. Não houve commit, push, deploy, `published:true` ou atribuição de aprovação humana. Não comprova completude dos temas. Ancoragem de documentos/trilhas depende da integração concomitante da produção1.

## Lacunas reais no catálogo atual

Foram lidos os quatro documentos prévios e audit-prevencao.md. Foram varridos títulos/slugs dos três catálogos completos recebidos em round2-base. O acervo tem ampla cobertura de CVOTs, incluindo casos de estatina/ezetimiba/PCSK9, ApoB, Lp(a), HF, intolerância/nocebo, SGLT2 e finerenona; portanto não repetidos.

1. Caso básico: interpretação de primeiro lipidograma com TG 460 mg/dL sem jejum e LDL calculado por Friedewald; distingue conta aritmética, validade analítica e meta individual. Não é mais um caso de ApoB discordante.
2. Caso avançado: DM2/DRC confirmada e retorno após iSGLT2 com declínio inicial da TFGe de 20,7%, sem sinais de hipovolemia/doença aguda. Decisão operacional de continuidade e observação da tendência; não pergunta qual CVOT demonstra benefício.
3. Material: preparo ao retorno, exames comparáveis, uso real, acesso e dúvidas. Complementa materiais genéricos de colesterol/estatina já existentes.
4. Checklist: medir resposta/adesão/distância da meta e fechar continuidade. Complementa checklists de início de estatina e SAMS; não repete protocolo de reexposição.

## Fontes verificadas e limites

- AHA 2026, síntese oficial acessada, atualização de 13/03/2026: https://professional.heart.org/en/science-news/2026-guideline-on-the-management-of-dyslipidemia/top-things-to-know . ApoB, metas individualizadas e consideração conjunta do percentual de redução estão presentes. Não foram criados alvos SBC/ESC/AHA intercambiáveis.
- EAS/EFLM 2016: resumo dos próprios autores no periódico/instituição acessível por busca: https://academic.oup.com/clinchem/article-abstract/62/7/930/5611880 e https://research.regionh.dk/en/publications/fasting-is-not-routinely-required-for-determination-of-a-lipid-pr/ . Confirma coleta inicial sem jejum e consideração de repetição se TG >440 mg/dL. A versão EHJ citada usa DOI 10.1093/eurheartj/ehw152; o acesso direto desse DOI falhou. As versões são o mesmo consenso, não duas evidências independentes.
- ESC/EAS 2019, tabelas oficiais hospedadas pela EAS acessadas: https://eas-society.org/wp-content/uploads/2022/11/2019_dyslipidaemias_guidelin.pdf . Apoia intervalo 8 ±4 semanas e monitorização dirigida. Documento visual oficial, não alegação de leitura integral do artigo.
- KDIGO 2024, PDF oficial acessado: https://kdigo.org/wp-content/uploads/2024/03/KDIGO-2024-CKD-Guideline.pdf . Recomendação 3.7.1 (1A) e pontos de prática 3.7.2–3.7.3. A redução inicial reversível da TFGe geralmente não impõe retirada. O retorno de 1–2 semanas foi rotulado como decisão individualizada, não norma obrigatória universal.
- Sampson et al., DOI 10.1001/jamacardio.2020.0013, referência já identificada no documento prévio; mantida como fonte analítica. A busca não recuperou corpo integral e não se alega nova leitura. O limite de Friedewald também consta explicitamente do protocolo canônico da produção1. Sem introdução de novo resultado quantitativo do estudo.

ADA 2026 chegou a ser procurada para uma hipótese de caso alternativo, mas acesso direto falhou. Nenhuma recomendação nova dependente da leitura desse capítulo foi incluída. Nenhum PMID adivinhado incluído. Cenários, números, opções, aritmética e roteiro operacional são originais; sínteses das fontes são curtas, sem reprodução literal de tabelas/figuras. Revisão cruzada deve confirmar a abrangência editorial e a segurança.

## Tudo com Tudo — ancoragem e relações a integrar

| Recurso novo | Documento pai válido da produção1 | Recursos já existentes confirmados |
|---|---|---|
| primeiro-lipidograma-triglicerideos-altos-ldl-calculado-nao-interpretavel | lipidograma-na-consulta-primeira-leitura-discordancia-e-decisao-clinica | exame perfil-lipidico-colesterol-total-ldl-hdl-e-triglicerideos; material colesterol-alto-e-prevencao-cardiovascular; trilha-consulta-progressiva-dislipidemia (produção1) |
| dm2-drc-queda-inicial-tfge-apos-isglt2-retorno-com-seguranca | consulta-cardiometabolica-no-dm2-avaliacao-inicial-e-plano-longitudinal | medicamento empagliflozina; exame uacr-e-tfge-no-rastreio-de-doenca-renal-cronica-no-diabetes; checklist inicio-de-isglt2-em-cardiopata-diabetico-avaliacao-basal-e-monitorizacao; trilha-consulta-progressiva-diabetes-cardiovascular (produção1) |
| preparar-retorno-colesterol-exames-remedios-e-duvidas | retorno-da-dislipidemia-resposta-insuficiente-seguranca-e-intensificacao | material colesterol-alto-e-prevencao-cardiovascular; exame perfil-lipidico-colesterol-total-ldl-hdl-e-triglicerideos |
| retorno-dislipidemia-uso-real-resposta-meta-e-continuidade | retorno-da-dislipidemia-resposta-insuficiente-seguranca-e-intensificacao | checklist inicio-de-estatina-avaliacao-basal-e-monitorizacao-de-seguranca; checklist manejo-da-intolerancia-a-estatina-avaliacao-e-reexposicao; medicamentos atorvastatina-calcica e ezetimiba |

Material usa documento_slug e checklist usa documento_origem exatamente com os slugs pai. Casos incluem links Markdown dentro de explicacao, preservando schema. O integrador deve adicionar arestas inversas documento→caso/material/checklist e incorporar casos como etapas das trilhas existentes, sem recriar trilhas. Não inventados IDs de calculadoras; aritmética didática não foi cadastrada como ferramenta médica nova. Os hubs de doenças comuns precisam resolução pelo coordenador na origem canônica, pois não aparecem como entradas simples no catálogo especializado de doenças fornecido.

## Verificação local

- Chaves superiores idênticas às dos exemplos dos catálogos; listas JSON válidas.
- Slugs novos sem colisão literal em nenhum catálogo correspondente.
- Dois casos explicitamente fictícios, 4 alternativas, resposta base 0 e explicação de cada uma.
- Não-HDL-C 244 − 38 = 206 mg/dL; cálculo Friedewald resulta 114 mg/dL, mas é inadequado clinicamente com TG 460.
- Declínio de TFGe: (58 − 46)/58 × 100 = 20,6897%, apresentado como 20,7%.
- Medicamento empagliflozina e exames de perfil lipídico/UACR-TFGe confirmados no catálogo base.
- Doses e dados clínicos do caso avançado foram preenchidos para tornar a decisão avaliável; não há ajuste obrigatório a 25 mg, nem suspensão de terapia de proteção pelo simples alcance de HbA1c/LDL.
