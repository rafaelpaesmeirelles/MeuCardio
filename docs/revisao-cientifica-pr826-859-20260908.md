# Revisão científica focal dos PRs 826–859 — 08/09/2026

Base de integração: c37de49b25446449b57cb5ecf7cdfad56cb1cf29 (origin/main). Worktree isolado, sem alteração do checkout de produção. 34 PRs auditados; 88 documentos preservados, 2 fragmentos (RC novo e vínculo cardiorrenal existente) e 1 dependência geriátrica corrigida. #830 e #854 excluídos como duplicatas editoriais.
# Escopo e evidência

Comentários, reviews inline e timeline completos foram obtidos com paginação. O ledger JSON acompanhante conserva texto, IDs, arquivos e SHA remoto por PR. Merged826/828/833 significa merge na release de emergência, não presença em main; seus conteúdos foram comparados/importados seletivamente. Comentário827 que cita SHA de828 não prova correção827. Relatos de commits locais sem remote/push não foram aceitos como código publicado; os fixes foram reconstruídos no HEAD efetivamente disponível.

A revisão foi contextual por documento e mecanismo, não promoção por correspondência lexical nem aprovação de full-corpus. Os63PMIDs usados nas referências deste escopo resolveram via E-utilities com títulos e DOIs reconciliados. Metadados bibliográficos foram normalizados a partir do registro principal PubMed, sem confundir DOIs de referências citadas com DOI do artigo. Fontes sem PMID foram verificadas em páginas primárias/DOI, incluindo KDIGO2024, ESC2026RC/IC/DRC, AHRQ, NIMH e documentos contemporâneos específicos. Identidade bibliográfica não foi tratada como prova de toda afirmação clínica.

Foram consultados textos/quadros primários ESC, AHA/ACC, KDIGO, ADA2026, IWGDF/IDSA2023, EHRA2024 e artigos originais. A correção valvar ezag193 foi lida: remove duplicação de texto em lacuna de evidência, sem mudança terapêutica. A existência do erratum Bauer42013187 foi confirmada, mas sua íntegra não estava acessível; por isso magnitudes dependentes foram removidas conservadoramente do documento geriátrico e do hub, sem alegar erratum lido.
# Decisões por PR

## #826 — reviewed_scoped_integration
HEAD remoto: `250edcb06e2e0ae5879667b52d1c1d92709552a8`. Base: `release/grok-content-emergency-20260908`. TOD preservado com critérios ESC; terapias separadas por DM2/ASCVD/IC/DRC; rastreio de FA alinhado à ESC 2024.

- `content/Diabetes_e_cardiologia/lesao-de-orgao-alvo-e-muito-alto-risco-cv-no-diabetes-esc-2023.md`
- `content/Diabetes_e_cardiologia/rastreamento-de-insuficiencia-cardiaca-e-fibrilacao-atrial-no-diabetes-esc-2023.md`

## #827 — reviewed_scoped_integration
HEAD remoto: `66c562b4a2e8afe36b605106637f4dcf0314e559`. Base: `main`. CKD modifica indicação e dose; Cockcroft–Gault; OAC pré-ablação no risco elevado e pelo menos dois meses pós-ablação; exclusão cirúrgica/percutânea distintas.

- `content/Fibrilação_atrial/fa-e-drc-anticoagulacao-enquadramento-de-ajuste-sem-doses-esc-2024.md`
- `content/Fibrilação_atrial/fa-pos-ablacao-principios-de-anticoagulacao-de-retorno-esc-2024.md`

## #828 — reviewed_scoped_integration
HEAD remoto: `f035a5396f54e33c5ce7331648adef25e5354d77`. Base: `release/grok-content-emergency-20260908`. PA confirmada persistente no ramo ambulatorial; obstetrícia PAS160 OU PAD110; busca de lesão aguda/fundoscopia; tratamento gradual e acesso real.

- `content/Hipertensão/fluxograma-sinais-de-alarme-ambulatoriais-hipertensao.md`
- `content/Hipertensão/pa-muito-elevada-no-consultorio-sem-lesao-aguda-conduta-ambulatorial.md`
- `content/Hipertensão/sinais-de-alarme-ambulatoriais-na-hipertensao-quando-encaminhar.md`

## #829 — reviewed_scoped_integration
HEAD remoto: `1653c3da307984373e4696ad8a59b91fa26bd2d8`. Base: `main`. Causa-G-A/persistência da DRC; albuminúria contextual; contraste associado não automaticamente causal; hidratação/congestão e hiperK com sinais de urgência; quelantes não prometem mortalidade.

- `content/Cardiorrenal/albuminuria-e-tfge-como-eixo-transversal-de-risco-cardiovascular.md`
- `content/Cardiorrenal/contraste-e-peri-procedimento-na-drc-principios-de-seguranca.md`
- `content/Cardiorrenal/hiperpotassemia-e-farmacos-prognosticos-na-ic-com-drc-seguranca-sem-abandonar-beneficio.md`

## #830 — duplicate_excluded
HEAD remoto: `b43162afcd9a46279c63e35a5e631bd91dc0d185`. Base: `main`. Duplicata editorial encerrada; #831 é a fonte única. Nenhum arquivo clínico importado deste PR.


## #831 — reviewed_scoped_integration
HEAD remoto: `069799203dc6303d515e5e57f3c34c1753b4643a`. Base: `main`. Contraindicações e perguntas obrigatórias; risco alto não inicia exclusivamente remoto; encaminhamento apenas antes de início/fase I; material do paciente; benefício por desenho e população; dependência geriátrica corrigida.

- `content/Reabilitação_cardíaca/estratificacao-de-risco-para-exercicio-na-reabilitacao-cardiaca.md`
- `content/Reabilitação_cardíaca/indicacoes-contraindicacoes-e-fases-da-reabilitacao-cardiaca.md`

## #832 — reviewed_scoped_integration
HEAD remoto: `0ae5b47658f33d981f4f060fdde37b1dbc7b9163`. Base: `main`. Teach-back como associação no estudo observacional; números originais conferidos; falha persistente exige nova estratégia e avaliação de alta segura; AHRQ.

- `content/Comunicação_clínica/fechamento-do-loop-letramento-limitado-e-teach-back-schillinger.md`
- `content/Comunicação_clínica/protocolo-operacional-teach-back-na-alta-cardiologica.md`

## #833 — reviewed_scoped_integration
HEAD remoto: `afaf526e8b9f005d8f5c24086841fbe20788e66e`. Base: `release/grok-content-emergency-20260908`. Preservadas correções remotas afaf526: ALI não exige seis Ps; CLTI não espera duas semanas para avaliar; AAA sintomático estável exige avaliação hospitalar urgente. ESC e ESVS corretas.

- `content/Aorta_e_doença_arterial_periférica/fluxograma-ambulatorial-dap-quando-encaminhar-urgencia-versus-vascular.md`
- `content/Aorta_e_doença_arterial_periférica/sinalizadores-ambulatoriais-de-aneurisma-de-aorta-abdominal-ameaca-de-rotura.md`
- `content/Aorta_e_doença_arterial_periférica/sinalizadores-ambulatoriais-de-isquemia-critica-ameacadora-de-membro-clti.md`

## #834 — reviewed_scoped_integration
HEAD remoto: `383365ac1545d9d925372fff36a87180c78d5e3c`. Base: `main`. ICI suspenso e avaliação hospitalar; sobreposição neuromuscular e TnI/TnT; CMR inicial negativa não exclui; vigilância antracíclica pelo risco; HER2 por CTRCD e equipe.

- `content/Cardio-oncologia/fluxograma-suspeita-miocardite-por-inibidor-de-checkpoint-ambulatorial.md`
- `content/Cardio-oncologia/sinalizadores-ambulatoriais-de-cardiotoxicidade-tardia-pos-antraciclina.md`
- `content/Cardio-oncologia/vigilancia-ambulatorial-pos-trastuzumabe-quando-escalar-imagem-e-biomarcador.md`

## #835 — reviewed_scoped_integration
HEAD remoto: `256e286c761679c7762a9099c400b7ce170524e6`. Base: `main`. Ruído de eletrodo mesmo com impedância normal; choque com síncope/TV sustentada emergência; tempestade elétrica não igual a dois choques; interrogação acionável.

- `content/Dispositivos/choque-do-cdi-no-ambulatorio-triagem-apropriado-versus-inapropriado-primeira-consulta.md`
- `content/Dispositivos/fluxograma-pos-choque-cdi-ambulatorial-destino.md`
- `content/Dispositivos/sinalizadores-ambulatoriais-de-disfuncao-de-eletrodo-quando-encaminhar.md`

## #836 — reviewed_scoped_integration
HEAD remoto: `b6d5d44b72be551c2730065c888ddb248fe01313`. Base: `main`. Risco cirúrgico antes de exames; teste só se risco e impacto na decisão; PCI/angioplastia sem stent e AVC/TIA com tempos próprios; fragilidade não cancela automaticamente.

- `content/Perioperatório/fluxograma-ambulatorial-risco-cardiovascular-preoperatorio-quando-escalar.md`
- `content/Perioperatório/sinalizadores-ambulatoriais-para-adiar-cirurgia-eletiva-nao-cardiaca.md`
- `content/Perioperatório/stent-coronario-recente-e-cirurgia-eletiva-janela-de-risco-ambulatorial.md`

## #837 — reviewed_scoped_integration
HEAD remoto: `8d46d9b52e3fbda6d65353a8cb022d09c3b2f87f`. Base: `main`. Seguimento PE 2026 e correção identificada; sintomas por gravidade, sangramento relevante e acesso à anticoagulação; recorrência não presumida.

- `content/Tromboembolismo/sinalizadores-ambulatoriais-pos-tep-quando-reencaminhar-urgencia.md`

## #838 — reviewed_scoped_integration
HEAD remoto: `2dbec90001ddc947ce5a9da70f56d47ddde90bd2`. Base: `main`. Monitorização amiodarona por tabela24 ACC2023; sem RX/PFR/oftalmo anual universal; interação com digoxina e meia-vida; coleta digoxina no tempo adequado e K/Mg.

- `content/Farmacologia/fluxograma-monitoramento-amiodarona-ambulatorial.md`
- `content/Farmacologia/monitoramento-ambulatorial-da-amiodarona-tireoide-figado-pulmao-e-olho.md`
- `content/Farmacologia/sinalizadores-ambulatoriais-de-toxicidade-da-digoxina.md`

## #839 — reviewed_scoped_integration
HEAD remoto: `e7397c8bddeaa601ecf794acc1c4a56b60603c05`. Base: `main`. TVNS: urgência por quadro agudo; cardiopatia estável não PS automático; substrato, CMR e esforço; idiopática requer avaliação.

- `content/Arritmias/sinalizadores-ambulatoriais-de-taquicardia-ventricular-nao-sustentada-quando-escalar.md`

## #840 — reviewed_scoped_integration
HEAD remoto: `8a8f0622f798a0600f2f0f113064df13fb3e8fb0`. Base: `main`. ESC/EACTS2025 substitui2021; corrigendum ezag193 lido; EA sintomática estável/angina não PS automático; intervenção precoce assintomática selecionada; IM por mecanismo.

- `content/Valvopatias/fluxograma-ambulatorial-valvopatia-quando-escalar-para-heart-team.md`
- `content/Valvopatias/sinalizadores-ambulatoriais-de-estenose-aortica-sintomatica-quando-encaminhar.md`
- `content/Valvopatias/sinalizadores-ambulatoriais-de-insuficiencia-mitral-descompensando.md`

## #841 — reviewed_scoped_integration
HEAD remoto: `3d93069aaf8031102a0917861bc24eda7e70a3ee`. Base: `main`. Cinco grupos antes de terapia; V/Q, DLCO, RHC; risco e síncope formal; gestação e falha de infusão; não suspender prostaciclina abruptamente; exceções PH-ILD.

- `content/Hipertensão_pulmonar/fluxograma-ambulatorial-hap-quando-escalar-ou-referenciar.md`
- `content/Hipertensão_pulmonar/sinalizadores-ambulatoriais-de-piora-na-hap.md`
- `content/Hipertensão_pulmonar/sinalizadores-ambulatoriais-nao-tratar-hp-grupo-2-3-como-hap.md`

## #842 — reviewed_scoped_integration
HEAD remoto: `bbbb701a52a9ca607e07af597243ddd958e87494`. Base: `main`. Piora IC por gravidade e acesso; ortopneia aguda não retorno em dias; STRONG-HF combina titulação e consultas até6semanas; peso operacional e laboratório contextual.

- `content/Insuficiência_cardíaca/fluxograma-ambulatorial-ic-piora-progressiva-destino.md`
- `content/Insuficiência_cardíaca/pos-alta-de-ic-checklist-de-alarme-nas-duas-primeiras-semanas.md`
- `content/Insuficiência_cardíaca/sinalizadores-ambulatoriais-de-descompensacao-de-ic-quando-encaminhar.md`

## #843 — reviewed_scoped_integration
HEAD remoto: `b08e33b2c20270f1cd047dc0c26cf2f77e384dd7`. Base: `main`. Dor: resposta a nitrato/ECG normal não excluem SCA; investigar mudança; exames dirigidos; acesso pós-PCI e antitrombóticos sem interrupção autônoma.

- `content/Doença_coronariana/fluxograma-ambulatorial-dor-toracica-cronica-quando-escalar.md`
- `content/Doença_coronariana/pos-iam-ambulatorial-sinais-de-alarme-nas-primeiras-semanas.md`
- `content/Doença_coronariana/sinalizadores-ambulatoriais-de-angina-instabilizando-quando-encaminhar.md`

## #844 — reviewed_scoped_integration
HEAD remoto: `0718284a4adb90c7d8190398e601bbdb2d379cf3`. Base: `main`. Amiloide exige imunofixação sérica/urinária+FLC e cintilografia/SPECT; HCM13mm somente contexto familiar/genético; AF/HCM OAC independente escore; Holter e imagem contextual.

- `content/Cardiomiopatias/fluxograma-ambulatorial-cardiomiopatia-quando-escalar-imagem-genetica.md`
- `content/Cardiomiopatias/sinalizadores-ambulatoriais-de-cardiomiopatia-hipertrofica-quando-encaminhar.md`
- `content/Cardiomiopatias/sinalizadores-ambulatoriais-de-suspeita-de-amiloidose-cardiaca.md`

## #845 — reviewed_scoped_integration
HEAD remoto: `43f646b878518a098655d811a1d5bd6a72fe5e14`. Base: `main`. ACHD/Fontan encaminhamento por alteração basal/gravidade; cardioversão estável com proteção tromboembólica; cateterismo dirigido; gestação em equipe.

- `content/Cardiopatias_congênitas/fluxograma-ambulatorial-achd-sintoma-novo-destino.md`
- `content/Cardiopatias_congênitas/sinalizadores-ambulatoriais-em-cardiopatia-congenita-do-adulto-quando-encaminhar.md`
- `content/Cardiopatias_congênitas/sinalizadores-ambulatoriais-pos-fontan-quando-escalar.md`

## #846 — reviewed_scoped_integration
HEAD remoto: `30ae1c2647af7655a7fa1da350cd773bfb172bd9`. Base: `main`. Marcadores maiores/menores independentes determinam avaliação hospitalar; Beck não necessário; recorrência objetiva; anti-IL1 não por dor isolada.

- `content/Pericárdio/fluxograma-ambulatorial-pericardite-piora-destino.md`
- `content/Pericárdio/pericardite-checklist-ambulatorial-de-alarme.md`
- `content/Pericárdio/sinalizadores-ambulatoriais-pericardite-quando-encaminhar.md`

## #847 — reviewed_scoped_integration
HEAD remoto: `e162a2765285acc7d0bc2edb32014ab9b6810882`. Base: `main`. Risco suicida avaliado no mesmo encontro sem gate verde por ausência de plano; segurança, rede, proteção contra coerção e cuidado cardiovascular paralelo.

- `content/Saúde_mental_e_cardiologia/checklist-ambulatorial-alarme-crise-psiquiatrica-cardiopata.md`
- `content/Saúde_mental_e_cardiologia/fluxograma-ambulatorial-crise-psiquiatrica-destino-cardiologia.md`
- `content/Saúde_mental_e_cardiologia/sinalizadores-ambulatoriais-crise-psiquiatrica-no-consultorio-de-cardiologia.md`

## #848 — reviewed_scoped_integration
HEAD remoto: `56cc9c32c3e5a4c8ade3d8ba3b567b4aaca364cf`. Base: `main`. Dor resolvida estável avaliada prioritariamente; ECG/palpação não liberam sozinhos; troponina contextual; participação individual e decisão compartilhada.

- `content/Cardiologia_do_Esporte_e_do_Exercício/dor-toracica-no-atleta-ambulatorial-quando-escalar.md`
- `content/Cardiologia_do_Esporte_e_do_Exercício/fluxograma-ambulatorial-sinalizadores-atleta-destino.md`
- `content/Cardiologia_do_Esporte_e_do_Exercício/sinalizadores-ambulatoriais-no-atleta-quando-suspender-e-encaminhar.md`

## #849 — reviewed_scoped_integration
HEAD remoto: `ab2c23ba6e158aadd7b9678b515148b9f190566b`. Base: `main`. PAS160 OU PAD110; tratar urgências independentemente de sintomas; TVP isolada mesmo dia; déficit focal, hipoperfusão, TV sustentada e hipoxemia explícitos; mWHO não triagem aguda.

- `content/Gravidez/fluxograma-ambulatorial-gravidez-cardiopatia-piora-destino.md`
- `content/Gravidez/gravidez-checklist-ambulatorial-de-alarme.md`
- `content/Gravidez/sinalizadores-ambulatoriais-gravidez-cardiopatia-quando-encaminhar.md`

## #850 — reviewed_scoped_integration
HEAD remoto: `bffa86f5123c233671fb768fccc53f252a1b6204`. Base: `main`. Atraso assintomático isolado: aplicação precoce/acesso, sem retorno artificial ou catch-up; sem ajuste genérico de intervalo; Jones e WHF com escopos corretos.

- `content/Febre_reumática/checklist-ambulatorial-alarme-progressao-cardiopatia-reumatica.md`
- `content/Febre_reumática/fluxograma-ambulatorial-dose-perdida-benzatina-destino.md`
- `content/Febre_reumática/sinalizadores-ambulatoriais-profilaxia-benzatina-dose-perdida-quando-agir.md`

## #851 — reviewed_scoped_integration
HEAD remoto: `e76c8f94804be7d4ca24c987f30aeecfa8537a85`. Base: `main`. ECG/sinais vitais antes de baixo risco; suspeita residual de SCA exige série segura; não casa aguardando troponina; trauma em anticoagulado e ortostatismo não encerra diferencial.

- `content/Cardiologia_geriátrica/fluxograma-ambulatorial-queda-sincope-idoso-destino.md`
- `content/Cardiologia_geriátrica/sca-atipica-idoso-fragil-sinalizadores-ambulatoriais-consultorio.md`
- `content/Cardiologia_geriátrica/sinalizadores-ambulatoriais-queda-sincope-idoso-quando-encaminhar.md`

## #852 — reviewed_scoped_integration
HEAD remoto: `f2e51bd500d2c1c3aae06e984319296881ce6bde`. Base: `main`. AEF sem tríade obrigatória e sem instrumentação esofágica não planejada; estenose venosa pulmonar/frênica estável prioritária; OAC ligada a827; IC etiológica e acesso seguro.

- `content/Fibrilação_atrial/fluxograma-ambulatorial-sinalizadores-fa-nao-anticoag-destino.md`
- `content/Fibrilação_atrial/sinalizadores-ambulatoriais-falha-controle-frequencia-e-novos-sintomas-de-ic-na-fa.md`
- `content/Fibrilação_atrial/sinalizadores-ambulatoriais-pos-ablacao-fa-alarme-complicacao-nao-recorrencia.md`

## #853 — reviewed_scoped_integration
HEAD remoto: `8681918675ca670fd4e10a2ff4110d638a151a2e`. Base: `main`. Não interromper antibiótico automaticamente; três conjuntos claros sem atraso de sepse; bolso infectado mesmo afebril; suspeita estável pode via estruturada; foco alternativo não encerra.

- `content/Endocardite/endocardite-checklist-ambulatorial-febre-protese-dispositivo.md`
- `content/Endocardite/fluxograma-ambulatorial-suspeita-endocardite-febre-valvula-destino.md`
- `content/Endocardite/sinalizadores-ambulatoriais-suspeita-endocardite-quando-encaminhar.md`

## #854 — duplicate_excluded
HEAD remoto: `4e70c2586437dbe8822649ccf2aa7bff78380bd1`. Base: `main`. Dois slugs não importados: colisão material com902, candidato canônico mais completo. Guardrails enviados à integração: CK antes de reexposição, rabdomiólise/IMNM, AKI e piora rápida.


## #855 — reviewed_scoped_integration
HEAD remoto: `2941563482d4d12d14a1500d8f77875382b50e8f`. Base: `main`. PMID diabetes corrigido37622663; tratar hipo atual antes de transporte; nível3 histórico resolvido não PS automático; euDKA cetonas/acidobásico e sick-day; GU/pé/GLP1 fenotipados.

- `content/Diabetes_e_cardiologia/fluxograma-ambulatorial-sinalizadores-diabetes-cv-destino.md`
- `content/Diabetes_e_cardiologia/sinalizadores-ambulatoriais-hipoglicemia-grave-no-consultorio-de-cardiologia.md`
- `content/Diabetes_e_cardiologia/sinalizadores-ambulatoriais-intolerancia-e-alarme-sglt2-glp1-sem-doses.md`

## #856 — reviewed_scoped_integration
HEAD remoto: `bd42191ee7cbef235c58ac69a4f591186b517ce7`. Base: `main`. Appelbaum17978292 e choice talk2012; capacidade específica e suporte antes de conclusão; urgência precede adiamento; recusa/emoção não incapacidade.

- `content/Comunicação_clínica/checklist-ambulatorial-capacidade-consentimento-consulta-cardiologica.md`
- `content/Comunicação_clínica/fluxograma-ambulatorial-capacidade-sdm-e-mas-noticias-destino.md`
- `content/Comunicação_clínica/sinalizadores-ambulatoriais-capacidade-e-sdm-no-consultorio-cardiologico.md`

## #857 — reviewed_scoped_integration
HEAD remoto: `2003b9b51abc9565ad0b8b52bcdeaa55bd88fa14`. Base: `main`. SCA/ICI antes do fluxo geral; intermediário agudo avaliação hospitalar; baixo agudo considerar internação; LGE extenso independente; CMR central e EMB individual; exercício mínimo1mês e seguimento6meses.

- `content/Pericárdio/fluxograma-ambulatorial-miocardite-risco-destino.md`
- `content/Pericárdio/miocardite-checklist-ambulatorial-de-alarme.md`
- `content/Pericárdio/sinalizadores-ambulatoriais-miocardite-quando-encaminhar.md`

## #858 — reviewed_scoped_integration
HEAD remoto: `e5ebcb690ff8ccc454997a2cb3ef70317d04f18d`. Base: `main`. Pausa não significa PS; síncope no esforço urgente mesmo recuperada; PA repetida na sessão; retorno por doença; abandono não anula benefício;48h explicitamente local; dependência831 resolvida.

- `content/Reabilitação_cardíaca/quando-pausar-o-exercicio-na-sessao-de-reabilitacao-cardiaca-sintomas-de-alarme.md`
- `content/Reabilitação_cardíaca/retorno-ao-programa-de-reabilitacao-cardiaca-apos-doenca-intercorrente.md`
- `content/Reabilitação_cardíaca/risco-de-abandono-na-reabilitacao-cardiaca-ambulatorial-sinais-e-retencao.md`

## #859 — reviewed_scoped_integration
HEAD remoto: `3549473ca63e8cd73e81dfa048e0885b5f8b1c6e`. Base: `main`. Reabrir risco após alta; sem pródromo isolado não alto; interrogação de dispositivo rápida; nem alto nem baixo→observação; direção exige gate próprio; recorrência inexplicada investigação prolongada.

- `content/Síncope/fluxograma-ambulatorial-sincope-pos-avaliacao-destino.md`
- `content/Síncope/sinalizadores-ambulatoriais-sincope-pos-alta-quando-retornar.md`
- `content/Síncope/sincope-gate-ambulatorial-retorno-atividades-trabalho-direcao.md`

# Limites e integração

Os dois slugs #854 não devem coexistir com o pacote #902. A integração central deve registrar sua exclusão e os vínculos diretos doença→documentos (incluindo os três de síncope). As dependências831→858,826→855,827→852,834→857 e846→857 estão presentes nesta árvore. Fonte de produção Grok preservada nos novos documentos; dependência geriátrica não recebeu atribuição inventada de produtor.

Revisão humana adicional continua possível; não se promete infalibilidade científica. Este relatório não autoriza push, merge, deploy ou aprovação global. Validações estruturais e funcionais finais constam abaixo após execução.

## Verificação final focal

88 documentos: frontmatter parseável, slugs únicos, fonte Grok preservada, source_refs presentes e links /biblioteca existentes. Hub RC: schema de questões/regras válido e seis cenários executados no motor real — manutenção sem encaminhamento espúrio, encaminhamento inicial sem data, alto risco remoto com oposição, instabilidade encaminhada ao fluxo de emergência, ausência de campos obrigatórios e remoto sem estratificação. Esses controles não equivalem a uma trava técnica de prescrição ou publicação.

A dependência geriátrica teve os quatro resumos primários relidos em 08/09/2026: 20026778, 31837892, 36799963, 39727820. Percentuais basais de Kehler corrigidos para o denominador dos concluintes (2.322). Bauer continua sem magnitudes por indisponibilidade do texto integral da correção. Amyloidose: declaração ESC primária ejhf.2140, páginas 3–6, confirmou SPECT, imunofixação sérica/urinária e FLC em paralelo e interpretação renal dependente do ensaio.

Gate `git diff --cached --check`: aprovado. Nenhum push, merge em main, reconciliação global ou deploy realizado nesta etapa.
