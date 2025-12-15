from pydantic_settings import BaseSettings
from pydantic import AnyUrl, Field
from typing import List, Optional


class Settings(BaseSettings):
    app_name: str = "Breathe AI API"
    environment: str = Field(default="development")

    # Mongo
    mongo_uri: AnyUrl | str = Field(default="mongodb://localhost:27017")
    mongo_db: str = Field(default="breathe_ai")
    
    GROQ_API_KEY: str

    # JWT
    jwt_secret_key: str = Field(default="change-this-secret")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=21600)
    refresh_token_expire_days: int = Field(default=15)

    # CORS
    cors_allow_origins: List[str] = Field(default_factory=lambda: ["*"])

    # Social providers
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None

    # Email settings
    mail_username: Optional[str] = None
    mail_password: Optional[str] = None
    mail_from: Optional[str] = None
    mail_from_name: str = "Breathe AI"
    mail_port: int = 587
    mail_server: str = "smtp.gmail.com"
    mail_starttls: bool = True
    mail_ssl_tls: bool = False
    use_credentials: bool = True
    validate_certs: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
