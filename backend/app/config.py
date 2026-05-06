import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.sqlite")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

    # LLM (OpenAI-compatible)
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-4o-mini")

    # Embedding (OpenAI-compatible)
    EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"))
    EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", os.getenv("LLM_API_KEY", ""))
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # Vector store
    CHROMADB_DIR = os.getenv("CHROMADB_DIR", os.path.join(os.path.dirname(__file__), "..", "instance", "chromadb"))
