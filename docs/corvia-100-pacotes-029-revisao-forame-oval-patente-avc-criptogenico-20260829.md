# CorVIA 100 pacotes — 029/100 — revisão adversarial: Forame oval patente e AVC criptogênico

Data: 29/08/2026  
Base auditada: `main` `59566e1196e0fa7f465df93516790ef454e1f565`  
Natureza: revisão clínica documental independente, sem alteração de runtime, manifesto, relações ou status editorial.

## Objeto auditado

Eixo de forame oval patente (FOP) e prevenção secundária após AVC isquêmico criptogênico, com foco em atribuição causal, seleção para fechamento percutâneo e prevenção de automação indevida do raciocínio “FOP encontrado = fechar”.

## Evidência crítica reconferida

- **RESPECT — seguimento estendido**, fechamento de FOP versus tratamento médico em pacientes de 18–60 anos com AVC isquêmico criptogênico e FOP. DOI `10.1056/NEJMoa1610057`.
- **REDUCE**, fechamento de FOP associado a terapia antiplaquetária versus terapia antiplaquetária isolada em pacientes selecionados com AVC criptogênico e FOP. PMID `28902580`; DOI `10.1056/NEJMoa1707404`.
- **CLOSE**, pacientes de 16–60 anos com AVC recente atribuído ao FOP e características anatômicas de maior risco, incluindo aneurisma do septo atrial ou grande shunt. DOI `10.1056/NEJMoa1705915`.

## Testes adversariais

1. **FOP é frequente na população e muitas vezes incidental.** A simples presença anatômica não demonstra causalidade do AVC.
2. **Os RCTs de fechamento estudaram pacientes selecionados, em geral jovens, com AVC isquêmico criptogênico após investigação adequada.** Não extrapolar automaticamente para qualquer TIA, cefaleia, achado incidental ou paciente idoso.
3. **Antes de atribuir causalidade ao FOP, excluir mecanismos alternativos relevantes.** Fibrilação atrial, aterosclerose, doença de pequenos vasos, dissecção, trombofilia/contexto venoso e outras fontes embólicas podem mudar completamente a estratégia.
4. **RoPE/PASCAL são ferramentas de atribuição/probabilidade, não gatilhos autônomos de fechamento.** Não converter escore em indicação automática.
5. **Grande shunt e aneurisma do septo atrial aumentam plausibilidade causal, mas não substituem contexto clínico e neurológico.**
6. **Fechamento reduz recorrência de AVC em populações selecionadas, mas introduz riscos procedimentais e maior ocorrência de fibrilação atrial em alguns estudos.** Benefício e dano devem ser apresentados juntos.
7. **Não transportar o benefício observado em pacientes até aproximadamente 60 anos para faixas etárias mais altas sem evidência específica.** A probabilidade de mecanismos alternativos cresce com a idade.
8. **“AVC criptogênico” não é sinônimo de investigação incompleta.** O conceito exige avaliação adequada antes de considerar o FOP como mecanismo provável.

## Resultado

**Sem erro clínico bloqueante confirmado no escopo documental auditado.** O principal risco para a IA clínica é um atalho causal: identificar FOP em um paciente com evento neurológico e recomendar fechamento sem demonstrar que o FOP é provavelmente causal.

### Guardrail central

O fluxo assistido deve ser:

`AVC isquêmico confirmado → investigação etiológica adequada → exclusão de causas alternativas relevantes → avaliação de plausibilidade causal do FOP → discussão neurocardiológica do fechamento`.

Nunca: `FOP + sintoma neurológico = fechamento`.

## Ação de produção

Nenhum arquivo clínico foi modificado. Este pacote deve orientar futuras integrações entre Guia de Doenças, AVC, ecocardiografia, monitorização de ritmo, tromboembolismo, calculadoras de atribuição e decisão compartilhada.
