#!/usr/bin/env python3
# freesmartsync.py — Point d'entrée FreeSmartSync Beta v0.8.5.3

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5 import QtWidgets, QtGui, QtCore

from modules.config import load_config, is_first_run
from modules.wizard import WizardWindow
from modules.main_window import MainWindow


class ReconnectDialog(QtWidgets.QDialog):
    """
    Assistant de reconnexion — affiché au relancement quand déjà configuré.
    Propose de se faire guider pour réactiver le débogage USB ou de passer directement.
    """
    def __init__(self, lang="fr", parent=None):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(
            "FreeSmartSync Beta — Nouvelle session"
            if lang == "fr" else
            "FreeSmartSync Beta — New session"
        )
        self.setMinimumSize(520, 320)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(30, 25, 30, 25)

        # Icône + titre
        title = QtWidgets.QLabel(
            "🔌 Nouvelle session de synchronisation"
            if lang == "fr" else
            "🔌 New sync session"
        )
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size:18px; font-weight:bold; color:#2c3e50;")

        # Message rappel débogage
        reminder = QtWidgets.QLabel(
            "Pour synchroniser votre téléphone, le <b>débogage USB</b> "
            "doit être activé sur votre smartphone.<br><br>"
            "Avez-vous besoin d'aide pour l'activer ?"
            if lang == "fr" else
            "To sync your phone, <b>USB debugging</b> "
            "must be enabled on your smartphone.<br><br>"
            "Do you need help enabling it?"
        )
        reminder.setWordWrap(True)
        reminder.setAlignment(QtCore.Qt.AlignCenter)
        reminder.setStyleSheet(
            "font-size:14px; color:#2c3e50; "
            "background:#eaf2ff; border:2px solid #3498db; "
            "border-radius:8px; padding:14px;"
        )

        # Boutons
        self.btn_guide = QtWidgets.QPushButton(
            "🔌 Oui, me guider pour activer le débogage USB"
            if lang == "fr" else
            "🔌 Yes, guide me to enable USB debugging"
        )
        self.btn_guide.setMinimumHeight(48)
        self.btn_guide.setStyleSheet(
            "background-color:#2ecc71; color:white; font-weight:bold; "
            "font-size:14px; padding:10px; border-radius:6px;"
        )

        self.btn_direct = QtWidgets.QPushButton(
            "▶ Non, je sais le faire — Lancer FreeSmartSync directement"
            if lang == "fr" else
            "▶ No, I know how — Launch FreeSmartSync directly"
        )
        self.btn_direct.setMinimumHeight(48)
        self.btn_direct.setStyleSheet(
            "background-color:#3498db; color:white; font-weight:bold; "
            "font-size:14px; padding:10px; border-radius:6px;"
        )

        self.btn_guide.clicked.connect(self.accept)   # → guide
        self.btn_direct.clicked.connect(self.reject)  # → direct

        layout.addWidget(title)
        layout.addWidget(reminder)
        layout.addSpacing(8)
        layout.addWidget(self.btn_guide)
        layout.addWidget(self.btn_direct)
        self.setLayout(layout)


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("FreeSmartSync Beta")
    app.setOrganizationName("FreeSmartSync")
    app.setQuitOnLastWindowClosed(False)

    icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QtGui.QIcon(icon_path))

    config = load_config()

    if is_first_run():
        # Premier lancement → wizard complet
        wizard = WizardWindow()
        wizard.wizard_done.connect(lambda cfg: launch_main(app, cfg))
        result = wizard.exec_()
        if result != QtWidgets.QDialog.Accepted:
            sys.exit(0)
    else:
        # Déjà configuré → assistant de reconnexion
        lang = config.get("lang", "fr")
        dlg  = ReconnectDialog(lang=lang)
        result = dlg.exec_()

        if result == QtWidgets.QDialog.Accepted:
            # L'utilisateur veut être guidé → ouvre le mini-wizard
            # (pages 3 + 4 seulement : procédure débogage + connexion USB)
            mini = MiniWizard(config, lang=lang)
            mini.wizard_done.connect(lambda cfg: launch_main(app, cfg))
            res2 = mini.exec_()
            if res2 != QtWidgets.QDialog.Accepted:
                # Annulé → lance quand même l'appli principale
                launch_main(app, config)
        else:
            # Direct → interface principale
            launch_main(app, config)

    sys.exit(app.exec_())


def launch_main(app, config):
    window = MainWindow(config)
    app._main_window = window


class MiniWizard(QtWidgets.QDialog):
    """
    Wizard rapide de reconnexion — affiche seulement :
    - Page procédure débogage USB (selon la marque)
    - Page connexion USB animée
    """
    wizard_done = QtCore.pyqtSignal(dict)

    def __init__(self, config, lang="fr", parent=None):
        super().__init__(parent)
        self.config = config
        self.lang   = lang

        self.setWindowTitle(
            "FreeSmartSync — Activation débogage USB"
            if lang == "fr" else
            "FreeSmartSync — Enable USB Debugging"
        )
        self.setMinimumSize(750, 580)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        from modules.wizard import PagePhone, PageUSBConnect

        self.stack = QtWidgets.QStackedWidget()

        self.page_phone = PagePhone(self)
        self.page_usb   = PageUSBConnect(self)

        self.pages = [self.page_phone, self.page_usb]
        for p in self.pages:
            self.stack.addWidget(p)

        self.btn_back   = QtWidgets.QPushButton()
        self.btn_next   = QtWidgets.QPushButton()
        self.btn_skip   = QtWidgets.QPushButton(
            "⏭ Passer directement" if lang == "fr" else "⏭ Skip"
        )

        self.btn_back.setMinimumHeight(38)
        self.btn_next.setMinimumHeight(38)
        self.btn_skip.setMinimumHeight(38)

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

        self.progress = QtWidgets.QLabel()
        self.progress.setAlignment(QtCore.Qt.AlignCenter)
        self.progress.setStyleSheet("color:#888; font-size:13px;")

        nav = QtWidgets.QHBoxLayout()
        nav.addWidget(self.btn_skip)
        nav.addStretch()
        nav.addWidget(self.btn_back)
        nav.addWidget(self.btn_next)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.stack)
        layout.addWidget(self.progress)
        layout.addLayout(nav)
        self.setLayout(layout)

        self.current = 0
        self._show_page(0)

    def _show_page(self, idx):
        self.current = idx
        self.stack.setCurrentIndex(idx)
        total = len(self.pages)

        self.btn_back.setVisible(idx > 0)
        self.progress.setText(f"{idx + 1} / {total}")

        if idx == total - 1:
            self.btn_next.setText(
                "🚀 Lancer FreeSmartSync" if self.lang == "fr"
                else "🚀 Launch FreeSmartSync"
            )
        else:
            self.btn_next.setText("Suivant →" if self.lang == "fr" else "Next →")

        self.btn_back.setText("← Retour" if self.lang == "fr" else "← Back")

        if idx == 0:
            self.page_phone.refresh(self.lang)
        if idx == 1:
            self.page_usb.refresh(self.lang)
            self.page_usb.start_timers()
            self.btn_next.setEnabled(bool(self.page_usb.get_device_id()))
        else:
            self.page_usb.stop_timers()
            self.btn_next.setEnabled(True)

    def _go_next(self):
        if self.current == 1:
            device_id = self.page_usb.get_device_id()
            if not device_id:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Téléphone non détecté" if self.lang == "fr" else "Phone not detected",
                    "Branchez votre téléphone et attendez la détection."
                    if self.lang == "fr" else
                    "Connect your phone and wait for detection."
                )
                return
            self.config["device_id"] = device_id
            self.wizard_done.emit(self.config)
            self.accept()
            return
        self._show_page(self.current + 1)

    def _go_back(self):
        if self.current > 0:
            self._show_page(self.current - 1)

    def _skip(self):
        """Passe directement sans guide."""
        self.page_usb.stop_timers()
        self.wizard_done.emit(self.config)
        self.reject()


if __name__ == "__main__":
    main()
