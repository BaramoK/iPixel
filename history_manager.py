"""Gestion de l'historique des envois au panneau LED."""
import json
import os
import shutil
import sys
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(__file__)

HISTORY_PATH = os.path.join(BASE_DIR, "history.json")
ASSETS_DIR = os.path.join(BASE_DIR, "history_assets")
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


# ------------------------------------------------------------------
# Assets : copie locale des images pour un rejeu autonome
# ------------------------------------------------------------------
def store_image_asset(source_path: str, entry_id: str) -> Optional[str]:
    """Copie l'image source dans le dossier géré et retourne son chemin.

    Renvoie ``None`` si la copie échoue ou si la source n'existe pas.
    """
    if not source_path or not os.path.isfile(source_path):
        return None
    try:
        os.makedirs(ASSETS_DIR, exist_ok=True)
        ext = os.path.splitext(source_path)[1].lower() or ".bin"
        dest = os.path.join(ASSETS_DIR, f"{entry_id}{ext}")
        shutil.copy2(source_path, dest)
        return dest
    except Exception as e:
        print(f"[HistoryManager] Erreur copie asset: {e}")
        return None


def _delete_asset(entry: Dict[str, Any]):
    """Supprime le fichier asset associé à une entrée (best effort)."""
    stored = (entry.get("data") or {}).get("stored_path")
    if stored and os.path.isfile(stored):
        try:
            os.remove(stored)
        except Exception as e:
            print(f"[HistoryManager] Erreur suppression asset: {e}")


def resolve_image_path(data: Dict[str, Any]) -> str:
    """Retourne le chemin utilisable pour rejouer une image.

    Priorité au fichier copié (``stored_path``) ; repli sur le chemin
    d'origine (``path``) pour les entrées antérieures à la copie locale.
    """
    stored = data.get("stored_path")
    if stored and os.path.isfile(stored):
        return stored
    return data.get("path", "")


def ensure_image_asset(entry: Dict[str, Any]) -> Optional[str]:
    """Migration paresseuse : copie l'original d'une entrée ancienne.

    Retourne le chemin du fichier copié (ou déjà présent), sinon ``None``.
    """
    data = entry.get("data") or {}
    stored = data.get("stored_path")
    if stored and os.path.isfile(stored):
        return stored
    source = data.get("path")
    if source and os.path.isfile(source):
        new_stored = store_image_asset(source, entry.get("id", ""))
        if new_stored:
            data.setdefault("original_path", source)
            data["stored_path"] = new_stored
            _update_entry(entry.get("id"), data)
            return new_stored
    return None


def _update_entry(entry_id: str, data: Dict[str, Any]):
    """Met à jour les données d'une entrée existante."""
    entries = load_history()
    for e in entries:
        if e.get("id") == entry_id:
            e["data"] = data
            break
    save_history(entries)


def prune_orphan_assets():
    """Supprime les fichiers du dossier géré non référencés par l'historique."""
    if not os.path.isdir(ASSETS_DIR):
        return
    referenced = set()
    for e in load_history():
        stored = (e.get("data") or {}).get("stored_path")
        if stored:
            referenced.add(os.path.normcase(os.path.abspath(stored)))
    try:
        for name in os.listdir(ASSETS_DIR):
            full = os.path.normcase(os.path.abspath(os.path.join(ASSETS_DIR, name)))
            if full not in referenced:
                try:
                    os.remove(os.path.join(ASSETS_DIR, name))
                except Exception:
                    pass
    except Exception as e:
        print(f"[HistoryManager] Erreur nettoyage assets: {e}")


def add_entry(entry_type: str, label: str, data: Dict[str, Any], status: str = "success") -> Dict[str, Any]:
    """Ajoute une entrée à l'historique.

    Pour les images, le fichier est copié dans ``history_assets/`` afin de
    pouvoir rejouer l'envoi même si l'original est déplacé ou supprimé.
    """
    entries = load_history()
    entry_id = uuid.uuid4().hex[:12]
    data = dict(data or {})
    if entry_type == "image":
        source = data.get("path")
        stored = store_image_asset(source, entry_id)
        if stored:
            data["original_path"] = source
            data["stored_path"] = stored
    entry = {
        "id": entry_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": entry_type,
        "label": label,
        "status": status,
        "data": data,
    }
    entries.append(entry)
    save_history(entries)
    prune_orphan_assets()
    return entry


def remove_entry(entry_id: str) -> bool:
    """Supprime une entrée par son ID (et son asset associé)."""
    entries = load_history()
    removed = [e for e in entries if e.get("id") == entry_id]
    if not removed:
        return False
    entries = [e for e in entries if e.get("id") != entry_id]
    for e in removed:
        _delete_asset(e)
    save_history(entries)
    return True


def clear_history():
    """Vide complètement l'historique et supprime les assets associés."""
    for e in load_history():
        _delete_asset(e)
    save_history([])
