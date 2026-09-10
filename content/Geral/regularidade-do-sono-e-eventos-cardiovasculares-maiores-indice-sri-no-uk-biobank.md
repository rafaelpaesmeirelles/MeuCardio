---
title: 'Regularidade do Sono (Não Só a Duração) e Eventos Cardiovasculares Maiores: o Índice SRI no UK Biobank'
slug: regularidade-do-sono-e-eventos-cardiovasculares-maiores-indice-sri-no-uk-biobank
theme: Geral
kind: estudo
review_status: revisado
source_refs:
- 'Chaput JP, Biswas RK, Ahmadi M, Cistulli PA, Rajaratnam SMW, Bian W, St-Onge MP, Stamatakis E. Sleep regularity
  and major adverse cardiovascular events: a device-based prospective study in 72 269 UK adults. J Epidemiol Community
  Health. 2025 Mar 10;79(4):257-264. DOI: 10.1136/jech-2024-222795. PMID: 39603689. PMCID: PMC12066246 — coorte
  prospectiva UK Biobank com acelerometria de punho por 7 dias, 72.269 adultos, seguimento médio de 7,8 anos'
legacy_source: 'Documento novo, escrito em 09/09/2026. A pasta Geral já cobre DURAÇÃO do sono (metanálise de Cappuccio)
  e desssincronização circadiana por trabalho em turnos, mas nenhum documento tratava da REGULARIDADE do sono —
  dia a dia, medida por dispositivo, independente de quantas horas a pessoa dorme em média — que é a pergunta clínica
  emergente e distinta captada pelo estudo de Chaput et al. (2025), o primeiro a associar o Índice de Regularidade
  do Sono (SRI), medido objetivamente por acelerômetro, a eventos cardiovasculares maiores em uma coorte prospectiva
  de grande porte. Nota de bastidor: ao levantar os arquivos já existentes sobre sono nesta pasta, encontrei dois
  documentos quase idênticos sobre a MESMA metanálise de Cappuccio (mesmo PMID 21300732) — ''duracao-do-sono-curta-e-longa-como-preditor-cardiovascular-metanalise-de-cappuccio.md''
  e ''sono-e-risco-cardiovascular-metanalise-de-cappuccio.md''. Não toquei neles (fora do escopo desta tarefa e
  da minha pasta de commit), mas registro o achado para limpeza futura.'
summary: null
tags: []
evidence_level: null
source_tier: A
gaps: []
published: true
---

# Regularidade do Sono (Não Só a Duração) e Eventos Cardiovasculares Maiores: o Índice SRI no UK Biobank

## A pergunta que a duração do sono, sozinha, não responde
Esta biblioteca já documenta que dormir pouco ou dormir demais prediz desfecho cardiovascular (ver `duracao-do-sono-curta-e-longa-como-preditor-cardiovascular-metanalise-de-cappuccio.md`). Mas duração média não captura outra dimensão do sono que também varia entre indivíduos e é biologicamente plausível como fator de risco: a **regularidade** — dormir e acordar em horários consistentes de um dia para o outro, versus um padrão errático, mesmo que a quantidade total de sono seja semelhante. Chaput JP et al. (J Epidemiol Community Health. 2025;79(4):257-264, PMID 39603689) testaram em uma coorte prospectiva com sono medido por dispositivo (não autorreferido) se a irregularidade do sono prediz eventos cardiovasculares maiores independentemente da duração.

## Desenho
Coorte prospectiva de participantes do UK Biobank, 40-79 anos, que usaram acelerômetro de punho por 7 dias consecutivos para permitir o cálculo objetivo do sono:
- **72.269 indivíduos** sem histórico prévio de evento cardiovascular maior (MACE) e sem evento no primeiro ano de seguimento
- Idade média **62,1 anos (DP 7,7)**; **42,9% homens** (57,1% mulheres)
- **Índice de Regularidade do Sono (SRI)** calculado por algoritmo validado a partir dos dados do acelerômetro, categorizado em três grupos:
  - **Regular**: SRI > 87,3 (grupo de referência)
  - **Moderadamente irregular**: SRI entre 71,6 e 87,3
  - **Irregular**: SRI < 71,6
- **Desfecho (MACE)**: composto de evento cardiovascular fatal, ou infarto do miocárdio não fatal (com ou sem supradesnivelamento do segmento ST), ou AVC, ou insuficiência cardíaca — o que ocorresse primeiro — obtido de registros de internação hospitalar e óbito
- **Seguimento médio: 7,8 anos (DP 1,3)**
- Análise adicional testando se dormir a duração recomendada para a idade **atenua ou elimina** o efeito da irregularidade sobre o risco de MACE

## Resultados
- **Sono irregular**: **HR 1,26** (IC95% 1,16-1,37) para MACE, comparado a sono regular
- **Sono moderadamente irregular:** a estimativa pontual publicada foi HR 1,08; o intervalo apresentado no resumo e no corpo é muito assimétrico e não é reproduzido aqui como medida precisa, diante de possível erro editorial. Essa ressalva não modifica o resultado principal do grupo irregular.
- **Análise dose-resposta** (SRI como variável contínua): relação **quase linear**, com redução de risco de MACE mais acentuada em escores de SRI mais altos (sono mais regular)
- **Subtipos de MACE, no grupo de sono irregular** (comparado a regular):
  - **Insuficiência cardíaca: HR 1,45** (IC95% 1,21-1,75)
  - **Infarto do miocárdio: HR 1,23** (IC95% 1,11-1,36)
  - **AVC: HR 1,22** (IC95% 1,01-1,48)
- **Análise conjunta de regularidade e duração do sono**: cumprir a recomendação de duração de sono específica para a idade **atenuou o risco** nos moderadamente irregulares (HR ajustado **1,07**, IC95% 0,96-1,18 — sem significância estatística), **mas permaneceu associação nos irregulares** (HR ajustado **1,19**, IC95% 1,06-1,35 — ainda significativo)

## Conclusão do próprio estudo
O estudo encontrou maior risco associado ao sono irregular, inclusive em participantes com duração considerada adequada. Os autores defendem a inclusão da regularidade do sono, ao lado da duração, nas diretrizes de saúde pública e na prática clínica como fator de risco cardiovascular.

## Por que isso muda a pergunta que se faz na anamnese
O achado central e prático é que **duração adequada coexistiu com maior risco observado no grupo de sono irregular** — a análise conjunta não demonstra que aumentar a duração do sono cause compensação de risco; compara grupos observacionais. Isso sustenta ampliar a anamnese de sono cardiovascular além da pergunta "quantas horas você dorme", incluindo também "os horários de dormir e acordar variam muito de um dia para o outro" — pergunta hoje pouco frequente na rotina clínica e que este estudo indica ter peso próprio, não redutível à duração.

## Limitações, declaradas com honestidade
- **Desenho observacional**: não estabelece causalidade. Irregularidade do sono pode ser marcador de doença subjacente não diagnosticada, de turno de trabalho, de comorbidade psiquiátrica ou de outros hábitos de vida não totalmente controlados no ajuste estatístico (causalidade reversa e confusão residual não podem ser excluídas).
- **SRI medido por apenas 7 dias de acelerometria** no início do seguimento — não captura mudança de padrão de sono ao longo dos 7,8 anos de acompanhamento subsequente.
- **Coorte do UK Biobank**: população predominantemente branca, mais saudável que a população geral do Reino Unido (viés de participação voluntária conhecido do UK Biobank), o que pode limitar a magnitude absoluta do risco observado em populações mais diversas.
- Faixa etária estudada foi **40-79 anos** no recrutamento — não informa sobre a mesma associação em adultos mais jovens.

## Tudo com Tudo

- [Duração do Sono Curta e Longa Como Preditor Cardiovascular: a Metanálise de Cappuccio](/biblioteca/duracao-do-sono-curta-e-longa-como-preditor-cardiovascular-metanalise-de-cappuccio)
- [Trabalho em Turnos Noturnos/Rotativos: Mecanismo de Dessincronização Circadiana e Risco Cardiovascular](/biblioteca/trabalho-em-turnos-noturnos-mecanismo-de-dessincronizacao-circadiana-e-risco-cardiovascular)
- [Trabalho em Turno Noturno Rotativo e Risco Coronariano: Nurses' Health Study](/biblioteca/trabalho-em-turno-noturno-rotativo-e-risco-coronariano-nurses-health-study)
- [Mudança Sazonal de Horário (Horário de Verão) e Risco Cardiovascular](/biblioteca/mudanca-sazonal-de-horario-horario-de-verao-e-risco-cardiovascular)
- [Dispositivos Vestíveis e Detecção de Fibrilação Atrial na População Geral: o Apple Heart Study](/biblioteca/dispositivos-vestiveis-e-deteccao-de-fibrilacao-atrial-na-populacao-geral-o-apple-heart-study)
- [Life's Essential 8: o Novo Construto de Saúde Cardiovascular da AHA](/biblioteca/lifes-essential-8-o-novo-construto-de-saude-cardiovascular-da-aha)

## Armadilhas clínicas
- **Perguntar só "quantas horas você dorme" e considerar a anamnese de sono completa** — este estudo mostra que a irregularidade tem associação própria com MACE, não plenamente explicada pela duração.
- **Usar os pontos de corte do SRI como metas terapêuticas validadas** — são categorias da análise, não alvos testados em ensaio de intervenção.
- **Tratar este achado como prova de causalidade** — é coorte observacional; irregularidade de sono pode ser marcador de outros fatores de risco não totalmente ajustados (turno de trabalho, transtorno psiquiátrico, uso de substâncias).
- **Extrapolar para adultos jovens (<40 anos)** — a coorte foi recrutada entre 40 e 79 anos.
- **Ignorar a mensagem prática mais forte do estudo**: a associação com irregularidade persistiu em quem dormia a duração recomendada, sem que isso prove efeito causal ou perda de todo benefício do sono adequado.
