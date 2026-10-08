"""Gestion simple du fichier de configuration JSON."""
import json
import os
import sys

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(__file__)

CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

DEFAULT_CONFIG = {
    "mac_address": "",
    "last_text": "Hello World!",
    "image_resize": "FIT",
    "image_slot": 0,
    "text_color": "00ff00",
    "text_bg_color": "000000",
    "text_animation": "SCROLL_LEFT",
    "text_speed": 50,
    "text_slot": 0,
    "text_font_path": "",
    "text_font_size": 16,
    "brightness": 50,
    "orientation": 0,
    "clock_style": 1,
    "clock_24h": True,
    "clock_date": True,
    "exit_clock_slot": 100,
}


def load_config():
    """Charge la configuration depuis le fichier JSON."""
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        merged = DEFAULT_CONFIG.copy()
        merged.update(cfg)
        return merged
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(cfg):
    """Sauvegarde la configuration dans le fichier JSON."""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[ConfigManager] Erreur sauvegarde config: {e}")
