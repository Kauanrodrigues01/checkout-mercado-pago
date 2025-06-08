from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.
    """

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    MP_PUBLIC_KEY: str
    MP_ACCESS_TOKEN: str
    MP_BASE_API_URL: str = 'https://api.mercadopago.com'
    NOTIFICATION_URL: str = 'https://yourdomain.com/notifications'
    DEFAULT_TIMEZONE: str = 'America/Sao_Paulo'


settings = Settings()
