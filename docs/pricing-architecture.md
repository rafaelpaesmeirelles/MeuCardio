# Arquitetura de preços e inteligência regulatória de medicamentos

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

## 5. Histórico de preço — modelo pronto, sem UI nova

`PriceObservation` é, por desenho, um registro imutável e datado — histórico
já é a estrutura natural (basta não fazer UPDATE, só INSERT, mesmo padrão
já usado em `CmedApresentacao`/`CmedVersao`). Métricas futuras (menor
preço observado, mediana, variação 30/90 dias) são agregações sobre essa
tabela, não exigem mudança de schema. Nenhuma UI nova nesta fase — a
arquitetura permite, a interface não foi construída (não há dado real
ainda para mostrar).

## 6. Patrocínio — separação estrita (já é princípio do projeto)

Camada comercial (marca, fabricante, apresentação, preço, patrocínio) e
camada científica (evidência, indicação, contraindicação, segurança,
`relevance_score` clínico) permanecem estruturalmente separadas — ver
`docs/knowledge-graph.md`, seção de patrocínio, para o desenho de como
isso se aplica também ao grafo de relações.
