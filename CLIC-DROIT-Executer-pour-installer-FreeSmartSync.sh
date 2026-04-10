#!/bin/bash
# Installer-FreeSmartSync.sh
# Installation graphique FreeSmartSync — double-clic et c'est parti !
# Aucun terminal nécessaire.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
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

# Barre de progression — retourne le PID du processus
start_progress() {
    local title="$1"
    local msg="$2"
    case "$GUI" in
        kdialog)
            DBUS_REF=$(kdialog --title "$title" --progressbar "$msg" 5 2>/dev/null)
            echo "kdialog:$DBUS_REF"
            ;;
        zenity|qarma)
            (
                echo "10"; sleep 1
                echo "30"; sleep 1
                echo "60"; sleep 1
                echo "90"; sleep 1
                echo "100"
            ) | zenity --progress \
                --title="$title" \
                --text="$msg" \
                --percentage=0 \
                --auto-close \
                --width=400 &
            echo "zenity:$!"
            ;;
        none) echo "none:0" ;;
    esac
}

close_progress() {
    local ref="$1"
    local tool="${ref%%:*}"
    local pid="${ref##*:}"
    if [ "$tool" = "kdialog" ] && [ -n "$pid" ]; then
        qdbus $pid /ProgressDialog close 2>/dev/null || true
    fi
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
        echo "urpmi android-tools python3 python3-pyqt5"
    elif echo "$distrib" | grep -qiE "nixos|glf"; then
        echo "nix-env -iA nixpkgs.android-tools nixpkgs.python3 nixpkgs.python3Packages.pyqt5"
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

if [ -d "$INSTALL_DIR" ] || [ -f "$DESKTOP_FILE" ]; then

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
            rm -rf "$INSTALL_DIR"
            rm -f "$DESKTOP_FILE"
            ;;
        uninstall)
            popup_question \
"Voulez-vous également supprimer votre configuration ?
(dossiers sélectionnés, répertoire de sauvegarde)" \
"$APP_NAME — Désinstallation"
            if [ $? -eq 0 ]; then
                rm -rf "$HOME/.config/freesmartsync"
                popup_info "✅ FreeSmartSync et sa configuration ont été supprimés." "$APP_NAME"
            else
                popup_info "✅ FreeSmartSync a été désinstallé.\nConfiguration conservée." "$APP_NAME"
            fi
            rm -rf "$INSTALL_DIR"
            rm -f "$DESKTOP_FILE"
            update-desktop-database "$HOME/.local/share/applications/" 2>/dev/null || true
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

    # Demande mot de passe
    PASSWORD=$(popup_password \
"Entrez votre mot de passe administrateur :" \
"$APP_NAME — Authentification")

    if [ -z "$PASSWORD" ]; then
        popup_error "Mot de passe requis pour l'installation." "$APP_NAME"
        exit 1
    fi

    # Installation — barre de progression indéterminée en arrière-plan
    INSTALL_LOG=$(mktemp)

    case "$GUI" in
        kdialog)
            # Lancer une barre indéterminée kdialog
            kdialog --title "$APP_NAME" --progressbar "Installation des outils nécessaires..." 0 &
            KDIALOG_PID=$!
            echo "$PASSWORD" | sudo -S $INSTALL_CMD > "$INSTALL_LOG" 2>&1
            INSTALL_STATUS=$?
            kill $KDIALOG_PID 2>/dev/null || true
            ;;
        zenity|qarma)
            # Pipe vers zenity --pulsate (indéterminé)
            (echo "$PASSWORD" | sudo -S $INSTALL_CMD > "$INSTALL_LOG" 2>&1; echo "DONE") |             zenity --progress                 --title="$APP_NAME"                 --text="Installation des outils nécessaires..."                 --pulsate                 --auto-close                 --width=400 &
            # Attendre la fin réelle de l'installation
            wait
            INSTALL_STATUS=$(cat "$INSTALL_LOG.status" 2>/dev/null || echo 0)
            echo "$PASSWORD" | sudo -S $INSTALL_CMD >> "$INSTALL_LOG" 2>&1
            INSTALL_STATUS=$?
            ;;
        *)
            echo "$PASSWORD" | sudo -S $INSTALL_CMD > "$INSTALL_LOG" 2>&1
            INSTALL_STATUS=$?
            ;;
    esac

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

# Copie des fichiers
mkdir -p "$INSTALL_DIR"

# Détermine le bon répertoire source
if [ -d "$SCRIPT_DIR/freesmartsync" ]; then
    SOURCE_DIR="$SCRIPT_DIR/freesmartsync"
else
    SOURCE_DIR="$SCRIPT_DIR"
fi

# Copie avec rsync si disponible, sinon cp
if command -v rsync &>/dev/null; then
    rsync -a --exclude="*.sh" --exclude="*.desktop" "$SOURCE_DIR/" "$INSTALL_DIR/"
else
    cp -r "$SOURCE_DIR/." "$INSTALL_DIR/"
fi

chmod +x "$INSTALL_DIR/freesmartsync.py"

# Icône PNG déjà incluse dans le zip — aucune génération nécessaire

# Création raccourci menu
mkdir -p "$(dirname "$DESKTOP_FILE")"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=FreeSmartSync
GenericName=Sauvegarde Android
Comment=Synchronisation bidirectionnelle Android ↔ Linux
Exec=python3 "$INSTALL_DIR/freesmartsync.py"
Icon=$INSTALL_DIR/assets/icon.png
Terminal=false
Categories=Utility;FileManager;
Keywords=android;sync;backup;adb;sauvegarde;telephone;
StartupNotify=true
StartupWMClass=freesmartsync
EOF

chmod +x "$DESKTOP_FILE"

# Créer aussi un lanceur sur le Bureau (Desktop) si disponible
DESKTOP_DIR="$HOME/Bureau"
[ ! -d "$DESKTOP_DIR" ] && DESKTOP_DIR="$HOME/Desktop"
[ ! -d "$DESKTOP_DIR" ] && DESKTOP_DIR=""

if [ -n "$DESKTOP_DIR" ]; then
    LAUNCHER="$DESKTOP_DIR/FreeSmartSync.desktop"
    cp "$DESKTOP_FILE" "$LAUNCHER"
    chmod +x "$LAUNCHER"
    # Sur GNOME/Zorin, marquer le .desktop comme "trusted"
    gio set "$LAUNCHER" metadata::trusted true 2>/dev/null || true
fi

# Mise à jour base applications
update-desktop-database "$HOME/.local/share/applications/" 2>/dev/null || true

close_progress "$PROG"

# ─────────────────────────────────────────────
# Popup de succès + lancement optionnel
# ─────────────────────────────────────────────

popup_question \
"✅ FreeSmartSync est installé !

Vous pouvez maintenant le lancer depuis :
  • Votre menu d'applications
  • Ou en cherchant 'FreeSmartSync'

Lancer FreeSmartSync maintenant ?" \
"$APP_NAME — Installation réussie !"

if [ $? -eq 0 ]; then
    # Mise à jour de la base d'applications
    update-desktop-database "$HOME/.local/share/applications/" 2>/dev/null || true
    sleep 1

    # Délai pour laisser le bureau se stabiliser
    sleep 2

    # Lancement multi-méthodes pour compatibilité GNOME/KDE/Cinnamon
    export DISPLAY="${DISPLAY:-:0}"
    export XAUTHORITY="${XAUTHORITY:-$HOME/.Xauthority}"

    if command -v python3 &>/dev/null; then
        # python3 direct — le plus fiable sur toutes les distros
        setsid python3 "$INSTALL_DIR/freesmartsync.py" >/dev/null 2>&1 &
        disown $!
    fi
fi

exit 0
