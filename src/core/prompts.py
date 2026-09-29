import src.core.env as env

from pathlib import Path
from functools import lru_cache
from supabase import Client, create_client


@lru_cache
def load_instruction(name: str) -> str:
    """Baca file instruksi berdasarkan nama file, contoh: load_instruction('agent-lead')"""
    path = env.INSTRUCTION_DIR / f"{name}.md"  # src/agents/Instructions/agent-lead.md

    if not path.exists():
        raise FileNotFoundError(
            f"File instruksitidak ditemukan di {path}. \n",
            f"cek nama file di {env.INSTRUCTION_DIR} dan memiliki ekstensi .md",
        )
    return path.read_text(
        encoding="utf-8"
    )  # utf-8 berguna agar karakter non-ascii seperti emoji bisa terbaca
