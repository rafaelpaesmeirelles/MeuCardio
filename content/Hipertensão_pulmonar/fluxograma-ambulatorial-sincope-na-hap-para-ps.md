---
title: "Fluxograma ambulatorial: síncope na HAP — quando ir ao PS"
slug: fluxograma-ambulatorial-sincope-na-hap-para-ps
theme: "Hipertensão pulmonar"
kind: fluxograma
fonte_producao: grok
summary: "Árvore de consultório: síncope ou pré-síncope em paciente com HAP/HP pré-capilar conhecida — gate de segurança para pronto-socorro vs observação apenas se claramente vasovagal sem esforço e com reavaliação imediata planejada. Sem doses."
review_status: pendente_revisao
review_note: "Irmão do pacote CTEPH/falência VD além #841 (07/09/2026). #841 cita síncope como red flag; este fluxograma densifica o destino PS. ESC/ERS 2022 PMID 36017548."
source_refs:
  - "Humbert M, Kovacs G, Hoeper MM, et al; ESC/ERS Scientific Document Group. 2022 ESC/ERS Guidelines for the diagnosis and treatment of pulmonary hypertension. Eur Heart J. 2022;43(38):3618-3731. DOI: 10.1093/eurheartj/ehac237. PMID: 36017548"
  - "Corpus MeuCardio: hipertensao-pulmonar-diagnostico-e-tratamento-escers-2022.md; estratificacao-de-risco-e-terapia-combinada-inicial-na-hipertensao-arterial-pulmonar.md; escore-reveal-2-0-estratificacao-de-risco-e-sobrevida-na-hap.md; sinalizadores-ambulatoriais-falencia-de-vd-na-hp.md."
---

# Fluxograma ambulatorial: síncope na HAP — quando ir ao PS

Prosa de falência direita: [`sinalizadores-ambulatoriais-falencia-de-vd-na-hp`](sinalizadores-ambulatoriais-falencia-de-vd-na-hp.md). Suspeita de CTEPH: [`sinalizadores-ambulatoriais-suspeita-de-cteph-quando-referenciar`](sinalizadores-ambulatoriais-suspeita-de-cteph-quando-referenciar.md).

Na estratificação ESC/ERS 2022, **síncope** é marcador de **alto risco** na HAP. No consultório, isso quase nunca é "ajuste de agenda".

## Árvore de decisão

```mermaid
flowchart TD
  R0["Retorno / demanda: paciente com HAP ou HP pré-capilar<br/>relata síncope ou pré-síncope"] --> D0{"Episódio relacionado a esforço<br/>ou em pé / caminhada / subir escada?"}

  D0 -->|"Sim — esforço ou ortostatismo de esforço"| C0(["PS / urgência AGORA<br/>Contatar centro de HP<br/>Não liberar para retorno eletivo"])

  D0 -->|"Não claro / em repouso"| D1{"Há sinais de falência de VD,<br/>hipotensão, hemoptise, confusão<br/>ou trauma craniano?"}

  D1 -->|"Sim"| C0

  D1 -->|"Não"| D2{"História tipicamente reflexa<br/>(prolongado em pé, calor, náusea prodômica)<br/>SEM esforço e SEM HP descompensada?"}

  D2 -->|"Dúvida"| C1(["Tratar como alto risco até prova em contrário<br/>PS ou observação com suporte<br/>+ contato com centro de HP"])

  D2 -->|"Muito típico reflexo E estável"| C2(["Exceção estreita: observação breve<br/>Reavaliação em horas/1 dia<br/>Orientação escrita: novo episódio → PS<br/>Avisar centro de HP no mesmo dia"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  classDef neutro fill:#eef2f7,stroke:#3d5a80,color:#102a43;
  class C0,C1 alerta;
  class C2 neutro;
```

## Notas

- **D0**: síncope de esforço na HAP = alarme clássico de alto risco / baixo débito sob pós-carga — destino padrão é **PS**, não "marcar eco na semana que vem".
- **D1**: acopla ao checklist de falência de VD; qualquer sinal de descompensação fecha a porta da observação eletiva.
- **D2/C2**: exceção **estreita** para quadro tipicamente reflexo sem esforço; ainda assim exige contato com o centro e plano escrito de retorno ao PS. Na dúvida, escolher C0/C1.
- Este fluxograma **não** diferencia causas neurológicas/arrítmicas detalhadas — no paciente com HAP, a prioridade ambulatorial é **não subestimar** o significado prognóstico da síncope.
- Não inventa doses, titulação nem indicação de dispositivo.
