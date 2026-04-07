# modules/deps.py — Détection distrib + installation dépendances

import os
import subprocess
import shutil


def detect_distrib():
    """
    Détecte la distribution Linux.
    Retourne (nom, pkg_manager, install_cmd, use_su)
      use_su=True  → utiliser 'su -c' (Mageia : user pas dans sudoers)
      use_su=False → utiliser 'sudo'
    """
    os_release = {}
    try:
        with open("/etc/os-release") as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    os_release[k] = v.strip('"')
    except Exception:
        pass

    did      = os_release.get("ID", "").lower()
    did_like = os_release.get("ID_LIKE", "").lower()
    dname    = os_release.get("PRETTY_NAME",
               os_release.get("NAME", "Linux inconnu"))

    # ── Debian / Ubuntu / Mint / Zorin / Pop / GLF-OS (base Ubuntu/Debian) ──
    if (did in ("ubuntu", "debian", "linuxmint", "pop", "zorin",
                "elementary", "kali", "parrot", "lmde")
            or "debian" in did_like or "ubuntu" in did_like):
        return (dname, "apt",
                "apt-get install -y android-tools-adb python3-pyqt5",
                False)

    # ── Fedora / RHEL / Nobara ──
    elif (did in ("fedora", "rhel", "centos", "rocky", "almalinux",
                  "nobara", "ultramarine")
            or "fedora" in did_like or "rhel" in did_like):
        return (dname, "dnf",
                "dnf install -y android-tools python3-qt5",
                False)

    # ── Arch / Manjaro ──
    elif (did in ("arch", "manjaro", "endeavouros", "artix", "garuda")
            or "arch" in did_like):
        return (dname, "pacman",
                "pacman -S --noconfirm android-tools python-pyqt5",
                False)

    # ── openSUSE ──
    elif (did in ("opensuse", "suse", "opensuse-leap", "opensuse-tumbleweed")
            or "suse" in did_like):
        return (dname, "zypper",
                "zypper install -y android-tools python3-qt5",
                False)

    # ── Mageia / OpenMandriva — use_su=True car sudo souvent non configuré ──
    elif did in ("mageia", "openmandriva") or "mageia" in did_like:
        return (dname, "urpmi",
                "urpmi --auto android-tools python3-pyqt5",
                True)   # ← su -c au lieu de sudo

    # ── NixOS / GLF-OS ──
    elif (did in ("nixos", "glf-os")
            or "nix" in did_like or "glf" in did
            or shutil.which("nix-env")):
        return (dname, "nix",
                "nix-env -iA nixpkgs.android-tools nixpkgs.python3Packages.pyqt5",
                False)

    # ── Fallback : détecter par binaire présent ──
    else:
        if shutil.which("apt-get"):
            return (dname, "apt",
                    "apt-get install -y android-tools-adb python3-pyqt5", False)
        elif shutil.which("dnf"):
            return (dname, "dnf",
                    "dnf install -y android-tools python3-qt5", False)
        elif shutil.which("pacman"):
            return (dname, "pacman",
                    "pacman -S --noconfirm android-tools python-pyqt5", False)
        elif shutil.which("zypper"):
            return (dname, "zypper",
                    "zypper install -y android-tools python3-qt5", False)
        elif shutil.which("urpmi"):
            return (dname, "urpmi",
                    "urpmi --auto android-tools python3-pyqt5", True)
        elif shutil.which("nix-env"):
            return (dname, "nix",
                    "nix-env -iA nixpkgs.android-tools nixpkgs.python3Packages.pyqt5", False)
        else:
            return (dname, "unknown", "", False)


def check_adb():    return shutil.which("adb") is not None
def check_python3():return shutil.which("python3") is not None
def check_pyqt5():
    try:
        import PyQt5; return True
    except ImportError:
        return False


def get_deps_status():
    return {"adb": check_adb(), "python": check_python3(), "pyqt5": check_pyqt5()}


def all_deps_ok():
    return all(get_deps_status().values())


def install_deps(distrib_name, pkg_manager, install_cmd,
                 use_su=False, password=None):
    """
    Installe les dépendances.
    - use_su=True + password → su -c "cmd" root  (Mageia)
    - use_su=False + password → sudo -S cmd
    - sans password → sudo cmd (NOPASSWD ou déjà authentifié)
    """
    if not install_cmd:
        return False, (
            "Gestionnaire de paquets non reconnu.\n\n"
            "Installez manuellement :\n"
            "  ADB   : android-tools ou android-tools-adb\n"
            "  PyQt5 : python3-pyqt5 ou python-pyqt5\n\n"
            "Puis relancez FreeSmartSync."
        )

    try:
        if use_su and password:
            # Mageia : su -c "commande" root  — mot de passe root demandé
            proc = subprocess.run(
                ["su", "-c", install_cmd, "root"],
                input=password + "\n",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=180
            )
        elif password:
            # sudo -S : lit le mot de passe sur stdin
            proc = subprocess.run(
                ["sudo", "-S"] + install_cmd.split(),
                input=password + "\n",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=180
            )
        elif use_su:
            # su sans mot de passe (rare)
            proc = subprocess.run(
                ["su", "-c", install_cmd, "root"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=180
            )
        else:
            # sudo sans mot de passe (NOPASSWD ou session déjà auth)
            proc = subprocess.run(
                ["sudo"] + install_cmd.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=180
            )

        return (proc.returncode == 0,
                proc.stdout if proc.returncode == 0 else proc.stderr or proc.stdout)

    except subprocess.TimeoutExpired:
        return False, "Timeout — vérifiez votre connexion internet."
    except Exception as e:
        return False, str(e)
