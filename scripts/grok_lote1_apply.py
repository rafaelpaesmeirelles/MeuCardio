#!/usr/bin/env python3
"""Aplica o lote 1 Grok (estudos + evidências) no clone local.

Fonte: síntese portuguesa já conferida contra abstracts PubMed em
/tmp/pubmed_lote1/keep.json. Não altera origin/main. Não publica.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TMP_EST = Path("/tmp/MeuCardio/estudos/metadados.json")
TMP_EVI = Path("/tmp/MeuCardio/evidencias/metadados.json")
KEEP_PATH = Path("/tmp/pubmed_lote1/keep.json")
DOC_PATH = Path("/tmp/document_slugs.json")
DOENCA_PATH = Path("/tmp/doenca_slugs.json")

JOURNAL = {
    "The New England journal of medicine": "New England Journal of Medicine",
    "The New England Journal of Medicine": "New England Journal of Medicine",
    "Lancet (London, England)": "Lancet",
    "The Lancet": "Lancet",
    "European heart journal": "European Heart Journal",
    "European Heart Journal": "European Heart Journal",
    "Journal of the American College of Cardiology": "Journal of the American College of Cardiology",
    "JAMA": "JAMA",
    "Circulation": "Circulation",
    "Nature medicine": "Nature Medicine",
    "Nature Medicine": "Nature Medicine",
}

# Segunda evidência: mensagem clínica DISTINTA (segurança, secundário, desenho).
# Números copiados da síntese já validada contra o abstract.
SECONDS: list[dict] = [
    dict(
        parent="commit-metoprolol-precoce-no-iam",
        slug="commit-metoprolol-precoce-excesso-de-choque-cardiogenico",
        statement="No COMMIT, o metoprolol IV/oral precoce aumentou choque cardiogênico (5,0% vs 3,9%; OR 1,30; IC95% 1,19-1,41; p<0,00001), sobretudo nos dias 0-1, apesar de menos reinfarto (2,0% vs 2,5%; p=0,001) e menos fibrilação ventricular (2,5% vs 3,0%; p=0,001). Não usar o sinal de arritmia para justificar betabloqueio IV rotineiro no IAM instável.",
        tags=["commit", "metoprolol", "choque cardiogênico", "segurança", "iam"],
    ),
    dict(
        parent="atlas-acs-2-timi-51-rivaroxabana-apos-sca",
        slug="atlas-acs-2-timi-51-sangramento-maior-e-hic",
        statement="No ATLAS ACS 2–TIMI 51, rivaroxabana aumentou sangramento maior não relacionado à CRM (2,1% vs 0,6%; p<0,001) e hemorragia intracraniana (0,6% vs 0,2%; p=0,009), sem excesso de sangramento fatal (0,3% vs 0,2%; p=0,66). A redução de morte apareceu na dose 2,5 mg 2x/dia (morte CV 2,7% vs 4,1%; p=0,002), não na de 5 mg. Não omitir o custo hemorrágico ao citar o primário isquêmico.",
        tags=["atlas-acs-2", "rivaroxabana", "sangramento", "HIC", "sca"],
    ),
    dict(
        parent="appraise-2-apixabana-com-antiagregacao-apos-sca",
        slug="appraise-2-apixabana-excesso-de-sangramento-maior-timi",
        statement="No APPRAISE-2, apixabana 5 mg 2x/dia após SCA aumentou sangramento maior TIMI (1,3% vs 0,5%; HR 2,59; IC95% 1,50-4,46; p=0,001), com mais sangramentos intracranianos e fatais, e o ensaio foi interrompido precocemente. Não adicionar apixabana em dose plena à antiagregação pós-SCA.",
        tags=["appraise-2", "apixabana", "sangramento", "sca", "interrupção precoce"],
    ),
    dict(
        parent="charisma-clopidogrel-mais-aspirina-em-aterotrombose",
        slug="charisma-subgrupo-so-com-fatores-de-risco-sinal-de-dano",
        statement="No CHARISMA, o subgrupo só com múltiplos fatores de risco (prevenção primária) teve primário 6,6% vs 5,5% (RR 1,2; IC95% 0,91-1,59; p=0,20) e mais morte cardiovascular com clopidogrel (3,9% vs 2,2%; p=0,01). Análise de subgrupo; não indicar DAPT crônica em prevenção primária com base neste sinal.",
        tags=["charisma", "prevenção primária", "subgrupo", "morte cardiovascular", "clopidogrel"],
    ),
    dict(
        parent="val-heft-valsartana-na-insuficiencia-cardiaca",
        slug="val-heft-mortalidade-semelhante-e-triplice-pos-hoc",
        statement="No Val-HeFT, a mortalidade global foi semelhante entre valsartana e placebo; o benefício foi o composto de morbimortalidade (RR 0,87; IC97,5% 0,77-0,97; p=0,009). A observação post hoc de efeito adverso no subgrupo já em IECA e betabloqueador não autoriza a tríplice IECA+BB+valsartana.",
        tags=["val-heft", "valsartana", "mortalidade", "post hoc", "icfer"],
    ),
    dict(
        parent="gissi-prevenzione-omega3-e-vitamina-e-pos-iam",
        slug="gissi-prevenzione-vitamina-e-sem-beneficio-pos-iam",
        statement="No GISSI-Prevenzione, vitamina E 300 mg/dia não teve benefício no primário de morte, infarto não fatal e AVC. Não converter vitamina E em prevenção secundária pós-IAM. O sinal de PUFA n-3 1 g/dia (queda relativa 10%; IC95% 1-18 na two-way) não se transfere à vitamina E.",
        tags=["gissi-prevenzione", "vitamina e", "pós-iam", "desfecho nulo"],
    ),
    dict(
        parent="oasis-6-fondaparinux-no-iamcsst",
        slug="oasis-6-fondaparinux-sem-beneficio-na-icp-primaria",
        statement="No OASIS-6, fondaparinux 2,5 mg reduziu morte ou reinfarto no conjunto (9,7% vs 11,2%; HR 0,86; p=0,008), mas o abstract registra ausência de benefício no subgrupo de ICP primária. O ganho concentrou-se em trombólise (HR 0,79; p=0,003) e na ausência de reperfusão (HR 0,80; p=0,03). Não extrapolar fondaparinux como padrão da ICP primária contemporânea.",
        tags=["oasis-6", "fondaparinux", "icp primária", "iamcsst", "subgrupo"],
    ),
    dict(
        parent="norstent-stents-farmacologicos-ou-nao-farmacologicos-na-dac",
        slug="norstent-menos-revascularizacao-sem-reduzir-morte-ou-iam",
        statement="No NORSTENT, DES contemporâneo reduziu nova revascularização (16,5% vs 19,8%; HR 0,76; IC95% 0,69-0,85; p<0,001) e teve menos trombose definitiva (0,8% vs 1,2%; p=0,0498), mas o primário de morte ou IAM espontâneo em 6 anos não diferiu (16,6% vs 17,1%; HR 0,98; p=0,66). Não vender DES como redutor de mortalidade neste ensaio.",
        tags=["norstent", "stent farmacológico", "revascularização", "desfecho secundário"],
    ),
    dict(
        parent="examination-stent-everolimo-versus-nao-farmacologico-no-iamcsst",
        slug="examination-trombose-de-stent-e-secundario-nao-primario",
        statement="No EXAMINATION, menos trombose definitiva (0,5% vs 1,9%; p=0,019) e menos revascularização da lesão (2,1% vs 5,0%; p=0,003) com stent de everolimo são secundários. O primário orientado ao paciente em 1 ano não diferiu (11,9% vs 14,2%; p=0,19). Não declarar superioridade clínica pelo primário.",
        tags=["examination", "trombose de stent", "secundário", "iamcsst"],
    ),
    dict(
        parent="cirt-metotrexato-baixa-dose-para-prevencao-aterosclerotica",
        slug="cirt-metotrexato-sem-queda-de-il6-pcr-e-mais-eventos-adversos",
        statement="No CIRT, metotrexato em baixa dose não reduziu IL-1β, IL-6 nem PCR e associou-se a mais elevação de enzimas hepáticas, queda de leucócitos/hematócrito e câncer de pele não basal, com primário cardiovascular nulo (HR 0,96; IC95% 0,79-1,16). Não usar metotrexato para prevenção aterosclerótica.",
        tags=["cirt", "metotrexato", "inflamação", "segurança", "desfecho neutro"],
    ),
    dict(
        parent="afire-antithromboticos-na-fa-com-dac-estavel",
        slug="afire-interrupcao-precoce-por-mortalidade-na-combinacao",
        statement="O AFIRE foi interrompido precocemente por maior mortalidade na combinação rivaroxabana + antiagregante. A monoterapia foi não inferior em eficácia (HR 0,72; p<0,001 para NI) e superior em sangramento maior ISTH (HR 0,59; p=0,01) em população japonesa com FA e DAC estável. Não ignorar a interrupção precoce nem extrapolar a dose automaticamente para outros países.",
        tags=["afire", "interrupção precoce", "mortalidade", "fa", "dac estável"],
    ),
    dict(
        parent="tth48-hipotermia-48-versus-24-horas-apos-pcr",
        slug="tth48-mais-eventos-adversos-e-uti-mais-longa",
        statement="No TTH48, prolongar TTM a 33 °C de 24 para 48 h aumentou eventos adversos (97% vs 91%; RR 1,06; p=0,04) e o tempo de UTI (151 vs 117 h; p<0,001), sem melhorar CPC 1-2 aos 6 meses (69% vs 64%; p=0,33). Não estender hipotermia para 48 h de rotina.",
        tags=["tth48", "hipotermia", "eventos adversos", "uti", "parada cardíaca"],
    ),
    dict(
        parent="adrenal-glicocorticoide-adjetivo-no-choque-septico",
        slug="adrenal-choque-resolve-mais-rapido-sem-ganho-de-sobrevida",
        statement="No ADRENAL, hidrocortisona 200 mg/dia acelerou a resolução do choque (mediana 3 vs 4 dias; HR 1,32; p<0,001) e encurtou o primeiro episódio de ventilação (6 vs 7 dias; HR 1,13; p<0,001), mas não reduziu morte em 90 dias (27,9% vs 28,8%; OR 0,95; p=0,50). Não indicar corticoide no choque séptico para reduzir mortalidade com base neste primário.",
        tags=["adrenal", "hidrocortisona", "choque séptico", "desfecho intermédio"],
    ),
    dict(
        parent="instead-endoprotese-na-dissecao-aortica-tipo-b",
        slug="instead-remodelamento-aortico-sem-ganho-de-sobrevida",
        statement="No INSTEAD, TEVAR eletivo produziu mais remodelamento aórtico (91,3% vs 19,4%; p<0,001) sem melhorar sobrevida em 2 anos vs terapia médica (88,9% vs 95,6%; p=0,15) em ensaio subpoderado. Não converter remodelamento em indicação de TEVAR de rotina na dissecção tipo B não complicada.",
        tags=["instead", "tevar", "remodelamento", "dissecção tipo b", "subpoderado"],
    ),
    dict(
        parent="glagov-evolocumabe-e-progressao-de-ateroma-por-ivus",
        slug="glagov-desfecho-de-imagem-nao-clinico",
        statement="O GLAGOV é ensaio de imagem (PAV por IVUS): diferença −1,0% (IC95% −1,8 a −0,64; p<0,001) em 76 semanas, com 846/968 imagens avaliáveis. O próprio abstract pede estudos de desfechos clínicos. Não converter regressão de placa em redução de morte ou infarto.",
        tags=["glagov", "ivus", "ateroma", "desfecho de imagem", "evolocumabe"],
    ),
    dict(
        parent="pacman-ami-alirocumabe-e-ateroma-apos-iam",
        slug="pacman-ami-desfecho-de-imagem-nao-clinico",
        statement="O PACMAN-AMI é ensaio de imagem em n=300 (265 com IVUS seriado): diferença de PAV −1,21% (IC95% −1,78 a −0,65; p<0,001) em 52 semanas. O abstract pede pesquisa de desfechos clínicos. Não converter regressão de placa em benefício clínico.",
        tags=["pacman-ami", "ivus", "alirocumabe", "desfecho de imagem"],
    ),
    dict(
        parent="orion-9-inclisirana-na-hipercolesterolemia-familiar-heterozigotica",
        slug="orion-9-reducao-de-ldl-sem-desfecho-clinico-primario",
        statement="O ORION-9 demonstrou redução de LDL na HFHe (diferença −47,9 pontos percentuais no dia 510; IC95% −53,5 a −42,3; p<0,001). O desfecho é laboratorial, não de eventos clínicos. Não afirmar redução de MACE com base neste ensaio.",
        tags=["orion-9", "inclisirana", "ldl", "hfhe", "desfecho laboratorial"],
    ),
    dict(
        parent="clear-harmony-acido-bempedoico-para-reduzir-ldl",
        slug="clear-harmony-gota-e-ausencia-de-mace-primario",
        statement="No CLEAR Harmony, o primário é segurança em 52 semanas (eventos adversos 78,5% vs 78,7%); houve mais descontinuação (10,9% vs 7,1%) e mais gota (1,2% vs 0,3%). A eficácia é LDL na semana 12 (diferença −18,1 pontos percentuais; p<0,001). Não é ensaio de MACE (CLEAR Outcomes é outro estudo).",
        tags=["clear-harmony", "ácido bempedoico", "gota", "segurança", "ldl"],
    ),
    dict(
        parent="spire-2-bococizumabe-em-pacientes-de-alto-risco",
        slug="spire-1-e-2-combinado-neutro-e-heterogeneidade",
        statement="Nos SPIRE-1/2, o combinado de 27.438 pacientes foi nulo (HR 0,88; IC95% 0,76-1,02; p=0,08). O ensaio de menor risco/menor duração teve HR 0,99 (p=0,94) e o de maior risco HR 0,79 (p=0,02). Reações no local da injeção 10,4% vs 1,3% (p<0,001). Não vender benefício global do bococizumabe.",
        tags=["spire-1", "spire-2", "bococizumabe", "combinado neutro", "imunogenicidade"],
    ),
    dict(
        parent="fourier-ole-evolocumabe-longo-prazo-em-dac",
        slug="fourier-ole-extensao-aberta-nao-substitui-o-parental",
        statement="O FOURIER-OLE é extensão aberta (6.635 dos 27.564 do parental; mediana 5,0 anos no OLE). A comparação usa a alocação original, sem novo placebo. LDL mediano 30 mg/dL às 12 semanas. Não substitui o FOURIER parental cego de desfechos.",
        tags=["fourier-ole", "extensão aberta", "evolocumabe", "limitação de desenho"],
    ),
    dict(
        parent="precombat-stents-versus-crm-no-tronco-esquerdo",
        slug="precombat-margem-larga-de-nao-inferioridade-nao-diretiva",
        statement="No PRECOMBAT, a não inferioridade de ICP vs CRM no MACCE de 1 ano usou margem larga (8,7% vs 6,7%; diferença 2,0 pontos; IC95% −1,6 a 5,6; p=0,01 para NI). Os autores do abstract afirmam que o resultado não é clinicamente diretivo. Houve mais revascularização do vaso-alvo por isquemia aos 2 anos (9,0% vs 4,2%; HR 2,18; p=0,02). Não tratar como equivalência à CRM.",
        tags=["precombat", "não inferioridade", "margem larga", "tronco esquerdo"],
    ),
    dict(
        parent="prague-2-transporte-para-angioplastia-versus-trombolise-imediata",
        slug="prague-2-subgrupo-temporal-e-as-treated-nao-substituem-itt",
        statement="No PRAGUE-2, a mortalidade em ITT não diferiu (10,0% vs 6,8%; p=0,12). A análise as-treated (ICP 6,0% vs TL 10,4%; p<0,05) e o subgrupo randomizado >3 h (15,3% vs 6%; p<0,02) são exploratórias. O composto secundário favoreceu o transporte (15,2% vs 8,4%; p<0,003). Não vender mortalidade ITT como positiva.",
        tags=["prague-2", "ITT", "as-treated", "subgrupo", "iamcsst"],
    ),
    dict(
        parent="relax-ahf-serelaxina-na-insuficiencia-cardiaca-aguda",
        slug="relax-ahf-mortalidade-180-dias-e-desfecho-adicional",
        statement="No RELAX-AHF, a mortalidade aos 180 dias (42 vs 65; HR 0,63; IC95% 0,42-0,93; p=0,019) é desfecho adicional, não primário. Os coprimários de dispneia foram discordantes (VAS-AUC p=0,007; Likert p=0,70) e morte CV ou reinternação em 60 dias foi nula (HR 1,02; p=0,89). O RELAX-AHF-2 testou a mortalidade e foi neutro. Não vender redução de morte.",
        tags=["relax-ahf", "serelaxina", "desfecho adicional", "mortalidade"],
    ),
    dict(
        parent="atmosphere-aliscireno-enalapril-ou-combinacao-na-ic",
        slug="atmosphere-combinacao-aliscireno-enalapril-mais-efeitos-adversos",
        statement="No ATMOSPHERE, a combinação aliscireno+enalapril vs enalapril não foi superior no primário (HR 0,93; IC95% 0,85-1,03) e aumentou hipotensão (13,8% vs 11,0%; p=0,005), creatinina elevada (4,1% vs 2,7%; p=0,009) e potássio elevado (17,1% vs 12,5%; p<0,001). Não associar inibidor de renina ao IECA na ICFEr.",
        tags=["atmosphere", "aliscireno", "combinação", "hipercalemia", "segurança"],
    ),
    dict(
        parent="define-flair-ifr-versus-ffr-para-guiar-icp",
        slug="define-flair-nao-inferioridade-nao-e-superioridade",
        statement="O DEFINE-FLAIR é ensaio de não inferioridade (margem 3,4 pontos percentuais), não de superioridade: MACE em 1 ano 6,8% vs 7,0% (diferença −0,2; IC95% −2,3 a 1,8; p<0,001 para NI; HR 0,95; p=0,78). Menos sintomas no procedimento (3,1% vs 30,8%) não autorizam declarar superioridade clínica do iFR.",
        tags=["define-flair", "ifr", "não inferioridade", "icp"],
    ),
    dict(
        parent="ifr-swedeheart-ifr-versus-ffr-para-guiar-icp",
        slug="ifr-swedeheart-ponto-estima-a-favor-do-ffr",
        statement="No iFR-SWEDEHEART, iFR foi não inferior ao FFR (6,7% vs 6,1%; diferença 0,7 pontos; IC95% −1,5 a 2,8; margem 3,2; p=0,007 para NI), com ponto estima discretamente a favor do FFR (HR 1,12; p=0,53). Não declarar superioridade do iFR.",
        tags=["ifr-swedeheart", "ifr", "ffr", "não inferioridade"],
    ),
    dict(
        parent="danami-2-angioplastia-versus-fibrinolise-no-iam",
        slug="danami-2-morte-isolada-nao-significativa",
        statement="No DANAMI-2, o ganho do composto em 30 dias veio do reinfarto (1,6% vs 6,3%; p<0,001). Morte isolada não diferiu (6,6% vs 7,8%; p=0,35) nem o AVC (1,1% vs 2,0%; p=0,15). A transferência ao centro invasivo ocorreu em ≤2 h na quase totalidade dos casos de referência. Não afirmar redução de mortalidade.",
        tags=["danami-2", "mortalidade", "reinfarto", "transferência"],
    ),
    dict(
        parent="gusto-i-quatro-estrategias-tromboliticas-no-iam",
        slug="gusto-i-excesso-de-avc-hemorragico-com-tpa",
        statement="No GUSTO-I, t-PA acelerado reduziu mortalidade em 30 dias vs estreptoquinase (6,3% vs 7,2-7,4%; redução 14%; p=0,001), com mais AVC hemorrágico (0,72% vs 0,49% e 0,54%; p=0,03). A combinação SK+t-PA teve ainda mais AVC hemorrágico (0,94%; p<0,001). O composto morte ou AVC incapacitante ainda favoreceu t-PA (6,9% vs 7,8%; p=0,006). Evidência da era trombolítica, não comparado com ICP primária.",
        tags=["gusto-i", "tpa", "avc hemorrágico", "segurança", "iam"],
    ),
    dict(
        parent="acuity-bivalirudina-nas-sindromes-coronarianas-agudas",
        slug="acuity-comparador-inclui-gp-iib-iiia-de-rotina",
        statement="No ACUITY, o comparador de bivalirudina isolada é heparina + GP IIb/IIIa de rotina, não heparina isolada contemporânea. Bivalirudina isolada foi não inferior em isquemia (7,8% vs 7,3%; p=0,32) e reduziu sangramento maior (3,0% vs 5,7%; RR 0,53; p<0,001). Não equivaler a comparar com heparina sem GP na era atual.",
        tags=["acuity", "bivalirudina", "gp iib/iiia", "comparador"],
    ),
    dict(
        parent="leaders-free-stent-farmacologico-sem-polimero-em-alto-risco-de-sangramento",
        slug="leaders-free-comparador-metalico-com-dapt-de-1-mes",
        statement="O LEADERS FREE compara stent de umirolimus sem polímero versus stent metálico semelhante, ambos com DAPT de 1 mês, em alto risco de sangramento. A superioridade em segurança (9,4% vs 12,9%; HR 0,71; p=0,005) e em revascularização da lesão-alvo (5,1% vs 9,8%; HR 0,50) não compara com outros farmacológicos contemporâneos sob DAPT curto.",
        tags=["leaders-free", "comparador metálico", "dapt 1 mês", "alto risco de sangramento"],
    ),
    dict(
        parent="host-exam-clopidogrel-versus-aspirina-monoterapia-pos-icp",
        slug="host-exam-populacao-coreana-e-desfecho-composto-misto",
        statement="O HOST-EXAM é aberto, em 37 centros na Coreia, e o primário mistura isquemia e sangramento BARC ≥3 (5,7% vs 7,7%; HR 0,73; p=0,0035). Não extrapolar automaticamente a outras etnias nem a ticagrelor/prasugrel em monoterapia. O abstract não separa os componentes do composto.",
        tags=["host-exam", "população coreana", "composto misto", "aberto"],
    ),
    dict(
        parent="credence-canagliflozina-diabetes-e-nefropatia",
        slug="credence-faixa-de-tfge-e-albuminuria-do-ensaio",
        statement="O CREDENCE randomizou diabetes tipo 2 com TFGe 30 a <90 mL/min/1,73 m² e relação albumina/creatinina >300 a 5.000 mg/g já sob SRAA (n=4.401; mediana 2,62 anos). O primário caiu (HR 0,70; IC95% 0,59-0,82; p=0,00001). Não extrapolar para TFGe <30 ou ausência de albuminúria, que o ensaio não testou. Interrompido precocemente por eficácia.",
        tags=["credence", "tfge", "albuminúria", "sglt2", "população"],
    ),
    dict(
        parent="castle-htx-ablacao-de-fa-na-ic-terminal",
        slug="castle-htx-amostra-pequena-e-interrupcao-precoce",
        statement="O CASTLE-HTx randomizou 97 pacientes por braço, foi interrompido precocemente por eficácia e teve cruzamento de 16% no controle (ablacão 84% vs 16%). O primário caiu (8% vs 30%; HR 0,24; IC95% 0,11-0,52; p<0,001). Não generalizar para IC não terminal nem ignorar o n pequeno.",
        tags=["castle-htx", "n pequeno", "interrupção precoce", "cruzamento", "fa"],
    ),
    dict(
        parent="camera-mri-ablacao-versus-controle-de-frequencia-na-fa-com-disfuncao",
        slug="camera-mri-desfecho-de-feve-em-n-pequeno",
        statement="O CAMERA-MRI randomizou 68 pacientes (33 em cada braço após 2 desistências; 301 rastreados) com desfecho de FEVE em 6 meses (+18±13% vs +4,4±13%; p<0,0001), não de mortalidade. Não substitui CASTLE-AF para morte ou internamento.",
        tags=["camera-mri", "feve", "n pequeno", "desfecho de função"],
    ),
    dict(
        parent="decaaf-fibrose-atrial-por-rm-e-ablacao-de-fa",
        slug="decaaf-associacao-observacional-nao-ensaio-de-estrategia",
        statement="O DECAAF é coorte observacional (272/329 com RM utilizável; 17% excluídos por imagem inadequada). Cada 1% de fibrose atrial associou-se a HR 1,06 (IC95% 1,03-1,08) de recorrência. Não é ensaio de ablação guiada por fibrose. O abstract pede investigação das implicações clínicas.",
        tags=["decaaf", "observacional", "fibrose atrial", "coorte"],
    ),
    dict(
        parent="transcend-telmisartana-em-intolerantes-a-ieca",
        slug="transcend-secundario-perde-significancia-apos-multiplicidade",
        statement="No TRANSCEND, o secundário de morte CV, infarto ou AVC (13,0% vs 14,8%; HR 0,87; IC95% 0,76-1,00; p=0,048 não ajustado) perde significância após ajuste por multiplicidade (p=0,068). O primário permaneceu nulo (15,7% vs 17,0%; HR 0,92; p=0,216). Não declarar superioridade da telmisartana neste ensaio.",
        tags=["transcend", "multiplicidade", "secundário", "telmisartana"],
    ),
    dict(
        parent="charm-preserved-candesartana-na-ic-com-feve-preservada",
        slug="charm-preserved-internamento-por-ic-e-secundario",
        statement="No CHARM-Preserved, menos internamento por IC ao menos uma vez (230 vs 279; p=0,017) é secundário. O primário não alcançou significância (22% vs 24%; HR 0,89; IC95% 0,77-1,03; p=0,118; ajustado p=0,051) e a morte CV foi 170 vs 170. O corte de FE >40% não coincide com a ICFEp contemporânea. Não converter internamento em indicação de BRA para ICFEp.",
        tags=["charm-preserved", "secundário", "internamento", "icfep"],
    ),
    dict(
        parent="rooby-crm-com-ou-sem-circulacao-extracorporea",
        slug="rooby-pior-patencia-e-menos-enxertos-concluidos",
        statement="No ROOBY, a CRM off-pump teve menos enxertos que o planejado (17,8% vs 11,1%; p<0,001) e pior patência em 1.371 pacientes/4.093 enxertos (82,6% vs 87,8%; p<0,01), além de pior composto de 1 ano (9,9% vs 7,4%; p=0,04). Não preferir off-pump de rotina com base neste ensaio.",
        tags=["rooby", "off-pump", "patência", "enxerto"],
    ),
    dict(
        parent="scot-heart-angiotomografia-coronaria-e-risco-de-infarto-em-5-anos",
        slug="scot-heart-mecanismo-por-mais-terapia-preventiva",
        statement="No SCOT-HEART, angiografia invasiva (491 vs 502) e revascularização foram semelhantes aos 5 anos, apesar de mais exames iniciais no braço angiotomografia. Houve mais terapia preventiva (OR 1,40) e antianginosa (OR 1,27). O ensaio é aberto; o primário caiu (2,3% vs 3,9%; HR 0,59; p=0,004). Não atribuir o ganho a mais ICP.",
        tags=["scot-heart", "angiotc", "terapia preventiva", "aberto"],
    ),
    dict(
        parent="bari-2d-revascularizacao-e-estrategia-glicemica-no-diabetes-com-dac",
        slug="bari-2d-estrato-crm-e-analise-de-interacao",
        statement="No BARI-2D, a sobrevida em 5 anos não diferiu com revascularização imediata (88,3% vs 87,8%; p=0,97) nem entre sensibilização vs oferta de insulina (88,2% vs 87,9%; p=0,89). Menos eventos CV no estrato CRM (22,4% vs 30,5%; p=0,01; interação p=0,002) é análise de interação, não o primário da população total. Era pré-SGLT2/agonistas GLP-1.",
        tags=["bari-2d", "interação", "crm", "subgrupo", "diabetes"],
    ),
]


def polish_journal(name: str) -> str:
    if not name:
        return name
    if name in JOURNAL:
        return JOURNAL[name]
    return name


def polish_text(s: str) -> str:
    if not s:
        return s
    s = s.replace("et al..", "et al.")
    s = s.replace("a todo paciente", "a qualquer paciente")
    s = s.replace("a todo o paciente", "a qualquer paciente")
    return s


def ordered_estudo(rec: dict) -> dict:
    keys = [
        "slug", "title", "study_type", "authors", "journal", "year", "doi", "pmid",
        "url", "summary", "key_findings", "clinical_implications", "limitations",
        "theme", "tags", "review_status", "published", "fonte_producao",
        "review_note", "document_slug", "disease_slug",
    ]
    out = {}
    for k in keys:
        if k in rec and rec[k] not in (None,):
            if k == "doi" and rec[k] == "" and "gissi-prevenzione" in rec["slug"]:
                continue  # omit empty DOI; review_note explains PubMed pii only
            out[k] = rec[k]
    for k, v in rec.items():
        if k not in out and v not in (None, ""):
            out[k] = v
    return out


def ordered_evidencia(rec: dict) -> dict:
    keys = [
        "slug", "statement", "recommendation_class", "evidence_level", "society",
        "year", "guideline_title", "reference", "theme", "tags", "review_status",
        "published", "document_slug", "fonte_producao", "pmid", "doi", "review_note",
    ]
    out = {}
    for k in keys:
        if k in rec and rec[k] not in (None, ""):
            out[k] = rec[k]
    for k, v in rec.items():
        if k not in out and v not in (None, ""):
            out[k] = v
    return out


def main() -> int:
    docs = set(json.loads(DOC_PATH.read_text()))
    doencas = set(json.loads(DOENCA_PATH.read_text()))
    keep = json.loads(KEEP_PATH.read_text())
    pmid2keep = {str(v["pmid"]): (k, v) for k, v in keep.items()}

    src_est = [r for r in json.loads(TMP_EST.read_text()) if r.get("fonte_producao") == "grok"]
    src_evi = [r for r in json.loads(TMP_EVI.read_text()) if r.get("fonte_producao") == "grok"]
    if len(src_est) != 69 or len(src_evi) != 69:
        print("unexpected source counts", len(src_est), len(src_evi))
        return 2

    est_path = ROOT / "estudos/metadados.json"
    evi_path = ROOT / "evidencias/metadados.json"
    estudos = json.loads(est_path.read_text())
    evidencias = json.loads(evi_path.read_text())

    if any(r.get("fonte_producao") == "grok" for r in estudos + evidencias):
        print("workspace already has grok records; abort to avoid double insert")
        return 2

    base_pmids = {str(r.get("pmid")).strip() for r in estudos if r.get("pmid")}
    base_dois = {str(r.get("doi")).strip().lower() for r in estudos if r.get("doi")}
    base_slugs = {r["slug"] for r in estudos} | {r["slug"] for r in evidencias}

    new_est = []
    for rec in src_est:
        r = deepcopy(rec)
        r["journal"] = polish_journal(r.get("journal") or "")
        for field in ("summary", "key_findings", "clinical_implications", "limitations", "title", "review_note"):
            r[field] = polish_text(r.get(field) or "")
        r["authors"] = polish_text(r.get("authors") or "")
        r["review_status"] = "pendente_revisao"
        r["published"] = False
        r["fonte_producao"] = "grok"
        note = r.get("review_note") or ""
        if "Lote 1 Grok" not in note:
            note = (
                "Lote 1 Grok 2026-08-30. Síntese portuguesa original a partir do abstract PubMed (efetch). "
                "Números restritos ao abstract. PDF integral não lido. "
                "Manter pendente_revisao até revisão independente de fonte, números, interpretação e segurança."
            )
        if r["slug"].startswith("gissi-prevenzione"):
            note += " PubMed lista apenas PMID 10465168 e pii S0140673699070725; DOI não indexado no efetch — campo omitido de propósito."
        r["review_note"] = note
        if r.get("document_slug") and r["document_slug"] not in docs:
            print("BAD DOC", r["slug"], r["document_slug"])
            return 2
        if r.get("disease_slug") and r["disease_slug"] not in doencas:
            print("BAD DISEASE", r["slug"], r["disease_slug"])
            return 2
        pmid = str(r.get("pmid") or "").strip()
        doi = str(r.get("doi") or "").strip().lower()
        if pmid in base_pmids:
            print("PMID collision", pmid, r["slug"])
            return 2
        if doi and doi in base_dois:
            print("DOI collision", doi, r["slug"])
            return 2
        if r["slug"] in base_slugs:
            print("slug collision", r["slug"])
            return 2
        if pmid not in pmid2keep:
            print("pmid not in keep", pmid, r["slug"])
            return 2
        new_est.append(ordered_estudo(r))

    evi_by_pmid: dict[str, dict] = {}
    new_evi = []
    for rec in src_evi:
        r = deepcopy(rec)
        r["statement"] = polish_text(r.get("statement") or "")
        r["reference"] = polish_text(r.get("reference") or "")
        r["review_note"] = polish_text(r.get("review_note") or "")
        r["review_status"] = "pendente_revisao"
        r["published"] = False
        r["fonte_producao"] = "grok"
        r["recommendation_class"] = "Ponderado"
        parent = next((e for e in new_est if str(e.get("pmid")) == str(r.get("pmid"))), None)
        if parent:
            r["guideline_title"] = parent["title"]
            authors = parent["authors"]
            if not authors.endswith("."):
                authors = authors.rstrip(".") + ""
            doi_part = f" DOI: {parent['doi']}." if parent.get("doi") else " DOI não indexado no PubMed."
            r["reference"] = (
                f"{parent['authors']}. {parent['title']}. {parent['journal']}. {parent['year']}."
                f"{doi_part} PMID: {parent['pmid']}."
            )
            r["year"] = parent["year"]
            r["theme"] = parent["theme"]
            if parent.get("document_slug"):
                r["document_slug"] = parent["document_slug"]
            else:
                r.pop("document_slug", None)
        if r["slug"] in base_slugs or r["slug"] in {e["slug"] for e in new_est}:
            print("evid slug collision", r["slug"])
            return 2
        new_evi.append(ordered_evidencia(r))
        evi_by_pmid[str(r.get("pmid"))] = r

    parent_by_slug = {e["slug"]: e for e in new_est}
    used_second_slugs = set()
    for spec in SECONDS:
        parent = parent_by_slug.get(spec["parent"])
        if not parent:
            print("missing parent", spec["parent"])
            return 2
        slug = spec["slug"]
        if slug in base_slugs or slug in {e["slug"] for e in new_est} or slug in {e["slug"] for e in new_evi} or slug in used_second_slugs:
            print("second slug collision", slug)
            return 2
        used_second_slugs.add(slug)
        doi_part = f" DOI: {parent['doi']}." if parent.get("doi") else " DOI não indexado no PubMed."
        rec = {
            "slug": slug,
            "statement": spec["statement"],
            "recommendation_class": "Ponderado",
            "evidence_level": "B-NR" if parent.get("study_type") == "coorte_prospectiva" else "B-R",
            "society": (
                "Coorte-índice" if parent.get("study_type") == "coorte_prospectiva"
                else "Meta-análise-índice" if parent.get("study_type") == "metanalise"
                else "RCT-índice"
            ),
            "year": parent["year"],
            "guideline_title": parent["title"],
            "reference": (
                f"{parent['authors']}. {parent['title']}. {parent['journal']}. {parent['year']}."
                f"{doi_part} PMID: {parent['pmid']}."
            ),
            "theme": parent["theme"],
            "tags": spec["tags"],
            "review_status": "pendente_revisao",
            "published": False,
            "fonte_producao": "grok",
            "pmid": parent["pmid"],
            "review_note": (
                "Segunda evidência do mesmo ensaio-índice (segurança, secundário ou limite de desenho). "
                "Não é classe de diretriz ESC/AHA/SBC. Números do abstract. "
                "Manter pendente_revisao até casar com tabela oficial e revisão independente."
            ),
        }
        if parent.get("doi"):
            rec["doi"] = parent["doi"]
        if parent.get("document_slug"):
            rec["document_slug"] = parent["document_slug"]
        new_evi.append(ordered_evidencia(rec))

    # empty / placeholder / superiority checks
    errors = []
    ph = re.compile(r"\b(TODO|TBD|placeholder)\b", re.I)
    # Portuguese "todo" is allowed; only English TODO/TBD/placeholder
    for rec in new_est:
        for field in ("summary", "key_findings", "clinical_implications", "limitations", "title"):
            val = rec.get(field) or ""
            if not val.strip():
                errors.append(("empty", field, rec["slug"]))
            if ph.search(val):
                errors.append(("placeholder", field, rec["slug"]))
            if "sujeita à aprovação" in val.lower() or "sujeita a aprovacao" in val.lower():
                errors.append(("hedge", field, rec["slug"]))
    for rec in new_evi:
        st = rec.get("statement") or ""
        if not st.strip():
            errors.append(("empty_statement", rec["slug"]))
        if ph.search(st):
            errors.append(("placeholder_st", rec["slug"]))

    if errors:
        print("preflight errors")
        for e in errors:
            print(" ERR", e)
        return 2

    estudos.extend(new_est)
    evidencias.extend(new_evi)
    est_path.write_text(json.dumps(estudos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    evi_path.write_text(json.dumps(evidencias, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("APPLIED lote 1")
    print("new estudos", len(new_est))
    print("new evidencias", len(new_evi), "(primary", 69, "+ secondary", len(SECONDS), ")")
    print("corpus estudos", len(estudos), "evidencias", len(evidencias), "total", len(estudos) + len(evidencias))
    print("unique pmids new", len({r["pmid"] for r in new_est}))
    print("themes", Counter(r["theme"] for r in new_est).most_common())
    return 0


if __name__ == "__main__":
    sys.exit(main())
