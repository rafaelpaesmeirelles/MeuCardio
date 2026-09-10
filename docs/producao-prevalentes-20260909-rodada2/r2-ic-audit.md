# Rodada 2 — IC — 09/09/2026

Entrega: duas vinhetas fictícias (básico e avançado), um material ao paciente e um checklist com nove itens. Arquivos em `round2/ic/`. Todos `pendente_revisao`, sem `published:true`, commit, push, importação ou alegação de revisão humana. Schema confrontado com os três catálogos desta rodada: chaves exatas, quatro alternativas, resposta em índice base zero, explicação de A–D, slugs novos, IDs de checklist inéditos e categorias existentes.

## Lacunas verificadas antes de escrever

Foram lidos os cinco documentos de IC de `production/content/Insuficiência_cardíaca`, a auditoria anterior e os catálogos atuais dos três tipos.

- O acervo já possui TRED-HF como caso de retirada global, casos STRONG-HF/EMPULSE, iSGLT2/ICFEp, cardiorrenal com congestão e três roteiros de titulação. Nenhum foi duplicado.
- Caso básico novo: decisão prática de **não iniciar** ARM com K 5,2, distinguindo limite inicial do limite de manutenção; causa corrigível e responsabilidade pelo controle.
- Caso avançado novo: **ICFEp no primeiro retorno após a alta**, com depleção volêmica, hipotensão sintomática e creatinina ascendente; não confundir perda excessiva de volume com congestão persistente nem banalizar a alteração renal como efeito esperado.
- Material novo: consulta após **melhora da FEVE**, orientação prática sobre continuidade, efeitos adversos e preparação do retorno. O material existente sobre fração de ejeção explica a medida, e o de alta trata principalmente teach-back; faltava o foco específico na continuidade após recuperação.
- Checklist novo: retorno longitudinal com FEVE melhorada. Complementa os roteiros de início/titulação; não repete o checklist de alta.

## Fontes efetivamente verificadas

- [AHA/ACC/HFSA 2022, slides oficiais](https://professional.heart.org/en/science-news/-/media/832EA0F4E73948848612F228F7FA2D35.ashx): ARM p74 (K <5,0 e TFGe >30 para início; limite de manutenção) e FEVE melhorada p109 (manutenção, I B-R). Síntese breve, sem copiar tabelas.
- [Aldactone, bula oficial Pfizer](https://labeling.pfizer.com/ShowLabeling.aspx?id=520), revisão 11/2025: contraindicação por hipercalemia, substituto de sal contendo K e controle em até uma semana após início/titulação.
- [Forxiga, EMA](https://www.ema.europa.eu/en/documents/product-information/forxiga-epar-product-information_en.pdf): seções 4.4/4.5, suspensão temporária na depleção, interações com diuréticos; não alegada equivalência regulatória brasileira.
- [TRED-HF, publicação original](https://pubmed.ncbi.nlm.nih.gov/30429050/), também texto completo PMC6319251: recaída após retirada em cardiomiopatia dilatada recuperada; população limitada, sem generalizar risco numérico para toda IC.
- [EMPULSE, publicação original](https://pubmed.ncbi.nlm.nih.gov/35228754/): pacientes estabilizados, FEVE e diabetes não restringiam a população; desfecho hierárquico, sem alegar mortalidade isolada ou equivalência dapagliflozina/empagliflozina.
- [AHA, sinais de IC](https://www.heart.org/en/health-topics/heart-failure/warning-signs-of-heart-failure): orientação de alarme no material ao paciente.

ESC 2026 foi previamente verificada pela coordenação e está incorporada ao documento canônico. A tentativa de reabrir os slides nesta rodada retornou erro; nenhuma nova classe/nível foi atribuída à ESC 2026 nos quatro derivados. Mantida a distinção entre mudança de nomenclatura e populações dos ensaios. DELIVER/STRONG-HF não foram usados para uma alegação nova de eficácia nesta entrega, pois seus registros retornaram sem texto na tentativa atual. Evitou-se copiar recomendações ou resultados não verificados.

## Segurança clínica e limites

Os enunciados são originais e não correspondem a pacientes reais. O básico fornece PA, FC, FEVE, K confirmado, TFGe, estabilidade, ausência de ARM/IECA concomitante e exposição ao K; repetir exame em 48–72h é uma proposta clínica específica da vinheta, não prazo universal. Não recomenda tratar automaticamente com quelante.

No avançado, a perda de peso é adicional **após alta sem congestão**; exames e sintomas sustentam depleção e LRA. TFGe numérica está identificada como calculada durante creatinina em mudança, sem ser tomada como função renal estável. A prioridade é atendimento no mesmo dia, com emergência se instabilidade persistir; nenhuma reposição fixa de volume ou suspensão permanente indiscriminada foi prescrita. O caso exige plano de reintrodução após estabilização. O EMPULSE é citado somente para a distinção entre paciente estabilizado elegível e episódio atual de instabilidade; não serve como ensaio de dapagliflozina.

O checklist é síntese operacional; `origem_secao` usa cabeçalhos reais do documento canônico, mas os itens não são transcrição literal. Não é instrumento validado. A manutenção após melhora não implica proibir ajustes por contraindicação ou intolerância. As fontes não foram apresentadas como revisão humana.

## Tudo com Tudo — integração solicitada à coordenação

Slugs de documentos existentes desta produção: `icfer-classificacao-diagnostico-quatro-pilares`, `ic-terapia-fundacional-seguranca-renal-potassio-e-hipotensao`, `ic-transicao-pos-alta-plano-primeiras-seis-semanas`, `icfep-diagnostico-e-terapias-avancadas-lvad-e-transplante`, `ic-primeira-consulta-dispneia-confirmacao-e-etiologia`.

| Novo recurso | Documentos prioritários para relação recíproca |
|---|---|
| `icfer-primeiro-retorno-potassio-52-antes-de-iniciar-espironolactona` | segurança renal/K; transição pós-alta; classificação/quatro pilares |
| `icfep-pos-alta-perda-de-peso-ortostatismo-e-lesao-renal-reavaliar-volemia` | ICFEp; segurança renal/K; transição pós-alta |
| `meu-coracao-melhorou-posso-parar-os-remedios-da-insuficiencia-cardiaca` | classificação/quatro pilares; segurança renal/K |
| `retorno-com-feve-melhorada-preservar-tratamento-e-reavaliar-tolerancia` | classificação/quatro pilares; segurança renal/K; transição pós-alta |

Os campos `documento_slug`/`documento_origem` apontam para o documento anterior real `icfer-classificacao-diagnostico-quatro-pilares`.

Doenças confirmadas no catálogo `base/doencas`: `insuficiencia-cardiaca`, `insuficiencia-cardiaca-no-idoso`.

Fármacos confirmados em `base/medicamentos`: `espironolactona`, `dapagliflozina`. Não inferir `furosemida` como slug de ficha a partir do nome; `furosemida-cloreto-de-potassio` é outro produto e **não deve ser vinculado como equivalente**. A presença de losartana e bisoprolol na vinheta não dispensa resolução pelo catálogo central.

Exames confirmados em `base/exames`: `monitorizacao-de-potassio-e-creatinina-apos-inicio-de-antagonista-mineralocorticoide-sobre-ieca-bra`, `potassio-serico-risco-arritmico-e-monitorizacao`. Relacionar ao caso básico e à segurança; não criar slug genérico de potássio/creatinina.

Documento histórico confirmado em `round2-paths.txt`: `fluxograma-icfer-com-fracao-de-ejecao-melhorada-manter-ou-retirar-a-terapia-tred-hf`, pertinente ao material e checklist. Caso histórico já existente: `cardiomiopatia-dilatada-recuperada-suspender-medicacao-de-ic-tred-hf`, pertinente para aprofundamento. Checklist histórico: `titulacao-sequenciada-da-terapia-quadrupla-conforme-barreira-de-seguranca-na-icfer`, pertinente como etapa anterior. Trilha da produção anterior: `trilha-consulta-progressiva-insuficiencia-cardiaca`; coordenação deve incorporar os quatro derivados nos pontos correspondentes e conferir reciprocidade.

Nenhuma alegação de completude integral da IC nem de navegação no site verificada. A incorporação ao grafo e a revisão cruzada estão com a coordenação.
