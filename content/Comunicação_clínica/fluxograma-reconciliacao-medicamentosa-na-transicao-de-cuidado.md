---
title: "Fluxograma: Reconciliação Medicamentosa na Transição de Cuidado"
slug: fluxograma-reconciliacao-medicamentosa-na-transicao-de-cuidado
theme: "Comunicação clínica"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
source_refs:
  - "Documento já publicado no acervo (tema Comunicação clínica): 'Reconciliação Medicamentosa e Transição de Cuidado: Onde o Erro Acontece' (slug: reconciliacao-medicamentosa-e-transicao-de-cuidado-onde-o-erro-acontece), de onde vêm a distinção entre discrepância e erro, os números de admissão versus alta e a recomendação de seguimento farmacêutico."
  - "Climente-Martí M, García-Mañón ER, Artero-Mora A, Jiménez-Torres NV. Potential risk of medication discrepancies and reconciliation errors at admission and discharge from an inpatient medical service. Ann Pharmacother. 2010;44(11):1747-1754. DOI: 10.1345/aph.1P184. PMID: 20923946."
  - "Mekonnen AB, McLachlan AJ, Brien JA. Effectiveness of pharmacist-led medication reconciliation programmes on clinical outcomes at hospital transitions: a systematic review and meta-analysis. BMJ Open. 2016;6(2):e010003. DOI: 10.1136/bmjopen-2015-010003. PMID: 26908524."
  - "Jacobs DM, Slazak E, Daly CJ, et al. Clinical and economic effectiveness of a pharmacy and primary care collaborative transition of care program. J Am Pharm Assoc. 2023;63(6):1722-1730.e3. DOI: 10.1016/j.japh.2023.08.014. PMID: 37611896."
---

# Fluxograma: Reconciliação Medicamentosa na Transição de Cuidado

Esta árvore segue a inversão central do documento-fonte: na admissão, a maioria das discrepâncias é intencional (96,6%) e o erro é raro (3,4%); na alta, o padrão se inverte — erro de reconciliação em 24,5% das discrepâncias, contra 3,4% na admissão (Climente-Martí et al., 2010). A árvore trata admissão e alta como dois ramos com lógica de verificação diferente, refletindo essa assimetria.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente cardiopata em transição de cuidado (admissão hospitalar ou alta)"] --> N1["Levantar com rigor a lista de medicamentos em uso antes da transição"]
  N1 --> D1{"Em que momento da transição a lista está sendo comparada?"}

  D1 -->|"Na admissão (primeiras 48h)"| D2{"Há discrepância entre a lista trazida pelo paciente e a prescrição admitida?"}
  D2 -->|"Não há discrepância"| C1(["Prosseguir a internação com a lista confirmada, documentada, para uso como referência na alta"])
  D2 -->|"Sim, há discrepância"| D3{"A mudança está documentada como intencional pelo prescritor (motivo clínico registrado)?"}
  D3 -->|"Sim, intencional e documentada"| C2(["Registrar a mudança como discrepância intencional, sem necessidade de correção; manter na lista de referência para a alta"])
  D3 -->|"Não, sem explicação registrada"| C3(["Tratar como possível erro de reconciliação na admissão; contatar o prescritor para confirmar a intenção antes de manter ou reverter a mudança"])

  D1 -->|"Na alta hospitalar"| D4{"A lista de alta foi comparada, item a item, com a lista pré-internação e com a prescrição durante a internação?"}
  D4 -->|"Não foi comparada"| C4(["Realizar a comparação antes de liberar a alta — é o ponto de maior risco de erro (erros 7x mais frequentes na alta que na admissão)"])
  D4 -->|"Sim, foi comparada"| D5{"Há discrepância não documentada como intencional?"}
  D5 -->|"Não, toda mudança está documentada e justificada"| C5(["Liberar a alta com a lista reconciliada, incluindo aconselhamento ao paciente sobre cada mudança"])
  D5 -->|"Sim, discrepância sem justificativa registrada (erro de reconciliação)"| C6(["Corrigir a lista antes da alta, com atenção redobrada a anticoagulante, antiarrítmico, digoxina e aos pilares de IC (margem terapêutica estreita); programar seguimento farmacêutico/telefônico nos primeiros 30 dias"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Sobre os critérios usados nesta árvore

A distinção entre discrepância e erro é, no documento-fonte, definida pela explicação registrada: "a diferença entre discrepância e erro é, literalmente, a explicação registrada". O estudo de Climente-Martí et al. (Ann Pharmacother 2010, PMID 20923946), com 120 pacientes de medicina interna, encontrou 109/120 (90,8%) com alguma discrepância e prevalência de erro de reconciliação de 20,8% — mas com a assimetria admissão/alta que estrutura os dois ramos desta árvore, e com número de discrepâncias na admissão associado a maior chance de erro na alta (OR 1,21).

O conduta final do ramo de alta com erro (C6) reúne duas recomendações do documento-fonte: a lista de fármacos de maior risco na cardiologia (anticoagulante, antiarrítmico, digoxina e os pilares de IC, por margem terapêutica estreita e suspensão silenciosa sem sintoma imediato) e a evidência de que programas de reconciliação conduzidos por farmacêutico, com seguimento telefônico ou domiciliar nos primeiros 30 dias, reduzem em 67% o retorno hospitalar por evento adverso de medicamento (RR 0,33; IC95% 0,20-0,53) e em 19% as readmissões (RR 0,81), sem redução de mortalidade (RR 1,05) — metanálise de Mekonnen et al. (BMJ Open 2016, PMID 26908524, 17 estudos, 21.342 pacientes). O documento-fonte também registra que o ensaio de Jacobs et al. (2023, PMID 37611896), citado como evidência adicional de atenção primária, tem desbalanço grave de alocação (36 vs. 264 pacientes) e deve ser lido com a devida ressalva.