---
title: 'Fluxograma: ICFEp com obesidade — onde entra a incretina após SUMMIT'
slug: fluxograma-icfep-obesidade-incretina-apos-summit
theme: Insuficiência cardíaca
kind: fluxograma
review_status: revisado
source_refs:
- Packer M, et al. Tirzepatide for Heart Failure with Preserved Ejection Fraction and Obesity. N Engl J Med. 2025;392:427-437.
  PMID 39555826.
- Køber L, Adamo M, et al. 2026 ESC Guidelines for the management of heart failure. Eur Heart J. 2026. DOI 10.1093/eurheartj/ehag100.
  PMID 42661420.
review_note: Corrigido corte de FE de 50 para 45% da ESC IIa B1, eliminada nomenclatura ICFEI e pré-requisito sequencial indevido
  de terapia completa; taxa GI identificada como descontinuação. SUMMIT integral e tabela ESC conferidos. Conexões temáticas
  selecionadas e links por slugs da fila conferidos.
summary: 'ESC 2026: classe IIa B1 para semaglutida ou tirzepatida na IC sintomática, FEVE ≥45% e IMC ≥30 kg/m², para peso,
  capacidade de exercício e qualidade de vida, com ou sem diabetes. STEP-HFpEF incluiu FEVE ≥45%; SUMMIT incluiu FEVE ≥50%.
  SUMMIT: composto 9,9% vs 15,3%; HR 0,62; puxado por piora de IC, não por morte CV (HR 1,58; IC atravessa 1). KCCQ +6,9.
  Não é SURPASS-CVOT.'
tags: []
source_tier: A
gaps: []
published: true
---

# Fluxograma: ICFEp com obesidade — onde entra a incretina após SUMMIT

ESC 2026: classe **IIa B1** para semaglutida ou tirzepatida na IC sintomática, **FEVE ≥45% e IMC ≥30 kg/m²**, para peso, capacidade de exercício e qualidade de vida, com ou sem diabetes. STEP-HFpEF incluiu FEVE ≥45%; SUMMIT incluiu FEVE ≥50%. SUMMIT: composto 9,9% vs 15,3%; HR 0,62; puxado por piora de IC, **não** por morte CV (HR 1,58; IC atravessa 1). KCCQ +6,9. Não é SURPASS-CVOT.



## Árvore de decisão

```mermaid
flowchart TD
  X0["Paciente com síndrome de IC"]
  D0{"FEVE ≥45% — recorte da recomendação de incretina?"}
  C0(["Fora do recorte desta recomendação de incretina. Tratar a IC conforme o fenótipo e avaliar outras indicações de controle de peso/DM"])
  D1{"IMC ≥30 kg/m²?"}
  C1(["ICFEp sem obesidade: incretina não herda SUMMIT. Otimizar diurético, PAS, FA, isquemia e comorbidades"])
  D2{"Tratamento da IC e comorbidades otimizado conforme elegibilidade?"}
  C2(["Otimizar em paralelo iSGLT2, ARM e demais terapias indicadas, respeitando contraindicações e tolerância"])
  D3{"Decisão compartilhada: tirzepatida (SUMMIT) versus semaglutida (STEP-HFpEF) — sintomas e eventos de IC, não morte"}
  C3A(["Tirzepatida: composto 36/364 vs 56/367; HR 0,62. Discutir interrupção por eventos adversos, principalmente GI: 6,3% vs 1,4%. Não promete morte CV"])
  C3B(["Semaglutida 2,4 mg no eixo STEP-HFpEF: capacidade e sintomas. Não misturar com SOUL/FLOW/SELECT"])
  C3C(["Encaminhar reabilitação cardíaca: exercício + educação + fármacos + psicossocial — ESC 2026 RC"])

  X0 --> D0
  D0 -->|"Não — FE reduzida"| C0
  D0 -->|"Sim — FE ≥45%"| D1
  D1 -->|"Não"| C1
  D1 -->|"Sim"| D2
  D2 -->|"Base incompleta"| C2
  C2 --> D3
  D2 -->|"Base em curso ou feita"| D3
  D3 -->|"Tirzepatida disponível e paciente concorda"| C3A
  D3 -->|"Semaglutida 2,4 mg / STEP"| C3B
  D3 -->|"Sempre — RC"| C3C

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f
  class C0,C1,C2,C3A,C3B,C3C conduta
```

## Tudo com Tudo

- [Incretinas na ICFEp com obesidade: ESC 2026 Classe IIa](/biblioteca/incretinas-na-icfep-com-obesidade-esc-2026-classe-iia)
- [SUMMIT: tirzepatida na ICFEp com obesidade](/biblioteca/summit-tirzepatida-icfep-com-obesidade)
- [STEP-HFpEF: semaglutida 2,4 mg — sintomas, não o SUMMIT](/biblioteca/step-hfpef-semaglutida-24-sintomas-nao-e-summit)
- [Fluxograma: ARM independente da FEVE — ESC 2026](/biblioteca/fluxograma-mra-independente-da-feve-esc-2026)
