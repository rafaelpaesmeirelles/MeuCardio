# Calculadoras de risco cardiovascular — 10/09/2026

Pedido: adicionar calculadoras de risco cardiovascular à função Calculadoras e pesquisar SBC, AHA, ACC e ESC. Manter Tudo com Tudo, fontes, domínio de aplicação e cálculo sem IA paga.

## Escopo concreto

- Framingham global 2008 (lipídios) e modelo de consultório (IMC): implementações matemáticas independentes; modelos históricos/comparativos, não apresentados como preferência atual SBC.
- PREVENT (SBC/AHA/ACC), SCORE2 e SCORE2-OP (ESC): páginas orientadoras no catálogo, com acesso explícito às ferramentas oficiais externas. Sem fingir execução nativa.
- SCORE2-Diabetes: acesso identificado à página oficial do aplicativo ESC. Não identificado como calculadora web nem como cálculo nativo.
- Fontes e limitações mantidas na página. Registro único alimenta API, busca Tudo com Tudo, grafo e Favoritos. Nenhum dado de paciente em URL externa.
- Sem novos modelos pagos, chamadas de IA, alteração de planos, conduta automática, migração ou mudança da versão publicada durante o desenvolvimento.

## Fontes primárias e seleção clínica

1. SBC, Diretriz Brasileira de Dislipidemias e Prevenção da Aterosclerose 2025. DOI 10.36660/abc.20250640. https://pmc.ncbi.nlm.nih.gov/articles/PMC12674852/
   Recomenda PREVENT-ASCVD em 10 anos para 30–79 anos sem DCV estabelecida (forte, certeza alta). Reconhece ausência de equação derivada no Brasil. O horizonte de 30 anos não tem os mesmos cortes de classificação.
2. AHA, Khan et al. Circulation 2024;149:430–449. DOI 10.1161/CIRCULATIONAHA.123.067626. https://pmc.ncbi.nlm.nih.gov/articles/PMC10910659/
3. ACC, CVD Risk Estimator Plus. https://tools.acc.org/CVD-Risk-Estimator-Plus/
   PREVENT 30–79 anos, horizonte de 30 anos somente 30–59. Riscos ASCVD, CVD total e IC são independentes; não somar. PCE antigo identificado pelo próprio ACC como não mais apoiado por suas políticas clínicas/diretrizes atuais.
4. Framingham Heart Study, equações originais e planilhas de referência: https://www.framinghamheartstudy.org/fhs-for-researchers/fhs-risk-functions/cardiovascular-disease-10-year-risk/
   D'Agostino et al. Circulation 2008;117:743–753. DOI 10.1161/CIRCULATIONAHA.107.699579. Prevenção primária, 30–74 anos; desfecho cardiovascular global, diferente de ASCVD.
5. ESC, SCORE2: DOI 10.1093/eurheartj/ehab309; SCORE2-OP: DOI 10.1093/eurheartj/ehab312; SCORE2-Diabetes: DOI 10.1093/eurheartj/ehad260.
   https://www.heartscore.org/en_GB/
   https://www.escardio.org/Education/Practice-Tools/CVD-prevention-toolbox/esc-cvd-risk-calculation-app
   Calibrações europeias não são calibrações brasileiras.

## Pendência concreta de incorporação nativa

AHA oferece integração PREVENT mediante acordo por representante autorizado:
https://professional.heart.org/en/guidelines-and-statements/about-prevent-calculator
https://www.jotform.com/240774577352161

O acordo prevê atribuição/versão e condições de monetização. Nenhum formulário foi submetido, nenhum aceite presumido e nenhum código PREVENT incorporado. Após aceite documentado, implementar e validar o motor contra os vetores oficiais, preservando PREVENT como ferramenta determinística e sem cobrança de IA.

Materiais/programa HeartScore: https://www.heartscore.org/en_GB/disclaimer . Não foi confirmada autorização de reprodução/incorporação comercial. Isso não é conclusão jurídica de que a matemática publicada seja necessariamente restrita. Esta entrega usa os acessos oficiais e não copia o programa.

## Validação

181 verificações isoladas passaram em 0,70 s: oito valores independentes das planilhas oficiais, cada um também no formato real string do formulário; ambos os sexos e tratamentos; domínio, entradas inválidas e bloqueio de execução dos recursos externos. A revisão encontrou e corrigiu a incompatibilidade inicial entre números string da UI e o backend. TypeScript sem diagnósticos. Verificação adicional do novo registro SBC: teste focal de recursos externos passou. Verificação visual inconclusiva: o harness sintético carregou duas identidades React Router; não há capturas válidas nem declaração de aprovação visual. Nenhum desvio foi aplicado no produto para acomodar o harness. Não executar CI backend completo ou focal: instrução persistente do responsável. PR preparado para revisão, sem contornar gates obrigatórios nem declarar publicação em produção.

## Calculadora própria SBC

Existência confirmada pelo histórico institucional da gestão 2016–2017: https://www.portal.cardiol.br/entidades/da . Registro próprio `sbc-risco-cardiovascular`, visível em “Acesso em confirmação”, bloqueado e sem URL executável inventada. A URL legada apresentou falhas de acesso/certificado; o portal atual não identifica versão, coeficientes ou endereço operacional. Pendência separada do PREVENT e das duas versões Framingham. Não declarada implementada nem publicada como ferramenta funcional.
