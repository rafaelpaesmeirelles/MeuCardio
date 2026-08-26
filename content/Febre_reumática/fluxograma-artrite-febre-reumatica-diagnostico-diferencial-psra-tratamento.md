---
title: "Fluxograma: Artrite na Febre Reumática Aguda — Diagnóstico Diferencial com PSRA e Tratamento Anti-inflamatório"
slug: fluxograma-artrite-febre-reumatica-diagnostico-diferencial-psra-tratamento
theme: "Febre reumática"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Lacuna confirmada por grep em 'kind: fluxograma' nos 22 documentos da pasta em 26/08/2026: os 4 fluxogramas já publicados cobrem os critérios de Jones (AHA 2015), a graduação e tratamento da cardite aguda (SBC 2022), a duração/esquema da profilaxia secundária e a intervenção na valvopatia mitral crônica — nenhum trata do manejo da artrite/poliartralgia na fase aguda nem do diagnóstico diferencial com artrite reativa pós-estreptocócica (PSRA), apesar de a pasta já ter dois documentos em prosa sobre exatamente esse recorte. Árvore construída a partir desses dois documentos já publicados e revisados nesta mesma pasta — 'Tratamento da Artrite na Febre Reumática Aguda: Naproxeno como Alternativa ao AAS' (slug tratamento-da-artrite-na-febre-reumatica-aguda-naproxeno-como-alternativa-ao-aas) e 'Artrite Reativa Pós-Estreptocócica (PSRA): Diagnóstico Diferencial com a Febre Reumática' (slug artrite-reativa-pos-estreptococica-psra-diagnostico-diferencial-com-febre-reumatica) — sem alterar nenhum valor, dose ou classificação já registrados neles. Os três PMIDs centrais (14517527, 39618634, 38586781) foram reconferidos nesta sessão via PubMed E-utilities (esummary), 26/08/2026: título, revista, ano e autoria batendo exatamente com o que os documentos-fonte já citavam. O PMID da revisão dos critérios de Jones (Gewitz et al., Circulation 2015) foi confirmado via esearch como 25908771, consistente com o DOI 10.1161/CIR.0000000000000205 já usado no fluxograma de Jones publicado nesta pasta — citado aqui só como referência cruzada de escopo, sem repetir a árvore diagnóstica completa, que já está no fluxograma dedicado. Nenhum PMID/DOI novo foi inventado."
source_refs: ["Hashkes PJ, Tauber T, Somekh E, Brik R, Barash J, Mukamel M, Harel L, Lorber A, Berkovitch M, Uziel Y; Pediatric Rheumatology Study Group of Israel. Naproxen as an alternative to aspirin for the treatment of arthritis of rheumatic fever: a randomized trial. J Pediatr. 2003;143(3):399-401. PMID: 14517527 — comparação direta naproxeno x AAS na artrite da febre reumática aguda.", "Silva Veiga R, Marques M, Fonseca J, Ventura H, Silva Marques J. Acute Rheumatic Fever or Post-streptococcal Reactive Arthritis: Two Different Entities. Cureus. 2024;16(10):e72687. DOI: 10.7759/cureus.72687. PMID: 39618634 — quadro comparativo de padrão articular, latência, resposta a AINE e necessidade de ecocardiograma entre FRA e PSRA.", "Jeong SH, Shekhar N, Mutyala N, Canaday O. Distinguishing Acute Rheumatic Fever From Post-streptococcal Reactive Arthritis. Cureus. 2024;16(3):e55739. DOI: 10.7759/cureus.55739. PMID: 38586781 — relato de caso com conduta terapêutica detalhada da PSRA (naproxeno, troca para celecoxibe, corticosteroide complementar).", "Gewitz MH, Baltimore RS, Tani LY, et al. Revision of the Jones Criteria for the Diagnosis of Acute Rheumatic Fever in the Era of Doppler Echocardiography: A Scientific Statement From the American Heart Association. Circulation. 2015;131(20):1806-1818. DOI: 10.1161/CIR.0000000000000205. PMID: 25908771 — referência de escopo para os critérios de Jones, já cobertos em árvore própria no fluxograma dedicado desta pasta."]
---

# Fluxograma: Artrite na Febre Reumática Aguda — Diagnóstico Diferencial com PSRA e Tratamento Anti-inflamatório

Este fluxograma parte de um cenário comum na prática: uma criança ou adolescente
chega com poliartrite ou poliartralgia semanas depois de uma faringite
estreptocócica, e a primeira pergunta não é "qual anti-inflamatório usar", é
"isto é febre reumática aguda ou é artrite reativa pós-estreptocócica (PSRA)?"
— porque a resposta muda ecocardiograma, profilaxia secundária e prognóstico
cardíaco. O diagnóstico de febre reumática em si (critérios de Jones revisados,
AHA 2015) já tem árvore própria nesta pasta; aqui a árvore assume que o quadro
articular já está caracterizado e decide o caminho a partir do padrão de
acometimento.

Duas ressalvas importantes, herdadas dos documentos-fonte:

- A diretriz da OMS 2024 **não recomenda a favor nem contra** o uso de
  anti-inflamatório na febre reumática aguda — declina a recomendação por
  insuficiência de evidência. O ramo de tratamento anti-inflamatório deste
  fluxograma pressupõe que a decisão de tratar já foi tomada por protocolo
  local, não que ela seja obrigatória.
- O ensaio que compara naproxeno e AAS (Hashkes et al., 2003) é pequeno (33
  pacientes) e não substitui uma diretriz robusta — é a melhor evidência
  comparativa direta disponível entre os dois agentes, não uma recomendação de
  classe.

## Árvore de decisão

```mermaid
flowchart TD
    A["Poliartrite ou artralgia iniciada 1 a 5 semanas após faringite ou piodermite por Streptococcus do grupo A"] --> B{"Padrão migratório em grandes articulações, com resposta rápida e dramática a AINE, fechando os critérios de Jones revisados (AHA 2015)?"}

    B -->|"Sim, fecha Jones"| X1["Diagnóstico de febre reumática aguda confirmado (ver fluxograma dedicado de critérios de Jones 2015)"]
    X1 --> D2{"Há cardite associada, clínica ou subclínica ao Doppler?"}

    D2 -->|"Cardite moderada a grave"| C1(["Seguir o fluxograma de graduação e tratamento da cardite reumática aguda (SBC 2022); tratar a artrite com anti-inflamatório conforme a escolha abaixo, em paralelo ao manejo da cardite"])

    D2 -->|"Sem cardite ou cardite leve"| D3{"Protocolo local indica uso de anti-inflamatório para controle da artrite? (a OMS 2024 não recomenda a favor nem contra)"}

    D3 -->|"Sim, iniciar anti-inflamatório"| D4{"Prioridade é posologia mais simples e menor hepatotoxicidade?"}
    D4 -->|"Sim"| C2(["Naproxeno via oral, 2x/dia — eficácia equivalente ao AAS no controle articular (tempo médio de resolução 2,9 dias em ambos os grupos), com elevação de enzimas hepáticas significativamente menos frequente (Hashkes et al., J Pediatr 2003)"])
    D4 -->|"Não, manter esquema já em uso no serviço"| C3(["AAS em dose anti-inflamatória, 4x/dia, com monitorização de nível sérico e vigilância de hepatotoxicidade e de sinais de intoxicação salicílica"])

    D3 -->|"Não, aguardar (lacuna formal da OMS 2024)"| C4(["Observação clínica sem anti-inflamatório sistemático; reavaliação seriada da artrite e ecocardiograma de seguimento"])

    B -->|"Não fecha Jones — padrão persistente/aditivo, latência ≤10 dias, resposta parcial a AINE"| X2["Suspeita de artrite reativa pós-estreptocócica (PSRA)"]
    X2 --> D5{"Ecocardiograma já foi realizado para excluir cardite subclínica?"}

    D5 -->|"Ainda não realizado"| C5(["Solicitar ecocardiograma antes de fechar o diagnóstico de PSRA — recomendado mesmo quando o quadro parece PSRA, porque cardite subclínica é descrita, ainda que rara, nessa entidade"])

    D5 -->|"Realizado, sem cardite"| D6{"Resposta ao AINE de primeira linha (naproxeno) é adequada?"}
    D6 -->|"Sim"| C6(["Manter naproxeno até resolução; sem indicação de profilaxia antibiótica secundária de rotina — a antibioticoterapia não altera o curso da artrite na PSRA"])
    D6 -->|"Não, refratária ou alívio mínimo"| C7(["Trocar para celecoxibe (inibidor seletivo de COX-2); considerar curso curto de corticosteroide se a resposta seguir insuficiente; curso de anti-inflamatório tipicamente mais prolongado que na febre reumática; sem profilaxia secundária de rotina"])

    D5 -->|"Realizado, com cardite subclínica identificada"| C8(["Reclassificar como febre reumática atípica pelos critérios de Jones — valvulite subclínica ao Doppler é critério maior — e iniciar profilaxia secundária conforme o fluxograma dedicado desta pasta"])

    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## Notas de leitura

- **A troca de classe de AINE na PSRA (naproxeno → celecoxibe) e o corticosteroide
  complementar vêm de relato de caso, não de ensaio clínico randomizado** — onde a
  diretriz formal (ESC/AHA/SBC) não define esquema específico para PSRA, isso é
  `VERIFICAÇÃO HUMANA NECESSÁRIA` antes de virar protocolo institucional, exatamente
  como já registrado no documento de origem desta árvore.
- **A decisão sobre profilaxia secundária em casos-limite é zona cinzenta
  reconhecida na literatura** — mesmo com PSRA confirmada sem cardite, alguns
  serviços optam por profilaxia "por precaução" diante de incerteza diagnóstica
  real. Este fluxograma segue a recomendação formal (sem profilaxia de rotina em
  PSRA), mas essa prática variável está descrita no documento-fonte.
- Este fluxograma **não repete** a árvore diagnóstica completa dos critérios de
  Jones nem a graduação de gravidade da cardite — cada uma já tem fluxograma
  próprio nesta pasta, referenciado nos nós correspondentes.
