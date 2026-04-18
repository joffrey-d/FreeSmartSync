#!/usr/bin/env bash
# Installer-FreeSmartSync.sh
# Installation graphique FreeSmartSync — double-clic et c'est parti !
# Aucun terminal nécessaire.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# S'assurer que les scripts sont exécutables (perms parfois perdues à l'extraction)
chmod +x "$SCRIPT_DIR/CLIC-DROIT-Executer-pour-installer-FreeSmartSync.sh" 2>/dev/null || true
chmod +x "$SCRIPT_DIR/freesmartsync.py" 2>/dev/null || true
INSTALL_DIR="$HOME/.local/share/freesmartsync"
DESKTOP_FILE="$HOME/.local/share/applications/freesmartsync.desktop"
APP_NAME="FreeSmartSync"

# ─────────────────────────────────────────────
# Détection outil graphique disponible
# ─────────────────────────────────────────────

detect_gui_tool() {
    if command -v kdialog &> /dev/null; then
        echo "kdialog"
    elif command -v zenity &> /dev/null; then
        echo "zenity"
    elif command -v qarma &> /dev/null; then
        echo "qarma"
    else
        echo "none"
    fi
}

GUI=$(detect_gui_tool)

# ─────────────────────────────────────────────
# Fonctions popup universelles
# ─────────────────────────────────────────────

popup_info() {
    local msg="$1"
    local title="${2:-$APP_NAME}"
    case "$GUI" in
        kdialog) kdialog --title "$title" --msgbox "$msg" ;;
        zenity|qarma) zenity --info --title="$title" --text="$msg" --width=420 ;;
        none) echo "[INFO] $msg" ;;
    esac
}

popup_error() {
    local msg="$1"
    local title="${2:-$APP_NAME — Erreur}"
    case "$GUI" in
        kdialog) kdialog --title "$title" --error "$msg" ;;
        zenity|qarma) zenity --error --title="$title" --text="$msg" --width=420 ;;
        none) echo "[ERREUR] $msg" ;;
    esac
}

popup_question() {
    # Retourne 0 si Oui, 1 si Non
    local msg="$1"
    local title="${2:-$APP_NAME}"
    case "$GUI" in
        kdialog) kdialog --title "$title" --yesno "$msg" ;;
        zenity|qarma) zenity --question --title="$title" --text="$msg" --width=420 ;;
        none) return 0 ;;
    esac
}

popup_password() {
    local msg="$1"
    local title="${2:-$APP_NAME}"
    case "$GUI" in
        kdialog) kdialog --title "$title" --password "$msg" ;;
        zenity|qarma) zenity --password --title="$title" --text="$msg" ;;
        none) echo "" ;;
    esac
}

# ─ Barre de progression — logique séparée zenity vs kdialog ───
#
# ZENITY  : lit stdin via FIFO → envoyer "50", "# message", "100"
#           → --auto-close se déclenche sur 100 : fermeture propre
#
# KDIALOG : utilise DBus, ignore stdin → FIFO inutile ici
#           → on le lance en arrière-plan et on le tue (kill) à la fin
#           → c'est la seule méthode fiable sur KDE Plasma
# ───────────────────────────────────────────────────────────────
_FIFO=""
_KDIALOG_PID=""

open_progress() {
    local title="$1"
    local msg="$2"
    case "$GUI" in
        kdialog)
            # KDE : lancer en arrière-plan, tuer avec kill à close_progress
            kdialog --title "$title" --progressbar "$msg" 0 &
            _KDIALOG_PID=$!
            ;;
        zenity|qarma)
            # GNOME/Cinnamon : FIFO → stdin → auto-close sur 100
            _FIFO=$(mktemp -u /tmp/fss_prog_XXXXXX)
            mkfifo "$_FIFO"
            zenity --progress \
                --title="$title" \
                --text="$msg" \
                --percentage=0 \
                --auto-close \
                --no-cancel \
                --width=420 < "$_FIFO" &
            exec 9>"$_FIFO"
            ;;
    esac
}

step_progress() {
    local pct="$1"
    local msg="${2:-}"
    case "$GUI" in
        zenity|qarma)
            [ -n "$msg" ] && echo "# $msg" >&9 2>/dev/null || true
            echo "$pct" >&9 2>/dev/null || true
            ;;
        kdialog)
            # kdialog DBus : pas de mise à jour de pourcentage nécessaire
            # la barre est indéterminée (0), elle s'anime toute seule
            true
            ;;
    esac
}

close_progress() {
    case "$GUI" in
        zenity|qarma)
            # Envoyer 100 → auto-close → fermeture propre
            echo "100" >&9 2>/dev/null || true
            exec 9>&- 2>/dev/null || true
            [ -n "$_FIFO" ] && rm -f "$_FIFO" 2>/dev/null || true
            sleep 0.3
            ;;
        kdialog)
            # KDE : tuer directement le processus kdialog
            [ -n "$_KDIALOG_PID" ] && kill "$_KDIALOG_PID" 2>/dev/null || true
            wait "$_KDIALOG_PID" 2>/dev/null || true
            ;;
    esac
    # Sécurité finale
    pkill -f "zenity --progress" 2>/dev/null || true
    pkill -f "kdialog --progressbar" 2>/dev/null || true
}

# Alias de compatibilité
start_progress() {
    open_progress "$1" "$2"
    echo "compat:0"
}

# ─────────────────────────────────────────────
# Détection distribution
# ─────────────────────────────────────────────

detect_distrib() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        # Retourne l'ID + ID_LIKE pour mieux détecter les dérivées
        echo "$ID ${ID_LIKE:-}"
    else
        echo "unknown"
    fi
}

is_debian_based() {
    local info="$1"
    echo "$info" | grep -qiE "ubuntu|debian|mint|zorin|pop|neon|elementary|kali|parrot|mx|deepin|lmde|peppermint|bodhi|tails|devuan|raspbian|buntu"
}

is_fedora_based() {
    local info="$1"
    echo "$info" | grep -qiE "fedora|rhel|centos|rocky|almalinux|nobara|ultramarine|bazzite"
}

is_arch_based() {
    local info="$1"
    echo "$info" | grep -qiE "arch|manjaro|endeavouros|garuda|artix|cachyos|crystal"
}

is_suse_based() {
    local info="$1"
    echo "$info" | grep -qiE "opensuse|suse|tumbleweed|leap"
}

is_mageia_based() {
    local info="$1"
    echo "$info" | grep -qiE "mageia|openmandriva"
}

get_install_cmd() {
    local distrib="$1"
    if is_debian_based "$distrib"; then
        echo "apt-get install -y android-tools-adb python3 python3-pyqt5"
    elif is_fedora_based "$distrib"; then
        echo "dnf install -y android-tools python3 python3-qt5"
    elif is_arch_based "$distrib"; then
        echo "pacman -S --noconfirm android-tools python python-pyqt5"
    elif is_suse_based "$distrib"; then
        echo "zypper install -y android-tools python3 python3-qt5"
    elif is_mageia_based "$distrib"; then
        echo "urpmi android-tools python3 python3-qt5"
    elif echo "$distrib" | grep -qiE "nixos|glf"; then
        # GLF-OS/NixOS : on utilise nix-env -iA avec le channel courant
        # Plusieurs tentatives car le nom du paquet PyQt5 varie selon la version
        echo ""  # GLF-OS géré directement dans le bloc dinstallation
    else
        echo ""
    fi
}

# ─────────────────────────────────────────────
# Vérification dépendances
# ─────────────────────────────────────────────

check_deps() {
    local missing=""
    command -v adb &>/dev/null    || missing="$missing adb"
    command -v python3 &>/dev/null || missing="$missing python3"
    python3 -c "import PyQt5" &>/dev/null || missing="$missing python3-pyqt5"
    echo "$missing"
}

# ─────────────────────────────────────────────
# DÉBUT INSTALLATION
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# Détection si déjà installé
# ─────────────────────────────────────────────

# Détection installation existante (chemin entre guillemets pour espaces)
if [ -d "$INSTALL_DIR" ] || [ -f "$DESKTOP_FILE" ] || [ -f "$HOME/.local/share/applications/freesmartsync.desktop" ]; then

    case "$GUI" in
        kdialog)
            CHOICE=$(kdialog --title "$APP_NAME — Déjà installé" \
                --menu "FreeSmartSync est déjà installé.\n\nQue souhaitez-vous faire ?" \
                "reinstall" "Réinstaller / Mettre à jour" \
                "uninstall" "Désinstaller FreeSmartSync" \
                "cancel" "Annuler")
            ;;
        zenity|qarma)
            CHOICE=$(zenity --list \
                --title="$APP_NAME — Déjà installé" \
                --text="FreeSmartSync est déjà installé.\n\nQue souhaitez-vous faire ?" \
                --column="id" --column="Action" \
                --hide-column=1 \
                "reinstall" "🔄 Réinstaller / Mettre à jour les fichiers" \
                "uninstall" "🗑️ Désinstaller FreeSmartSync" \
                --width=480 --height=200 2>/dev/null)
            [ -z "$CHOICE" ] && CHOICE="cancel"
            ;;
        *)
            CHOICE="reinstall"
            ;;
    esac

    case "$CHOICE" in
        reinstall)
            popup_info \
"🔄 Réinstallation en cours...

Les fichiers vont être mis à jour.
Votre configuration sera conservée." \
"$APP_NAME — Réinstallation"
            [ -n "$INSTALL_DIR" ] && [ "$INSTALL_DIR" != "/" ] && rm -rf "$INSTALL_DIR"
            rm -f "$DESKTOP_FILE"
            ;;
        uninstall)
            # ── Lire le chemin de sauvegarde configuré ──
            SAVE_DIR=""
            CFG="$HOME/.config/freesmartsync/config.json"
            if [ -f "$CFG" ]; then
                SAVE_DIR=$(python3 -c "
import json,os
try:
    d=json.load(open('$CFG'))
    print(d.get('local_base',''))
except: pass
" 2>/dev/null)
            fi
            SAVE_INFO=""
            [ -n "$SAVE_DIR" ] && SAVE_INFO="
⚠️  Répertoire de sauvegarde : $SAVE_DIR
    (vos fichiers synchronisés — NON supprimé)"

            # ── Question 1 : conserver config + profils ? ──
            popup_question "Désinstallation de FreeSmartSync

Ce qui sera TOUJOURS supprimé :
  • L'application et ses fichiers
  • Les raccourcis (menu + Bureau)
$SAVE_INFO

Voulez-vous CONSERVER votre configuration et vos profils ?

OUI → profils et paramètres conservés (retrouvés à la réinstallation)
NON → tout est supprimé définitivement" "$APP_NAME — Désinstallation"
            KEEP_CONFIG=$?

            if [ $KEEP_CONFIG -eq 0 ]; then
                popup_info "Les profils et paramètres seront conservés dans :
$HOME/.config/freesmartsync/" "$APP_NAME"
            else
                rm -rf "$HOME/.config/freesmartsync"
            fi

            # ── Suppression de l'application ──
            [ -n "$INSTALL_DIR" ] && [ "$INSTALL_DIR" != "/" ] && rm -rf "$INSTALL_DIR"
            rm -f "$DESKTOP_FILE"
            rm -f "$HOME/Bureau/FreeSmartSync.desktop" 2>/dev/null || true
            rm -f "$HOME/Desktop/FreeSmartSync.desktop" 2>/dev/null || true
            rm -f "$HOME/.local/share/icons/hicolor/256x256/apps/freesmartsync.png" 2>/dev/null || true
            update-desktop-database "$HOME/.local/share/applications/" 2>/dev/null || true

            popup_info "✅ FreeSmartSync a été désinstallé.

Note : ADB et Python ne sont pas supprimés
(ils peuvent être utilisés par d'autres logiciels)." "$APP_NAME"
            exit 0
            ;;
        *)
            popup_info "Opération annulée." "$APP_NAME"
            exit 0
            ;;
    esac

else
    popup_info \
"Bienvenue dans l'installation de FreeSmartSync !

FreeSmartSync synchronise votre smartphone Android
avec votre ordinateur Linux, dans les deux sens.

Cliquez sur OK pour commencer l'installation." \
"$APP_NAME — Installation"
fi

# Vérification dépendances
MISSING=$(check_deps)
DISTRIB_INFO=$(detect_distrib)
INSTALL_CMD=$(get_install_cmd "$DISTRIB_INFO")

if [ -n "$MISSING" ]; then

    if [ -z "$INSTALL_CMD" ]; then
        popup_error \
"Votre distribution Linux n'est pas encore reconnue
par FreeSmartSync.

Rendez-vous sur notre page GitHub pour obtenir
de l'aide ou signaler votre distribution :
github.com/freesmartsync-beta" \
"$APP_NAME — Distribution non supportée"
        exit 1
    fi

    popup_question \
"Des outils manquants ont été détectés :
$MISSING

FreeSmartSync va les installer automatiquement.
Votre mot de passe administrateur sera demandé.

Continuer ?" \
"$APP_NAME — Dépendances manquantes"

    if [ $? -ne 0 ]; then
        popup_info "Installation annulée." "$APP_NAME"
        exit 0
    fi

    # ── Installation sécurisée des dépendances ──────────────────────────────────
    # Méthode 1 : pkexec (Polkit) — ouvre la fenêtre native du système, gère
    #             sudo ET su selon la distro. Aucun mot de passe en mémoire.
    # Méthode 2 : su -c — fallback pour Mageia/urpmi (utilisateur non sudoer)
    # Méthode 3 : sudo — fallback classique
    # ─────────────────────────────────────────────────────────────────────────
    INSTALL_LOG=$(mktemp)

    INSTALL_STATUS=1

    # ── Stratégie selon la distribution ──────────────────────────────────────
    # GLF-OS/NixOS : nix-env avec tentative de plusieurs noms de paquets
    # Mageia : su -c en direct (l'user n'est pas sudoer, pkexec ne trouve pas urpmi)
    # Autres : pkexec d'abord (fenêtre native Polkit), puis sudo en fallback
    # ─────────────────────────────────────────────────────────────────────────

    if echo "$DISTRIB_INFO" | grep -qiE "nixos|glf"; then
        # Nix : essayer plusieurs variantes du paquet PyQt5
        for NIX_QT in "python3Packages.pyqt5" "python39Packages.pyqt5" "python310Packages.pyqt5" "python311Packages.pyqt5"; do
            if nix-env -iA "nixpkgs.$NIX_QT" > "$INSTALL_LOG" 2>&1; then
                INSTALL_STATUS=0
                break
            fi
        done
        # Installer ADB séparément (nom stable)
        if [ $INSTALL_STATUS -eq 0 ]; then
            nix-env -iA nixpkgs.android-tools nixpkgs.python3 >> "$INSTALL_LOG" 2>&1 || true
        fi
    elif is_mageia_based "$DISTRIB_INFO"; then
        # Mageia / OpenMandriva : su -c avec mot de passe root
        if [ "$GUI" = "kdialog" ]; then
            ROOT_PASS=$(kdialog --title "$APP_NAME — Mot de passe root"                 --password "Entrez le mot de passe root pour installer les dependances :")
        else
            ROOT_PASS=$(zenity --password                 --title="$APP_NAME — Mot de passe root" 2>/dev/null)
        fi
        if [ -n "$ROOT_PASS" ]; then
            echo "$ROOT_PASS" | su -c "urpmi --auto android-tools python3 python3-qt5"                 > "$INSTALL_LOG" 2>&1
            INSTALL_STATUS=$?
        fi
        unset ROOT_PASS
    else
        # Méthode 1 : pkexec (Polkit) — universel sur Fedora/Ubuntu/Zorin
        if command -v pkexec &>/dev/null; then
            pkexec bash -c "$INSTALL_CMD" > "$INSTALL_LOG" 2>&1
            INSTALL_STATUS=$?
            # Vérifier que l'installation a vraiment marché (pkexec peut retourner 0
            # même si la commande n'a rien fait)
            if [ $INSTALL_STATUS -eq 0 ]; then
                python3 -c "import PyQt5" 2>/dev/null || INSTALL_STATUS=99
            fi
        fi

        # Méthode 2 : sudo (fallback si pkexec absent ou insuffisant)
        if [ $INSTALL_STATUS -ne 0 ]; then
            if [ "$GUI" = "kdialog" ]; then
                SUDO_PASS=$(kdialog --title "$APP_NAME — Authentification"                     --password "Entrez votre mot de passe administrateur :")
            else
                SUDO_PASS=$(zenity --password                     --title="$APP_NAME — Authentification" 2>/dev/null)
            fi
            if [ -n "$SUDO_PASS" ]; then
                echo "$SUDO_PASS" | sudo -S bash -c "$INSTALL_CMD"                     > "$INSTALL_LOG" 2>&1
                INSTALL_STATUS=$?
            fi
            unset SUDO_PASS
        fi
    fi

    if [ $INSTALL_STATUS -ne 0 ]; then
        popup_error \
"L'installation des dépendances a échoué.

Détail de l'erreur :
$(tail -5 "$INSTALL_LOG")

Vérifiez votre connexion internet et réessayez." \
"$APP_NAME — Erreur d'installation"
        rm -f "$INSTALL_LOG"
        exit 1
    fi
    rm -f "$INSTALL_LOG"
fi

# ─────────────────────────────────────────────
# Copie des fichiers FreeSmartSync
# ─────────────────────────────────────────────

# Barre de progression synchrone — se ferme proprement à la fin
open_progress "$APP_NAME — Installation" "Installation de FreeSmartSync en cours..."
step_progress 10 "Préparation..."

# Copie des fichiers
mkdir -p "$INSTALL_DIR"

# Détermine le bon répertoire source
if [ -d "$SCRIPT_DIR/freesmartsync" ]; then
    SOURCE_DIR="$SCRIPT_DIR/freesmartsync"
else
    SOURCE_DIR="$SCRIPT_DIR"
fi

step_progress 30 "Copie des fichiers..."
# Copie avec rsync si disponible, sinon cp puis nettoyage
if command -v rsync &>/dev/null; then
    rsync -a --exclude="*.sh" --exclude="*.desktop" "$SOURCE_DIR/" "$INSTALL_DIR/"
else
    cp -r "$SOURCE_DIR/." "$INSTALL_DIR/"
    # Nettoyer les fichiers d'installation du répertoire cible
    rm -f "$INSTALL_DIR/"*.sh "$INSTALL_DIR/Double-clic"*.desktop 2>/dev/null || true
fi

step_progress 60 "Configuration..."
chmod +x "$INSTALL_DIR/freesmartsync.py"

# Icône PNG déjà incluse dans le zip
# Installer aussi dans XDG icon dirs pour que KDE/GNOME affiche l'icône dans les fenêtres
XDG_ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
mkdir -p "$XDG_ICON_DIR"
cp "$INSTALL_DIR/assets/icon.png" "$XDG_ICON_DIR/freesmartsync.png"
# Mettre à jour le cache d'icônes
gtk-update-icon-cache "$HOME/.local/share/icons/hicolor/" 2>/dev/null || true
kbuildsycoca5 --noincremental 2>/dev/null || true  # KDE Plasma 5
kbuildsycoca6 --noincremental 2>/dev/null || true  # KDE Plasma 6

# Création raccourci menu
mkdir -p "$(dirname "$DESKTOP_FILE")"
cat > "$DESKTOP_FILE" << DEOF
[Desktop Entry]
Version=1.0
Type=Application
Name=FreeSmartSync
GenericName=Sauvegarde Android
Comment=Synchronisation bidirectionnelle Android ↔ Linux
Exec=python3 "${INSTALL_DIR}/freesmartsync.py"
Icon=${INSTALL_DIR}/assets/icon.png
Terminal=false
Categories=Utility;FileManager;
Keywords=android;sync;backup;adb;sauvegarde;telephone;
StartupNotify=true
StartupWMClass=freesmartsync
DEOF

chmod +x "$DESKTOP_FILE"

# Créer aussi un lanceur sur le Bureau (Desktop) si disponible
# xdg-user-dir est universel et gère Bureau/Desktop/Escritorio selon la locale
DESKTOP_DIR=$(xdg-user-dir DESKTOP 2>/dev/null)
[ -z "$DESKTOP_DIR" ] && DESKTOP_DIR="$HOME/Bureau"
[ ! -d "$DESKTOP_DIR" ] && DESKTOP_DIR="$HOME/Desktop"
[ ! -d "$DESKTOP_DIR" ] && DESKTOP_DIR=""

if [ -n "$DESKTOP_DIR" ]; then
    LAUNCHER="$DESKTOP_DIR/FreeSmartSync.desktop"
    cp "$DESKTOP_FILE" "$LAUNCHER"
    chmod +x "$LAUNCHER"
    # Marquer comme exécutable/trusted selon le DE
    # GNOME / Zorin / Ubuntu
    gio set "$LAUNCHER" metadata::trusted true 2>/dev/null || true
    # Nautilus (GNOME Files)
    dbus-send --session --print-reply         --dest=org.gnome.Nautilus /org/gnome/Nautilus         org.freedesktop.FileManager1.ShowItems         array:string:"file://$LAUNCHER" string:"" 2>/dev/null || true
    # Cinnamon / Nemo
    if command -v nemo-action >/dev/null 2>&1 || [ "$XDG_CURRENT_DESKTOP" = "X-Cinnamon" ]; then
        gio set "$LAUNCHER" metadata::trusted true 2>/dev/null || true
    fi
    # KDE Plasma : mettre à jour le cache sycoca pour reconnaissance icône
    kbuildsycoca5 --noincremental 2>/dev/null || true
    kbuildsycoca6 --noincremental 2>/dev/null || true
fi

# Mise à jour base applications
update-desktop-database "$HOME/.local/share/applications/" 2>/dev/null || true

step_progress 90 "Finalisation..."
close_progress

# ─────────────────────────────────────────────
# Popup de succès + lancement optionnel
# ─────────────────────────────────────────────

popup_question \
"✅ FreeSmartSync est installé avec succès !

Lancer FreeSmartSync maintenant ?

⚠️ Si le logiciel ne démarre pas automatiquement,
cliquez sur son icône dans le menu d'applications
ou sur le Bureau." \
"$APP_NAME — Installation réussie !"

if [ $? -eq 0 ]; then
    export DISPLAY="${DISPLAY:-:0}"
    export XAUTHORITY="${XAUTHORITY:-$HOME/.Xauthority}"
    # Méthode 1 : gtk-launch via le .desktop installé (meilleure intégration GNOME/Cinnamon)
    if command -v gtk-launch &>/dev/null && [ -f "$HOME/.local/share/applications/freesmartsync.desktop" ]; then
        gtk-launch freesmartsync 2>/dev/null &
    # Méthode 2 : setsid + nohup (détachement complet du groupe de processus)
    elif command -v setsid &>/dev/null; then
        cd "$INSTALL_DIR" && setsid nohup python3 freesmartsync.py >/dev/null 2>&1 &
        disown $!
    # Méthode 3 : nohup seul (fallback universel)
    else
        cd "$INSTALL_DIR" && nohup python3 freesmartsync.py >/dev/null 2>&1 &
        disown $!
    fi
fi

exit 0
