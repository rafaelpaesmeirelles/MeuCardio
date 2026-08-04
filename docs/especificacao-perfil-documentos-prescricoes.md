# Perfil profissional, documentos clínicos e históricos

Data: 04/08/2026

## Estado da implementação

O primeiro lote funcional está na branch do PR #42 para certificação: perfil profissional ampliado, forma de tratamento, local de trabalho, contraste automático da logo e pesquisa dos históricos. O fluxo também admite contas internas marcadas para complementação obrigatória: no primeiro acesso, a navegação fica restrita à página **Minha conta** até o salvamento dos dados pessoais e profissionais, sem exigir troca de senha. Os modelos regulados permanecem bloqueados até a reprodução e validação dos formulários oficiais vigentes.

## Contexto observado

O receituário de exemplo enviado pelo proprietário mostrou três falhas concretas:

1. profissional biomédica aparecendo com conselho genérico `OUTRO-SP`, em vez de `CRBM`;
2. nome impresso com prefixo fixo `Dr.`, mesmo quando o cadastro não define essa forma de tratamento;
3. logo profissional sem contraste suficiente, ficando invisível no PDF.

O sistema já possui parte da infraestrutura necessária: endereço profissional, telefone profissional, upload de logo, classificação de substâncias controladas, modelos de atestado/laudo e histórico de receitas/documentos. Esta entrega deve completar e uniformizar esses fluxos.

## 1. Cadastro e perfil profissional

### Conselhos

O catálogo deve incluir, no autocadastro, Minha Conta e criação direta pelo administrador:

- CRM — Conselho Regional de Medicina;
- CRO — Conselho Regional de Odontologia;
- CRBM — Conselho Regional de Biomedicina;
- COREN — Conselho Regional de Enfermagem;
- CRF — Conselho Regional de Farmácia;
- CREFITO — Conselho Regional de Fisioterapia e Terapia Ocupacional;
- CRN — Conselho Regional de Nutrição;
- CRP — Conselho Regional de Psicologia;
- CREF — Conselho Regional de Educação Física;
- CRESS — Conselho Regional de Serviço Social;
- Outro.

O backend deve aceitar e persistir o conselho sem converter `Outro` em uma sigla falsa no documento.

### Forma de tratamento

Adicionar campo opcional `professional_title`/forma de tratamento, com catálogo:

- sem título;
- Sr.;
- Sra.;
- Dr.;
- Dra.;
- Prof.;
- Profa.;
- Prof. Dr.;
- Profa. Dra.;
- Me.;
- Ma.;
- Esp.

O título não pode ser inferido pelo conselho ou pela profissão. Todos os PDFs, visualizações para impressão, e-mails e textos que hoje prefixam `Dr.` ou `Dr(a).` devem usar o valor cadastrado; na ausência, imprimir somente o nome.

### Local de trabalho

Adicionar campos opcionais:

- nome da instituição/local de trabalho;
- setor/unidade/departamento;
- cargo/função;
- observações profissionais complementares;
- opção `include_workplace_on_documents` para incluir ou não essas informações nos documentos.

Esses dados complementam, mas não substituem, endereço e telefone profissionais já existentes.

### Privacidade e compatibilidade

- campos novos devem ser opcionais e não quebrar usuários existentes;
- nenhum endereço, telefone ou local de trabalho aparece por padrão sem opção explícita;
- CPF integral do profissional não deve aparecer em documentos comuns;
- a forma de tratamento deve ser validada por allowlist no backend.

## 2. Logo profissional legível

### Problema

Logos PNG/WEBP transparentes com arte branca ou muito clara desaparecem sobre a página branca. O fundo branco forçado atualmente agrava o problema.

### Correção

Implementar fundo de contraste automático para logo profissional:

1. decodificar a imagem com Pillow;
2. considerar somente pixels visíveis (alfa acima de limiar);
3. calcular luminância média/percentil da arte visível;
4. se a arte for predominantemente clara, desenhar placa navy com margem e cantos discretos;
5. se a arte for predominantemente escura, usar placa branca;
6. preservar proporção e transparência;
7. aplicar a mesma decisão no PDF e na visualização/impressão do navegador;
8. arquivo ilegível não pode derrubar a geração do documento;
9. adicionar testes com logo branca transparente, logo escura transparente e JPEG.

Não achatar permanentemente a imagem original do usuário; o contraste deve ser decisão de renderização.

## 3. Identidade profissional em todos os documentos

Auditar todas as saídas PDF/print e garantir o mesmo bloco profissional:

- receituário comum;
- Receita de Controle Especial e receitas reguladas que forem habilitadas;
- atestado;
- laudo;
- documento genérico;
- material/informação ao paciente;
- documentos públicos reabertos por link;
- exportações clínicas que identifiquem emissor;
- qualquer visualização de impressão no frontend.

O bloco deve receber:

- logo profissional legível;
- forma de tratamento + nome;
- profissão;
- especialidade;
- conselho/UF/número;
- RQE quando aplicável;
- local de trabalho quando autorizado;
- endereço/telefone profissional somente quando selecionados.

Documentos já emitidos e persistidos não devem mudar retroativamente. Para novas emissões, gravar snapshot dos dados de identificação necessários para reprodução determinística.

## 4. Receitas controladas e anabolizantes

### Regra de segurança

Nenhum formulário regulado deve ser habilitado com layout aproximado ou numeração simulada. A implementação deve reproduzir os campos e dizeres obrigatórios das fontes oficiais vigentes e manter fail-closed quando faltar número SNCR/autorização aplicável.

### Receita de Controle Especial

Implementar PDF em duas vias/páginas, com identificação explícita da destinação de cada via, campos obrigatórios do prescritor e paciente, data, itens, quantidade por extenso quando exigida, assinatura e demais dizeres normativos.

### Anabolizantes/hormônios — Lista C5

Quando qualquer item tiver `lista == "C5"`, exigir antes da emissão:

- CPF do prescritor;
- endereço profissional completo;
- telefone profissional;
- nome completo do paciente;
- endereço do paciente;
- CID;
- identificação do conselho e número de registro;
- retenção e vias conforme o tipo regulatório aplicável.

Adicionar campo de CID na interface, validar preenchimento e impedir emissão incompleta. O CPF do prescritor deve ser usado somente nesse documento regulado e nunca exposto em respostas genéricas da API.

### Outros tipos

- NRA, NRB, NRB2, NRR, NRT e RET devem continuar bloqueados se faltar numeração oficial ou requisito externo;
- quando o requisito externo estiver disponível, o renderizador deve selecionar o layout pelo `PrescriptionType`, sem permitir ao usuário forçar um tipo incompatível sem revisão e justificativa auditada;
- manter trilha de auditoria e versão da lista normativa.

## 5. Histórico por paciente e tipo

### Receitas

O histórico de prescrições deve:

- agrupar visualmente por nome do paciente;
- permitir busca por nome completo ou qualquer parte do nome, sem diferenciar maiúsculas/minúsculas ou acentos;
- permitir filtro por tipo/código/nome de receita;
- permitir combinação dos filtros;
- mostrar data, tipos gerados, status e ações existentes;
- manter isolamento por profissional.

Como o nome do destinatário é cifrado, a primeira implementação pode filtrar em memória após decifrar apenas os registros do próprio usuário, com limite/paginação explícitos. Não criar índice em texto claro sem desenho de privacidade específico.

### Documentos

O histórico de atestados, laudos e demais documentos deve:

- armazenar snapshot cifrado do nome do paciente/destinatário nas novas emissões;
- aceitar nome explícito no formulário de geração e, por compatibilidade, reconhecer variáveis `nome`, `paciente` ou `nome_paciente`;
- agrupar por paciente;
- permitir busca parcial/acento-insensível pelo nome;
- permitir filtro por tipo (`atestado`, `laudo`, `outro`) e título;
- manter compatibilidade com documentos antigos, exibindo `Paciente não informado` quando não for possível recuperar o nome.

## 6. Testes obrigatórios

- migration em banco vazio e upgrade idempotente;
- usuários antigos sem campos novos;
- autocadastro, edição de perfil e criação direta admin com CRBM;
- validação da allowlist de títulos;
- nenhum `Dr.` hardcoded em PDFs/e-mails/prints;
- logo branca transparente visível em fundo navy;
- logo escura visível em fundo branco;
- todos os geradores clínicos recebem logo e identidade;
- C5 bloqueia sem CPF/endereço/telefone/CID e gera duas vias quando completo;
- tipos dependentes de numeração continuam fail-closed;
- busca parcial/acento-insensível de receitas e documentos;
- filtros por tipo;
- isolamento entre usuários;
- PDFs reais começam com `%PDF` e terminam com `%%EOF`;
- frontend build e suíte completa.


## Estado de implementação regulatória — 04/08/2026

- RCE física no modelo Anvisa V2: implementada em duas vias, frente e verso.
- Lista C5: validação obrigatória de CRM/CRO, CPF do prescritor, endereço e telefone profissionais, endereço do paciente e CID.
- NRA, NRB, NRB2, NRR, NRT e RET: permanecem fail-closed sem numeração oficial/integração aplicável; nenhum número é simulado.
- Emissão RCE disponível somente como documento físico com assinatura manual enquanto as funcionalidades eletrônicas do SNCR não estiverem integradas.

- RCE: cada item exige quantidade em algarismos e por extenso, conforme art. 52, §1º, da Portaria SVS/MS nº 344/1998.
