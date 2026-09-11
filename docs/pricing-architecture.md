# Arquitetura de preços e inteligência regulatória de medicamentos

## Decisão vigente — manter K@iros e adiar novo fornecedor (11/09/2026)

Pedido expresso do responsável pelo CorVIA: **manter por enquanto os preços
fornecidos pela K@iros**, aproveitar os arquivos previamente anexados e registrar
a contratação de outro fornecedor como pendência.
Esta decisão substitui qualquer sugestão anterior de contratação imediata.

- **Em uso no candidato local, ainda não publicado:**
  `medicamentos/kairos-453-2026-08.json`, edição 453, agosto/2026, ampliado para
  **6.320 apresentações**, 3.025 pares marca/laboratório e 46.180 células de preço.
  Há **5.360 apresentações com PMC** e 960 apenas com PF; estas últimas não
  recebem preço ao consumidor inventado. SHA-256:
  `ff070fdf46b257253d9e618de56bfb63f3e2b33333bab332e734537d05ec8363`.
  As 52 apresentações anteriores permanecem com descrições, valores, ordem e
  identificadores preservados. O recorte histórico está na fixture
  `backend/tests/fixtures/kairos-453-2026-08-cardiovascular.json`.
- **Fonte original localizada após indicação do responsável:**
  `/opt/meucardio/medicamentos/kairos-453-2026-08-fontes/`, contendo revista
  editorial, suplemento de preços e planilha da edição. O suplemento
  `08-ago-2026-suplemento-precos-kairos-453.pdf` tem 80 páginas, edição 453,
  agosto/2026, SHA-256
  `32e4dff5205f7387040900df9820a65b78825e12028db698aa11c482297bc142`.
  O arquivo `kairos-ago-2026-modelo-1.xlsx` acompanha o PDF. Leitura/cópia para
  análise local, sem alteração dos originais no servidor. A inspeção compara
  colunas e apresentações antes de declarar uma ampliação da base.
- **Ampliação rastreável:** o importador geométrico
  `backend/scripts/import_kairos_453_pdf.py` extrai linhas literais, e
  `backend/scripts/prepare_kairos_snapshot.py` valida a edição e o hash do bruto
  aprovado antes de preparar um arquivo separado. Não há ingestão automática
  de futuras edições nem alteração do PDF. O provider continua lendo o snapshot.
  Não foram criados preços, equivalências clínicas ou cotações em tempo real.
- **Pendência comercial aberta — contratar outro sistema de preços de medicamentos.**
  Responsável pela decisão/contrato: administração do CorVIA. Sem fornecedor,
  prazo, orçamento ou contratação aprovados. Critérios de aceite: ofertas por
  apresentação/EAN e região, data/condições do preço, cobertura demonstrada em
  amostra, API/feed documentado, autorização de exibição/cache e SLA definidos.
  A integração técnica somente será iniciada após seleção e autorização.

Os valores atuais devem continuar identificados por fonte, edição e competência,
separados da referência regulatória CMED; não devem ser descritos como preços
efetivamente cobrados por farmácias. A pesquisa abaixo fica como subsídio futuro,
não como serviço contratado, recurso disponível ou requisito para manter K@iros.

**Decisão complementar do responsável: usar o menor valor.** A interface passa
a mostrar o menor PMC publicado para a apresentação selecionada e a somar esses
valores de referência. A faixa original continua nos dados para rastreabilidade;
não se atribui automaticamente uma alíquota à UF do paciente. Entre duplicatas
da mesma edição/marca/laboratório/apresentação, a preparação escolhe uma linha
original inteira com o menor PMC positivo, mantendo as variantes no relatório.
Não monta uma linha sintética escolhendo mínimos independentes de várias linhas,
não mistura PF com PMC e não agrega doses/embalagens diferentes. Empates de PMC
conservam a ordem da fonte. Registros com composição ambígua continuam separados:
o menor preço não resolve inconsistência de identidade.

### Inspeção dos originais recuperados

Os hashes locais conferem com os arquivos do servidor. O JSON remoto ainda
correspondia ao recorte de 13 produtos/52 apresentações, SHA-256
`7a7ac549bead518f3566dce41e64702090448545c35d7b56e3316d79ef896e9e`;
o diretório de fontes não era consumido automaticamente pelo provider.

- O suplemento PDF tem tabela vetorial em duas colunas, páginas físicas8–78,
  com pares PF/PMC20%,18%,17%,12%. Há linhas sem PMC, alíquotas vazias e
  continuidade de produto entre colunas/páginas. A extração precisa respeitar
  a posição de cada célula; uma divisão por espaços deslocaria preços ausentes.
- A planilha `kairos-ago-2026-modelo-1.xlsx`, SHA-256
  `8183d08637423093716991a34d3f97c0d4278a98ea7da388655d8e26df5beac0`, tem uma
  aba ALTAS,A1:AI1965:1.964 linhas de apresentações,795 códigosPRO e105
  laboratórios. Termina em BEROTEC: **é recorte, não catálogo completo**.
- A planilha contém11 pares FAB/PUB por alíquota, de23% a12%, além de
  BARRAS/REGISTRO/GGREM. Há13 datas de vigência entre abril2025 e agosto2026;
  somente38 linhas registram1º de agosto2026. O nome do arquivo não autoriza
  mudar a vigência de cada linha. Não foi feita associação automática de
  alíquota aUF nem incorporação dos identificadores por mera semelhança.
- A chavePRO+PRE é única. Existem19 grupos repetidos por marca/laboratório/
  apresentação normalizados e12 códigos de barras repetidos,9 deles com preços
  divergentes. Dez células monetárias com zero e ausências não devem virar
  preços utilizáveis. Isso exige validação de identidade, não escolha da
  primeira ocorrência ou do menor valor.
- Comparação independente do recorte antigo com a planilha:27 apresentações
  com correspondência única,216/216 células monetárias iguais. As outras25
  não foram comparáveis por chave/recorte; isso não demonstra divergência.
  Uma leitura manual inicial de46,73 foi corrigida por extração independente
  para46,71 antes de qualquer importação; PDF e XLSX concordam nessa célula.

Originais preservados no servidor e cópias somente para análise. Os dados de
PDF e XLSX não foram mesclados por inferência, nem a revista foi apresentada
como uma fonte de transações em tempo real. A inspeção da planilha orientou
a separação das fontes e o tratamento explícito de lacunas/duplicatas.

### Preparação e cobertura efetivamente verificadas

A extração das páginas 8–78 produziu 6.371 apresentações e 46.562 preços.
A comparação independente com o XLSX encontrou 411 apresentações inequívocas,
3.022 preços idênticos e nenhuma divergência nesse subconjunto; não certifica
linhas não comparadas. O suplemento identifica a lista como atualizações/
lançamentos, não como cobertura integral do mercado.

O candidato final exclui 14 apresentações para revisão de identidade:
MICARDIS/BOEHRINGER (3), MIRUGELL/CRISTÁLIA (2), TRIPLIXAM/SERVIER (7) e
REPATHA/AMGEN (2). Outras 37 ocorrências duplicadas, em 33 grupos, deixam de
se repetir. Nove grupos têm valores divergentes; a escolha preserva uma linha
original inteira conforme a política do menor PMC, ou PF quando só há PF.
Todas as variantes e motivos ficam em
`medicamentos/kairos-453-2026-08-curation-audit.json`, com hashes do candidato
e da auditoria integral. Campos ausentes permanecem ausentes.

**Cobertura de preços não é cobertura do catálogo clínico.** Pelas regras
conservadoras existentes, o recorte anterior tinha opções para 14 entradas
clínicas (56 opções/52 apresentações distintas). O ampliado tem opções para
84 das 206 entradas revisadas no `medicamentos/metadados.json` local:
541 opções/537 apresentações distintas. Não se verificou a publicação dessas
entradas no banco de produção; não se afirma que as 6.320 apresentações estejam
todas pesquisáveis em Prescrever. Marcas sem vínculo clínico inequívoco não
foram ligadas por semelhança nem transformadas em novas monografias.

Os identificadores das linhas novas usam edição/página/lado/linha, evitando
colisões entre laboratórios e doses. As 46.180 observações do arquivo produziram
6.320 identificadores de apresentação distintos, sem colisões; os 52 antigos
permanecem idênticos. Não há atribuição de UF automática nem associação de PF
a preço de varejo.

Reprodução controlada, a partir da raiz do repositório e com `pdfplumber`
disponível no ambiente offline de análise (não é dependência da requisição web):

```sh
python3 backend/scripts/import_kairos_453_pdf.py \
  --source /opt/meucardio/medicamentos/kairos-453-2026-08-fontes/08-ago-2026-suplemento-precos-kairos-453.pdf \
  --schema-template backend/tests/fixtures/kairos-453-2026-08-cardiovascular.json \
  --output-dir /tmp/corvia-kairos-453-review-new --write-candidate
python3 backend/scripts/prepare_kairos_snapshot.py \
  /tmp/corvia-kairos-453-review-new/candidate.json \
  --source-pdf /opt/meucardio/medicamentos/kairos-453-2026-08-fontes/08-ago-2026-suplemento-precos-kairos-453.pdf \
  --output /tmp/corvia-kairos-453-review-new/prepared.json \
  --audit-output /tmp/corvia-kairos-453-review-new/preparation-audit.json
```

O diretório deve ser novo; o segundo comando recusa candidatos diferentes do
V3 aprovado e ambos impedem ativação direta do snapshot. Não contornar o guard
de hash se outra versão de extração produzir bytes diferentes: revisar primeiro.
As duas saídas da preparação são atômicas individualmente, não como par; após
qualquer erro, rejeitar o par parcial e conferir hashes antes de promover.
Os comandos acima são preparação local/offline, não instruções de deploy por SSH.

## Atualização — preço real no Prescrever (11/09/2026)

**Estado verificado no código local, não certificação de produção:** há adaptadores
CMED, K@iros e BPS, mas nenhum feed ativo de ofertas de farmácia. As seções
numeradas abaixo preservam a investigação de agosto e seus registros históricos;
afirmações de cron, acesso e cobertura daquela data não são verificações atuais.

### O que falta hoje

- `pricing/kairos_provider.py` consulta um snapshot de agosto de 2026,
  agora ampliado localmente para **6.320 apresentações**, sem EAN e sem
  atualização automática. A produção ainda precisa receber a versão revisada.
  A K@iros publica PF/PMC por alíquota, não necessariamente transações de varejo;
  ampliar apenas essa tabela não resolve preço efetivamente praticado.
  [Instruções da publicação oficial, suplemento 449, abril/2026](https://bra.kairosweb.com/wp-content/uploads/2026/04/Suplemento-449.pdf).
- `pricing/base.py::PriceObservation` é uma **dataclass imutável, não uma tabela
  persistida**. O protocolo não entrega sozinho agregação, histórico, estoque,
  expiração ou integração de varejo. Esses componentes ainda precisam ser implementados.
- `models/cmed.py::CmedApresentacao` e `services/cmed_precos.py` preservam EAN1;
  falta consolidar os demais identificadores de embalagem quando fornecidos pela
  origem e expor o identificador exato nas opções do Prescrever. O vínculo com
  `Drug` é opcional: a cobertura comercial não deve ficar limitada às monografias clínicas.
- As faixas calculadas em `api/drugs.py` são diferenças de PF/PMC por alíquota,
  **não mínimo/máximo de farmácias**. BPS representa compras institucionais.
- O contrato de itens do receituário conserva campos históricos CMED, não um
  snapshot completo de oferta varejista. A seleção futura deverá preservar
  apresentação, fonte, condições e instante de observação, inclusive ao reabrir a receita.

### Fontes avaliadas e decisão proposta

Pesquisa pública somente leitura em 11/09/2026. Nenhuma conta, contratação,
coleta massiva, uso de API privada ou ativação de provedor foi realizada.

| Fonte | Evidência pública | Adequação e limite |
|---|---|---|
| Consulta Remédios | Ofertas de farmácias variam por CEP/estoque; preços de internet. | Candidato a feed licenciado de ofertas. Os termos comuns não autorizam uso comercial, formação de bases ou coleta automatizada; é necessária autorização específica. API de saída e SLA não comprovados. [Termos, §§3, 4 e 9](https://consultaremedios.com.br/termos). |
| CliqueFarma | Integra XML/VTEX de farmácias com leitura anunciada a cada cinco minutos. | Candidato a parceria. Essa frequência é **farmácia → comparador**, não API pública nem SLA para CorVIA. Exigir esquema de saída e direito de exibição/cache. [Documentação de integração](https://www.cliquefarma.com.br/perguntas-frequentes/parceiro/como-conecto-meus-produtos-no-cliquefarma). |
| IQVIA Price Monitor | Portal brasileiro descreve coleta em lojas físicas e internet. | Possível fornecedor; evidência em portal UAT/legado não confirma disponibilidade comercial atual, cobertura, API ou periodicidade. [Portal oficial](https://uat-ipec.solutions.iqvia.com/?ReturnUrl=%2F). |
| Close-Up | Dados de vendas, preço por canal, estoque/embalagem; entrega publicada entre 7º e 11º dia útil mensal. | Referência analítica, não oferta atual garantida. API e redistribuição dependem de contrato. [Descrição oficial](https://close-upinternational.com/pt-br/dados-de-vendas-do-mercado/). |
| Menor Preço / SEFAZ | Preço da última NF-e/NFC-e, atualizado pela emissão; consulta por localização/código de barras quando presente na nota. | Referência de transação real, não garantia de estoque ou preço atual. API B2B e licença de redistribuição não localizadas. [FAQ oficial, seção 07](https://nfg.sefaz.rs.gov.br/site/duvidas.aspx?a=a_cidadao). |

**Recomendação técnica:** avaliar primeiro um feed autorizado de ofertas de
Consulta Remédios e/ou CliqueFarma, por amostra e contrato, antes de escolher o
fornecedor. Manter preços transacionados e referências analíticas em categorias
separadas. Não foi encontrada uma API pública nacional reutilizável que permita
ativar imediatamente cobertura ampla de medicamentos com preço de varejo atual.

Catálogos de marketplace e APIs para vendedores enviarem estoque não comprovam
um feed de preços para terceiros. A API contratável Consulta NF-e do Serpro
exige identificação de nota conhecida; não descobre ofertas por EAN + CEP.
[Descrição oficial do serviço](https://www.gov.br/pt-br/servicos/obter-solucao-de-consulta-de-dados-de-nota-fiscal-eletronica-nfe).

### Contrato de dados e atualização contínua — ainda não implementados

1. **Identificação:** EAN/GTIN, marca/fabricante, concentração, forma farmacêutica
   e quantidade da embalagem. Correspondência por marca isolada é insuficiente.
   Embalagens diferentes não entram na mesma faixa de preço; evitar unir combinação
   a princípio ativo isolado. Novos itens comerciais não criam conteúdo científico automaticamente.
2. **Oferta contextualizada:** farmácia/filial, canal, região/CEP, estoque,
   preço da embalagem e condições (público, fidelidade, PBM, cupom, pagamento).
   Frete separado. O menor preço condicionado não é apresentado como disponível
   a qualquer paciente. [Exemplo de condições de fidelidade/PBM](https://paguemenos.vteximg.com.br/arquivos/LIVRETOPROGRAMADEFIDELIDADE-PAGUEMENOS.pdf).
3. **Rastreabilidade:** fonte e URL, observação na origem, recebimento pelo CorVIA,
   validade/expiração e tipo de preço. Refazer uma consulta não renova artificialmente
   a data de uma observação antiga. Guardar histórico e snapshot da seleção.
4. **Atualização sem deploy:** sincronização de catálogo, ingestão incremental de
   ofertas e revalidação sob demanda por trabalhadores agendados, com cache,
   limites, backoff e isolamento de falhas. Cadências/TTL devem ser definidos pelo
   SLA e licença da fonte; não prometer atualização de todos os produtos a cada minuto.
   Ofertas vencidas saem de “preço atual”, mantendo referência histórica datada.
5. **Interface:** preço da apresentação selecionada, origem, local, condições e
   data visíveis. Sem cotação elegível: “Sem oferta atual para esta apresentação/localização”.
   Totais parciais indicam itens sem preço; somar ofertas de várias farmácias não
   equivale ao valor final de uma compra, sobretudo sem frete.
6. **Privacidade e independência:** consulta inicial por produto + região, sem
   nome, CPF, diagnóstico ou receita completa do paciente. Qualquer elegibilidade
   PBM individual exige fluxo autorizado separado. Comissão comercial não altera
   ranking científico ou escolha clínica.

O PMC deve continuar acessível como **teto regulatório**, separado das ofertas;
nunca aplicar desconto arbitrário à CMED para inventar preço de balcão, nem
misturar BPS/PF/PMC com mediana de varejo.
[Definição oficial e listas CMED](https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/cmed/precos).

### Critério de contratação e aceite

- Solicitar amostra com EANs de marcas, genéricos, associações e embalagens
  distintas nas regiões atendidas; medir **EANs medicamentosos com oferta ativa ×
  região × idade da cotação**, não número total de SKUs incluindo cosméticos.
- Validar correspondência exata, atualidade, estoque e condições. Só ativar após
  testar indisponibilidade, expiração e retorno sem oferta, além do caminho de sucesso.
- Contrato deve permitir consulta automatizada, exibição a médicos/pacientes,
  atribuição, cache, histórico, eventual exportação e limites operacionais.
- Pendência externa objetiva: acesso/licença de um feed real e amostra verificável.
  Não contratar, contatar fornecedores ou vincular CNPJ por inferência desta pesquisa.

---

## Registro histórico — 11/08/2026

Registro de auditoria e decisão de arquitetura — issue #52 (nova fase:
Medicamentos + inteligência regulatória/preços + Knowledge Graph),
11/08/2026. Toda inspeção de produção descrita aqui foi read-only
(`crontab -l`, leitura de log, leitura de código) — nenhuma escrita em
`/opt/meucardio`.

## 1. Os três níveis de preço — nunca misturados

| Nível | O que é | Fonte hoje | Status |
|---|---|---|---|
| **Preço regulatório** | PF/PMC — teto de venda definido pela CMED | `backend/app/services/cmed_precos.py` | Em produção, automatizado |
| **Preço observado de mercado** | O que se paga de fato numa farmácia/rede | Nenhuma fonte própria hoje | Não implementado — arquitetura pronta (`PriceProvider`) |
| **Preço PBM/programa** | Programa de desconto/acesso do fabricante | Nenhuma fonte hoje | Não implementado |

O sistema **nunca** deve rotular PMC como "preço real de balcão" — é teto
regulado, a farmácia vende abaixo. Isso já era uma regra documentada no
projeto (ver `CLAUDE.md`, Tarefa A) e continua valendo.

## 2. Auditoria da CMED (read-only, confirmado em produção)

`infra/cmed_cron.sh` **já está instalado no crontab de produção**
(`crontab -l`, 0 6 * * *) e **já é o pipeline completo que a seção 14 do
pedido descreve**:

```
CMED (localizar_url_planilha, detecta timestamp/competência)
  ↓
compara com CmedVersao.publicado_em mais recente
  ↓ (só segue se mudou, ou forcar=True)
baixar_planilha (download)
  ↓
parsear_linhas (validação/normalização de schema — .xlsx dentro do .zip)
  ↓
casar_substancia / casar_combinacao (comparação com o catálogo local)
  ↓
INSERT em transação única (CmedVersao + CmedApresentacao) — nunca DELETE
  ↓
histórico permanente (uma linha CmedVersao por competência importada)
```

**Confirmado nos logs de produção** (`infra/cmed_cron.log`, últimas
execuções, 09 e 10/08/2026): `{'atualizado': False, 'motivo': 'mesma
versão já importada', 'publicado_em': '20260721'}` — o cron roda todo dia,
consulta a fonte oficial, e corretamente não reimporta nada porque a
competência de julho/2026 continua sendo a mais recente publicada. Isso
**é o comportamento correto**, não uma falha silenciosa: o pipeline
verifica diariamente mesmo sabendo que a publicação é mensal, exatamente
como a seção 14 pediu.

**Idempotência e não-destrutividade confirmadas por leitura de código**:
`atualizar()` só faz `INSERT`, nunca `DELETE` — uma falha na importação
nunca apaga a base anterior, porque a base anterior nunca é tocada; o
"apontar para a versão mais nova" acontece na query de leitura (via
`cmed_versao_id` mais recente), não por substituição destrutiva.

**Gap real, pequeno, registrado**: `GET /api/admin/cmed/status` devolve a
competência/contagem da última importação, mas não calcula "isto está
stale?" comparando contra a cadência esperada de publicação — só reporta o
fato bruto. Não corrigido nesta fase (baixo risco, o cron diário já é a
proteção operacional de fato); candidato a pequena melhoria futura,
mesmo padrão do achado de `check-backup-freshness.sh` da fase anterior.

## 3. Kairos (bra.kairosweb.com) — avaliado, não integrado

Pedido complementar do Rafael durante esta fase: avaliar a Kairos como
fonte complementar de inteligência de mercado (novas marcas, altas/baixas,
mudança de preço, laboratório) — nunca como substituta da CMED/ANVISA como
fonte regulatória oficial.

**O que foi possível confirmar, só por leitura pública (nenhuma tentativa
de acesso autenticado, nenhum scraping)**:

- `bra.kairosweb.com` e `br.kairosweb.com` (as duas variantes de domínio)
  devolvem **403 Forbidden** em toda página testada, inclusive a home —
  proteção Cloudflare ativa, confirmada pelo próprio comentário no
  `robots.txt` ("BEGIN Cloudflare Managed content"). **Acesso
  programático à Kairos não é tecnicamente viável neste ambiente**, com
  ou sem autorização — o site bloqueia o robô antes de qualquer decisão
  nossa sobre uso.
- O `robots.txt` público (200, acessível) declara explicitamente, via o
  protocolo IETF de Content-Signals: **`Content-Signal: search=yes,
  ai-train=no, use=reference`** — ou seja, o operador do site autoriza
  indexação por busca, mas **proíbe explicitamente treinar modelos de IA
  com o conteúdo**. Isso não impede um assistente de ler uma página
  pontualmente para responder a uma pergunta (o sinal de "ai-input" fica
  sem posição declarada), mas reforça exatamente a cautela que o pedido já
  trazia: nada de pipeline automatizado de coleta em massa sem antes
  resolver a questão de licenciamento.
- Por busca (não por acesso direto ao site), há indício forte — não
  confirmado em primeira mão — de que a Kairos é a operadora da **"Revista
  Kairos"**, uma publicação de referência de preços farmacêuticos já
  estabelecida no mercado brasileiro (categoria comparável a
  Brasíndice/ABCFarma), e que oferece um produto **"Kairos Base de
  Dados"** citado por terceiros como planilha Excel licenciada. Não foi
  possível confirmar preço, condições contratuais, frequência de
  atualização ou existência de API/feed formal — a página que descreveria
  isso (`/kairos-base-de-dados/`) também devolveu 403.

**Conclusão e recomendação, seguindo o princípio do pedido (ANVISA/CMED =
verdade regulatória; Kairos = inteligência complementar; nunca scraping
como solução principal)**:

1. **Não implementar nenhum acesso automatizado à Kairos nesta fase** — é
   tecnicamente bloqueado e teria também o problema de licenciamento não
   resolvido.
2. **Ação recomendada, comercial/humana, não técnica**: contato direto com
   a Kairos para avaliar a existência e o custo de uma base de dados
   licenciada (Excel/feed/API) — decisão do Rafael, fora do escopo desta
   sessão.
3. **A arquitetura abaixo (`PriceProvider`) já reserva o encaixe** para um
   `KairosProvider` no dia em que houver acesso legítimo — sem exigir
   nenhuma mudança estrutural quando isso acontecer.

## 4. Arquitetura multi-fonte de preços — `PriceProvider`

Implementado nesta fase como abstração real, mas deliberadamente **sem
nenhum provider novo além do que já existe (CMED)** — não há hoje uma
segunda fonte de preço observado disponível e legítima para conectar; criar
um provider vazio ou com dado fabricado violaria a régua de "nada
fabricado" deste projeto.

```python
# backend/app/services/pricing/base.py
class PriceObservation:
    source: str              # "cmed" | "kairos" | "market_partner" | "pbm"
    source_type: str         # "regulatory" | "market_intelligence" | "retail" | "pbm"
    price_type: str          # "pf" | "pmc" | "observed" | "pbm"
    observed_at: datetime
    product_id: int | None   # Drug.id, quando casado
    presentation_ref: str    # identifica a apresentação (ggrem/registro/ean)
    price: Decimal
    currency: str = "BRL"
    region: str | None       # UF, quando aplicável (alíquota ICMS)
    confidence: str          # "official" | "high" | "medium" | "estimated"
    metadata: dict
```

`CMEDProvider` é a única implementação concreta hoje — um adaptador fino
sobre `cmed_precos.py` já existente (não duplica lógica, só expõe pelo
formato `PriceObservation` comum). `MarketPartnerProvider`/`PBMProvider`/
`KairosProvider` ficam **declarados como interface, não implementados** —
cada um só ganha código quando houver uma fonte real e legítima conectada.

**Nunca implementar** `preço_real = PMC × fator_arbitrário` — nenhum
desconto médio nacional (ex. um índice tipo IDEC) substitui preço
observado real de um produto específico. Se um dia uma estimativa desse
tipo for usada para contexto analítico, ela entra rotulada explicitamente
como `confidence: "estimated"`, nunca como `"official"` nem exibida como
se fosse preço de produto individual.

## 5. Histórico de preço — intenção arquitetural, sem persistência própria

`PriceObservation` é uma dataclass imutável e datada. **Correção documental
em 11/09/2026:** isso não constitui uma tabela ou histórico persistido. Um
histórico próprio de varejo e suas agregações ainda exigem modelo persistente,
migração, ingestão e consultas; a estratégia de versões CMED não os implementa
automaticamente. Nenhuma UI de ofertas reais foi construída nesta fase.

## 6. Patrocínio — separação estrita (já é princípio do projeto)

Camada comercial (marca, fabricante, apresentação, preço, patrocínio) e
camada científica (evidência, indicação, contraindicação, segurança,
`relevance_score` clínico) permanecem estruturalmente separadas — ver
`docs/knowledge-graph.md`, seção de patrocínio, para o desenho de como
isso se aplica também ao grafo de relações.

## 7. POC de fontes de preço de varejo/institucional — 11/08/2026

Continuação da avaliação de fontes desta fase (issue #52), depois da
avaliação da Kairos (seção 3). Nenhuma mudança em produção — tudo abaixo
foi pesquisa/implementação de código, sem cadastro concluído em nenhum
provedor comercial.

### 7.1 BPS (Banco de Preços em Saúde) — IMPLEMENTADO, camada institucional real

`GET https://apidadosabertos.saude.gov.br/economia-da-saude/bps` — API
pública do Ministério da Saúde, **sem autenticação, sem cadastro**.
Confirmada funcionando ao vivo nesta sessão: consulta real por
`codigoCatmat=268856` (losartana potássica 50mg) devolveu preços reais de
compra pública em 2026 (instituição compradora, fornecedor, fabricante,
UF, data, preço unitário/total, modalidade de compra).

**Implementado**: `backend/app/services/pricing/bps_provider.py`
(`BPSProvider`, `source_type = "institutional"` — nunca confundido com
varejo, avisado explicitamente no próprio campo `metadata.aviso` de cada
observação), 6 testes (`test_pricing_bps_provider.py`), rede sempre mockada
nos testes.

**Limitação real, documentada no próprio módulo, não escondida**: a API
exige `codigoCatmat` (código do Catálogo de Materiais do governo) ou
`cnpjInstituicao` como filtro obrigatório — não busca por nome de fármaco
nem por `registroAnvisa` sozinho. **Não existe hoje nenhum crosswalk
Drug → CATMAT no catálogo** — construir um em escala exigiria baixar o
Catálogo de Materiais oficial e casar por nome, tarefa maior, fora do
escopo deste POC. O crosswalk implementado
(`CROSSWALK_CATMAT_VERIFICADO`) tem, de propósito, **só o par verificado
nesta sessão** (losartana potássica → 268856) — qualquer fármaco fora
dessa lista devolve `[]` sem tentar adivinhar o código.

### 7.2 Data Market (Cnova Tech) — avaliado, NÃO ativado

Cadastro é self-service (API key na hora, 14 dias grátis, 50 requisições,
sem cartão de crédito) — mas **as 12 categorias monitoradas
(Mercearia, Bebidas, Higiene/Beleza, Limpeza, Laticínios, Hortifruti,
Congelados, Bebê, Carnes, Pet, Padaria) não incluem farmácia/medicamento**,
confirmado na própria documentação pública do produto. Isso é forte
indício de cobertura nula/quase nula para o catálogo de medicamentos da
Corvia — a mesma régua de "não assumir cobertura" que motivou verificar em
vez de supor.

**Não ativado, por dois motivos**: (1) a baixa cobertura esperada não
justifica gastar o teste gratuito único por CNPJ da empresa; (2) mesmo
sendo self-service, criar a conta exige vincular um e-mail/CNPJ real da
Corvia — decisão que cabe ao Rafael, não a esta sessão (mesmo padrão de
"credencial/cadastro que vincula a empresa exige decisão humana" já
seguido para Kairos). **BLOCKED/NEEDS HUMAN**, não por dificuldade técnica,
mas por decisão de negócio + baixa expectativa de valor.

### 7.3 CliqueFarma — documentado, sem integração técnica encontrada

Comparador de preços de medicamentos ao consumidor, com parcerias
declaradas com farmácias em todo o Brasil. **Nenhuma API/feed B2B público
foi encontrado** nesta pesquisa (site majoritariamente voltado ao
consumidor final, sem documentação técnica de integração). Path provável
para uma integração real: contato comercial direto com a CliqueFarma —
**BLOCKED/NEEDS HUMAN** (conversa de parceria, não tarefa técnica). Nenhum
scraping foi feito ou é recomendado.

### 7.4 Resumo do estado de preço de varejo, depois desta rodada

Nenhuma fonte de **preço de varejo ao consumidor** foi ativada — Kairos
segue bloqueada por acesso (seção 3), Data Market tem cobertura
provavelmente nula para farmácia, CliqueFarma não tem integração técnica
pública. O que mudou nesta rodada é a camada **institucional**: BPS é real,
gratuita, sem cadastro, e já tem um adapter funcional — a primeira fonte de
preço além da CMED que a arquitetura `PriceProvider` de fato usa. Continua
valendo a regra central: preço institucional nunca é apresentado como
preço de varejo, e nenhuma das três camadas (regulatório/institucional/
observado de mercado) é misturada com as outras.
