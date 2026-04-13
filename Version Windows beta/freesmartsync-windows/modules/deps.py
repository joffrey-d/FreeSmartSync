# modules/deps.py — FreeSmartSync Windows v0.8.6.2
# Sur Windows les dépendances sont embarquées — ce module gère ADB uniquement

import os
import subprocess
import shutil


def detect_distrib():
    """Sur Windows, pas de gestionnaire de paquets — ADB doit être installé manuellement."""
    return "Windows", "winget", "winget install Google.PlatformTools", False


def check_adb():
    """Vérifie si ADB est disponible (PATH ou dossier local)."""
    # Chercher adb.exe dans le PATH
    if shutil.which("adb"):
        return True
    # Chercher dans le dossier local tools/
    local_adb = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "tools", "adb.exe"
    )
    return os.path.exists(local_adb)


def check_python3():
    return True  # Python est embarqué dans l'exe


def check_pyqt5():
    try:
        import PyQt5
        return True
    except ImportError:
        return False


def get_deps_status():
    return {"adb": check_adb(), "python": check_python3(), "pyqt5": check_pyqt5()}


def all_deps_ok():
    return all(get_deps_status().values())


def install_deps(distrib_name, pkg_manager, install_cmd,
                 use_su=False, password=None):
    """Sur Windows : ouvrir le guide d'installation ADB."""
    import webbrowser
    webbrowser.open("https://developer.android.com/studio/releases/platform-tools")
    return False, (
        "ADB (Android Platform Tools) doit être installé manuellement.\n\n"
        "1. Téléchargez Platform Tools : https://developer.android.com/studio/releases/platform-tools\n"
        "2. Extrayez dans C:\\Android\\platform-tools\\\n"
        "3. Ajoutez ce dossier à votre variable PATH\n"
        "4. Redémarrez FreeSmartSync"
    )
