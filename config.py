import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

def get_env_variable(var_name: str, is_required: bool = True) -> str:
    value = os.getenv(var_name)
    if is_required and not value:
        raise ValueError(f"CRITICAL ERROR: Env '{var_name}' doesn't set up in .env")
    return value or ""

# --- 1. API Keys ---
GEMINI_API_KEY = get_env_variable("GEMINI_API_KEY")
GROQ_API_KEY   = get_env_variable("GROQ_API_KEY")
COHERE_API_KEY = get_env_variable("COHERE_API_KEY")
HF_TOKEN       = get_env_variable("HF_TOKEN")

# --- 2. Model Names ---
GEMINI_MODEL = "models/gemini-flash-latest"
GROQ_MODEL   = "llama-3.3-70b-versatile"
COHERE_MODEL = "command-r7b-12-2024"
HF_MODEL     = "deepseek-ai/DeepSeek-V4-Pro"

# --- 3. Context Limits (Tokens) ---
GEMINI_CONTEXT_LIMIT = 1000000
GROQ_CONTEXT_LIMIT   = 128000
COHERE_CONTEXT_LIMIT = 128000
HF_CONTEXT_LIMIT     = 32768
MAX_TOKENS = 512
OLLAMA_CONTEXT_LIMIT = 8192

# --- 4. Conversation Settings ---
MAX_HISTORY_TURNS = 10

# --- 5. Retry Logic ---
MAX_RETRIES = 3
INITIAL_BACKOFF = 1.0  
BACKOFF_MULTIPLIER = 2.0

# --- 6. Directories ---
BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / "logs"
EXPORT_DIR = BASE_DIR / "exports"
LOG_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)


# --- 7. Default Settings ---
DEFAULT_PROVIDER = "gemini"
DEFAULT_PERSONA = "expert"

print("Config loaded successfully.")