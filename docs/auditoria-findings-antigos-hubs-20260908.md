# Correções de findings antigos — checkpoint 2026-09-08

Escopo desta etapa: PRs 700, 715–719 e 723. Foram confrontadas as regras efetivamente compostas na release, não apenas comentários de revisão. O estado anterior ainda reproduzia os problemas clínicos abaixo apesar de `revisado`.

- AL: investigação não realizada não tranquiliza; tipagem indeterminada com clonalidade alterada ganha encaminhamento; AL confirmada exige tratamento em todos os estágios; Mayo IV não equivale a AL-ISS IIIC; retirada de rendimento indevidamente atribuído a cada sítio de biópsia e de venetoclax genérico.
- IAo: intervenção por regurgitação exige grau grave; risco cirúrgico categórico; Classe I e IIb separadas; Marfan com/sem fatores adicionais separado de outras aortopatias.
- ACM: modelos ARVC 2019/2021 e seus desfechos separados; referências pediátricas registradas, limitações explícitas; terapia de IC separada de antiarrítmicos; restrição esportiva condicionada a doença/variante causal; achados elétricos não pontuam automaticamente critérios.
- Sarcoidose: biópsia não universal, alternativa JCS um maior/dois menores, respostas histológicas completas; fluxos de urgência; AHA 2024 com corrigendum e primer 2026.
- QT adquirido: causas sem fármaco reconhecidas; Ray restrito ao subgrupo correto; Tisdale e seus limites explícitos; total manual conferido não é cálculo automático; TV polimórfica tem fluxo imediato; QTc inválido rejeitado; QTc isolado não força PS.
- Prótese mecânica: tamanho/embolia/persistência separados; fibrinólise exige ausência explícita de contraindicação; preferência não supera impossibilidade de AVK; idade e posição participam; INR inadequado também na via aguda; PROACT Xa incluído.
- EAo: risco procedural e FEVE nos caminhos de intervenção precoce; discordância não presume baixo fluxo; idade/modo de intervenção dependem de indicação; EA moderada com cirurgia concomitante contemplada.

Validação: 46 cenários no motor real, incluindo respostas representativas do renderer (select envia strings), passaram. A composição atual de doenças foi usada pelos testes. Os gates de inventário/editorial globais ainda aguardam o fechamento de todo o corpus; este documento não certifica que todos os demais PRs antigos estejam resolvidos.

Fontes: ESC/EACTS VHD2025, erratum EHJ2026 ehag625 (NYHA II–IV, sem mudança de trombo); ESC aorta2024; estudos primários ARVC30915475/33296238 e pediátricos34998950/37781308; AL41353737/38095141; AHA sarcoidose1240/corrigendum1275, primer42475441; Tisdale23716032, AHA ALS2025; PROACT Xa38320162. Identidades bibliográficas e fontes estão nos registros compostos.

### Colapso/PCR e BAV — PRs #535 e #686

Correção adicional do hub de PCR, triagem de colapso e checklist: pulso definido com apneia segue ventilação/reavaliação, inconsciência com respiração normal aciona emergência sem compressões automáticas, antes da puberdade há via pediátrica, cena insegura impede instruções de aproximação e gestação isolada não dispara emergência. ROSC atual muda a fase para cuidado pós-parada. Fontes: AHA/AAP BLS 2025 (DOIs 1369/1370) e AHA/Red Cross primeiros socorros 2024. O checklist passa a procedimento e o carregador preserva `scope_type`, coluna já existente; criação/recarga verificadas sem promover publicação automaticamente (2 cenários).

No BAV, a indicação de dispositivo permanente em Mobitz II/alto grau/completo sem causa reversível/fisiológica independe de sintomas; os fluxos não mandam esperar Holter ambulatorial para bloqueio avançado documentado. Instabilidade geral é separada de bradicardia causadora da instabilidade antes de recomendar estimulação. BAV 2:1 não equivale a Mobitz II. BRASH inclui uso de bloqueador nodal AV. Sorologia de Lyme isolada não define cardite ativa, nem serve para confirmar cura; suspeita clínica consistente não deve aguardar resultado para manejo. Fontes: ESC pacing 2021, AHA ALS 2025, CDC diagnóstico e cardite de Lyme, URLs versionadas no hub.

A revisão é restrita aos itens descritos; demais findings e lotes continuam pendentes, sem autorização global ou deploy nesta etapa.

### Canalopatias hereditárias — PR #585

Separados evento agudo/antecedente remoto e choque único estável/múltiplos choques; a história familiar isolada não gera emergência. Corrigida a soma de Schwartz, o limiar Shanghai e a distinção de padrão Brugada febril/farmacológico. Tratamento de tempestade de Brugada não é supressão catecolaminérgica; CPVT tem estratégia distinta. QT curto não recebe a proibição universal de prolongadores do QT da LQTS. Retiradas equivalência entre ablação e cura, indicação automática de CDI por síncope e exclusão de doença hereditária por ECG normal. Prevenção em assintomáticos, neonatal/genética e puerpério foram contextualizados. A coorte CPVT não comprovou o aumento puerperal descrito em LQTS.

Validação: 19/19 PMIDs do hub resolvidos pelo PubMed; nenhum par PMID/DOI divergente. CASPER, coorte de betabloqueadores CPVT e gestação CPVT conferidos em seus resumos primários; referências AHA 2025, ESC 2022, GeneReviews e BrugadaDrugs vinculadas. A rodada clínica ampliada passou em 77 cenários, além dos dois cenários focados do carregador de checklists. Estes resultados não substituem o gate global ainda pendente.

### Dispositivos — PR #599

A composição atual já contém DANISH na bibliografia e separa disfunção do circuito de choque de mera independência de pacing, além de encaminhar RM com eletrodos de risco para avaliação específica. Esses achados foram confirmados, sem refazer correções já presentes. Corrigidos os residuais: choque isolado com recuperação completa requer contato rápido/interrogação; choques repetidos em 24 horas ou instabilidade exigem emergência sem depender de adequação ou de terceiro choque. ERI foi separado de EOL e o estado de dependência modifica a resposta. Condicionalidade de RM se refere ao sistema completo/rotulagem; a segurança não foi reduzida a reset reversível. Referências SCMR 2024 e HRS clínica remota 2023 adicionadas. Preservadas as fontes e as relações já presentes.


## Dependências documentais: SCA e estatina — 08/09/2026

Dois fluxogramas canônicos corrigidos após revisão adversarial das dependências dos checklists. SCA: janela e contraindicações da fibrinólise, NSTEMI confirmado como alto risco, rule-in sem confirmação etiológica automática, rule-out sem excluir angina instável e encaminhamento hospitalar quando suspeita forte. Fonte: ESC 2023, Recommendation Table 4 e seções 5.1–5.3, artigo primário em repisalud.isciii.es. Estatina: alto risco PREVENT e LDL ≥190 não terminam sem tratamento; risco limítrofe/intermediário e risco de 30 anos separados; CAC sem conversão inventada; via individual após 75 anos. Fonte: material oficial AHA/ACC 2026 PREVENT para clínicos (731B2098BB23427F9EA8EDDF98E08145), não alegada leitura integral dos slides indisponíveis. Limiar ApoB 140 não confirmado e removido.

Validação: 2/2 blocos Mermaid analisados pelo parser real; YAML dos dois documentos e diff verificados. Preservados slugs e fonte_producao preexistente. Esta revisão focal não constitui autorização global do corpus.
