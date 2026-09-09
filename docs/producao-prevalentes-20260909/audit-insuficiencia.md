# Auditoria e entrega — insuficiência cardíaca — 09/09/2026

Base: main 64796aa973316c94b47dcf8dc75a474415ecba34; documentos centrais lidos pelo GitHub fetch_file. Corpus anterior usado somente para identificar recursos; vínculos finais confrontados com current-paths.txt e metadados atuais base/.

## Entrega

Diretório: production/content/Insuficiência_cardíaca/.

Novos: ic-primeira-consulta-dispneia-confirmacao-e-etiologia.md; ic-terapia-fundacional-seguranca-renal-potassio-e-hipotensao.md; ic-transicao-pos-alta-plano-primeiras-seis-semanas.md.

Atualizados preservando slug/path: icfer-classificacao-diagnostico-quatro-pilares.md; icfep-diagnostico-e-terapias-avancadas-lvad-e-transplante.md.

## Lacunas reais e correções

- Básico original ainda afirmava que ESC 2026 não fora publicada; corrigido após localizar portal e slide set oficial, publicado 28/08/2026. Removido extenso desvio temporal de consenso 2026, sem afirmar que fosse inexistente. A nova versão guarda distinção entre nomenclatura atual e critérios de inclusão de ensaios históricos.
- Original generalizava mortalidade isolada dos quatro pilares e de EMPEROR-Reduced; corrigido para diferenças de desfecho/população. Também atribuía incorporação de iSGLT2 na ICFEr ao documento ESC 2023; corrigido.
- CDI original abrangia NYHA II–IV indistintamente: corrigido para II–III na prevenção primária usual, etiologia e classe/nível ESC 2026, intervalo pós-IAM e exclusão de IV refratária sem candidatura a terapia avançada.
- ICFEP original dizia que HFA-PEFF tinha maior utilidade que H2FPEF com referência inadequada: removido, citados estudos primários de cada ferramenta.
- ICFEP original misturava indicação ampla de LVAD com FEVE preservada: corrigido para encaminhamento individual e ausência de papel rotineiro do LVAD nessa síndrome.
- ICFEP atual incorpora iSGLT2/ARM na ESC 2026 e FINEARTS-HF, distinguindo razão de taxas de HR e desfecho composto de mortalidade isolada.
- Os novos textos fornecem raciocínio diagnóstico, segurança renal/K/PA e plano de transição. Casos e checklists são síntese operacional original, identificada como proposta adaptável; não são escores validados nem cronograma literal dos ensaios.

## Fontes primárias efetivamente abertas

- ESC 2026 portal: https://www.escardio.org/guidelines/clinical-practice-guidelines/all-esc-practice-guidelines/heart-failure/ — publicação 28/08/2026.
- ESC 2026 slide set: https://dam-assets.escardio.org/download/b2e587389baa11f185de06bdfb3e4be9 — 105 páginas. Verificados classificação p7, terapia p50–52, CDI p53–54, TRC p56. DOI 10.1093/eurheartj/ehag100 confirmado no material oficial. Texto completo OUP excedeu tamanho da ferramenta; o slide set resolveu a verificação específica. Sínteses breves, sem reprodução das tabelas/imagens.
- AHA/ACC/HFSA 2022 portal e slide set oficial: https://professional.heart.org/en/science-news/2022-guideline-for-the-management-of-heart-failure e https://professional.heart.org/en/science-news/-/media/832EA0F4E73948848612F228F7FA2D35.ashx — 211 páginas. ARM, doses e transição p74/87–89/154–155 conferidos.
- H2FPEF original PMID 29792299; HFA-PEFF PMID 31504452; estudo diagnóstico CPET PMID 29803552 — abertos no PubMed, não usados para alegar superioridade universal de escores.
- STRONG-HF PMID 36356631 — 15,2% vs 23,3%, RR0,66; EMPULSE PMID35228754 — N530 e desenho hierárquico; EMPEROR-Preserved PMID34449189 — 13,8% vs17,1%, HR0,79; FINEARTS-HF PMID39225278 — razão de taxas0,84 e ausência de significância para mortalidade CV isolada. Todos registros originais abertos.
- Entresto, informação oficial Novartis: https://www.novartis.com/us-en/sites/novartis_us/files/entresto.pdf — doses, washout, gestação, angioedema e função renal.
- Forxiga, informação oficial EMA: https://www.ema.europa.eu/en/documents/product-information/forxiga-epar-product-information_en.pdf — dose, DKA, volemia e interrupção em doença/cirurgia. Não alegada aprovação ou regra regulatória brasileira a partir de bula europeia.

## Tudo com Tudo para integração pelo coordenador

Slugs de doença atuais: insuficiencia-cardiaca (principal); insuficiencia-cardiaca-no-idoso quando aplicável. Não criar IDs por inferência.

Fármacos existentes: sacubitrilvalsartana, bisoprolol-hemifumarato, espironolactona, dapagliflozina, empagliflozina. São relações de tratamento contextual, não prescrição automática a todos os fenótipos.

Exames existentes: nt-probnp; monitorizacao-de-potassio-e-creatinina-apos-inicio-de-antagonista-mineralocorticoide-sobre-ieca-bra; potassio-serico-risco-arritmico-e-monitorizacao.

Calculadoras com documentos reais: escore-h2fpef-probabilidade-diagnostica-de-icfep-em-dispneia-inexplicada; escore-maggic-predicao-de-mortalidade-na-insuficiencia-cardiaca. Usar a resolução de IDs centrais do coordenador, não assumir que o slug documental equivale a ID do motor de cálculo.

Fluxos já vinculados: descompensação; encaminhamento IC avançada; doses quatro pilares; hipercalemia. Documento de comunicação teach-back na alta conectado à transição.

## Verificação e limites

Cinco documentos, YAML parseado, slugs mantidos/únicos no lote e todos links relativos conferidos com paths atuais ou novos arquivos do lote: zero links inexistentes no momento da entrega. Revisão científica desta frente é assistida por IA, explicitada no review_note, sem alegação de revisão humana independente. Não realizado commit/push, importação no banco ou deploy; coordenador integra e valida navegação/reciprocidade do grafo. Não alegada completude de toda a insuficiência cardíaca nem corrigidos todos os documentos históricos. Limites regulatórios brasileiros específicos e atualização integral das fichas de medicamentos permanecem no escopo das respectivas fontes/fichas.
