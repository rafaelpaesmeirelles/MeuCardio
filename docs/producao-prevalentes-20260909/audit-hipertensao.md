# Auditoria da frente Hipertensão — 2026-09-09

## Adendo final após revisão cruzada

As pendências do central descritas historicamente abaixo foram corrigidas em rodada adicional: diagnóstico não pode ser concluído por DCV isolada; emergência não fica condicionada ao corte 180/110; PREVENT foi delimitado a prevenção primária/população elegível; tabela de resistência por contagem foi substituída por critérios de regime adequado, doses, adesão e medida extraconsultório; espironolactona/eplerenona receberam condicionantes explícitos de potássio, TFG, interações e monitoramento; retirados percentual universal de 90%, obrigatoriedade absoluta de combinação, painel inteiro anual, exames de imagem universais e equivalência de betabloqueadores para diálise/desejo reprodutivo. Também individualizado o conselho de potássio alimentar. O texto de hipocalemia agora explicita condições de coleta e efeito de IECA/BRA/diuréticos sobre renina.

Fontes adicionais PRIMÁRIAS efetivamente abertas e lidas nesta rodada:

- AHA/ACC 2025, síntese oficial: https://professional.heart.org/en/science-news/2025-high-blood-pressure-guideline/top-things-to-know
- AHA 2024, ambiente agudo: https://professional.heart.org/en/science-news/management-of-elevated-blood-pressure-in-the-acute-care-setting/top-things-to-know
- AHA, população e finalidade PREVENT: https://professional.heart.org/en/guidelines-and-statements/about-prevent-calculator
- AHA 2018, resistência: https://professional.heart.org/en/science-news/resistant-hypertension-detection-evaluation-and-management/top-things-to-know

Os complementos foram identificados como AHA/KDIGO no corpo e em `source_refs`, sem atribuir texto não lido à SBC. A ressalva de revisão focal consta também no frontmatter. Central ESC não alterado nesta frente: texto integral primário permanece indisponível e não seria correto transplantar limiares AHA para um documento ESC. Root pode decidir correção editorial focal separada da síntese.

## Base, escopo e limites

Base confirmada pelo conector GitHub: main `64796aa973316c94b47dcf8dc75a474415ecba34`. Foram lidos remotamente `hipertensao-arterial-classificacao-diagnostico-metas.md` (blob `d12e998e39a810cc4149796e167a1e8c8e6ad9a9`) e `hipertensao-arterial-e-pressao-arterial-elevada-esc-2024.md` (blob `7d11e8fe62d25b50f3e20a9acb30312a7f2c8f0c`). Inventário de caminhos atual confrontado com o corpus anterior apenas para reconhecer cobertura.

Já existem múltiplos documentos de diagnóstico, metas, fenótipo, resistência, emergências, ensaios e doença renal. Não foi assumido que títulos equivalem a completude. A contribuição concentra três lacunas operacionais: fechamento da primeira consulta com seguimento verificável; edema durante tratamento e atribuição causal responsável; e interpretação de resultados hormonais incompletos em paciente hipocalêmico.

## Arquivos entregues

1. `content/Hipertensão/hipertensao-primeira-consulta-plano-longitudinal-e-retorno-seguro.md` — novo, básico → intermediário → segurança na titulação; 793 palavras aproximadas.
2. `content/Hipertensão/edema-no-hipertenso-em-uso-de-bcc-avaliacao-e-represcricao.md` — novo, mecanismo → avaliação → caso fictício → limites da troca → seguimento; 822 palavras.
3. `content/Hipertensão/hipertensao-hipocalemia-e-renina-alta-interpretacao-sem-atalhos.md` — novo, amostra → unidades → caso fictício → integração com confirmação/subtipagem; 806 palavras.
4. `content/Hipertensão/hipertensao-arterial-classificacao-diagnostico-metas.md` — correção focal do arquivo existente, preservando slug: retirada da falsa afirmação de novidade de três estágios; retirada de metas e manutenção medicamentosa formuladas de modo absoluto; inclusão de individualização e links para percurso completo. Não é revisão integral da SBC 2025.

## Fontes efetivamente consultadas

- AHA, Home Blood Pressure Monitoring: página oficial acessível e lida; sustenta técnica residencial e necessidade de supervisão. https://www.heart.org/en/health-topics/high-blood-pressure/understanding-blood-pressure-readings/monitoring-your-blood-pressure-at-home
- KDIGO 2024, PDF integral acessível; consultados principalmente pontos 3.6.2–3.6.5 e recomendação contra duplo bloqueio. Não se atribuiu classe de ensaio a ponto de prática. https://kdigo.org/wp-content/uploads/2024/03/KDIGO-2024-CKD-Guideline.pdf
- NHS SPS, Managing peripheral oedema caused by calcium channel blockers, revisão de 26/05/2026: orientação institucional própria, lida; não é ensaio randomizado nem diretriz SBC. https://sps.nhs.uk/articles/managing-peripheral-oedema-caused-by-calcium-channel-blockers/
- Endocrine Society, Primary Aldosteronism 2025: página oficial com recomendações e notas técnicas acessível; recomendação de rastreio 2, baixa certeza foi conferida. https://www.endocrine.org/clinical-practice-guidelines/primary-aldosteronism-2
- WHO 2021: página institucional acessível, confirma escopo de farmacoterapia/seguimento; PDF de download não foi recuperado. Não foram atribuídos intervalos específicos ao texto inacessível. https://www.who.int/publications/i/item/9789240033986
- ESC 2024: página oficial acessível, confirma título, publicação e corrigendum de fevereiro de 2025. Texto completo OUP redirecionou para conteúdo bloqueado. https://www.escardio.org/guidelines/clinical-practice-guidelines/all-esc-practice-guidelines/elevated-blood-pressure-and-hypertension/
- SBC 2025: DOI 10.36660/abc.20250624 e HTML/PDF do ABC tentados; falha 403. Nenhuma afirmação nova foi apresentada como extraída diretamente da SBC inacessível.

Textos novos contêm síntese original de prática e casos inteiramente fictícios, sem transcrição extensa. `review_status: revisado` indica revisão científica automatizada desta rodada, não certificação ou revisão humana. O status prévio do central foi preservado; não transforma a correção focal em auditoria integral.

## Pendências materiais identificadas na base

O central SBC ainda necessita checagem integral contra o PDF para: exceções à confirmação diagnóstica; indicações e periodicidade universal de exames; linguagem absoluta sobre Framingham/PREVENT; limite rígido 180/110 na definição de emergência; critérios exatos das combinações para resistência/refratariedade e meta aplicável. Não foi seguro inventar a redação exata atribuída à SBC sem acesso ao texto. A formulação 'três estágios, não mais dois' foi retirada sem substituir por alegação histórica não verificada nesta rodada.

O central ESC contém trecho sugerindo monoterapia em toda a categoria 120–139/70–89, sem separar o limiar de farmacoterapia, além de repetir '<130/80 para todos' e falsa novidade dos três estágios brasileiros. Reportado à integração central; arquivo ESC não editado porque faltou recuperação do texto primário correspondente. Não confundir documento ainda existente com conteúdo validado nesta rodada.

## Tudo com Tudo: IDs e proposta de relações

IDs abaixo conferidos nos metadados ATUAIS em `base/`:

- Doença fonte: `hipertensao-arterial-sistemica`.
- Exames: `mapa-monitorizacao-ambulatorial-pressao-arterial`; `mrpa-monitorizacao-residencial-da-pressao-arterial`; `potassio-serico-risco-arritmico-e-monitorizacao`; `monitorizacao-de-potassio-e-creatinina-apos-inicio-de-antagonista-mineralocorticoide-sobre-ieca-bra`.
- Medicamentos: `anlodipino-besilato`; `olmesartana-medoxomila`; `indapamida`.
- Trilhas: `trilha-hipertensao-arterial`; `trilha-hipertensao-secundaria-e-populacoes-especiais`.
- Material paciente `hipertensao-arterial`: confirmado no corpus anterior; catálogo atual não foi fornecido nesta frente, conferir antes de mutação central.

Relações propostas: a doença HAS deve apontar para os três documentos novos; documento de primeira consulta deve integrar MAPA/MRPA, PREVENT, monitoramento e trilha básica; documento de edema deve integrar BCC, anti-hipertensivos relevantes, MAPA/MRPA e material paciente; documento de hipocalemia deve integrar potássio, monitoramento, investigação secundária e trilha correspondente. Calculadoras relacionadas por links para arquivos Markdown reais: PREVENT; Rockwood (contexto geriátrico, sem diagnosticar edema); Cockcroft–Gault (ajuste renal, sem interpretar ARR).

O formato observado em `doencas/relacoes-explicitas.json` utiliza `source_disease_slug`, `target_type`, `target_slug`, `relation_type`, `review_status`, `provenance_type`, `confidence`, `relevance_score`, `evidence_source`, `review_note`. Sugestão para integração central: `target_type: documento`, `relation_type: associated_with`, `confidence: explicit`, com justificativa clínica por documento e proveniência que explicite revisão automatizada. Não atribuir relações genéricas a todos os itens nem inventar IDs de calculadoras executáveis.

Validação realizada: todos os links Markdown relativos dos quatro documentos resolvem para caminhos existentes em `current-paths.txt` ou novos arquivos desta entrega; zero caminhos quebrados. Links para catálogos JSON são ponteiros verificáveis de fonte e não comprovam navegação na interface. Não houve commit, push, PR, importação de banco ou deploy nesta frente. Integração de arestas, teste bidirecional na busca e revisão de prontidão de lançamento permanecem responsabilidade da rodada central.
