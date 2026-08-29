# CorVIA 100 pacotes — 022/100 — revisão adversarial: Endocardite infecciosa

Data: 29/08/2026  
Base auditada: `main` `59566e1196e0fa7f465df93516790ef454e1f565`  
Natureza: revisão clínica documental independente, sem alteração de runtime, manifesto, relações ou status editorial.

## Objeto auditado

O hub adulto `endocardite-infecciosa` e o respectivo relatório de construção Tudo com Tudo. O acervo já possui alta densidade de conteúdo e vínculos diretos; portanto o objetivo deste pacote não é adicionar links, e sim testar extrapolações perigosas e coerência temporal das evidências.

## Evidência crítica reconferida

- **ESC Endocarditis 2023**, guideline vigente da ESC para manejo de endocardite, com corrigendum posterior que deve acompanhar a referência corrente quando aplicável. PMID `37622656`.
- **POET**, ensaio randomizado de troca parcial para antibiótico oral em pacientes **selecionados e clinicamente estáveis** com endocardite esquerda. PMID `30152252`; DOI `10.1056/NEJMoa1808312`.
- **POET, seguimento de 5 anos**, que sustenta a durabilidade da estratégia na população selecionada do ensaio, sem converter essa população em regra universal. PMID `35139280`; DOI `10.1056/NEJMc2114046`.
- **EASE / Early Surgery**, ensaio randomizado em pacientes selecionados com endocardite esquerda, doença valvar grave e vegetações grandes; o benefício do desfecho composto precoce foi fortemente relacionado à prevenção de eventos embólicos, sem demonstrar licença para cirurgia precoce indiscriminada em toda endocardite. PMID `22738096`; DOI `10.1056/NEJMoa1112843`.
- **Duke-ISCVID 2023**, critérios diagnósticos contemporâneos. PMID `37138445`.

## Testes adversariais

1. **POET não equivale a “tratamento oral para toda endocardite”.** Qualquer síntese deve preservar estabilidade clínica, seleção microbiológica/estrutural, avaliação por equipe experiente e fase inicial parenteral conforme o protocolo/estratégia aplicável.
2. **EASE não equivale a “operar toda endocardite em até 48 horas”.** A população foi altamente selecionada; indicação cirúrgica continua dependente de insuficiência cardíaca, infecção não controlada, prevenção de embolia e contexto anatômico/microbiológico.
3. **Não transformar redução de embolia em benefício de mortalidade não demonstrado.** Desfecho composto e seus componentes devem permanecer separados.
4. **Profilaxia antibiótica deve permanecer restrita às categorias de alto risco definidas pela diretriz vigente.** Não ampliar por analogia a grupos não contemplados.
5. **Prótese/dispositivo/TAVI exigem distinção diagnóstica e de estratégia.** Não tratar infecção de bolsa isolada, endocardite de eletrodo e endocardite valvar como entidades intercambiáveis.
6. **Citações ESC devem apontar para a versão corrente/corrigida quando pertinente.** Não perpetuar tabela ou redação sabidamente corrigida apenas porque aparece em documento histórico do corpus.

## Resultado

**Sem erro clínico bloqueante identificado no escopo documental revisado.** O hub é denso e já possui guardrails relevantes. O principal risco é de simplificação excessiva de estudos de seleção estrita, especialmente POET e EASE.

### Guardrails que devem permanecer explícitos

- POET: somente população selecionada/estável; não generalizar para bacteremia persistente, complicação não controlada ou cenários fora dos critérios da estratégia estudada.
- EASE: cirurgia precoce em contexto selecionado; não vender o ensaio como benefício universal de mortalidade.
- Critérios Duke-ISCVID auxiliam diagnóstico, mas não substituem julgamento clínico, microbiologia, imagem multimodal e Heart/Endocarditis Team.
- Nenhuma conclusão de um estudo individual deve substituir a estratificação por indicação cirúrgica formal da diretriz.

## Ação de produção

Nenhum arquivo clínico foi modificado neste pacote. O resultado deve servir como trava para futuras sínteses, cards, IA clínica e materiais Tudo com Tudo relacionados a endocardite.
