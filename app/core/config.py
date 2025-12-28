from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 horas
    
    # API
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "MedControl API"
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: str = "https://medcontrol-paraizodaniels-projects.vercel.app,http://localhost:51731"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Converte string de origins para lista"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
