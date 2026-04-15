#!/usr/bin/env python3
# freesmartsync.py — Point d'entrée FreeSmartSync v0.8.7.3

import sys
import os
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt5 import QtWidgets, QtGui, QtCore
except ImportError:
    print("ERREUR : PyQt5 n'est pas installé.")
    print("Relancez le script d'installation : bash CLIC-DROIT-Executer-pour-installer-FreeSmartSync.sh")
    import subprocess, os
    # Tenter d'afficher un message graphique si possible
    msg = "FreeSmartSync — Composant manquant\n\nPyQt5 n'est pas installé.\nRelancez le script d'installation."
    subprocess.run(["kdialog", "--error", msg], check=False) if os.path.exists("/usr/bin/kdialog") else None
    subprocess.run(["zenity", "--error", "--text", msg], check=False) if os.path.exists("/usr/bin/zenity") else None
    sys.exit(1)

try:
    from modules.config import load_config, is_first_run
    from modules.wizard import WizardWindow
    from modules.main_window import MainWindow, APP_VERSION
    from modules.updater import check_and_show_update
except Exception as _import_err:
    print(f"ERREUR import module : {_import_err}")
    print(f"Répertoire courant : {os.getcwd()}")
    print(f"sys.path : {sys.path[:3]}")
    sys.exit(1)

# Chemin icône global
_ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")


def get_connected_device():
    """Détecte automatiquement le téléphone branché via ADB."""
    try:
        res = subprocess.run(
            ["adb", "devices"], capture_output=True, text=True, timeout=2
        )
        for line in res.stdout.strip().split('\n')[1:]:
            if "\tdevice" in line:
                return line.split('\t')[0]
    except Exception:
        pass
    return None


def _apply_icon(widget):
    """Applique l'icône FSS via l'icône déjà chargée dans QApplication."""
    app = QtWidgets.QApplication.instance()
    if app and not app.windowIcon().isNull():
        widget.setWindowIcon(app.windowIcon())


class ReconnectDialog(QtWidgets.QDialog):
    """
    Dialogue de lancement :
    - Sélection du profil (affiché en premier si des profils existent)
    - Bouton "Lancer" (accès direct à la fenêtre principale)
    - Bouton "Aide / Nouvel appareil" (ouvre le mini-wizard de reconnexion)
    """

    def __init__(self, lang="fr", parent=None):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(
            "FreeSmartSync — Nouvelle session"
            if lang == "fr" else
            "FreeSmartSync — New session"
        )
        self.setMinimumSize(520, 340)
        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint
        )
        _apply_icon(self)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(14)
        layout.setContentsMargins(30, 25, 30, 25)

        title = QtWidgets.QLabel(
            "🔌 Quelle session lancer ?" if lang == "fr"
            else "🔌 Which session to launch?"
        )
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet(
            "font-size:18px; font-weight:bold; color:#2c3e50;"
        )

        # ── Sélecteur de profil ──────────────────────────
        from modules.profiles import load_profiles
        profiles = load_profiles()

        profile_lbl = QtWidgets.QLabel(
            "👤 Profil à utiliser :" if lang == "fr"
            else "👤 Profile to use:"
        )
        profile_lbl.setStyleSheet("font-size:13px; font-weight:bold; color:#2c3e50;")

        self.profile_combo = QtWidgets.QComboBox()
        self.profile_combo.setMinimumHeight(34)
        self.profile_combo.setStyleSheet("font-size:13px; padding:4px;")
        self.profile_combo.addItem(
            "— Configuration actuelle —" if lang == "fr"
            else "— Current config —",
            None
        )
        for name in profiles:
            self.profile_combo.addItem(f"👤 {name}", name)

        # Si un seul profil, le pré-sélectionner
        if len(profiles) == 1:
            self.profile_combo.setCurrentIndex(1)

        # ── Boutons ──────────────────────────────────────
        reminder = QtWidgets.QLabel(
            "Le <b>débogage USB</b> doit être activé sur votre téléphone."
            if lang == "fr" else
            "<b>USB debugging</b> must be enabled on your phone."
        )
        reminder.setWordWrap(True)
        reminder.setAlignment(QtCore.Qt.AlignCenter)
        reminder.setStyleSheet(
            "font-size:12px; color:#555; background:#eaf2ff; "
            "border:1px solid #aed6f1; border-radius:6px; padding:8px;"
        )

        self.btn_direct = QtWidgets.QPushButton(
            "▶  Lancer FreeSmartSync" if lang == "fr"
            else "▶  Launch FreeSmartSync"
        )
        self.btn_direct.setMinimumHeight(48)
        self.btn_direct.setStyleSheet(
            "background-color:#3498db; color:white; font-weight:bold; "
            "font-size:14px; padding:10px; border-radius:6px;"
        )

        self.btn_guide = QtWidgets.QPushButton(
            "🔌 Aide — Activer le débogage USB" if lang == "fr"
            else "🔌 Help — Enable USB debugging"
        )
        self.btn_guide.setMinimumHeight(40)
        self.btn_guide.setStyleSheet(
            "background-color:#f8f9fa; color:#2c3e50; "
            "border:1px solid #dee2e6; border-radius:6px; font-size:13px;"
        )

        # reject → lancer directement (MainWindow)
        # accept → ouvrir le mini-wizard
        self.btn_direct.clicked.connect(self.reject)
        self.btn_guide.clicked.connect(self.accept)

        layout.addWidget(title)
        layout.addWidget(profile_lbl)
        layout.addWidget(self.profile_combo)
        layout.addWidget(reminder)
        layout.addSpacing(4)
        layout.addWidget(self.btn_direct)
        layout.addWidget(self.btn_guide)
        self.setLayout(layout)

    def get_selected_profile(self):
        """Retourne le nom du profil sélectionné ou None."""
        return self.profile_combo.currentData()


class MiniWizard(QtWidgets.QDialog):
    """Wizard rapide de reconnexion : procédure débogage + connexion USB."""

    wizard_done = QtCore.pyqtSignal(dict)

    def __init__(self, config, lang="fr", parent=None):
        super().__init__(parent)
        self.config    = config
        self.lang      = lang
        self._launched = False

        self.setWindowTitle(
            "FreeSmartSync — Activation débogage USB"
            if lang == "fr" else
            "FreeSmartSync — Enable USB Debugging"
        )
        self.setMinimumSize(750, 580)
        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint
        )
        _apply_icon(self)

        from modules.wizard import PagePhone, PageUSBConnect
        self.stack      = QtWidgets.QStackedWidget()
        self.page_phone = PagePhone(self)
        self.page_usb   = PageUSBConnect(self)

        for p in [self.page_phone, self.page_usb]:
            self.stack.addWidget(p)

        self.btn_back = QtWidgets.QPushButton()
        self.btn_next = QtWidgets.QPushButton()
        self.btn_skip = QtWidgets.QPushButton(
            "⏭ Passer directement" if lang == "fr" else "⏭ Skip"
        )

        for btn in (self.btn_back, self.btn_next, self.btn_skip):
            btn.setMinimumHeight(38)

        self.btn_next.setStyleSheet(
            "background-color:#2ecc71; color:white; font-weight:bold; "
            "font-size:14px; padding:8px;"
        )
        self.btn_back.setStyleSheet("font-size:13px; padding:6px;")
        self.btn_skip.setStyleSheet(
            "background-color:#95a5a6; color:white; font-size:13px; padding:6px;"
        )

        self.btn_back.clicked.connect(self._go_back)
        self.btn_next.clicked.connect(self._go_next)
        self.btn_skip.clicked.connect(self._skip)

        self.progress_lbl = QtWidgets.QLabel()
        self.progress_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_lbl.setStyleSheet("color:#888; font-size:13px;")

        nav = QtWidgets.QHBoxLayout()
        nav.addWidget(self.btn_skip)
        nav.addStretch()
        nav.addWidget(self.btn_back)
        nav.addWidget(self.btn_next)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.stack)
        layout.addWidget(self.progress_lbl)
        layout.addLayout(nav)
        self.setLayout(layout)

        self._show_page(0)

    def _show_page(self, idx):
        self.current = idx
        self.stack.setCurrentIndex(idx)
        self.btn_back.setVisible(idx > 0)
        self.progress_lbl.setText(f"{idx + 1} / 2")
        self.btn_next.setText(
            "🚀 Lancer FreeSmartSync" if idx == 1
            else "Suivant →"
        )
        self.btn_back.setText("← Retour" if self.lang == "fr" else "← Back")

        if idx == 0:
            self.page_phone.refresh(self.lang)
            self.page_usb.stop_timers()
            self.btn_next.setEnabled(True)
        elif idx == 1:
            self.page_usb.refresh(self.lang)
            self.page_usb.start_timers()
            self.btn_next.setEnabled(bool(self.page_usb.get_device_id()))

    def _go_next(self):
        if self.current == 0:
            self._show_page(1)
        elif self.current == 1:
            device_id = self.page_usb.get_device_id()
            if device_id:
                self._launch_with_device(device_id)

    def _go_back(self):
        if self.current > 0:
            self._show_page(self.current - 1)

    def _skip(self):
        self.page_usb.stop_timers()
        if not self._launched:
            self._launched = True
            self.wizard_done.emit(self.config)
            self.accept()

    def _launch_with_device(self, device_id):
        self.page_usb.stop_timers()
        if not self._launched:
            self._launched = True
            self.config["device_id"] = device_id
            self.wizard_done.emit(self.config)
            self.accept()


def main():
    # Identification Linux pour l'icône dans les fenêtres (StartupWMClass)
    if sys.platform.startswith("linux"):
        try:
            QtCore.QCoreApplication.setApplicationName("freesmartsync")
        except Exception:
            pass

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("freesmartsync")
    app.setApplicationDisplayName("FreeSmartSync")
    app.setOrganizationName("FreeSmartSync")
    app.setQuitOnLastWindowClosed(False)

    # Charger l'icône avec plusieurs résolutions pour KDE
    if os.path.exists(_ICON_PATH):
        _app_icon = QtGui.QIcon(_ICON_PATH)
        extra = os.path.join(os.path.dirname(_ICON_PATH), "icon_256.png")
        if os.path.exists(extra):
            _app_icon.addFile(extra)
        app.setWindowIcon(_app_icon)
        QtWidgets.QApplication.setWindowIcon(_app_icon)

    config = load_config()

    # ── Premier lancement (pas de config) → wizard complet ──
    if is_first_run():
        wizard = WizardWindow()
        wizard.wizard_done.connect(lambda cfg: launch_main(app, cfg))
        if wizard.exec_() != QtWidgets.QDialog.Accepted:
            sys.exit(0)

    # ── Lancement normal → ReconnectDialog avec profils ──
    else:
        # Détection automatique du téléphone
        device = get_connected_device()
        if device:
            config["device_id"] = device

        lang = config.get("lang", "fr")
        dlg  = ReconnectDialog(lang=lang)
        result = dlg.exec_()

        # Appliquer le profil sélectionné
        profile_name = dlg.get_selected_profile()
        if profile_name:
            from modules.profiles import get_profile
            config.update(get_profile(profile_name))
            config["active_profile"] = profile_name

        if result == QtWidgets.QDialog.Accepted:
            # Bouton "Aide" → MiniWizard
            mini     = MiniWizard(config, lang=lang)
            launched = [False]

            def on_mini_done(cfg):
                if not launched[0]:
                    launched[0] = True
                    launch_main(app, cfg)

            mini.wizard_done.connect(on_mini_done)
            mini.exec_()
            if not launched[0]:
                launch_main(app, config)
        else:
            # Bouton "Lancer" → direct
            launch_main(app, config)

    sys.exit(app.exec_())


def launch_main(app, config):
    """Lance la fenêtre principale — évite les instances multiples."""
    if hasattr(app, "_main_window") and app._main_window is not None:
        try:
            app._main_window._show_from_tray()
            return
        except Exception:
            pass

    window = MainWindow(config)
    app._main_window = window
    window.show()

    lang = config.get("lang", "fr")
    QtCore.QTimer.singleShot(
        3000,
        lambda: check_and_show_update(APP_VERSION, lang=lang, parent=window)
    )


if __name__ == "__main__":
    main()
