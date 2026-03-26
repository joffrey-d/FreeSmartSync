# modules/deps.py
# Détection de la distribution et installation des dépendances

import os
import subprocess
import shutil


def detect_distrib():
    """
    Détecte la distribution Linux via /etc/os-release.
    Retourne (nom_distrib, gestionnaire_paquets, commande_install)
    """
    os_release = {}
    try:
        with open("/etc/os-release", "r") as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    os_release[k] = v.strip('"')
    except Exception:
        pass

    distrib_id = os_release.get("ID", "").lower()
    distrib_id_like = os_release.get("ID_LIKE", "").lower()
    distrib_name = os_release.get("NAME", "Linux inconnue")

    # Détection gestionnaire de paquets
    if distrib_id in ("ubuntu", "debian", "linuxmint", "pop") or "debian" in distrib_id_like:
        return distrib_name, "apt", "sudo apt install -y android-tools-adb python3-pyqt5"
    elif distrib_id in ("fedora", "rhel", "centos", "rocky", "almalinux") or "fedora" in distrib_id_like:
        return distrib_name, "dnf", "sudo dnf install -y android-tools python3-qt5"
    elif distrib_id in ("arch", "manjaro", "endeavouros") or "arch" in distrib_id_like:
        return distrib_name, "pacman", "sudo pacman -S --noconfirm android-tools python-pyqt5"
    elif distrib_id in ("opensuse", "suse", "opensuse-leap", "opensuse-tumbleweed") or "suse" in distrib_id_like:
        return distrib_name, "zypper", "sudo zypper install -y android-tools python3-qt5"
    elif distrib_id in ("mageia",) or "mageia" in distrib_id_like:
        return distrib_name, "urpmi", "sudo urpmi android-tools python3-pyqt5"
    elif distrib_id in ("nixos",) or "nixos" in distrib_id_like:
        return distrib_name, "nix", "nix-env -iA nixpkgs.android-tools nixpkgs.python3 nixpkgs.python3Packages.pyqt5"
    else:
        return distrib_name, "unknown", ""


def check_adb():
    """Vérifie si ADB est installé."""
    return shutil.which("adb") is not None


def check_python3():
    """Vérifie si Python3 est installé."""
    return shutil.which("python3") is not None


def check_pyqt5():
    """Vérifie si PyQt5 est installé."""
    try:
        import PyQt5
        return True
    except ImportError:
        return False


def get_deps_status():
    """Retourne le statut de toutes les dépendances."""
    return {
        "adb":    check_adb(),
        "python": check_python3(),
        "pyqt5":  check_pyqt5(),
    }


def all_deps_ok():
    """Retourne True si toutes les dépendances sont présentes."""
    status = get_deps_status()
    return all(status.values())


def install_deps(distrib_name, pkg_manager, install_cmd, password=None):
    """
    Lance l'installation des dépendances manquantes.
    Retourne (success, output)
    """
    if not install_cmd:
        return False, "Gestionnaire de paquets non supporté."

    try:
        if password:
            # Utilise sudo avec mot de passe via stdin
            proc = subprocess.run(
                ["sudo", "-S"] + install_cmd.replace("sudo ", "").split(),
                input=password + "\n",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=120
            )
        else:
            proc = subprocess.run(
                install_cmd.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=120
            )
        if proc.returncode == 0:
            return True, proc.stdout
        else:
            return False, proc.stderr
    except subprocess.TimeoutExpired:
        return False, "Timeout — installation trop longue."
    except Exception as e:
        return False, str(e)
