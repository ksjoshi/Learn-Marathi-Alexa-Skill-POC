from pydantic_settings import BaseSettings
from typing import Dict, Any

class Settings(BaseSettings):
    # Database Configuration
    DB_NAME: str = "marathi_knowledge"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"

    @property
    def DB_CONFIG(self) -> Dict[str, str]:
        return {
            "dbname": self.DB_NAME,
            "user": self.DB_USER,
            "password": self.DB_PASSWORD,
            "host": self.DB_HOST,
            "port": self.DB_PORT
        }

    # Ollama Configuration
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_TRANSLATE_MODEL: str = "translategemma"
    OLLAMA_GENERATE_MODEL: str = "llama3.2"

    # Embedding Model Configuration
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Marathi Skill API"

settings = Settings()
