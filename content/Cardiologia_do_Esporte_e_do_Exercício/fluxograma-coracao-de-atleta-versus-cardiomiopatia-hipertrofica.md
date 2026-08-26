---
title: "Coração de atleta versus cardiomiopatia hipertrófica: diferenciação na zona cinzenta"
slug: fluxograma-coracao-de-atleta-versus-cardiomiopatia-hipertrofica
theme: "Cardiologia do Esporte e do Exercício"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
source_refs:
  - "Documento já publicado no acervo Corvia: coracao-de-atleta-versus-cardiomiopatia-hipertrofica-diferenciacao-na-zona-cinzenta (tema Cardiologia do Esporte e do Exercício)"
  - "Pagourelias ED, Ouzouni S, Salmatzidis P, Sargiannidis T, Tsiouli E, Ntelios D, Kouidi E, Vassilikos VP. A concise guide of contemporary cardiovascular imaging practices to differentiate athlete's heart in the gray zone. Heart Fail Rev. 2025;30(6):1215-1224. PMID: 40576890. PMCID: PMC12618444. DOI: 10.1007/s10741-025-10541-y."
  - "Wiradinata W, Aditya MR, Subali AD, Lestari H, Hardani RB, Mukti NH. Distinguishing athlete's heart from hypertrophic cardiomyopathy by ECG features in the pediatric population: a systematic review and meta-analysis. Eur J Pediatr. 2025;184(12):802. PMID: 41313487. DOI: 10.1007/s00431-025-06657-w."
  - "Deligiannis A, Bompotis G, Deligiannis P, Anifanti M, Kouidi E. Artificial intelligence in the differential diagnosis of hypertrophic cardiomyopathy and physiological hypertrophy: a scoping review. Hellenic J Cardiol. 2026 May 15. PMID: 42142808. DOI: 10.1016/j.hjc.2026.05.001."
---

# Coração de atleta versus cardiomiopatia hipertrófica: diferenciação na zona cinzenta

## Árvore de decisão

```mermaid
flowchart TD
    A["Atleta com hipertrofia ventricular esquerda em zona de sobreposição entre coração de atleta e cardiomiopatia hipertrófica"] --> D1{"O ECG de repouso mostra achados mais prevalentes em cardiomiopatia hipertrófica (QTc prolongado, alteração de onda T ou de segmento ST, onda Q patológica — sobretudo em atleta jovem)?"}
    D1 -->|"Não, ECG compatível com adaptação fisiológica"| D2{"O ecocardiograma com avaliação de deformação miocárdica (strain) sugere padrão fisiológico ou patológico?"}
    D2 -->|"Padrão fisiológico"| C1(["Considerar remodelamento compatível com coração de atleta; manter reavaliação periódica, sem restrição esportiva"])
    D2 -->|"Padrão patológico ou inconclusivo"| C2(["Escalonar para ressonância magnética cardíaca para diferenciação estrutural mais detalhada antes de decidir a participação esportiva"])
    D1 -->|"Sim, achados sugestivos de cardiomiopatia hipertrófica"| D3{"O ecocardiograma com deformação miocárdica confirma padrão patológico?"}
    D3 -->|"Sim"| C3(["Tratar como suspeita de cardiomiopatia hipertrófica: investigação estrutural completa com ressonância magnética cardíaca e avaliação especializada antes de qualquer liberação esportiva"])
    D3 -->|"Não, ecocardiograma inconclusivo ou discordante do ECG"| C4(["Escalonar para ressonância magnética cardíaca para resolver a discordância entre ECG e ecocardiograma antes de decidir a participação"])

    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C1,C2,C3,C4 conduta;
```

## Critérios usados na árvore

O documento de origem reúne três fontes (Pagourelias et al., *Heart Fail Rev*. 2025, PMID 40576890; Wiradinata et al., *Eur J Pediatr*. 2025, PMID 41313487; Deligiannis et al., *Hellenic J Cardiol*. 2026, PMID 42142808) e conclui que **nenhuma das três propõe um critério único e definitivo**. O padrão que emerge de forma consistente entre elas é uma abordagem **multimodal e hierárquica**: ECG de repouso como primeira triagem, seguido de imagem cardíaca estruturada (ecocardiografia com deformação miocárdica, escalando para ressonância magnética cardíaca quando a dúvida persistir).

Os achados eletrocardiográficos usados na árvore vêm da metanálise pediátrica de Wiradinata et al. (25 estudos), que encontrou diferenças significativas — mais prevalentes no grupo com cardiomiopatia hipertrófica do que na adaptação fisiológica do atleta jovem — em **prolongamento do intervalo QTc**, **alterações de onda T e do segmento ST** e **ondas Q patológicas** (achados complementares, de estudos de braço único, também apontaram diferença em desvio de eixo, aumento atrial e bloqueios de ramo). A própria metanálise recomenda que uma alteração de ECG detectada deve **motivar investigação adicional**, nunca servir como critério diagnóstico definitivo isolado — por isso a árvore nunca resolve o caso só pelo ECG, sempre escalando para imagem.

A escolha de escalonar para ecocardiografia com avaliação de deformação miocárdica (strain), com possível escalonamento adicional para ressonância magnética cardíaca, segue o guia de imagem multimodal de Pagourelias et al., que descreve a imagem cardiovascular como processo central para diferenciar fenótipos normais de anormais na zona cinzenta.

**Não foram usados cortes numéricos de espessura parietal, diâmetro de câmara ou função diastólica** nesta árvore, porque o próprio documento de origem registra que esses limiares específicos, citados no guia de Pagourelias et al., não estão detalhados no resumo indexado da fonte e exigem **verificação humana** contra o texto completo antes de aplicação clínica — incluí-los aqui seria fabricar um dado que a fonte primária publicada no acervo explicitamente não fornece. A inteligência artificial, mencionada na terceira fonte (Deligiannis et al.) como ferramenta emergente com apenas 1 de 8 estudos comparando diretamente contra coração de atleta (AUC 0,93), não entrou na árvore por ainda não ser considerada validada especificamente para esta população pela própria fonte.