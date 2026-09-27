from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
import os
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent  # .. /src
INSTRUCTION_DIR = SRC_DIR / "agents" / "instructions"  # .. /src/agents/instruction
DOCS_DIR = SRC_DIR / "docs"  # .. /src/docs
OUTPUT_DIR = SRC_DIR / "output"  # .. /src/output
TEMP = SRC_DIR / "temp"  # .. /src/temp


def _read_env_variable(name: str) -> str:
    """Ambil env wajib. apabila gagal tampilkan pesan error"""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Environment variable '{name}' belum diatur.")
    return value


GEMINI_API_KEY = _read_env_variable("GEMINI_API_KEY")
GEMINI_MODEL = _read_env_variable("GEMINI_MODEL")
GEMINI_MODEL_TTS = _read_env_variable("GEMINI_MODEL_TTS")

SUPABASE_URL = _read_env_variable("SUPABASE_URL")
SUPABASE_KEY = _read_env_variable("SUPABASE_KEY")

TELEGRAM_BOT_TOKEN = _read_env_variable("TELEGRAM_BOT_TOKEN")
