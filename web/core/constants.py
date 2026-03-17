"""
constants.py — Costanti condivise tra bot e web app.
Questo file NON importa da bot.py: è il punto di verità per il deployment
su ambienti dove il bot Telegram non è installato (es. Render).
"""
import os
from pathlib import Path

# Se l'env var NT_DATA_DIR è impostata (es. su Render con disco persistente),
# usa quella come root. Altrimenti usa la directory del progetto locale.
_env_data = os.environ.get("NT_DATA_DIR")
if _env_data:
    BASE_DIR = Path(_env_data)
else:
    # In locale: la root del progetto è tre livelli sopra questo file
    # web/core/constants.py → web/core → web → root
    BASE_DIR = Path(__file__).parent.parent.parent

PDF_BYTES_DIR = BASE_DIR / "data" / "pdf_bytes"

TOPICS: dict[str, str] = {
    "energia":     "⚡ Energia",
    "gioco":       "🎰 Gioco",
    "tecnologia":  "💻 Tecnologia",
    "concessioni": "📋 Concessioni",
    "altro":       "📌 Altro",
}

_NORMA_ALIASES: list[tuple[str, list[str]]] = [
    # GDPR
    ("Reg. UE 2016/679", ["gdpr", "general data protection", "regolamento generale protezione", "2016/679"]),
    # AI Act
    ("Reg. UE 2024/1689", ["ai act", "artificial intelligence act", "regolamento ia", "2024/1689"]),
    # DSA
    ("Reg. UE 2022/2065", ["dsa", "digital services act", "2022/2065"]),
    # DMA
    ("Reg. UE 2022/1925", ["dma", "digital markets act", "2022/1925"]),
    # NIS2
    ("Dir. UE 2022/2555", ["nis2", "nis 2", "2022/2555"]),
    # Data Act
    ("Reg. UE 2023/2854", ["data act", "2023/2854"]),
    # Data Governance Act
    ("Reg. UE 2022/868", ["data governance act", "dga", "2022/868"]),
    # ePrivacy
    ("Dir. 2002/58/CE", ["eprivacy", "e-privacy", "2002/58"]),
    # MiCA
    ("Reg. UE 2023/1114", ["mica", "markets in crypto", "2023/1114"]),
    # DORA
    ("Reg. UE 2022/2554", ["dora", "digital operational resilience", "2022/2554"]),
]


def _normalize_norma(norma: str) -> str:
    """
    Riconduce varianti di nome (acronimo, nome esteso, numero) alla forma canonica.
    Esempio: "GDPR" → "Reg. UE 2016/679"
    Se non trova corrispondenza, restituisce la stringa originale.
    """
    lower = norma.lower().strip()
    for canonical, aliases in _NORMA_ALIASES:
        if lower == canonical.lower():
            return canonical
        for alias in aliases:
            if alias in lower or lower in alias:
                return canonical
    return norma
