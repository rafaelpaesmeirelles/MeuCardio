# ADR — Prontuário Eletrônico CorVIA

**Status:** proposto para implantação incremental  
**Data:** 2026-08-22  
**Escopo:** paciente identificável, atendimento clínico longitudinal, timeline, agenda, documentos, prescrições, Round e suporte à decisão.

## Contexto

O CorVIA já possui várias peças de um prontuário eletrônico, porém distribuídas em domínios que nasceram para finalidades diferentes:

- `PatientProfile`: cadastro identificável, escopado por profissional e com campos sensíveis cifrados em repouso, usado para documentos;
- `Patient`: paciente anonimizado do Round hospitalar, com iniciais + número de prontuário e dados clínicos do internado;
- `Appointment`: agenda própria/integrada;
- `Prescription`, `PrescriptionDocument` e `PrescriptionRecipient`: intenção clínica, documentos emitidos e destinatário cifrado;
- `GeneratedDocument`: documentos clínicos com snapshot histórico do paciente;
- `PatientTimeline`, `PatientPrescricao` e `PatientDocumentos`: superfícies já usadas no Round para visão longitudinal.

A nova função de Prontuário Eletrônico deve unificar a experiência sem apagar as fronteiras de privacidade que foram deliberadamente criadas. Em especial, o Round não deve ser “desanonimizado” implicitamente.

## Decisão central

O **paciente identificável canônico do prontuário ambulatorial será `PatientProfile`**. Não será criada uma terceira entidade concorrente de paciente.

O `Patient` atual do Round permanece anonimizado e separado. Quando houver necessidade clínica e autorização de produto para ligar um episódio hospitalar ao prontuário identificável, essa ligação deverá ser **explícita, opcional, auditável e sem copiar nome/CPF/endereço para a tabela `patients`**.

A unidade longitudinal de assistência será um novo conceito de **Encounter/Atendimento**. Agenda, consulta ambulatorial, retorno, pré-operatório, teleatendimento e outros contatos clínicos passam a apontar para o mesmo paciente e, quando iniciados, para um Encounter.

## Modelo conceitual

### 1. PatientProfile — identidade clínica longitudinal

Permanece como origem de verdade para:

- nome completo;
- CPF/documento quando informado;
- data de nascimento;
- sexo;
- telefone;
- e-mail;
- endereço.

Campos sensíveis continuam cifrados com o cofre existente. O cadastro recebe progressivamente dados clínicos longitudinais próprios, preferencialmente em tabelas relacionadas, e não como um JSON monolítico.

### 2. Encounter — episódio clínico

Cada atendimento deve registrar, no mínimo:

- `id`;
- `owner_id`/tenant;
- `patient_profile_id`;
- `appointment_id` opcional;
- tipo: consulta, retorno, pré-operatório, teleatendimento, encaixe, outro;
- local e modalidade;
- estado: `draft`, `in_progress`, `finalized`, `amended`, `cancelled`;
- início/fim;
- motivo/queixa principal;
- anamnese/HDA;
- antecedentes relevantes;
- exame físico;
- sinais vitais;
- avaliação clínica;
- plano/conduta;
- autor responsável;
- `created_at`, `updated_at`, `finalized_at`.

Um Encounter finalizado torna-se **imutável como registro histórico**. Correções posteriores são feitas por adendo/versionamento, sem apagar silenciosamente o conteúdo anterior.

### 3. Problemas e diagnósticos

Criar lista longitudinal separada do texto do Encounter:

- problema/diagnóstico;
- conceito/código opcional;
- status: ativo, resolvido, histórico, descartado;
- início/resolução quando conhecidos;
- origem: manual, Encounter, importação;
- confirmação humana obrigatória para sugestões de IA.

Esses conceitos serão a ponte segura entre prontuário e o grafo científico “Tudo com Tudo”.

### 4. Alergias e intolerâncias

Devem existir como entidade longitudinal própria, com:

- substância/agente;
- reação;
- gravidade quando conhecida;
- status;
- data/observação;
- fonte e autoria.

Nenhuma alergia inferida por IA entra automaticamente como fato clínico.

### 5. Medicações longitudinalmente reconciliadas

Separar:

- **medicação atual declarada** do paciente;
- **prescrição emitida** pelo CorVIA;
- histórico de início, mudança e suspensão.

A emissão de receita nunca altera automaticamente a lista ativa sem confirmação do médico. Divergências podem gerar alerta de reconciliação.

### 6. Observações, resultados e anexos

Resultados de exames, imagens, arquivos e observações devem ser vinculáveis ao paciente e opcionalmente ao Encounter que os motivou. O armazenamento histórico deve preservar o artefato original e seus metadados; alterações de cadastro do paciente não podem modificar retrospectivamente documentos emitidos.

## Integração com módulos já existentes

### Agenda

`Appointment` deve ganhar vínculo opcional com `PatientProfile`. Paciente avulso continua permitido antes do cadastro formal. Ao iniciar atendimento a partir de um agendamento, o sistema pode criar um Encounter idempotente e vincular os dois objetos.

Fluxo-alvo:

`Agenda → Paciente → Iniciar atendimento → Encounter → finalizar → Timeline`.

### Prescrição

A prescrição deve poder ser iniciada dentro de um Encounter e vinculada ao `PatientProfile`, mas os documentos emitidos continuam preservando **snapshot próprio do destinatário**. O prontuário fornece contexto; não substitui a imutabilidade documental.

### Documentos clínicos

`GeneratedDocument.patient_profile_id` já é a ponte correta para navegação. O `patient_snapshot_cifrado` continua sendo a fonte histórica da emissão. Documentos podem receber `encounter_id` opcional para aparecer automaticamente no atendimento e na timeline.

### Round hospitalar

O Round continua usando `Patient` anonimizado. Não migrar nem substituir registros automaticamente.

Futuro vínculo opcional:

`PatientProfile ← explícito/auditado → Patient do Round`.

Esse elo deve exigir posse compatível e não pode replicar PII na tabela hospitalar anonimizada.

### Timeline

A timeline do paciente identificável será uma projeção de eventos, não uma segunda fonte de verdade. Ela agrega:

- Encounters;
- agendamentos relevantes;
- prescrições/documentos emitidos;
- pedidos e resultados de exames;
- alterações de problemas/diagnósticos;
- alterações reconciliadas de medicação;
- anexos;
- eventos hospitalares vinculados explicitamente.

## Interface clínica

A referência funcional observada em sistemas de mercado é útil pela organização, mas a interface do CorVIA deve ser própria.

### Cabeçalho persistente

Exibir apenas dados necessários ao cuidado:

- nome;
- idade/data de nascimento;
- sexo;
- telefone quando pertinente;
- badges de alergia, anticoagulação, dispositivo e problemas críticos quando confirmados;
- última consulta;
- próxima consulta;
- pendências.

### Navegação do prontuário

1. Resumo clínico
2. Atendimentos / Evoluções
3. Problemas e diagnósticos
4. Alergias
5. Medicamentos
6. Prescrições
7. Exames / resultados
8. Laudos e formulários
9. Atestados / orientações
10. Imagens
11. Arquivos
12. Linha do tempo
13. Agenda
14. Documentos assinados

### Iniciar atendimento

O usuário poderá escolher modelos como:

- consulta cardiológica;
- retorno;
- pré-operatório;
- insuficiência cardíaca;
- hipertensão;
- arritmia;
- check-up;
- texto livre.

Modelos organizam a captura, mas o armazenamento final permanece estruturado e auditável.

## CorVIA Assist no prontuário

A IA pode:

- estruturar ditado/texto em rascunho de evolução;
- resumir a história longitudinal;
- comparar consulta atual com anterior;
- apontar exames pendentes;
- sugerir reconciliação de medicamentos;
- sugerir calculadoras e conteúdo científico pertinentes;
- sinalizar potenciais inconsistências;
- propor problemas/diagnósticos candidatos.

Regra obrigatória: **IA sugere; profissional aceita ou rejeita.** Nenhum diagnóstico, alergia, prescrição, problema, resultado ou alteração de prontuário é confirmado silenciosamente pela IA.

## Integração com “Tudo com Tudo”

O prontuário não copia o grafo científico para dentro do registro clínico. Ele cria referências seguras entre fatos clínicos confirmados e conceitos científicos.

Exemplo:

`Problema confirmado: insuficiência cardíaca com fração de ejeção reduzida`

pode abrir contexto de:

`doença → diretriz → estudos → medicamentos → contraindicações/interações → exames → calculadoras → checklist → material do paciente`.

A relação contextual não altera o prontuário e não transforma recomendação de guideline em ordem automática.

## Segurança, privacidade e auditoria

A liberação do prontuário exige:

1. isolamento por tenant/profissional em todos os endpoints;
2. RBAC/delegação explícita para equipe;
3. trilha de auditoria para leitura e escrita sensível;
4. PII cifrada em repouso conforme padrão atual;
5. finalização imutável de Encounter + adendo/versionamento;
6. autoria e timestamp em cada registro clínico;
7. exclusão lógica quando histórico assistencial não puder ser apagado;
8. proteção contra IDOR e acesso cruzado;
9. snapshots imutáveis para documentos emitidos;
10. logs sem PII/segredos;
11. backup/restore testado antes de migrations de produção;
12. testes específicos de tenant, auditoria e imutabilidade.

## Estratégia de implantação

### Fase 1 — núcleo do prontuário

- evoluir `PatientProfile` como paciente canônico ambulatorial;
- criar Encounter;
- problemas/diagnósticos longitudinais;
- alergias;
- medicações reconciliadas;
- resumo do paciente;
- timeline identificável;
- interface `Prontuário > Pacientes` e ficha do paciente.

### Fase 2 — integrar ferramentas existentes

- Agenda → Encounter;
- Prescrição → PatientProfile + Encounter;
- pedidos de exame/documentos/atestados → PatientProfile + Encounter;
- assinatura A1 e PDFs preservados;
- anexos e resultados.

### Fase 3 — Clinical Intelligence

- contexto “Tudo com Tudo”;
- calculadoras contextuais;
- checklists;
- interações e segurança medicamentosa;
- CorVIA Assist com confirmação humana.

### Fase 4 — ecossistema

- portal do paciente;
- compartilhamento seguro;
- importação estruturada de resultados;
- interoperabilidade progressiva, incluindo FHIR quando houver contrato real de dados;
- clínicas/equipes e permissões avançadas.

## Alternativas rejeitadas

- **Transformar `Patient` do Round no paciente universal:** viola a decisão anterior de anonimização e mistura contexto hospitalar com PII.
- **Criar uma terceira tabela “medical_record_patient”:** duplicaria identidade e aumentaria risco de divergência.
- **Usar apenas documentos/textos como prontuário:** impede reconciliação longitudinal e suporte clínico contextual.
- **Persistir toda a evolução em um único JSON:** reduz auditabilidade, indexação e evolução segura do modelo.
- **Permitir que IA escreva fatos clínicos automaticamente:** risco clínico e de governança inaceitável.
- **Copiar interface/implementação de PEP externo:** referência funcional não implica replicação de design, código ou contratos privados.

## Critérios de aceite para a primeira entrega funcional

- paciente criado/consultado/editado apenas pelo tenant autorizado;
- Encounter pode ser criado, salvo como rascunho e finalizado;
- Encounter finalizado não pode ser sobrescrito; correção usa adendo;
- problemas, alergias e medicações têm autoria/status/histórico;
- agenda pode iniciar atendimento sem duplicar Encounter;
- documentos e prescrições existentes continuam funcionando;
- Round continua anonimizado e funcional;
- timeline mostra eventos do paciente sem duplicar a fonte de verdade;
- build frontend + testes backend + migrations + RC2 passam;
- testes de IDOR/tenant/auditoria/imutabilidade passam;
- nenhuma migration destrutiva ou deploy automático nesta fase.
