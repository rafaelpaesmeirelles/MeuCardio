# CorVIA 100 pacotes — 024/100 — revisão adversarial: Hipertensão pulmonar

Data: 29/08/2026  
Base auditada: `main` `59566e1196e0fa7f465df93516790ef454e1f565`  
Natureza: revisão clínica documental independente, sem alteração de runtime, manifesto, relações ou status editorial.

## Objeto auditado

Hub adulto `hipertensao-pulmonar`, com foco em separar recomendação formal da ESC/ERS 2022 de evidência posterior, distinguir hipertensão arterial pulmonar (HAP, grupo 1) dos demais grupos e evitar extrapolação de terapias recentes.

## Evidência crítica reconferida

- **ESC/ERS Pulmonary Hypertension 2022**, guideline formal de referência para classificação, diagnóstico e tratamento. PMID `36017548`.
- **STELLAR**, sotatercept em HAP sintomática (WHO FC II/III) sobre terapia de base estável. O endpoint primário foi mudança na distância do teste de caminhada de 6 minutos; houve benefício de aproximadamente 40,8 m em 24 semanas e melhora de múltiplos endpoints secundários. PMID `36877098`; DOI `10.1056/NEJMoa2213558`.
- **ZENITH**, sotatercept em HAP de maior risco, sobre terapia máxima tolerada. O endpoint primário composto de morte por qualquer causa, transplante pulmonar ou hospitalização por piora de HAP foi reduzido; o ensaio foi interrompido precocemente por eficácia. PMID `40167274`; DOI `10.1056/NEJMoa2415160`.
- **HYPERION**, evidência posterior em HAP diagnosticada recentemente, risco intermediário/alto e terapia de base dupla/tripla, avaliando piora clínica. PMID `41025556`; DOI `10.1056/NEJMoa2508170`.

## Achado temporal importante

O relatório de construção do hub descreve tratamento do grupo 1 em termos de **“4 classes farmacológicas”**. Isso é coerente com uma fotografia terapêutica anterior à incorporação prática da sinalização activina/sotatercept, mas pode tornar-se uma descrição incompleta em conteúdo contemporâneo.

Este pacote **não presume que o registro clínico composto atual esteja desatualizado**, porque houve produção posterior ao relatório histórico. Antes de alterar qualquer conteúdo de runtime, é obrigatório ler o estado composto vigente. O ponto registrado é uma trava temporal: sínteses futuras não devem manter uma contagem fixa de classes sem reconciliar a evidência 2023–2025 e a regulamentação/diretriz aplicável.

## Testes adversariais

1. **Sotatercept foi estudado em HAP/grupo 1, não em hipertensão pulmonar indiferenciada.** Não extrapolar STELLAR/ZENITH/HYPERION para grupos 2, 3, 4 ou 5.
2. **STELLAR não é um ensaio de mortalidade isolada.** O endpoint primário foi capacidade funcional; benefícios em outros desfechos devem ser descritos conforme hierarquia e desenho.
3. **ZENITH demonstrou forte redução do endpoint composto**, mas o resultado não deve ser transformado automaticamente em afirmação de redução isolada de mortalidade sem a devida separação dos componentes e limitação do estudo.
4. **Evidência pós-2022 não deve receber retroativamente Classe/Nível ESC/ERS 2022 inventados.** Deve ser rotulada como RCT contemporâneo posterior à guideline formal.
5. **Grupo 2 e grupo 3 exigem cautela extrema com vasodilatadores pulmonares.** Não transportar algoritmos de HAP para doença cardíaca esquerda ou doença pulmonar crônica por proximidade temática.
6. **CTEPH é uma entidade própria e tem frentes concorrentes no repositório.** Este pacote não modifica conteúdo de CTEPH para evitar colisão; mantém apenas a separação conceitual entre grupo 4 e HAP.
7. **Estratificação de risco é longitudinal.** Não reduzir decisão terapêutica a uma única classe funcional ou a um único biomarcador.

## Resultado

**Sem erro clínico bloqueante confirmado no estado documental auditado.** Foram identificados dois riscos de atualização futura:

- contagem terapêutica estática potencialmente envelhecida diante da classe activina/sotatercept;
- risco de converter resultados pós-2022 em recomendações formais ESC/ERS que a diretriz de 2022 não contém.

## Ação de produção

Nenhum arquivo clínico foi modificado. O pacote funciona como guardrail para futuras atualizações de HAP e para o mecanismo de Diretrizes/Alertas Clínicos do CorVIA.
