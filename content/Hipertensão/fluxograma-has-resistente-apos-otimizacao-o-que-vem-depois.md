---
kind: fluxograma
published: true
review_note: Conferidos PATHWAY-2, TARGET/ADVANCE/LAUNCH e KARDIA conforme o conteúdo;
  corrigidos elegibilidade e segurança dos fluxogramas, doses ADVANCE, distinção entre
  eventos atribuídos e totais, atualização KARDIA-3 e situação regulatória sem alegação
  de aprovação brasileira.
review_status: revisado
slug: fluxograma-has-resistente-apos-otimizacao-o-que-vem-depois
source_refs:
- 'McEvoy JW, McCarthy CP, Bruno RM, et al.; ESC Scientific Document Group. 2024 ESC
  Guidelines for the management of elevated blood pressure and hypertension. Eur Heart
  J. 2024 Oct 7;45(38):3912-4018. DOI: 10.1093/eurheartj/ehae178. PMID: 39210715.'
- 'Jones DW, Ferdinand KC, Taler SJ, et al. 2025 AHA/ACC/AANP/AAPA/ABC/ACCP/ACPM/AGS/AMA/ASPC/NMA/PCNA/SGIM
  Guideline for the Prevention, Detection, Evaluation, and Management of High Blood
  Pressure in Adults. J Am Coll Cardiol. 2025;86(18):1567-1678. DOI: 10.1016/j.jacc.2025.05.007.
  PMID: 40815242. Também Circulation. 2025;152:e114-e218. DOI: 10.1161/CIR.0000000000001356.'
- 'Williams B, MacDonald TM, Morant S, Webb DJ, Sever P, McInnes G, Ford I, Cruickshank
  JK, Caulfield MJ, Salsbury J, Mackenzie I, Padmanabhan S, Brown MJ; British Hypertension
  Society''s PATHWAY Studies Group. Spironolactone versus placebo, bisoprolol, and
  doxazosin to determine the optimal treatment for drug-resistant hypertension (PATHWAY-2):
  a randomised, double-blind, crossover trial. Lancet. 2015 Nov 21;386(10008):2059-2068.
  DOI: 10.1016/S0140-6736(15)00257-3. PMID: 26414968. PMCID: PMC4655321.'
theme: Hipertensão
title: 'Fluxograma: HAS resistente após otimização — o que vem depois'
---

# Fluxograma: HAS resistente após otimização — o que vem depois

Árvore qualitativa para o adulto com **pressão aparentemente não controlada em três classes**. A lógica segue as diretrizes ESC 2024 e AHA/ACC 2025: confirmar resistência verdadeira, excluir pseudo-resistência, otimizar a tríade (tiazida-like + IECA ou BRA + bloqueador de cálcio) e, então, adicionar antagonista do receptor mineralocorticoide — espironolactona como próximo passo usual. **Esta ficha não atribui Classe/COR aos nós.** Números de Classe saem das diretrizes, não desta árvore.

Zilebesiran e lorundrostat, se aparecerem no fim, estão **rotulados como investigacionais**. Não são padrão de cuidado.

## Árvore de decisão

```mermaid
flowchart TD
 A["Adulto não gestante com PA alta em três classes; excluir emergência"] --> B{"Resistência verdadeira confirmada?"}
 B -->|Não| C(["Corrigir técnica, adesão, interferentes e avaliar avental branco"])
 B -->|Sim| D["Investigar causas secundárias; otimizar tríade e diurético conforme função renal"]
 D --> E{"PA ainda elevada e elegível para ARM após avaliar TFGe e potássio?"}
 E -->|Controlada| F(["Manter e monitorar"])
 E -->|Contraindicação ao ARM| G(["Escolher alternativa em centro especializado; não substituir automaticamente por eplerenona"])
 E -->|Sim| H["Adicionar espironolactona e monitorar potássio e função renal"]
 H --> I{"Resposta e tolerância?"}
 I -->|Controlada e tolerada| J(["Manter e reavaliar"])
 I -->|Intolerância endócrina com função renal e potássio adequados| K(["Considerar eplerenona ou outra opção individualizada"])
 I -->|Hipercalemia, disfunção renal ou persistência do descontrole| L(["Reavaliar segurança e encaminhar a centro de HAS; dispositivo apenas se elegível e após decisão compartilhada"])
 classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
 class C,F,G,J,K,L conduta;
```

Suspeita de emergência hipertensiva exige atendimento imediato; este percurso é ambulatorial. A investigação de hiperaldosteronismo deve ser considerada antes do ARM, quando viável, pois este interfere na avaliação.

## Como ler cada ramo

**Confirmar resistência verdadeira.** PA de consultório alta em três classes, nas doses máximas toleradas, **não basta**. Confirmar fora do consultório (MAPA ou MRPA). ESC 2024 define resistência quando diurético (tiazida ou tiazida-like) + bloqueador do SRA + bloqueador de cálcio falham em baixar a PA de consultório a <140/90 mmHg, com confirmação fora do consultório. AHA/ACC 2025 trabalha com a tríade IECA/BRA + BCC + tiazida-like (clortalidona ou indapamida). Com TFGe baixa, o diurético de alça entra na definição — detalhe de diretriz, não inventado aqui.

**Excluir pseudo-resistência.** Técnica (manguito, posição, repouso), adesão (incluindo combinação em pílula única quando possível), hipertensão do avental branco e fármacos interferentes (AINE, descongestionantes, simpaticomiméticos, glicocorticoide, eritropoetina, entre outros). Enquanto a pseudo-resistência não foi excluída, **não** se rotula o caso como resistente verdadeira e **não** se avança para o quarto fármaco por esse rótulo.

**Otimizar as três classes.** Tiazida-like (indapamida ou clortalidona, conforme a diretriz em uso) + IECA ou BRA + bloqueador de cálcio di-hidropiridínico, nas doses máximas toleradas. Hidroclorotiazida em dose baixa, sem tiazida-like, **não** fecha a tríade. Sem essa otimização, o próximo nó não se aplica.

**Adicionar ARM.** Espironolactona é o próximo passo **usual** na resistência verdadeira. PATHWAY-2 (PMID **26414968**) mostrou superioridade da espironolactona 25–50 mg sobre placebo, doxazosina e bisoprolol na PAS domiciliar — ensaio de pressão, não de MACE. Potássio e TFGe limitam o uso; a AHA/ACC 2025 condiciona o ARM a TFGe ≥45 mL/min/1,73 m² no recorte de resistência. Em intolerância endócrina, eplerenona pode ser discutida se potássio e função renal permitirem; hipercalemia ou contraindicação renal exigem outra estratégia — sem hierarquia numérica nesta árvore.

**Derivar, secundária, dispositivo.** Encaminhar a centro experiente. Rastrear hiperaldosteronismo primário mesmo sem hipocalemia (mensagem da AHA/ACC 2025). Denervação renal: opção em **selecionados**, após decisão compartilhada, em centro com volume, **não** atalho para quem ainda não otimizou tríade e ARM.

**Investigacionais.** Zilebesiran (KARDIA, PAS ambulatória, fase 2) e lorundrostat (Target-HTN, Launch-HTN, Advance-HTN — PAS, não MACE) **não** substituem o ARM aprovado. Se o paciente pergunta, o rótulo é ensaio.

Nós verdes (estádio) são condutas. Losangos são decisões. Cada nó tem um único pai: quando a mesma ideia reaparece, o texto se repete em vez de fechar um ciclo.

## Tudo com Tudo

- **Hipertensão:** esta árvore começa **depois** de três classes otimizadas; não substitui o início de fármaco nem a meta.
- **Farmacologia:** ARM (receptor) ≠ inibidor da sintase da aldosterona ≠ siRNA contra angiotensinogênio. Só o primeiro é o passo usual hoje.
- **Cardiorrenal:** TFGe e potássio decidem se o ARM cabe; DRC avançada muda o diurético da tríade.
- **Prevenção e lipídios:** controlar a PA resistente reduz risco; este fluxograma não escolhe estatina.
- **Comunicação clínica:** “o quarto comprimido com evidência hoje é a espironolactona; os novos estão em ensaio.” Ver [Como conversar HAS resistente e ensaios de novos fármacos](/biblioteca/como-conversar-has-resistente-e-ensaios-de-novos-farmacos).
