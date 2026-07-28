# Briefing de implementação — MeuCardio (parte 2)

Continuação do `BRIEFING_CLAUDE_CODE.md`. As regras transversais definidas lá (nunca inventar dado clínico, sinalizar "VERIFICAÇÃO HUMANA NECESSÁRIA" onde não houver certeza, dado de saúde exige storage seguro e LGPD, nunca simular etapa que depende de credencial externa, apresentar plano antes de executar tarefa grande) valem integralmente para tudo abaixo. Não repetir aqui não significa que deixaram de valer.

Numeração continua a partir da Tarefa 7 já em execução.

---

## 8. Checador de interação medicamentosa

Nova funcionalidade dentro do módulo Medicamentos já existente: o médico monta uma lista de fármacos (os que o paciente já usa + o que está prescrevendo) e o sistema aponta interações relevantes entre eles.

- Reaproveitar a base de Medicamentos já estruturada — não recriar do zero.
- Cada interação apontada precisa vir com classificação de gravidade e a fonte que a sustenta (bulário, diretriz ou estudo), seguindo o mesmo padrão de rastreabilidade do resto do conteúdo.
- Onde não houver uma fonte confiável para uma combinação específica, não incluir a interação — melhor a lista ficar incompleta do que ter um dado inventado.

## 9. Alerta de atualização de diretriz

Quando uma diretriz que embasa um protocolo, medicamento ou calculadora já publicado é revisada (nova versão ESC, AHA/ACC ou SBC), o sistema deve notificar os usuários que utilizam aquele conteúdo.

- Precisa de um campo de "diretriz de origem" e "versão/ano" já vinculado a cada item de conteúdo — se esse vínculo não existir hoje de forma estruturada, é pré-requisito desta tarefa criá-lo antes da notificação em si.
- O alerta é sobre a diretriz ter mudado, não sobre o conteúdo do MeuCardio já estar desatualizado — são coisas diferentes. Enquanto o conteúdo não for revisado internamente (o que continua exigindo checkpoint humano, como em qualquer atualização de conteúdo clínico), o alerta apenas avisa que há uma revisão publicada a ser considerada.

## 10. Painel de indicadores pessoais

Tela para o próprio médico acompanhar sua atividade na plataforma: quantidade de laudos/consultorias emitidos no mês, tempo médio de resposta frente ao SLA prometido, e receita gerada pelo telediagnóstico no período.

- Os dados já existem (fila de atendimento, `service_orders`, pagamentos via Stripe) — esta tarefa é de agregação e visualização, não de captura de dado novo.
- Não expor esse painel para outros usuários além do próprio médico dono dos dados.

## 11. Educação médica continuada

Duas frentes, reaproveitando o conteúdo já verificado na Fase B (protocolos, farmacologia, biblioteca científica) — não é uma frente de conteúdo novo do zero:

**11a. Casos clínicos interativos.** Um caso (anonimizado, sem dado real de paciente) é apresentado, o usuário decide a conduta, o sistema mostra a conduta correta com a evidência que a sustenta. Todo caso precisa ser fictício ou anonimizado de forma irreversível — nunca um caso real identificável.

**11b. Trilhas de estudo por tema.** Sequência guiada de conteúdo já existente (ex.: trilha de Insuficiência Cardíaca reunindo o protocolo, a farmacologia relacionada, os estudos pivotais e as calculadoras pertinentes, nessa ordem). É essencialmente curadoria/organização do que já existe, não criação de conteúdo novo.

Considerar, ao desenhar essas duas frentes, se fazem sentido como parte da assinatura atual ou como um produto/preço à parte — não decidir isso sozinho, apresentar as opções no plano antes de implementar.

## 12. Material educativo para o paciente

A partir do conteúdo já curado sobre uma condição (ex.: fibrilação atrial, insuficiência cardíaca), gerar um documento simples e em linguagem acessível que o médico possa entregar ao paciente explicando a condição.

- Linguagem para leigo, não para médico — isso é uma reescrita de registro, não uma cópia do conteúdo técnico existente.
- Gerar como PDF, no mesmo padrão de geração de documento já usado na Tarefa 4.
- Este material é educativo, não prescritivo — não deve conter dose, conduta ou recomendação terapêutica individualizada, apenas explicação da condição em si.

## 13. Leitura assistida de ECG por IA — v1, escopo Classe I/II

Decisão tomada: construir agora uma v1 desta funcionalidade, deliberadamente limitada ao que se enquadra em Classe I/II da ANVISA (regime de notificação, não registro), para poder lançar em prazo curto. Sugestão de diagnóstico ou causa provável **fica fora desta versão** — é visão de v2 futura, condicionada a um processo de registro Classe III/IV que ainda não foi iniciado.

**O que a v1 pode fazer:**
- Digitalizar e estruturar o traçado a partir da foto/PDF enviado (sem interpretação clínica).
- Controle de qualidade técnica do exame: identificar ruído, traçado incompleto, derivação ausente ou mal posicionada.
- Comparação histórica: mostrar o ECG atual lado a lado com exames anteriores do mesmo paciente, sem apontar automaticamente o que mudou.
- Ferramenta de anotação manual: o médico marca achados na tela (a IA não marca nada sozinha) — reaproveitável nos casos clínicos interativos da Tarefa 11a.
- Medição automática de parâmetros objetivos: frequência cardíaca, intervalos PR/QRS/QT, QTc pela fórmula padrão — sempre exibidos como número calculado, nunca como classificação de risco ou recomendação de conduta.
- Assistente de referência: o médico digita o achado que ele próprio identificou, e o sistema busca conteúdo relacionado já existente na plataforma (protocolos, diretrizes) — quem interpreta o traçado continua sendo o médico, a IA só busca no que já está indexado.

**O que fica de fora da v1, mesmo parecendo pequeno:**
- Qualquer texto que aponte causa provável, hipótese diagnóstica, ou classificação de risco derivada do traçado.
- Estruturação automática de laudo por ditado/voz — o CFM já trata isso como risco intermediário, não incluir sem checagem própria.
- Qualquer função de realce/marcação automática (feita pela IA, não pelo médico) quando o resultado alimenta diretamente um laudo — a própria ANVISA já esclareceu que isso caracteriza dispositivo médico regulável, mesmo sem sugerir diagnóstico.

Em caso de dúvida se uma função específica ainda cabe no escopo acima, marcar como pendente e não implementar — não presumir a favor de incluir.

## 13b. Notificação da v1 na ANVISA (Classe I/II)

Vamos seguir com o registro/notificação desta funcionalidade — vale a pena, é uma ferramenta que faz diferença real. Isso corre em paralelo ao desenvolvimento da 13, não depois dele.

- Preciso que você monte o dossiê técnico exigido pela RDC 657/2022 para o regime de notificação (classes I e II): informação técnica do software, lista de modelos/componentes, e um arquivo de gerenciamento de risco (a referência de mercado para isso é a ISO 14971 — se o projeto ainda não tem esse tipo de documento para nenhuma outra parte do sistema, será o primeiro).
- Preciso também das instruções de uso e rotulagem no formato que a RDC exige, cobrindo exatamente o escopo definido acima (não pode prometer, no texto de rotulagem, nada que a função não faça — isso é o tipo de inconsistência que a própria Anvisa audita).
- Antes de submeter qualquer coisa à ANVISA, monte um resumo do dossiê para eu revisar — com apoio de um profissional especializado em regulatório de dispositivo médico, que ainda vou contratar separadamente. Isso não sai sem essa revisão.
- Deixe claro, junto ao dossiê, exatamente quais das funções listadas no escopo da Tarefa 13 estão de fato implementadas em cada submissão — não notificar função que ainda não existe.

Além da ANVISA, essa funcionalidade também precisa atender à Resolução CFM nº 2.454/2026, sobre uso clínico de IA — isso é adicional à notificação, não substitui:
- Log auditável por análise: qual modelo e versão processou aquele ECG, o que foi calculado/exibido.
- Interface com tempo e contexto reais para o médico revisar (nunca um fluxo que "passa" a menos que o médico interrompa).
- Texto de consentimento informando o paciente quando o uso de IA influencia materialmente a conduta — se o TCLE do telediagnóstico (Tarefa 5) puder ser estendido para cobrir isso, reaproveite; se não, sinalize a necessidade de um texto próprio para eu revisar.

## 15. Modo Emergência

Uma interface separada do resto do sistema, desenhada especificamente para o momento de pressão real — não mais uma tela de consulta entre várias, e sim um modo com regras próprias de design:

- Acesso em no máximo 1-2 toques a partir de qualquer lugar do sistema (ex.: botão fixo sempre visível, não escondido em menu).
- Conteúdo restrito aos protocolos de risco imediato de vida já existentes e já verificados na Fase B — PCR/RCP, síndrome coronariana aguda, choque cardiogênico, taquiarritmia instável, entre outros que se encaixem nesse critério. Esta tarefa é de **redesenho e filtragem** do conteúdo já existente, não de criação de conteúdo novo — não escrever protocolo novo para esta tarefa.
- Fonte grande, alto contraste, o mínimo de rolagem possível até a informação crítica — a prioridade de design aqui é velocidade de leitura sob estresse, não densidade de informação.
- Precisa funcionar 100% offline, já que é exatamente na hora de uma emergência que a conexão pode falhar — reforçar que essa tela em especial não pode depender de chamada de rede para o conteúdo já baixado.

## 16. Modo Apresentação/Ensino

Exportar qualquer protocolo, caso clínico ou fluxograma já existente na plataforma em formato pronto para uso em aula ou round de residência (slide ou PDF apresentável).

- Reaproveitar o conteúdo já existente — esta tarefa é de formatação/exportação, não de criação de conteúdo.
- Gerar no mesmo padrão visual da marca (paleta da Tarefa 1), pronto para abrir direto numa tela de projeção.
- Permitir que o médico adicione uma anotação própria antes de exportar (por exemplo, uma observação para aquele round específico), sem alterar o conteúdo original verificado.

## 18. Checklist de alta pós-evento cardiovascular

Lista estruturada do que não pode faltar na alta de uma internação por evento/doença cardíaca — cobrindo os cenários já existentes como protocolo na plataforma (pós-IAM, IC descompensada, arritmia, entre outros), não só um único tipo de evento.

- Reaproveitar o conteúdo já verificado dos protocolos existentes — os itens do checklist (classes de medicação, orientações, agendamento de retorno) devem vir do protocolo correspondente, não ser escritos do zero.
- Cada protocolo pode ter um checklist de alta próprio, já que os itens variam por condição — estruturar de forma que dê para adicionar checklist a um protocolo novo sem redesenhar a funcionalidade.
- O médico deve poder marcar item por item e ver o que falta antes de finalizar a alta — não é só uma lista estática de leitura.

## 19. Alerta de contraindicação por situação clínica especial

Diferente do Checador de Interação Medicamentosa (Tarefa 8, que é fármaco × fármaco): aqui o alerta é fármaco ou exame × condição do paciente — por exemplo, contraste em paciente com doença renal crônica, anticoagulante em gestante, determinado fármaco em insuficiência hepática.

- Reaproveitar a base de Medicamentos e Exames já existente — adicionar a esses registros, onde a fonte permitir confirmar com segurança, as contraindicações por condição especial relevante.
- Mesma regra de sempre: onde não houver fonte confiável para uma contraindicação específica, não incluir — marcar como pendente em vez de supor.
- O médico informa as condições especiais relevantes do paciente (ex.: gestante, DRC, hepatopatia) e o sistema cruza com o que está prestes a ser prescrito ou solicitado.

## 20. Roteiro de conversa difícil

Um roteiro estruturado de apoio para conduzir conversas de prognóstico reservado ou más notícias em cardiologia — por exemplo, diante de insuficiência cardíaca avançada ou indicação de cuidados paliativos.

- Este conteúdo é sobre **como conduzir a conversa** com o paciente/família, não sobre explicar a doença em si — isso já é o papel do Material Educativo para o Paciente (Tarefa 12). Não misturar as duas finalidades num único conteúdo.
- Por não ser um conteúdo de tratamento/dose, a exigência de fonte aqui é diferente do resto do sistema — vale se apoiar em literatura de comunicação em saúde/cuidados paliativos estabelecida, e isso deve ficar explícito na origem do conteúdo, mas não precisa (nem faz sentido) citar diretriz de cardiologia para isso.
- Formato sugerido: estrutura em etapas (abertura, entrega da informação, checagem de entendimento, próximos passos), não um texto corrido — mais fácil de seguir no momento real da conversa.

## 21. Atualizar o Painel principal — segunda passada

A Tarefa 6 já reformulou o Painel para dar acesso rápido às funções existentes. Agora que a lista de funcionalidades cresceu, atualizar essa mesma tela para refletir tudo — incluindo as novas desta rodada, mesmo as que ainda estão em desenvolvimento (marcadas como "em breve" quando ainda não estiverem prontas).

Esta tela é a primeira impressão do sistema — o objetivo é que, ao abrir o Painel, a pessoa tenha a sensação imediata de estar diante de uma plataforma extremamente completa, não de uma lista burocrática de links.

- Cada funcionalidade em destaque, com nome, uma descrição curta e concreta da utilidade real (não o nome técnico reformulado — o que ela resolve na prática), e ícone/cor de destaque.
- Agrupar por tema faz mais sentido visualmente do que uma lista única de itens soltos — por exemplo: "Apoio à decisão clínica" (protocolos, calculadoras, medicamentos, interação medicamentosa, alerta de contraindicação especial), "Ciência e atualização" (biblioteca científica, evidências, alerta de diretriz), "Telediagnóstico e documentos" (laudo/consultoria, prescrição, atestado, checklist de alta), "Educação continuada" (casos clínicos, trilhas, roteiro de conversa difícil), "Modo Emergência" e "Modo Apresentação/Ensino" em destaque próprio (não escondidos dentro de outro grupo, dado o valor diferencial deles), "Minha conta" (indicadores pessoais, assinatura). Ajuste os grupos como fizer mais sentido visualmente, mas não deixe tudo numa lista plana.
- Seguir a paleta de cores já migrada (Tarefa 1) e a mesma linha visual do resto do sistema — impacto visual vem de hierarquia e destaque bem construídos, não de cores fora do sistema já definido.
- Continua valendo o princípio da Tarefa 6: cada card leva direto para a função, o menu lateral continua existindo em paralelo.

## 22. Mais autonomia na verificação de conteúdo (Tarefa 2 Fase B)

Continue a verificação de conteúdo dos itens marcados como "VERIFICAÇÃO HUMANA NECESSÁRIA" com mais autonomia — não precisa parar a cada lote pequeno para minha aprovação individual. Pode avançar sozinho por mais itens de uma vez, buscando fonte real para cada um e corrigindo o que for necessário.

A marcação só pode ser removida quando o item de fato tiver sido verificado contra uma fonte válida — **nunca remover a marcação sem completar essa checagem**. Isso continua valendo mesmo com mais autonomia de execução: autonomia é sobre quantos itens processar antes de falar comigo, não sobre pular a verificação em si.

Me apresente um relatório consolidado a cada bloco maior (ex.: a cada 20-30 itens), em vez de a cada 5.

## 23. Antes de escrever Medicamentos do zero, procurar o arquivo do CardioBene

Você já identificou que a seção Medicamentos está vazia porque não há fonte estruturada no repositório atual — o carregador espera arquivos `.md` de um formato antigo (do ZIP original do projeto, na época em que ele se chamava CardioBene) que não existe mais aí.

Antes de tratar Medicamentos como conteúdo a ser escrito do zero (Fase B), procure primeiro se esse conteúdo já existe em algum lugar — um arquivo, pasta ou backup remanescente do projeto CardioBene, no servidor ou em qualquer local que você tenha acesso — contendo a biblioteca de medicamentos já estruturada (a base cobre IECA, BRA, betabloqueadores, bloqueadores de canal de cálcio, diuréticos, nitratos, anticoagulantes orais e heparinas, hipoglicemiantes com benefício cardiovascular, e hipolipemiantes incluindo inibidores de PCSK9 — cada entrada com dose, ajustes, evidência pivotal e referências).

- Se encontrar esse material: use como fonte para popular Medicamentos, mas **não publique sem passar pela mesma verificação contra fonte real** que os outros módulos já passaram na Fase B — esse conteúdo é antigo e pode ter os mesmos tipos de defeito já encontrados alhures (dado sem fonte rastreável, fonte inadequada, valor desatualizado).
- Se não encontrar nada, me avise antes de começar a escrever do zero — talvez eu ainda tenha esse material salvo em outro lugar e possa te enviar.

---

Apresente o plano de execução por tarefa antes de começar, como de costume — especialmente as tarefas 9 (depende de estrutura de dado que pode não existir), 13 (escopo já definido acima, mas confirme antes de codificar que nenhuma função da lista de exclusão está sendo implementada por engano) e 13b (não submeta nada à ANVISA sem a revisão externa combinada).
