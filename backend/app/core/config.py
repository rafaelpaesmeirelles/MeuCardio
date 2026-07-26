from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Preferível deixar essas três — não a DATABASE_URL inteira — porque é
    # o que o container oficial do Postgres já lê (POSTGRES_USER/PASSWORD/DB).
    # Ter uma DATABASE_URL solta e desincronizada foi a causa de um bug real
    # de autenticação: o valor fixo abaixo ficava sempre valendo porque a
    # variável DATABASE_URL nunca era definida de fato no .env.
    postgres_user: str = "cardiobene"
    postgres_password: str = "cardiobene"
    postgres_db: str = "cardiobene"
    postgres_host: str = "db"
    postgres_port: int = 5432

    database_url: str = ""  # deixe vazio — é montado sozinho, ver model_validator abaixo
    redis_url: str = "redis://redis:6379/0"
    jwt_secret: str = "dev-only-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 720
    content_dir: str = "/content"
    admin_email: str = "admin@cardiobene.local"
    admin_password: str = "cardiobene"
    cors_origins: str = "http://localhost:5173,http://localhost:8080"

    # --- IA clínica --------------------------------------------------------
    ai_enabled: bool = False
    ai_provider: str = "openai"  # openai | anthropic
    ai_daily_limit: int = 50
    ai_max_output_tokens: int = 1800
    ai_top_k: int = 8
    ai_max_context_chars: int = 24000

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
    smtp_from: str = "MeuCardio <nao-responda@meucardio.med.br>"
    public_url: str = "https://meucardio.med.br"

    @property
    def smtp_configurado(self) -> bool:
        return bool(self.smtp_host and self.smtp_user and self.smtp_password)

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

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
