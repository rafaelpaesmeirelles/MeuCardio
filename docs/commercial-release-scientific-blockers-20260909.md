# Bloqueio científico da publicação comercial — 09/09/2026

**Conclusão:** não há evidência suficiente para atualizar automaticamente o manifesto integral de 11.581 para 12.160 itens. O pacote incremental autorizado de 09/09 fornece cobertura verificável para parte da diferença, mas não para todo o corpus atual. Esta verificação não realizou revisão clínica nem alterou conteúdo, publicação ou aprovações.

## Snapshot e ampliação posterior do deploy

Os números deste relatório correspondem ao snapshot comercial `366946de`, anterior à integração do PR #915. **12.160 não é o total final da release ampliada.** A root informou autorização explícita posterior para incluir o PR #915 (`d7f51132`) e o patch da rodada 2; esse lote está sendo preparado separadamente. Seu handoff, conforme informado pela coordenação, também distingue revisão assistida por IA de revisão humana e orienta não fabricar aprovação geral. Este relatório não contou nem validou os itens adicionais do PR #915; eles exigem reconciliação própria no snapshot final.

## Evidências e escopo

- Manifesto integral: `editorial-approvals/full-corpus-release-20260907.json`, última alteração em `fedf818cbb248869a20f2db2949e8fe9884f90c7`. Declara expressamente escopo restrito aos mesmos 11.581 itens, excluindo os PRs pendentes do Grok e determinados alvos fora do repositório.
- `backend/app/services/corpus_release_authorization.py` exige identidade de contagens, slugs, hashes das fontes e status revisado de todos os itens. O bloqueio de 11.581 versus 12.160 é correto; mudar somente contagem/hash não resolve o requisito editorial.
- Pacote incremental em `releases/scientific-20260909/reviewed-content.json`: 697 fontes e 716 registros, com autorização expressa do proprietário registrada no campo `authorization`. SHA-256 conferido: `9c5a671b37558f3bb71ac338d9069845ccc95c373f25bf22a4d474f71a9c92c9`.
- `docs/MANIFESTO_CONTEUDO_REVISADO_2026-09-09.json`, `releases/scientific-20260909/review-ledger.json` e README registram revisão editorial/bibliográfica assistida por Codex, explicitamente **sem assinatura de revisão médica humana**. Essa distinção não invalida a autorização de publicação daquele pacote, mas impede atribuir uma revisão humana que não está registrada.
- O pacote foi incorporado em `d154f6ae6bc546e9545891e81290624d9e4fe4f7`; a publicação limitada e a exclusão da produção posterior do Work estão registradas em `1c8454d132bfc6ecedec802c731dbb26b4d1e6da` e `releases/scientific-20260909/deployment-result.json`.

## Reconciliação documental, sem dupla contagem

Comparação do último manifesto integral com a árvore comercial atual, somente em `content/`:

| Conjunto | Arquivos |
|---|---:|
| Adições desde o manifesto | 579 |
| Modificações de arquivos já existentes | 22 |
| Total de caminhos diferentes | 601 |
| Cobertos por caminho no source_inventory incremental | 547 |
| Com hash integral exatamente igual ao inventário | 547 |
| Sem cobertura de caminho nesse inventário | 54 |
| Marcados pendente_revisao entre os 601 | 9 |
| Pendentes que também pertencem aos 54 sem cobertura | 7 |
| Pendentes cobertos documentalmente, mas excluídos como duplicatas | 2 |
| União dos 54 sem cobertura com os 9 pendentes | 56 |

Os 54 sem cobertura têm metadados: 7 pendente_revisao, 47 revisado. Flags isoladas não comprovam aprovação editorial vinculada ao pacote. “Sem cobertura” significa ausência no inventário incremental examinado, não prova de ausência de qualquer revisão histórica.

As duas pendências cobertas pelo inventário são consolidações intencionais em `merged_duplicates`: pirtobrutinibe BRUIN CLL-314 e a metanálise tirzepatida/semaglutida. O pacote determina preservar os originais e **não republicar as duplicatas**. Uma aprovação integral dos 12.160 que promovesse todos os slugs contrariaria essa instrução.

## Nove fontes com status pendente_revisao

| Caminho | Cobertura do pacote |
|---|---|
| `content/Cardio-oncologia/cardiotoxicidade-do-osimertinibe-insuficiencia-cardiaca-e-eixo-gata4-mylk3.md` | Sem cobertura por caminho |
| `content/Cardio-oncologia/pirtobrutinibe-btk-nao-covalente-versus-ibrutinibe-o-ensaio-bruin-cll-314.md` | Inventariado; duplicata explicitamente não republicável |
| `content/Cardio-oncologia/radioterapia-da-mama-dose-a-descendente-anterior-versus-dose-media-ao-coracao.md` | Sem cobertura por caminho |
| `content/Comunicação_clínica/decisao-compartilhada-entre-tavi-e-troca-cirurgica-da-valva-aortica-o-estudo-impact-sdm.md` | Sem cobertura por caminho |
| `content/Hipertensão/tirzepatida-e-semaglutida-efeito-sobre-a-pressao-arterial-metanalise-de-32-ensaios.md` | Inventariado; duplicata explicitamente não republicável |
| `content/Hipertensão_pulmonar/denervacao-da-arteria-pulmonar-na-hipertensao-pulmonar-do-grupo-2-ensaio-padn-hf-ph.md` | Sem cobertura por caminho |
| `content/Hipertensão_pulmonar/hipertensao-pulmonar-persistente-do-recem-nascido-metanalise-em-rede-terapias-2024.md` | Sem cobertura por caminho |
| `content/Hipertensão_pulmonar/imatinibe-inalado-av-101-hap-impahct-fase-2b-negativo.md` | Sem cobertura por caminho |
| `content/Saúde_mental_e_cardiologia/psicopatologia-pos-traumatica-e-risco-cardiovascular-coorte-caso-controle-dinamarquesa-de-sumner-2026.md` | Sem cobertura por caminho |

## Cinquenta e quatro caminhos sem cobertura no inventário incremental

Último commit que alterou cada arquivo apresentado para rastreabilidade, sem inferir aprovação a partir da autoria ou do título do commit.

| Caminho | Alteração | Status atual | Último commit |
|---|---|---|---|
| `content/Arritmias/cpvt-quando-dispensar-o-betabloqueador-e-quando-dispensar-o-cdi-registro-internacional-e-lcsd.md` | Adição | `revisado` | `7119c967` |
| `content/Arritmias/etripamil-nasal-para-reversao-da-taquicardia-supraventricular-paroxistica-rapid-e-node-303.md` | Adição | `revisado` | `30522288` |
| `content/Arritmias/fibrilacao-ventricular-mediada-por-purkinje-ablacao-de-gatilho-versus-substrato.md` | Adição | `revisado` | `c1bf9b21` |
| `content/Arritmias/mtmr4-gene-modificador-na-sindrome-do-qt-longo-efeito-oposto-em-lqt1-e-lqt2.md` | Adição | `revisado` | `4310d881` |
| `content/Arritmias/risco-nao-modificavel-na-sindrome-de-brugada-sexo-mutacao-scn5a-e-escore-poligenico.md` | Adição | `revisado` | `50e7b9a0` |
| `content/Calculadoras/cadillac-risk-score-predicao-de-mortalidade-apos-angioplastia-primaria-no-iam.md` | Adição | `revisado` | `68f82eb9` |
| `content/Calculadoras/escore-iabp-shock-ii-estratificacao-de-risco-de-mortalidade-no-choque-cardiogenico-pos-iam.md` | Adição | `revisado` | `2b544ac9` |
| `content/Calculadoras/escore-ncdr-cathpci-predicao-de-mortalidade-apos-intervencao-coronaria-percutanea.md` | Adição | `revisado` | `cb750689` |
| `content/Calculadoras/qrisk3-risco-cardiovascular-em-10-anos-derivacao-e-validacao-na-coorte-qresearch.md` | Adição | `revisado` | `ba40c897` |
| `content/Cardio-oncologia/cardiotoxicidade-do-osimertinibe-insuficiencia-cardiaca-e-eixo-gata4-mylk3.md` | Adição | `pendente_revisao` | `7b016939` |
| `content/Cardio-oncologia/empagliflozina-como-cardioprotecao-primaria-contra-antraciclina-modelo-suino-jacc-cardiooncology-2025.md` | Adição | `revisado` | `d9fad7e1` |
| `content/Cardio-oncologia/radioterapia-da-mama-dose-a-descendente-anterior-versus-dose-media-ao-coracao.md` | Adição | `pendente_revisao` | `e0f5c5e7` |
| `content/Comunicação_clínica/decisao-compartilhada-entre-tavi-e-troca-cirurgica-da-valva-aortica-o-estudo-impact-sdm.md` | Adição | `pendente_revisao` | `48097436` |
| `content/Comunicação_clínica/ferramenta-de-comunicacao-de-risco-cardiovascular-your-heart-forecast-o-ensaio-dany.md` | Adição | `revisado` | `790127e9` |
| `content/Comunicação_clínica/ia-generativa-para-rascunho-de-respostas-a-mensagens-do-portal-do-paciente.md` | Adição | `revisado` | `57e785d5` |
| `content/Diabetes_e_cardiologia/finerenona-reduz-fibrilacao-atrial-de-novo-no-espectro-cardio-renal-metabolico-fine-heart.md` | Adição | `revisado` | `4747075f` |
| `content/Diabetes_e_cardiologia/retatrutida-agonista-triplo-gip-glp-1-glucagon-e-risco-cardiovascular-transcend-t2d-1.md` | Adição | `revisado` | `56c42ef2` |
| `content/Dispositivos/carga-de-fibrilacao-atrial-detectada-por-cied-apos-inicio-de-antiarritmico-uma-analise-multicentrica.md` | Adição | `revisado` | `5313f182` |
| `content/Dispositivos/inicio-espontaneo-de-taquiarritmia-ventricular-na-sindrome-de-brugada-o-registro-start-brs.md` | Adição | `revisado` | `32070469` |
| `content/Dispositivos/sensor-implantavel-de-veia-cava-inferior-para-monitorizacao-de-congestao-o-programa-future-hf.md` | Adição | `revisado` | `ce20f1a0` |
| `content/Dispositivos/sistema-modular-marca-passo-sem-eletrodo-e-cdi-subcutaneo-em-comunicacao-sem-fio-o-ensaio-modular-atp.md` | Adição | `revisado` | `2563db38` |
| `content/Farmacologia/milvexian-sca-ensaio-librexia-acs-interrompido-por-futilidade.md` | Adição | `revisado` | `03184545` |
| `content/Farmacologia/vutrisiran.md` | Adição | `revisado` | `5619c5ed` |
| `content/Fibrilação_atrial/closure-af-oclusao-do-apendice-atrial-esquerdo-versus-terapia-medica-em-alto-risco.md` | Adição | `revisado` | `eb924f78` |
| `content/Fibrilação_atrial/perda-de-peso-no-idoso-com-fibrilacao-atrial-persistente-o-ensaio-lose-af.md` | Adição | `revisado` | `30973763` |
| `content/Fibrilação_atrial/timing-de-doac-apos-avc-por-fibrilacao-atrial-optimas-e-a-metanalise-catalyst.md` | Adição | `revisado` | `83be5e8d` |
| `content/Geral/exposicao-a-luz-artificial-a-noite-e-incidencia-de-doenca-cardiovascular-uk-biobank.md` | Adição | `revisado` | `ada914cd` |
| `content/Geral/exposicao-a-pfas-quimicos-eternos-e-incidencia-de-doenca-cardiovascular-o-estudo-dppos.md` | Adição | `revisado` | `ce9a09fb` |
| `content/Geral/regularidade-do-sono-e-eventos-cardiovasculares-maiores-indice-sri-no-uk-biobank.md` | Adição | `revisado` | `e5df24e9` |
| `content/Gravidez/doenca-arterial-periferica-apos-desfechos-gestacionais-adversos-coorte-sueca-de-coirmas-2026.md` | Adição | `revisado` | `fa7890c5` |
| `content/Gravidez/hipertensao-na-gestacao-e-risco-de-demencia-o-million-women-study-2025.md` | Adição | `revisado` | `5d71130a` |
| `content/Hipertensão/denervacao-renal-por-radiofrequencia-aos-3-anos-seguimento-final-do-spyral-htn-on-med.md` | Adição | `revisado` | `89fa31f3` |
| `content/Hipertensão/labetalol-versus-nifedipina-na-hipertensao-pos-parto-risco-de-reinternacao.md` | Adição | `revisado` | `d7e32fa3` |
| `content/Hipertensão/vicadrostat-terceiro-inibidor-da-aldosterona-sintase-da-drc-a-hipertensao.md` | Adição | `revisado` | `0d93a736` |
| `content/Hipertensão_pulmonar/denervacao-da-arteria-pulmonar-na-hipertensao-pulmonar-do-grupo-2-ensaio-padn-hf-ph.md` | Adição | `pendente_revisao` | `093cc5a7` |
| `content/Hipertensão_pulmonar/hipertensao-pulmonar-persistente-do-recem-nascido-metanalise-em-rede-terapias-2024.md` | Adição | `pendente_revisao` | `c54fe203` |
| `content/Hipertensão_pulmonar/imatinibe-inalado-av-101-hap-impahct-fase-2b-negativo.md` | Adição | `pendente_revisao` | `1c6505b4` |
| `content/Hipertensão_pulmonar/selexipague-na-cteph-inoperavel-ou-persistente-recorrente-o-ensaio-select.md` | Adição | `revisado` | `8eebd53c` |
| `content/Insuficiência_cardíaca/dapagliflozina-pos-infarto-agudo-do-miocardio-sem-diabetes-ou-ic-o-ensaio-dapa-mi.md` | Adição | `revisado` | `5e802357` |
| `content/Insuficiência_cardíaca/ferro-endovenoso-na-icfer-pos-ironman-definicao-de-deficiencia-e-adjudicacao-de-causas-2024.md` | Adição | `revisado` | `e1486b15` |
| `content/Insuficiência_cardíaca/terapia-de-ativacao-barorreflexa-barostim-na-icfer-beat-hf-e-o-ensaio-confirmatorio-benefit-hf.md` | Adição | `revisado` | `bf585e6c` |
| `content/Prevenção_e_lipídios/corcal-outcomes-escore-de-calcio-versus-pooled-cohort-equation-para-guiar-estatina-em-prevencao-primaria.md` | Adição | `revisado` | `8cce106f` |
| `content/Prevenção_e_lipídios/inclisirana-como-primeira-linha-o-programa-victorion-mono-e-initiate.md` | Adição | `revisado` | `cac00002` |
| `content/Prevenção_e_lipídios/lepodisiran-e-fosfolipidios-oxidados-na-lipoproteina-a-analise-post-hoc-do-ensaio-alpaca.md` | Adição | `revisado` | `8dca7df7` |
| `content/Prevenção_e_lipídios/lipoproteina-a-horizon-pelacarsena-nao-atingiu-desfecho-primario-de-mace-topline-2026.md` | Adição | `revisado` | `fb9e1ae2` |
| `content/Prevenção_e_lipídios/orion-4-hps-4-timi-65-o-desenho-do-primeiro-ensaio-de-desfecho-cardiovascular-com-inclisirana.md` | Adição | `revisado` | `e522ad35` |
| `content/Saúde_mental_e_cardiologia/isolamento-social-solidao-e-risco-de-doenca-cardiovascular-incidente-metanalise-de-wang-2025.md` | Adição | `revisado` | `66b4ea81` |
| `content/Saúde_mental_e_cardiologia/psicopatologia-pos-traumatica-e-risco-cardiovascular-coorte-caso-controle-dinamarquesa-de-sumner-2026.md` | Adição | `pendente_revisao` | `597442e6` |
| `content/Terapia_intensiva/angiotensina-ii-guiada-por-renina-na-vasoplegia-pos-cirurgia-cardiaca-o-estudo-piloto-de-munster.md` | Adição | `revisado` | `45765281` |
| `content/Terapia_intensiva/hemoadsorcao-cardiopulmonar-em-cirurgia-cardiaca-para-endocardite-infecciosa-o-ensaio-remove.md` | Adição | `revisado` | `ec5dc119` |
| `content/Terapia_intensiva/transporte-intra-parada-precoce-versus-rcp-prolongada-na-cena-para-parada-refrataria-o-ensaio-evidence.md` | Adição | `revisado` | `2bd4e0a1` |
| `content/Tromboembolismo/roxi-vte-i-e-ii-anticorpos-anti-fator-xi-na-profilaxia-de-tev-pos-artroplastia-de-joelho.md` | Adição | `revisado` | `529f051f` |
| `content/Tromboembolismo/tep-subsegmentar-isolado-anticoagular-ou-vigiar-stopape-e-metanalise-2026.md` | Adição | `revisado` | `55a704c3` |
| `content/Tromboembolismo/tromboprofilaxia-farmacologica-pos-cesarea-a-lacuna-de-evidencia-randomizada-e-os-ensaios-piloto.md` | Adição | `revisado` | `57edda40` |

## Encaminhamento

A evidência existente permite reconhecer o pacote incremental autorizado, preservando suas exclusões e destinos canônicos. Não autoriza ampliar automaticamente a aprovação integral para todos os itens atuais. Para liberar uma publicação científica integral, é necessário reconciliar os itens fora do pacote e as exclusões, concluir a revisão efetivamente necessária e registrar aprovação editorial/clinicamente responsável para o inventário exato resultante. A autorização de implantar planos comerciais não substitui essa decisão científica.

Uma publicação apenas de aplicação deve preservar o conteúdo já publicado e respeitar os gates existentes; este relatório não autoriza desativá-los, modificar manifestos, promover pendências ou simular revisão.
