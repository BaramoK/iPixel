"""Gestion de l'historique des envois au panneau LED."""
import json
import os
import sys
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(__file__)

HISTORY_PATH = os.path.join(BASE_DIR, "history.json")
MAX_ENTRIES = 100


def load_history() -> List[Dict[str, Any]]:
    """Charge l'historique depuis le fichier JSON."""
    if not os.path.exists(HISTORY_PATH):
        return []
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data[-MAX_ENTRIES:]
        return []
    except Exception:
        return []


def save_history(entries: List[Dict[str, Any]]):
    """Sauvegarde l'historique dans le fichier JSON."""
    try:
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(entries[-MAX_ENTRIES:], f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[HistoryManager] Erreur sauvegarde: {e}")


def add_entry(entry_type: str, label: str, data: Dict[str, Any], status: str = "success") -> Dict[str, Any]:
    """Ajoute une entrée à l'historique."""
    entries = load_history()
    entry = {
        "id": uuid.uuid4().hex[:12],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": entry_type,
        "label": label,
        "status": status,
        "data": data,
    }
    entries.append(entry)
    save_history(entries)
    return entry


def remove_entry(entry_id: str) -> bool:
    """Supprime une entrée par son ID."""
    entries = load_history()
    original_len = len(entries)
    entries = [e for e in entries if e.get("id") != entry_id]
    if len(entries) != original_len:
        save_history(entries)
        return True
    return False


def clear_history():
    """Vide complètement l'historique."""
    save_history([])
