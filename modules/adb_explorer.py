# modules/adb_explorer.py
# Explorateur de fichiers ADB — sélection simple ou multiple

import os
import subprocess
from PyQt5 import QtWidgets, QtCore


class ADBExplorer(QtWidgets.QDialog):
    def __init__(self, device_id, parent=None, multi_select=False):
        super().__init__(parent)
        self.device_id    = device_id
        self.multi_select = multi_select

        self.setWindowTitle(
            "Explorateur ADB — Sélection de dossiers"
        )
        self.setMinimumSize(560, 480)

        # Instructions
        info_lbl = QtWidgets.QLabel()
        info_lbl.setWordWrap(True)
        if multi_select:
            info_lbl.setText(
                "📁 Naviguez dans les dossiers de votre téléphone.<br>"
                "💡 <b>Maintenez Ctrl</b> pour sélectionner <b>plusieurs dossiers à la fois</b>.<br>"
                "Double-clic sur un dossier pour l'explorer."
            )
        else:
            info_lbl.setText(
                "📁 Naviguez dans les dossiers de votre téléphone.<br>"
                "Double-clic pour explorer, clic simple pour sélectionner."
            )
        info_lbl.setStyleSheet(
            "font-size:13px; background:#eaf2ff; border:1px solid #3498db; "
            "border-radius:4px; padding:8px; margin-bottom:4px;"
        )

        # Arbre des dossiers
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabel("📱 Téléphone — /sdcard")
        self.tree.setStyleSheet("font-size:13px;")
        self.tree.setAnimated(True)

        if multi_select:
            # Checkboxes pour sélection multiple — compatible toutes distros
            self.tree.setSelectionMode(
                QtWidgets.QAbstractItemView.SingleSelection
            )
        else:
            self.tree.setSelectionMode(
                QtWidgets.QAbstractItemView.SingleSelection
            )

        # Double-clic pour naviguer
        self.tree.itemExpanded.connect(self._on_expand)
        self.tree.itemDoubleClicked.connect(self._on_double_click)

        # Sélection en cours
        self.selection_lbl = QtWidgets.QLabel()
        self.selection_lbl.setWordWrap(True)
        self.selection_lbl.setStyleSheet(
            "font-size:12px; color:#27ae60; font-style:italic; "
            "min-height:20px;"
        )
        if multi_select:
            # Mise à jour quand on coche une case
            self.tree.itemChanged.connect(lambda item, col: self._update_selection_label())
        else:
            self.tree.itemSelectionChanged.connect(self._update_selection_label)

        # Boutons
        btn_select = QtWidgets.QPushButton(
            "✅ Valider la sélection" if multi_select else "✅ Sélectionner"
        )
        btn_select.setMinimumHeight(40)
        btn_select.setStyleSheet(
            "background-color:#2ecc71; color:white; font-weight:bold; "
            "font-size:14px; padding:8px; border-radius:4px;"
        )
        btn_cancel = QtWidgets.QPushButton("Annuler")
        btn_cancel.setStyleSheet("font-size:13px; padding:6px;")

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()
        btn_row.addWidget(btn_select)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.addWidget(info_lbl)
        layout.addWidget(self.tree)
        layout.addWidget(self.selection_lbl)
        layout.addLayout(btn_row)
        self.setLayout(layout)

        btn_select.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        self.load_root()

    def run_cmd(self, cmd):
        return subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

    def load_root(self):
        root = QtWidgets.QTreeWidgetItem(["📱 /sdcard"])
        root.setData(0, QtCore.Qt.UserRole, "/sdcard")
        # Placeholder pour indiquer qu'il y a des enfants
        placeholder = QtWidgets.QTreeWidgetItem(["⏳ Chargement..."])
        root.addChild(placeholder)
        self.tree.addTopLevelItem(root)
        root.setExpanded(True)
        self._load_children(root)

    def _load_children(self, item):
        path = item.data(0, QtCore.Qt.UserRole)
        if not path:
            return

        result = self.run_cmd(
            ["adb", "-s", self.device_id, "shell",
             f"ls -d \"{path}\"/*/ 2>/dev/null"]
        )

        # Supprimer les placeholders
        while item.childCount() > 0:
            item.removeChild(item.child(0))

        if result.returncode != 0 or not result.stdout.strip():
            return

        for line in result.stdout.splitlines():
            line = line.strip().rstrip("/")
            if not line:
                continue
            name  = os.path.basename(line)
            child = QtWidgets.QTreeWidgetItem([f"📁 {name}"])
            child.setData(0, QtCore.Qt.UserRole, line)
            if self.multi_select:
                child.setFlags(
                    QtCore.Qt.ItemIsEnabled |
                    QtCore.Qt.ItemIsSelectable |
                    QtCore.Qt.ItemIsUserCheckable
                )
                child.setCheckState(0, QtCore.Qt.Unchecked)
            else:
                child.setFlags(
                    QtCore.Qt.ItemIsEnabled |
                    QtCore.Qt.ItemIsSelectable
                )
            # Placeholder si sous-dossiers possibles
            placeholder = QtWidgets.QTreeWidgetItem(["⏳"])
            child.addChild(placeholder)
            item.addChild(child)

    def _on_expand(self, item):
        """Charge les sous-dossiers au premier expand."""
        if item.childCount() == 1:
            child = item.child(0)
            if child and child.text(0) in ("⏳", "⏳ Chargement..."):
                self._load_children(item)

    def _on_double_click(self, item, _col):
        """Double-clic → expand/collapse."""
        if item.isExpanded():
            item.setExpanded(False)
        else:
            item.setExpanded(True)

    def _update_selection_label(self):
        """Met à jour le label de sélection en cours."""
        paths = self.selected_paths()
        if not paths:
            if self.multi_select:
                self.selection_lbl.setText(
                    "Cochez les dossiers à sélectionner"
                    if hasattr(self, 'lang') else "Check folders to select"
                )
            else:
                self.selection_lbl.setText("")
        elif len(paths) == 1:
            self.selection_lbl.setText(f"✅ Sélectionné : {paths[0]}")
        else:
            self.selection_lbl.setText(
                f"✅ {len(paths)} dossiers sélectionnés : "
                + ", ".join(os.path.basename(p) for p in paths)
            )

    def selected_paths(self):
        """Retourne la liste des chemins sélectionnés (relatifs à /sdcard)."""
        paths = []
        if self.multi_select:
            # Mode checkbox — parcourir tout l'arbre
            def collect_checked(item):
                if (item.data(0, QtCore.Qt.UserRole) and
                        item.checkState(0) == QtCore.Qt.Checked):
                    path = item.data(0, QtCore.Qt.UserRole)
                    if path and path != "/sdcard":
                        rel = path.replace("/sdcard/", "")
                        if rel:
                            paths.append(rel)
                for i in range(item.childCount()):
                    collect_checked(item.child(i))
            for i in range(self.tree.topLevelItemCount()):
                collect_checked(self.tree.topLevelItem(i))
        else:
            item = self.tree.currentItem()
            if item:
                path = item.data(0, QtCore.Qt.UserRole)
                if path and path != "/sdcard":
                    rel = path.replace("/sdcard/", "")
                    if rel:
                        paths.append(rel)
        return paths

    def selected_path(self):
        """Compatibilité — retourne le premier chemin sélectionné."""
        paths = self.selected_paths()
        return paths[0] if paths else None
