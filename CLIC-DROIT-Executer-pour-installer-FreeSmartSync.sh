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
            [ -n "$INSTALL_DIR" ] && [ "$INSTALL_DIR" != "/" ] && rm -rf "$INSTALL_DIR"
            rm -f "$DESKTOP_FILE"
            ;;
        uninstall)
            # OUI = conserver la config (comportement par defaut le plus sur)
            # NON = tout supprimer
            popup_question \
"Voulez-vous conserver votre configuration et vos profils ?

OUI : configuration et profils conserves.
      Retrouves automatiquement a la reinstallation.

NON : tout sera supprime definitivement." \
"$APP_NAME - Desinstallation"
            if [ $? -eq 0 ]; then
                # OUI = conserver : on ne touche PAS a config.json
                # L'application retrouvera son etat exact (setup_done=True, profils intacts)
                popup_info "FreeSmartSync desinstalle.
Configuration et profils conserves.
Ils seront retrouves automatiquement a la reinstallation." "$APP_NAME"
            else
                # NON = tout supprimer
                rm -rf "$HOME/.config/freesmartsync"
                popup_info "FreeSmartSync et sa configuration ont ete supprimes." "$APP_NAME"
            fi
            [ -n "$INSTALL_DIR" ] && [ "$INSTALL_DIR" != "/" ] && rm -rf "$INSTALL_DIR"
            rm -f "$DESKTOP_FILE"
            rm -f "$HOME/Bureau/FreeSmartSync.desktop" 2>/dev/null || true
            rm -f "$HOME/Desktop/FreeSmartSync.desktop" 2>/dev/null || true
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

    # ── Installation sécurisée des dépendances ──────────────────────────────────
    # Méthode 1 : pkexec (Polkit) — ouvre la fenêtre native du système, gère
    #             sudo ET su selon la distro. Aucun mot de passe en mémoire.
    # Méthode 2 : su -c — fallback pour Mageia/urpmi (utilisateur non sudoer)
    # Méthode 3 : sudo — fallback classique
    # ─────────────────────────────────────────────────────────────────────────
    INSTALL_LOG=$(mktemp)

    popup_info "L'installation des composants nécessaires va démarrer.
Une fenêtre système vous demandera votre mot de passe." "$APP_NAME"

    INSTALL_STATUS=1

    # ── Stratégie selon la distribution ──────────────────────────────────────
    # Mageia : su -c en direct (l'user n'est pas sudoer, pkexec ne trouve pas urpmi)
    # Autres : pkexec d'abord (fenêtre native Polkit), puis sudo en fallback
    # ─────────────────────────────────────────────────────────────────────────

    if is_mageia_based "$DISTRIB_INFO"; then
        # Mageia / OpenMandriva : su -c avec mot de passe root
        if [ "$GUI" = "kdialog" ]; then
            ROOT_PASS=$(kdialog --title "$APP_NAME — Mot de passe root"                 --password "Entrez le mot de passe root pour installer les dependances :")
        else
            ROOT_PASS=$(zenity --password                 --title="$APP_NAME — Mot de passe root" 2>/dev/null)
        fi
        if [ -n "$ROOT_PASS" ]; then
            echo "$ROOT_PASS" | su -c "urpmi --auto android-tools python3 python3-pyqt5"                 > "$INSTALL_LOG" 2>&1
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
