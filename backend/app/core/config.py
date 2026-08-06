from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # Preferível deixar essas três — não a DATABASE_URL inteira — porque é
    # o que o container oficial do Postgres já lê (POSTGRES_USER/PASSWORD/DB).
    # Ter uma DATABASE_URL solta e desincronizada foi a causa de um bug real
    # de autenticação: o valor fixo abaixo ficava sempre valendo porque a
    # variável DATABASE_URL nunca era definida de fato no .env.
    postgres_user: str = "meucardio"
    postgres_password: str = "meucardio"
    postgres_db: str = "meucardio"
    postgres_host: str = "db"
    postgres_port: int = 5432

    database_url: str = ""  # deixe vazio — é montado sozinho, ver model_validator abaixo
    redis_url: str = "redis://redis:6379/0"
    jwt_secret: str = "dev-only-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 720
    content_dir: str = "/content"
    # Volume gravável para arquivos enviados pelo usuário (hoje só foto de
    # perfil). Fica fora do banco de propósito: binário em coluna infla dump e
    # backup sem necessidade. O Caddy serve o mesmo volume em /fotos/*.
    uploads_dir: str = "/uploads"
    # Exame de paciente NÃO fica junto com os uploads públicos: o volume de
    # /uploads é servido pelo Caddy, e arquivo de exame não pode ter URL
    # alcançável de fora. Este volume não é montado no Caddy — o acesso passa
    # obrigatoriamente por rota autenticada, que registra quem leu.
    exames_dir: str = "/exames-pacientes"
    # PDF assinado/emitido, cifrado com o mesmo cofre dos exames (Tarefa 4).
    # Mesma razão do exames_dir: documento clínico não pode ter URL alcançável
    # de fora do Caddy, e este volume não é montado lá — só rota autenticada
    # ou o link público com token de `documentos_publicos.py` servem o PDF.
    documentos_dir: str = "/documentos-emitidos"
    storage_encryption_key: str = ""
    # Janela de plantão para o SLA de 2h do pedido urgente. Fora dela, o
    # prazo passa a contar como eletivo (decisão do Rafael: 7h às 22h, todos
    # os dias, horário de São Paulo).
    plantao_inicio_hora: int = 7
    plantao_fim_hora: int = 22
    fuso_operacao: str = "America/Sao_Paulo"
    # --- Agenda Integrada -------------------------------------------------
    # O núcleo local fica disponível. Escrita em sistemas externos permanece
    # bloqueada por padrão até homologação explícita do conector e da conta.
    agenda_integrations_enabled: bool = True
    agenda_external_writes_enabled: bool = False
    agenda_background_sync_enabled: bool = False
    agenda_sync_lookback_days: int = 30
    agenda_sync_horizon_days: int = 365
    agenda_sync_batch_size: int = 200
    agenda_outbox_max_attempts: int = 8
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    # App OAuth do Google em modo "Testing" (teto de 100 contas na lista de
    # testador, sem API pra automatizar — confirmado 06/08/2026). Enquanto
    # True, o front pré-cadastra o pedido em vez de mandar o assinante direto
    # pro OAuth real (ver GoogleTestUserRequest). Trocar pra False só depois
    # que a verificação sensitive-scope do Google for aprovada — nunca antes,
    # senão o assinante cai na tela "Acesso bloqueado" do próprio Google.
    google_oauth_modo_teste: bool = True
    microsoft_oauth_client_id: str = ""
    microsoft_oauth_client_secret: str = ""
    microsoft_oauth_tenant: str = "common"
    traffic_provider: str = "google_routes"  # google_routes | mapbox
    google_routes_api_key: str = ""
    # Chave pública separada, restrita por HTTP referrer a corvia.med.br e
    # autorizada somente para Maps JavaScript API. Nunca reutilizar aqui a
    # chave privada do Routes, que é restrita ao IP do backend.
    google_maps_browser_api_key: str = ""
    mapbox_access_token: str = ""

    @property
    def traffic_configured(self) -> bool:
        if self.traffic_provider == "google_routes":
            return bool(self.google_routes_api_key)
        if self.traffic_provider == "mapbox":
            return bool(self.mapbox_access_token)
        return False
    admin_email: str = "admin@meucardio.local"
    admin_password: str = "troque-esta-senha"
    cors_origins: str = "http://localhost:5173,http://localhost:8080"

    # --- IA clínica --------------------------------------------------------
    ai_enabled: bool = False
    ai_provider: str = "openai"  # openai | anthropic — só pra geração de resposta
    ai_embedding_provider: str = "openai"
    # A Anthropic não oferece API de embeddings — esse campo é sempre "openai"
    # na prática, mesmo com ai_provider="anthropic". Existe como campo explícito
    # (não hardcoded) pra o dia em que outro provedor de embedding for suportado.
    ai_daily_limit: int = 50
    # 1800 era curto demais com a busca na internet ligada: cada rodada de
    # web_search consome tokens de saída em blocos de tool_use/tool_result
    # antes do texto final, e o teto baixo cortava a resposta no meio (texto
    # final vazio) ou forçava stop_reason=pause_turn sem terminar o raciocínio.
    ai_max_output_tokens: int = 4096
    ai_top_k: int = 8
    ai_max_context_chars: int = 24000
    # Desligada por padrão: dá ao assistente acesso a ferramentas que agem
    # sobre dados reais do médico (agenda, e-mail, deslocamento), não só
    # texto. Precisa estar ligada no servidor E o médico ter consentido
    # individualmente (users.ia_ferramentas_consent_em) — as duas condições,
    # não uma ou outra. Ver app/services/ia/assistant_tools.py.
    ai_assistant_tools_enabled: bool = False

    openai_api_key: str = ""
    # Confirme o identificador exato do modelo no painel da OpenAI antes do piloto.
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"

    embedding_dim: int = 1536  # text-embedding-3-small

    # --- E-mail (opcional) --------------------------------------------------
    # Se ficar em branco, o sistema não tenta enviar e-mail — reset de senha e
    # notificação de solicitação de acesso continuam funcionando pelo painel
    # de admin, sem depender disso.
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    # "Corvia <contato@corvia.med.br>" — aprovado pelo Rafael em 02/08/2026
    # (ver emails-transacionais-spec.md). O valor real de produção já está
    # gravado no .env do servidor; este default só evita divergir em quem
    # rodar sem `.env` configurado (dev local, teste).
    smtp_from: str = "Corvia <contato@corvia.med.br>"
    public_url: str = "https://corvia.med.br"

    # --- Caixa de e-mail do assinante — Zoho Mail360 (Tarefa 28) ------------
    # Mesma filosofia do SMTP acima: em branco, o recurso fica indisponível
    # (a rota devolve 503 em vez de tentar chamar uma API sem credencial) —
    # nunca simulado. `mail360_dominio` é o domínio dentro do qual o Mail360
    # cria cada caixa nativa (precisa estar previamente verificado lá).
    mail360_client_id: str = ""
    mail360_client_secret: str = ""
    mail360_refresh_token: str = ""
    mail360_dominio: str = "corvia.med.br"

    @property
    def mail360_configurado(self) -> bool:
        return bool(self.mail360_client_id and self.mail360_client_secret and self.mail360_refresh_token)

    # CorvIA Mail é cobrado à parte da assinatura principal (decisão do
    # Rafael, 30/07/2026). Preço em centavos, de propósito deixado em 0
    # ("em branco") — o Rafael define depois. Diferente do `stripe_price_id`
    # da assinatura principal (que aponta pra um Price pré-criado no painel
    # do Stripe), aqui o valor vira `price_data` inline no checkout, no mesmo
    # padrão já usado pelos cursos parceiros — assim, quando o preço for
    # definido, basta pôr o número no `.env`, sem precisar criar nada no
    # painel do Stripe antes. Enquanto for 0, o checkout de e-mail recusa com
    # 409 em vez de cobrar um valor inventado.
    corvia_mail_preco_centavos: int = 0

    @property
    def corvia_mail_preco_definido(self) -> bool:
        return self.corvia_mail_preco_centavos > 0

    # --- Stripe / Assinatura -----------------------------------------------
    stripe_publishable_key: str = ""
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    @property
    def stripe_webhook_secrets(self) -> list[str]:
        """Todos os secrets aceitos na validação de assinatura.

        Durante uma migração de domínio existem **dois endpoints ativos no
        Stripe**, um por domínio, e cada um tem secret próprio. Com um único
        secret configurado, todo evento vindo do endpoint novo é rejeitado com
        400 — e o Stripe apenas reenfileira em silêncio, sem que nada no
        sistema acuse problema. Foi medido: 400 no domínio novo enquanto o
        antigo passava.

        Aceita lista separada por vírgula justamente para a janela em que os
        dois convivem. Depois da migração, volta a ser um só.
        """
        return [s.strip() for s in (self.stripe_webhook_secret or "").split(",") if s.strip()]
    stripe_price_id: str = ""

    @property
    def smtp_configurado(self) -> bool:
        return bool(self.smtp_host and self.smtp_user and self.smtp_password)

    # --- Assinatura digital de documento clínico (Tarefa 4) -----------------
    # Mesma filosofia do Mail360/SMTP acima: em branco, o provedor fica
    # indisponível — a emissão devolve 409 explicando, nunca assina de
    # mentira. "Regra que não se flexibiliza: nunca simular a assinatura"
    # (CLAUDE.md). Cada par abaixo corresponde a um provedor do catálogo em
    # `app/services/assinatura/catalogo.py`; só ganha adaptador real (e
    # credencial preenchida) quando o Rafael conseguir a credencial daquele
    # provedor — até 02/08/2026, nenhum tinha.
    assinatura_metodo_padrao: str = "MANUAL"

    vidaas_client_id: str = ""
    vidaas_client_secret: str = ""

    @property
    def vidaas_configurado(self) -> bool:
        return bool(self.vidaas_client_id and self.vidaas_client_secret)

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @model_validator(mode="after")
    def _montar_database_url(self) -> "Settings":
        """Se DATABASE_URL não foi definida explicitamente no ambiente, monta
        a partir de POSTGRES_USER/PASSWORD/DB — assim a senha do .env sempre
        é a que a aplicação realmente usa, sem precisar duplicar em dois
        lugares."""
        if not self.database_url:
            self.database_url = (
                f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )
        return self


settings = Settings()
