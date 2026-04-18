# modules/config.py
# Gestion de la configuration FreeSmartSync

import os
import json

CONFIG_FILE = os.path.expanduser("~/.config/freesmartsync/config.json")
SYNC_STATE_FILE = ".sync_state.json"


def load_config():
    """Charge la config. Retourne {} si inexistante."""
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(cfg):
    """Sauvegarde la config."""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def is_first_run():
    """Retourne True si c'est le premier lancement."""
    cfg = load_config()
    return not cfg.get("setup_done", False)


def mark_setup_done(cfg):
    """Marque le wizard comme complété."""
    cfg["setup_done"] = True
    save_config(cfg)


def load_sync_state(local_base):
    """Charge le journal de sync. Retourne None si inexistant."""
    path = os.path.join(local_base, SYNC_STATE_FILE)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("files", []))
    except Exception:
        return None


def save_sync_state(local_base, remote_set):
    """Sauvegarde l'état de sync dans le journal."""
    from datetime import datetime
    path = os.path.join(local_base, SYNC_STATE_FILE)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "last_sync": datetime.now().isoformat(),
                "files": sorted(remote_set)
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Impossible sauvegarder le journal : {e}")


def get_free_space(path):
    """Retourne l'espace disque disponible en octets."""
    try:
        st = os.statvfs(path)
        return st.f_bavail * st.f_frsize
    except Exception:
        return 0


def format_size(size_bytes):
    """Formate une taille en octets en chaîne lisible."""
    for unit in ["o", "Ko", "Mo", "Go", "To"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} Po"
