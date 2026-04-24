import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY   = os.getenv("GOOGLE_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
SERPAPI_API_KEY  = os.getenv("SERPAPI_API_KEY", "")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_ENV     = os.getenv("PINECONE_ENV", "us-east-1")

PINECONE_INDEX_NAME = "business-context"
PINECONE_CLOUD      = "aws"
PINECONE_REGION     = "us-east-1"
EMBEDDING_MODEL     = "text-embedding-ada-002"
EMBEDDING_DIMENSION = 1536

DEFAULT_MODEL    = "gpt-4o"
AVAILABLE_MODELS = [
    "gpt-4o",
    "gpt-4-turbo",
    "gpt-3.5-turbo",
    "gemini-1.5-flash",
    "deepseek-reasoner",
]

WEB_CACHE_TTL_HOURS = 1
WEB_CACHE_MAX_SIZE  = 50
MIN_CONTEXT_CHARS   = 200
CHUNK_SIZE          = 1000
CHUNK_OVERLAP       = 200
RAG_TOP_K           = 3
