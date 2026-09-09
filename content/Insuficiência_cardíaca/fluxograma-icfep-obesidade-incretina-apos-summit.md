---
kind: fluxograma
published: true
review_note: Conferidos ensaios primários e tabelas ESC 2026 pertinentes; corrigidos
  limites de população, segurança, doses ou interpretação quando aplicável.
review_status: revisado
slug: fluxograma-icfep-obesidade-incretina-apos-summit
source_refs:
- Packer M, et al. Tirzepatide for Heart Failure with Preserved Ejection Fraction
  and Obesity. N Engl J Med. 2025;392:427-437. PMID 39555826.
- McDonagh TA, et al. 2026 ESC Guidelines for acute and chronic heart failure. Eur
  Heart J. 2026. PMID 42661420.
- 'Køber L, Adamo M, et al. ESC 2026 Heart Failure. DOI 10.1093/eurheartj/ehag100.
  PMID 42661420. Slides oficiais: https://dam-assets.escardio.org/download/b2e587389baa11f185de06bdfb3e4be9'
theme: Insuficiência cardíaca
title: 'Fluxograma: ICFEp com obesidade — onde entra a incretina após SUMMIT'
---

# Fluxograma: ICFEp com obesidade — onde entra a incretina após SUMMIT

ESC 2026: classe **IIa** para semaglutida/tirzepatida na ICFEp com obesidade. SUMMIT: composto 9,9% vs 15,3%; HR 0,62; puxado por piora de IC, **não** por morte CV (HR 1,58; IC atravessa 1). KCCQ +6,9. Não é SURPASS-CVOT.

Otimizar iSGLT2, ARM, diurético e demais tratamentos conforme indicação e tolerância, em paralelo. Não há pré-requisito de completar toda titulação antes de avaliar incretina. Reabilitação e cuidados psicossociais acompanham os ramos elegíveis; não são alternativa mutuamente exclusiva ao medicamento.

## Árvore de decisão

```mermaid
flowchart TD
 X0["IC sintomática: confirmar diagnóstico e otimizar tratamento indicado"] --> D0{"FEVE ≥45%?"}
 D0 -->|Não| C0(["Fora da recomendação de incretina para este fenótipo. Tratar IC conforme etiologia e FEVE."])
 D0 -->|Sim| D1{"IMC ≥30 kg/m²?"}
 D1 -->|Não| C1(["Não aplicar STEP-HFpEF/SUMMIT ao paciente sem obesidade. Avaliar outras indicações individualmente."])
 D1 -->|Sim| D2{"Contraindicação ou intolerância relevante?"}
 D2 -->|Sim| C2(["Não iniciar o fármaco contraindicado; planejar abordagem alternativa e seguimento."])
 D2 -->|Não| C3(["Considerar semaglutida ou tirzepatida: IIa B1 para peso, exercício e qualidade de vida. Decisão compartilhada; evidência SUMMIT de eventos é FEVE ≥50%."])
 classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
 class C0,C1,C2,C3 conduta;
```

## Tudo com Tudo

- Insuficiência cardíaca
- Diabetes e cardiologia
- Reabilitação cardíaca
- Farmacologia
- Comunicação clínica
- Prevenção e lipídios
