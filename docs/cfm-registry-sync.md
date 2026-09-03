# Base oficial de médicos do CFM

## Fonte aprovada

O CorVIA trata a base fornecida diretamente pelo Conselho Federal de Medicina (CFM) como fonte oficial para cadastro nacional de médicos. A arquitetura preserva o conteúdo recebido e mantém uma camada derivada apenas para pesquisa e decisão defensiva.

A integração segue a separação definida pelo próprio CFM:

- `TOTAL.ZIP`: carga completa/local da base nacional;
- Web Service SOAP `Consultar(crm, uf, chave)`: consulta pontual de um médico, sob demanda;
- o Web Service **não** é usado para percorrer/extrair toda a base por chamadas sucessivas.

Documentação oficial de referência:

- `https://sistemas.cfm.org.br/listamedicos/arquivos/especificacao.pdf`
- `https://sistemas.cfm.org.br/listamedicos/arquivos/manualwebservices.pdf`

## Atualização automática

O CFM informa que o `TOTAL.ZIP` é gerado diariamente entre 12h e 14h de Brasília e recomenda o download após 14h. O workflow:

`.github/workflows/cfm-registry-sync.yml`

é agendado para **14:23 de Brasília** (`17:23 UTC`) e executa em produção somente contra o SHA exato já implantado.

Fluxo:

1. GitHub Actions resolve o SHA atual de `main`.
2. O acesso SSH restrito aceita somente `cfm-sync <SHA>`.
3. O backend de produção baixa o snapshot oficial sem expor a credencial.
4. O ZIP é validado antes de qualquer desativação: 27 UFs, UTF-8 e 6 campos por registro.
5. Os registros são aplicados por `UPSERT` usando `UF + CRM bruto` como chave de identidade.
6. Apenas após a carga integral bem-sucedida registros ausentes no novo snapshot deixam de ser `is_current`.
7. A execução, SHA-256, contagens e horário são registrados em `cfm_sync_runs`.

Uma falha parcial **não** desativa registros anteriores.

## Carga inicial

Depois da migration `f95c20260902`, um snapshot oficial local pode ser carregado com:

```bash
cd /opt/meucardio/backend
python -m app.commands.sync_cfm_registry \
  --zip /caminho/TOTAL.zip \
  --sha256 <sha256-esperado>
```

O snapshot oficial recebido para a implantação inicial foi auditado separadamente. O hash deve ser conferido antes da primeira carga e nunca substituído por um valor inferido.

## Credenciais

A credencial do CFM é segredo de backend. Nunca deve existir em frontend, repositório, logs, URL, screenshot público ou artefato de CI.

Configuração obrigatória para a consulta SOAP:

```env
CFM_WEBSERVICE_CHAVE=<segredo>
```

`CFM_WEBSERVICE_URL` é opcional; quando vazio o backend usa o endpoint oficial:

```text
https://ws.cfm.org.br:8080/WebServiceConsultaMedicos/ServicoConsultaMedicos
```

A sincronização do `TOTAL.ZIP` usa a credencial privada configurada no backend. Se o CFM emitir credenciais distintas para download e SOAP, a implementação deve manter segredos separados; nunca reutilizar uma credencial por suposição operacional.

## Web Service pontual

A checagem KYC/CRM agora usa o Web Service oficial de forma fail-closed:

- resposta regular confirmada: `ativo_confirmado`;
- CRM/UF não localizado ou situação não regular: `nao_confirmado`;
- indisponibilidade, erro transitório ou credencial inválida: `erro_checagem` e revisão manual.

O CFM pode devolver erro de negócio com HTTP 200. Por isso o cliente sempre verifica `codigoErro`; códigos transitórios conhecidos recebem retry limitado.

## Tratamento de anomalias do snapshot

O CorVIA não reescreve o dado oficial. Exemplos como CRM negativo, situação textual inválida ou RQE incompleto são preservados no registro bruto e recebem flags derivadas. Um identificador só é enviado ao Web Service quando puder ser normalizado com segurança para um número natural de 1 a 7 dígitos.

A identidade de uma inscrição no snapshot é `UF + CRM bruto`; nome nunca é chave de deduplicação.

## Operação manual

Download + carga imediata, dentro do backend de produção:

```bash
python -m app.commands.sync_cfm_registry --download
```

A execução usa advisory lock no PostgreSQL para impedir duas sincronizações simultâneas.
