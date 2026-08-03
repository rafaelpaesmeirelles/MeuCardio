# Segurança de uploads

A Corvia aceita arquivo somente em cinco superfícies conhecidas:

| Superfície | Limite do arquivo | Formatos |
|---|---:|---|
| foto de perfil | 3 MB | JPEG, PNG, WEBP |
| logo profissional | 3 MB | JPEG, PNG, WEBP |
| exame de telediagnóstico | 20 MB | JPEG, PNG, WEBP, PDF |
| anexo do CorvIA Mail | 15 MB | PDF, JPEG, PNG, WEBP, DOCX, XLSX, PPTX, TXT, CSV |
| material administrativo de curso | 40 MB | PDF, JPEG, PNG, DOCX, XLSX, PPTX |

A lista é intencionalmente fechada. Executáveis, scripts, HTML/SVG, arquivos
compactados genéricos e formatos Office legados não são aceitos.

O material de curso tem política própria porque apostilas podem ser maiores que
anexos de e-mail, mas não precisam de TXT, CSV ou WEBP. O upload continua
restrito a administradores pelo router existente.

## Validação antes da rota

`UploadSecurityMiddleware` e `CourseUploadSecurityMiddleware` são executados
antes do parser do endpoint em produção. Eles:

1. identificam a política pela combinação de método e caminho;
2. exigem `multipart/form-data`;
3. rejeitam `Content-Length` acima do limite antes de ler o body;
4. também contam bytes recebidos, protegendo contra body sem tamanho ou
   `Transfer-Encoding: chunked`;
5. exigem exatamente um arquivo;
6. validam nome, tamanho e conteúdo real;
7. reproduzem o mesmo body aprovado para o router FastAPI.

O limite inclui uma margem de 512 KB para boundary e cabeçalhos multipart. O
arquivo em si continua obedecendo ao limite exato da tabela.

## Imagens

Não basta apresentar magic bytes. A imagem é realmente decodificada pelo
Pillow e precisa:

- corresponder a JPEG, PNG ou WEBP quando o tipo de upload permitir;
- ter extensão compatível com o conteúdo;
- possuir no máximo 25 megapixels;
- conter somente um frame;
- passar pela verificação estrutural sem truncamento;
- não disparar proteção contra bomba de descompressão.

## PDF

O arquivo precisa iniciar em `%PDF-` e conter marcador final `%%EOF`. PDFs com
JavaScript, ação de lançamento, arquivo incorporado ou conteúdo RichMedia são
recusados, pois esses recursos não são necessários para ECG, Holter, MAPA,
laudos ou apostilas.

Esta verificação reduz a superfície, mas não substitui um mecanismo antivírus
quando a operação justificar essa camada adicional.

## Documentos Office

Somente Office Open XML sem macro:

- `.docx`;
- `.xlsx`;
- `.pptx`.

O ZIP interno precisa ter estrutura correspondente à extensão. São recusados:

- caminhos relativos ou absolutos;
- arquivo interno criptografado;
- macro VBA;
- ActiveX;
- objeto incorporado;
- mais de 2.000 entradas;
- expansão total acima de 100 MB;
- taxa de compactação individual acima de 200:1.

Isso também reduz risco de ZIP bomb.

## Nomes de arquivo

O nome serve apenas para exibição. Não decide onde o arquivo é armazenado.
São rejeitados:

- `/` e `\\`;
- aspas;
- NUL;
- CR/LF e demais controles;
- nomes vazios.

O nome é limitado a 180 caracteres. O exame clínico continua sendo salvo no
cofre com UUID aleatório, sem nome, CPF ou outro dado do paciente no caminho.
O material de curso também permanece em volume privado, servido apenas pela
rota autenticada de download.

## Rate limiting

Cada superfície aceita 20 uploads por cliente em 10 minutos. O contador usa
Redis e hash do IP, compartilhado entre workers. O upload excedente recebe 429
com `Retry-After`. Quando o Redis falha, a operação retorna 503 em vez de fazer
fail-open.

A proteção de origem do PR de segurança HTTP permanece na camada externa. Uma
origem cruzada é bloqueada antes que o middleware carregue o multipart.

## Inventário obrigatório

O teste `test_inventario_de_rotas_upload_exige_politica_central` pesquisa todos
os módulos de API com `UploadFile`. A CI falha quando surgir um novo módulo sem
revisão da allowlist e sem política de upload correspondente. O inventário atual
inclui conta, e-mail, telediagnóstico e cursos parceiros.

## Limitações deliberadas

- os middlewares validam e limitam, mas não fazem diagnóstico antivírus;
- anexos são enviados ao Mail360 após aprovação local;
- documentos cifrados dependem da preservação separada da
  `STORAGE_ENCRYPTION_KEY`;
- formatos clínicos adicionais, como DICOM, exigem política e validador próprios
  antes de serem liberados.
