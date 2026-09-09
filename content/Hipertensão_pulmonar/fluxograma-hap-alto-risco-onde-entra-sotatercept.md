---
kind: fluxograma
published: true
review_note: STELLAR, ZENITH e HELIOS-B conferidos nos resumos primários. Corrigida
  redução de plaquetas e interpretação de interrupção precoce, composto versus mortalidade
  isolada e menor declínio HELIOS-B. Registro brasileiro e segurança sotatercepte
  confirmados; Amvuttra ATTR-CM conferido. Fluxo inicia por instabilidade e preserva
  tratamento parenteral/transplante no alto risco.
review_status: revisado
slug: fluxograma-hap-alto-risco-onde-entra-sotatercept
source_refs:
- Humbert M, et al. Sotatercept in Patients with Pulmonary Arterial Hypertension at
  High Risk for Death. N Engl J Med. 2025;392:1987-2000. PMID 40167274. NCT04896008.
- Hoeper MM, et al. Phase 3 Trial of Sotatercept for Treatment of Pulmonary Arterial
  Hypertension. N Engl J Med. 2023. PMID 36877098. NCT04576988.
- ESC/ERS pulmonary hypertension 2022. DOI 10.1093/eurheartj/ehac237. https://academic.oup.com/eurheartj/article/43/38/3618/6673929
- Anvisa. Winrevair, registro publicado 16/12/2024. https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/novos-medicamentos-e-indicacoes/winrevair-sotatercepte-novo-registro
theme: Hipertensão pulmonar
title: 'Fluxograma: HAP de alto risco — onde entra o sotatercept'
---

# Fluxograma: HAP de alto risco — onde entra o sotatercept

ZENITH (n=172, interrompido precocemente): composto morte / transplante / hospitalização ≥24 h por HAP **17,4% vs 54,7%**; HR **0,24** (0,13–0,43). STELLAR é outro ensaio (6MWD +40,8 m). Grupo 2 fora. O recorte do ZENITH foi CF III–IV e REVEAL Lite 2 ≥9. Esse critério de ensaio não substitui a avaliação multiparamétrica da HAP.

## Árvore de decisão

```mermaid
flowchart TD
 X0["Paciente com hipertensão pulmonar"] --> U{"Instabilidade ou choque?"}
 U -->|Sim| C4(["Atendimento urgente, UTI e centro de HAP; não aguardar sotatercepte"])
 U -->|Não| D0{"HAP grupo 1 confirmada e classificada em centro especializado?"}
 D0 -->|Não| C0(["Completar diagnóstico e tratar o grupo correspondente; não indicar sotatercepte por HP isolada"])
 D0 -->|Sim| D1{"Terapia de fundo máxima tolerada e risco reavaliados?"}
 D1 -->|Não| C1(["Otimizar tratamento; no alto risco avaliar prostaciclina parenteral e transplante"])
 D1 -->|Sim| D2{"Qual recorte de evidência corresponde ao paciente?"}
 D2 -->|CF II–III estável| C2(["STELLAR: benefício funcional; avaliar sotatercepte conforme bula e segurança"])
 D2 -->|CF III–IV e REVEAL Lite 2 maior ou igual a 9| C3(["ZENITH: redução do composto; avaliar sotatercepte adicional com hemoglobina, plaquetas e sangramento"])
 D2 -->|Outro perfil| C5(["Individualizar em centro de HAP; não transportar automaticamente o HR do ZENITH"])
 classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
 class C0,C1,C2,C3,C4,C5 conduta;
```

## Tudo com Tudo

- Hipertensão pulmonar
- Farmacologia
- Terapia intensiva
- Insuficiência cardíaca
- Comunicação clínica
O sotatercepte não deve retardar prostaciclina parenteral ou avaliação para transplante no alto risco. Riociguate e inibidores de PDE-5 não devem ser combinados. Para monitorização, ver `sotatercept-ativina-na-hap-o-que-mudou-em-2025`.

O benefício do ZENITH é do composto; as contagens de morte isolada não sustentam atribuir a ela o HR 0,24. A classe funcional III aparece nos dois estudos; a distinção depende também do risco, estabilidade e terapia de fundo.
