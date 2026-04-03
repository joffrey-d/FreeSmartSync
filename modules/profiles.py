# modules/profiles.py
# Gestion des profils de synchronisation — plusieurs téléphones/utilisateurs

import os
import json
from PyQt5 import QtWidgets, QtCore, QtGui


PROFILES_FILE = os.path.expanduser("~/.config/freesmartsync/profiles.json")


def load_profiles():
    """Charge tous les profils depuis le fichier JSON."""
    if not os.path.exists(PROFILES_FILE):
        return {}
    try:
        with open(PROFILES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_profiles(profiles):
    """Sauvegarde tous les profils."""
    os.makedirs(os.path.dirname(PROFILES_FILE), exist_ok=True)
    with open(PROFILES_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)


def get_profile(name):
    """Retourne un profil par son nom."""
    return load_profiles().get(name, {})


def save_profile(name, data):
    """Sauvegarde un profil."""
    profiles = load_profiles()
    profiles[name] = data
    save_profiles(profiles)


def delete_profile(name):
    """Supprime un profil."""
    profiles = load_profiles()
    profiles.pop(name, None)
    save_profiles(profiles)


class ProfileDialog(QtWidgets.QDialog):
    """
    Gestionnaire de profils — permet de créer, modifier, supprimer et
    sélectionner un profil de synchronisation.
    Chaque profil a : nom, dossiers téléphone, répertoire PC de sauvegarde.
    """
    profile_selected = QtCore.pyqtSignal(str, dict)  # nom, config

    def __init__(self, current_config, lang="fr", parent=None):
        super().__init__(parent)
        self.lang           = lang
        self.current_config = current_config
        self.setWindowTitle(
            "👤 Gestion des profils" if lang == "fr" else "👤 Profile management"
        )
        self.setMinimumSize(580, 480)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 16, 20, 16)

        # Titre
        title = QtWidgets.QLabel(
            "👤 Profils de synchronisation"
            if lang == "fr" else
            "👤 Sync profiles"
        )
        title.setStyleSheet("font-size:18px; font-weight:bold; color:#2c3e50;")

        # Explication
        info = QtWidgets.QLabel(
            "Chaque profil correspond à un téléphone ou un utilisateur différent.\n"
            "Chacun a ses propres dossiers à synchroniser et son répertoire de sauvegarde."
            if lang == "fr" else
            "Each profile corresponds to a different phone or user.\n"
            "Each has its own folders to sync and its own backup directory."
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            "font-size:13px; color:#555; background:#f8f9fa; "
            "border:1px solid #dee2e6; border-radius:4px; padding:8px;"
        )

        # Liste des profils
        self.profile_list = QtWidgets.QListWidget()
        self.profile_list.setStyleSheet("font-size:14px;")
        self.profile_list.currentRowChanged.connect(self._on_select)

        # Détails du profil sélectionné
        self.detail_box = QtWidgets.QTextEdit()
        self.detail_box.setReadOnly(True)
        self.detail_box.setMaximumHeight(120)
        self.detail_box.setStyleSheet(
            "font-size:13px; background:#f8f9fa; "
            "border:1px solid #dee2e6; border-radius:4px;"
        )

        # Boutons de gestion
        self.btn_new    = QtWidgets.QPushButton("➕ Nouveau profil" if lang == "fr" else "➕ New profile")
        self.btn_edit   = QtWidgets.QPushButton("✏️ Modifier" if lang == "fr" else "✏️ Edit")
        self.btn_delete = QtWidgets.QPushButton("🗑️ Supprimer" if lang == "fr" else "🗑️ Delete")
        self.btn_use    = QtWidgets.QPushButton(
            "✅ Utiliser ce profil" if lang == "fr" else "✅ Use this profile"
        )
        self.btn_save_current = QtWidgets.QPushButton(
            "💾 Sauvegarder config actuelle comme profil"
            if lang == "fr" else
            "💾 Save current config as profile"
        )

        self.btn_new.setStyleSheet("font-size:13px; padding:5px;")
        self.btn_edit.setStyleSheet("font-size:13px; padding:5px;")
        self.btn_delete.setStyleSheet(
            "background-color:#e74c3c; color:white; font-size:13px; padding:5px;"
        )
        self.btn_use.setStyleSheet(
            "background-color:#2ecc71; color:white; font-weight:bold; "
            "font-size:14px; padding:8px; border-radius:4px;"
        )
        self.btn_save_current.setStyleSheet(
            "background-color:#3498db; color:white; font-size:13px; padding:6px;"
        )

        self.btn_new.clicked.connect(self._new_profile)
        self.btn_edit.clicked.connect(self._edit_profile)
        self.btn_delete.clicked.connect(self._delete_profile)
        self.btn_use.clicked.connect(self._use_profile)
        self.btn_save_current.clicked.connect(self._save_current)

        mgmt_row = QtWidgets.QHBoxLayout()
        mgmt_row.addWidget(self.btn_new)
        mgmt_row.addWidget(self.btn_edit)
        mgmt_row.addWidget(self.btn_delete)
        mgmt_row.addStretch()

        btn_close = QtWidgets.QPushButton("Fermer" if lang == "fr" else "Close")
        btn_close.setStyleSheet("font-size:13px; padding:6px;")
        btn_close.clicked.connect(self.reject)

        bottom_row = QtWidgets.QHBoxLayout()
        bottom_row.addWidget(self.btn_save_current)
        bottom_row.addStretch()
        bottom_row.addWidget(btn_close)
        bottom_row.addWidget(self.btn_use)

        layout.addWidget(title)
        layout.addWidget(info)
        layout.addSpacing(4)
        layout.addWidget(self.profile_list)
        layout.addWidget(self.detail_box)
        layout.addLayout(mgmt_row)
        layout.addLayout(bottom_row)
        self.setLayout(layout)

        self._refresh_list()

    def _refresh_list(self):
        self.profile_list.clear()
        profiles = load_profiles()
        for name in profiles:
            item = QtWidgets.QListWidgetItem(f"👤 {name}")
            item.setData(QtCore.Qt.UserRole, name)
            self.profile_list.addItem(item)

        if self.profile_list.count() == 0:
            self.detail_box.setPlainText(
                "Aucun profil créé. Cliquez sur 'Nouveau profil' pour commencer."
                if self.lang == "fr" else
                "No profiles yet. Click 'New profile' to get started."
            )
        self.btn_use.setEnabled(self.profile_list.count() > 0)
        self.btn_edit.setEnabled(self.profile_list.count() > 0)
        self.btn_delete.setEnabled(self.profile_list.count() > 0)

    def _on_select(self, row):
        if row < 0:
            return
        name    = self.profile_list.item(row).data(QtCore.Qt.UserRole)
        profile = get_profile(name)
        folders = profile.get("folders", [])
        dest    = profile.get("local_base", "—")
        html = (
            f"<b>📁 Dossiers téléphone :</b><br>"
            + ("".join(f"&nbsp;&nbsp;• {f}<br>" for f in folders) if folders else "&nbsp;&nbsp;<i>Aucun</i><br>")
            + f"<b>💾 Sauvegarde :</b> {dest}"
        )
        self.detail_box.setHtml(html)

    def _new_profile(self):
        name, ok = QtWidgets.QInputDialog.getText(
            self,
            "Nouveau profil" if self.lang == "fr" else "New profile",
            "Nom du profil (ex: Joffrey, Samsung Galaxy, iPhone Marie) :"
            if self.lang == "fr" else
            "Profile name (e.g. John, Samsung Galaxy, Marie's iPhone):"
        )
        if ok and name.strip():
            name = name.strip()
            if name in load_profiles():
                QtWidgets.QMessageBox.warning(
                    self,
                    "Erreur" if self.lang == "fr" else "Error",
                    f"Un profil '{name}' existe déjà."
                    if self.lang == "fr" else
                    f"Profile '{name}' already exists."
                )
                return
            # Crée un profil vide
            save_profile(name, {
                "folders": [],
                "local_base": os.path.expanduser(f"~/FreeSmartSync-{name}/")
            })
            self._refresh_list()
            # Sélectionner le nouveau profil
            for i in range(self.profile_list.count()):
                if self.profile_list.item(i).data(QtCore.Qt.UserRole) == name:
                    self.profile_list.setCurrentRow(i)
                    break

    def _edit_profile(self):
        item = self.profile_list.currentItem()
        if not item:
            return
        name    = item.data(QtCore.Qt.UserRole)
        profile = get_profile(name)

        dlg = ProfileEditDialog(name, profile, lang=self.lang, parent=self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            save_profile(name, dlg.get_profile())
            self._refresh_list()
            self._on_select(self.profile_list.currentRow())

    def _delete_profile(self):
        item = self.profile_list.currentItem()
        if not item:
            return
        name = item.data(QtCore.Qt.UserRole)
        rep  = QtWidgets.QMessageBox.question(
            self,
            "Confirmer" if self.lang == "fr" else "Confirm",
            f"Supprimer le profil '{name}' ?"
            if self.lang == "fr" else
            f"Delete profile '{name}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if rep == QtWidgets.QMessageBox.Yes:
            delete_profile(name)
            self._refresh_list()

    def _save_current(self):
        """Sauvegarde la configuration actuelle comme nouveau profil."""
        name, ok = QtWidgets.QInputDialog.getText(
            self,
            "Sauvegarder comme profil" if self.lang == "fr" else "Save as profile",
            "Nom du profil :" if self.lang == "fr" else "Profile name:"
        )
        if ok and name.strip():
            name = name.strip()
            profile = {
                "folders":    self.current_config.get("folders", []),
                "local_base": self.current_config.get("local_base", ""),
                "device_id":  self.current_config.get("device_id", ""),
            }
            save_profile(name, profile)
            self._refresh_list()
            QtWidgets.QMessageBox.information(
                self,
                "✅ Sauvegardé" if self.lang == "fr" else "✅ Saved",
                f"Configuration sauvegardée comme profil '{name}'."
                if self.lang == "fr" else
                f"Configuration saved as profile '{name}'."
            )

    def _use_profile(self):
        item = self.profile_list.currentItem()
        if not item:
            return
        name    = item.data(QtCore.Qt.UserRole)
        profile = get_profile(name)
        self.profile_selected.emit(name, profile)
        self.accept()


class ProfileEditDialog(QtWidgets.QDialog):
    """Dialogue d'édition d'un profil."""

    def __init__(self, name, profile, lang="fr", parent=None):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(f"✏️ Modifier le profil : {name}")
        self.setMinimumSize(480, 360)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(18, 14, 18, 14)

        # Dossiers
        folders_lbl = QtWidgets.QLabel(
            "📁 Dossiers téléphone à synchroniser :"
            if lang == "fr" else
            "📁 Phone folders to sync:"
        )
        folders_lbl.setStyleSheet("font-size:13px; font-weight:bold;")

        # Liste des dossiers avec boutons Ajouter/Supprimer
        self.folders_list = QtWidgets.QListWidget()
        self.folders_list.setStyleSheet("font-size:13px;")
        self.folders_list.setMaximumHeight(130)
        self.folders_list.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        for f in profile.get("folders", []):
            self.folders_list.addItem(f)

        # Boutons gestion dossiers
        btn_add_adb = QtWidgets.QPushButton(
            "📁 Ajouter via explorateur ADB"
            if lang == "fr" else
            "📁 Add via ADB explorer"
        )
        btn_add_adb.setStyleSheet(
            "background-color:#3498db; color:white; font-size:12px; padding:4px;"
        )
        btn_remove = QtWidgets.QPushButton(
            "🗑️ Supprimer sélection" if lang == "fr" else "🗑️ Remove selected"
        )
        btn_remove.setStyleSheet("font-size:12px; padding:4px;")

        # device_id — récupéré depuis la config si disponible
        self._device_id = profile.get("device_id", "")

        def add_via_adb():
            device_id = self._device_id
            if not device_id:
                # Demander l'ID du device
                device_id, ok = QtWidgets.QInputDialog.getText(
                    self,
                    "Device ADB" if lang == "fr" else "ADB Device",
                    "ID du téléphone ADB (ex: RFXXXXXXX) :"
                    if lang == "fr" else
                    "ADB device ID (e.g.: RFXXXXXXX):"
                )
                if not ok or not device_id.strip():
                    return
                device_id = device_id.strip()
                self._device_id = device_id

            try:
                from modules.adb_explorer import ADBExplorer
                explorer = ADBExplorer(device_id, self, multi_select=True)
                if explorer.exec_():
                    paths = explorer.selected_paths()
                    for path in paths:
                        # Vérifier doublons
                        exists = any(
                            self.folders_list.item(i).text() == path
                            for i in range(self.folders_list.count())
                        )
                        if not exists:
                            self.folders_list.addItem(path)
            except Exception as e:
                QtWidgets.QMessageBox.warning(
                    self, "Erreur",
                    f"Impossible d'ouvrir l'explorateur ADB :\n{e}"
                )

        def remove_selected():
            for item in self.folders_list.selectedItems():
                self.folders_list.takeItem(self.folders_list.row(item))

        btn_add_adb.clicked.connect(add_via_adb)
        btn_remove.clicked.connect(remove_selected)

        folders_btn_row = QtWidgets.QHBoxLayout()
        folders_btn_row.addWidget(btn_add_adb)
        folders_btn_row.addWidget(btn_remove)

        # Répertoire de sauvegarde
        dest_lbl = QtWidgets.QLabel(
            "💾 Répertoire de sauvegarde PC :"
            if lang == "fr" else
            "💾 PC backup directory:"
        )
        dest_lbl.setStyleSheet("font-size:13px; font-weight:bold;")

        dest_row = QtWidgets.QHBoxLayout()
        self.dest_edit = QtWidgets.QLineEdit()
        self.dest_edit.setStyleSheet("font-size:13px;")
        self.dest_edit.setText(profile.get("local_base", ""))
        btn_browse = QtWidgets.QPushButton("📂")
        btn_browse.setFixedWidth(36)
        btn_browse.clicked.connect(self._browse)
        dest_row.addWidget(self.dest_edit)
        dest_row.addWidget(btn_browse)

        # Boutons
        btn_ok = QtWidgets.QPushButton("✅ Enregistrer" if lang == "fr" else "✅ Save")
        btn_ok.setStyleSheet(
            "background-color:#2ecc71; color:white; font-weight:bold; "
            "font-size:13px; padding:6px;"
        )
        btn_cancel = QtWidgets.QPushButton("Annuler" if lang == "fr" else "Cancel")
        btn_cancel.setStyleSheet("font-size:13px; padding:6px;")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()
        btn_row.addWidget(btn_ok)

        layout.addWidget(folders_lbl)
        layout.addWidget(self.folders_list)
        layout.addLayout(folders_btn_row)
        layout.addWidget(dest_lbl)
        layout.addLayout(dest_row)
        layout.addStretch()
        layout.addLayout(btn_row)
        self.setLayout(layout)

    def _browse(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Choisir le répertoire de sauvegarde"
            if self.lang == "fr" else
            "Choose backup directory"
        )
        if folder:
            self.dest_edit.setText(folder)

    def get_profile(self):
        folders = [
            self.folders_list.item(i).text()
            for i in range(self.folders_list.count())
        ]
        return {
            "folders":    folders,
            "local_base": self.dest_edit.text().strip(),
            "device_id":  self._device_id,
        }
