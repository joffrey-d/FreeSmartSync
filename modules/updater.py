# modules/updater.py
# Vérification et téléchargement des mises à jour FreeSmartSync via GitHub

import subprocess
import os
import json
import threading
from PyQt5 import QtWidgets, QtCore, QtGui

# URL du fichier de version sur GitHub (branche main)
VERSION_URL = "https://raw.githubusercontent.com/joffrey-d/FreeSmartSync/main/version.json"
DOWNLOAD_URL_BASE = "https://github.com/joffrey-d/FreeSmartSync/releases/latest/download"


def parse_version(v):
    """Convertit '0.8.5.5' en tuple (0, 8, 5, 5) pour comparaison."""
    v = v.lstrip("v")
    try:
        return tuple(int(x) for x in v.split("."))
    except Exception:
        return (0,)


def check_update_available(current_version):
    """
    Vérifie si une nouvelle version est disponible sur GitHub.
    Retourne (True, latest_version, download_url) ou (False, None, None).
    Lance la requête dans un thread pour ne pas bloquer l'UI.
    """
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "8", VERSION_URL],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.returncode != 0 or not result.stdout.strip():
            # Essai avec wget si curl échoue
            result = subprocess.run(
                ["wget", "-q", "-O", "-", "--timeout=8", VERSION_URL],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
        if result.returncode != 0 or not result.stdout.strip():
            return False, None, None

        data    = json.loads(result.stdout.strip())
        latest  = data.get("version", "")
        dl_url  = data.get("download_url", f"{DOWNLOAD_URL_BASE}/freesmartsync-{latest}.zip")
        notes   = data.get("notes", "")

        if not latest:
            return False, None, None

        if parse_version(latest) > parse_version(current_version):
            return True, latest, dl_url, notes
        return False, latest, None, None

    except Exception:
        return False, None, None, None


class UpdateDialog(QtWidgets.QDialog):
    """Popup de mise à jour — simple, claire, avec 2 boutons."""

    def __init__(self, current_version, latest_version, download_url,
                 notes="", lang="fr", parent=None):
        super().__init__(parent)
        self.download_url     = download_url
        self.current_version  = current_version
        self.latest_version   = latest_version
        self.lang             = lang

        self.setWindowTitle(
            "🔄 Mise à jour disponible" if lang == "fr" else "🔄 Update available"
        )
        self.setMinimumSize(480, 280)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(14)
        layout.setContentsMargins(24, 20, 24, 20)

        # Titre
        title = QtWidgets.QLabel(
            "🔄 Une nouvelle version est disponible !"
            if lang == "fr" else
            "🔄 A new version is available!"
        )
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size:17px; font-weight:bold; color:#2c3e50;")

        # Versions
        ver_lbl = QtWidgets.QLabel(
            f"Version actuelle : <b>{current_version}</b> &nbsp;→&nbsp; "
            f"Nouvelle version : <b style='color:#27ae60'>{latest_version}</b>"
            if lang == "fr" else
            f"Current version: <b>{current_version}</b> &nbsp;→&nbsp; "
            f"New version: <b style='color:#27ae60'>{latest_version}</b>"
        )
        ver_lbl.setAlignment(QtCore.Qt.AlignCenter)
        ver_lbl.setStyleSheet("font-size:14px;")

        # Notes de version (si disponibles)
        if notes:
            notes_box = QtWidgets.QTextEdit()
            notes_box.setReadOnly(True)
            label_new = "Nouveautés" if lang == "fr" else "What's new"
            notes_box.setHtml(
                f"<b style='font-size:13px'>{label_new} :</b><br>"
                f"<span style='font-size:13px'>{notes}</span>"
            )
            notes_box.setMaximumHeight(100)
            notes_box.setStyleSheet(
                "background:#f8f9fa; border:1px solid #dee2e6; "
                "border-radius:4px; font-size:13px;"
            )
        else:
            notes_box = None

        # Boutons
        btn_download = QtWidgets.QPushButton(
            "⬇️ Télécharger et installer" if lang == "fr" else "⬇️ Download and install"
        )
        btn_download.setMinimumHeight(44)
        btn_download.setStyleSheet(
            "background-color:#2ecc71; color:white; font-weight:bold; "
            "font-size:14px; padding:10px; border-radius:6px;"
        )

        btn_later = QtWidgets.QPushButton(
            "Plus tard" if lang == "fr" else "Later"
        )
        btn_later.setMinimumHeight(44)
        btn_later.setStyleSheet(
            "background-color:#95a5a6; color:white; "
            "font-size:14px; padding:10px; border-radius:6px;"
        )

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(btn_later)
        btn_row.addWidget(btn_download)

        btn_download.clicked.connect(self._download)
        btn_later.clicked.connect(self.reject)

        layout.addWidget(title)
        layout.addWidget(ver_lbl)
        if notes_box:
            layout.addWidget(notes_box)
        layout.addStretch()
        layout.addLayout(btn_row)
        self.setLayout(layout)

    def _download(self):
        """Ouvre le navigateur sur l'URL de téléchargement."""
        try:
            subprocess.Popen(["xdg-open", self.download_url])
        except Exception:
            try:
                import webbrowser
                webbrowser.open(self.download_url)
            except Exception:
                QtWidgets.QMessageBox.information(
                    self,
                    "Téléchargement" if self.lang == "fr" else "Download",
                    f"Téléchargez la nouvelle version ici :\n{self.download_url}"
                    if self.lang == "fr" else
                    f"Download the new version here:\n{self.download_url}"
                )
        self.accept()


class UpdateChecker(QtCore.QThread):
    """Thread de vérification des mises à jour — non bloquant."""
    update_available = QtCore.pyqtSignal(str, str, str)  # latest, url, notes

    def __init__(self, current_version):
        super().__init__()
        self.current_version = current_version

    def run(self):
        result = check_update_available(self.current_version)
        available = result[0]
        latest    = result[1]
        url       = result[2] if len(result) > 2 else ""
        notes     = result[3] if len(result) > 3 else ""
        if available and latest and url:
            self.update_available.emit(latest, url or "", notes or "")


def check_and_show_update(current_version, lang="fr", parent=None, silent=True):
    """
    Vérifie les mises à jour.
    silent=True  → popup seulement si MAJ disponible (démarrage auto)
    silent=False → popup dans tous les cas (bouton manuel)
    """
    from PyQt5 import QtWidgets, QtCore

    checker = UpdateChecker(current_version)
    _found  = [False]

    def on_update(latest, url, notes):
        _found[0] = True
        dlg = UpdateDialog(
            current_version=current_version,
            latest_version=latest,
            download_url=url,
            notes=notes,
            lang=lang,
            parent=parent
        )
        dlg.exec_()

    def on_finished():
        if not silent and not _found[0]:
            QtWidgets.QMessageBox.information(
                parent,
                "✅ À jour" if lang == "fr" else "✅ Up to date",
                f"FreeSmartSync {current_version} est la dernière version disponible."
                if lang == "fr" else
                f"FreeSmartSync {current_version} is already the latest version."
            )

    checker.update_available.connect(on_update)
    checker.finished.connect(on_finished)
    checker.start()
    if parent:
        parent._update_checker = checker
    return checker
