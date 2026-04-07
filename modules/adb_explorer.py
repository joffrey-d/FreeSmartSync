# modules/adb_explorer.py
# Explorateur de fichiers ADB — sélection simple ou multiple (checkboxes)

import os
import subprocess
from PyQt5 import QtWidgets, QtCore


class ADBExplorer(QtWidgets.QDialog):

    def __init__(self, device_id, parent=None, multi_select=False):
        super().__init__(parent)
        self.device_id    = device_id
        self.multi_select = multi_select
        self._loading     = False  # Verrou anti-boucle pendant le chargement

        self.setWindowTitle("Explorateur ADB — Sélection de dossiers")
        self.setMinimumSize(580, 500)

        # ── Instructions ──────────────────────────────────────────
        info_lbl = QtWidgets.QLabel()
        info_lbl.setWordWrap(True)
        if multi_select:
            info_lbl.setText(
                "📁 Cochez les dossiers à synchroniser.<br>"
                "Cliquez sur ▶ pour explorer les sous-dossiers."
            )
        else:
            info_lbl.setText(
                "📁 Cliquez sur un dossier pour le sélectionner.<br>"
                "Cliquez sur ▶ pour explorer les sous-dossiers."
            )
        info_lbl.setStyleSheet(
            "font-size:13px; background:#eaf2ff; border:1px solid #3498db; "
            "border-radius:4px; padding:8px;"
        )

        # ── Arbre ─────────────────────────────────────────────────
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabel("📱 Téléphone — /sdcard")
        self.tree.setStyleSheet("font-size:13px;")
        self.tree.setAnimated(True)
        self.tree.setUniformRowHeights(True)
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.tree.itemExpanded.connect(self._on_expand)

        # ── Label sélection ───────────────────────────────────────
        self.selection_lbl = QtWidgets.QLabel("")
        self.selection_lbl.setWordWrap(True)
        self.selection_lbl.setStyleSheet(
            "font-size:12px; color:#27ae60; font-style:italic; min-height:20px;"
        )

        if multi_select:
            # Connecter APRES load_root pour éviter boucle pendant init
            pass
        else:
            self.tree.itemSelectionChanged.connect(self._update_selection_label)

        # ── Boutons ───────────────────────────────────────────────
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

        # Charger la racine (SANS setExpanded pour éviter _on_expand prématuré)
        self._load_root()

        # Connecter itemChanged APRES le chargement initial
        if multi_select:
            self.tree.itemChanged.connect(self._on_item_changed)

    # ─── ADB ──────────────────────────────────────────────────────

    def _run(self, cmd, timeout=10):
        try:
            return subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, timeout=timeout
            )
        except Exception:
            class R:
                returncode = 1; stdout = ""; stderr = ""
            return R()

    def _list_dirs(self, path):
        """
        Liste les sous-dossiers directs d'un chemin sur le téléphone.
        Utilise find -maxdepth 1 -type d (plus fiable que ls -d /*/  ).
        Retourne une liste de chemins absolus.
        """
        result = self._run(
            ["adb", "-s", self.device_id, "shell",
             f"find \"{path}\" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | sort"],
            timeout=15
        )
        dirs = []
        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.splitlines():
                line = line.strip()
                if line and not line.startswith("find:"):
                    dirs.append(line)
        return dirs

    # ─── Chargement arbre ─────────────────────────────────────────

    def _load_root(self):
        """Charge /sdcard et ses sous-dossiers directs."""
        self._loading = True
        self.tree.clear()

        root = QtWidgets.QTreeWidgetItem(["📱 /sdcard"])
        root.setData(0, QtCore.Qt.UserRole, "/sdcard")
        root.setFlags(QtCore.Qt.ItemIsEnabled)  # Racine non sélectionnable
        self.tree.addTopLevelItem(root)

        # Charger les sous-dossiers de /sdcard directement
        dirs = self._list_dirs("/sdcard")

        if not dirs:
            err = QtWidgets.QTreeWidgetItem(["⚠️ Aucun dossier trouvé — vérifiez la connexion ADB"])
            err.setFlags(QtCore.Qt.ItemIsEnabled)
            root.addChild(err)
        else:
            for dpath in dirs:
                child = self._make_item(dpath)
                root.addChild(child)

        self._loading = False

        # Expand la racine APRÈS le chargement (ne déclenche plus de chargement inutile)
        root.setExpanded(True)

        if self.multi_select:
            self.selection_lbl.setText("Cochez les dossiers à synchroniser")

    def _make_item(self, path):
        """Crée un item QTreeWidget pour un dossier."""
        name  = os.path.basename(path)
        child = QtWidgets.QTreeWidgetItem([f"📁 {name}"])
        child.setData(0, QtCore.Qt.UserRole, path)

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

        # Placeholder pour indiquer qu'on peut explorer
        ph = QtWidgets.QTreeWidgetItem(["⏳"])
        ph.setFlags(QtCore.Qt.ItemIsEnabled)
        child.addChild(ph)
        return child

    def _on_expand(self, item):
        """Chargement lazy : sous-dossiers chargés au premier expand."""
        if self._loading:
            return
        if item.childCount() == 1:
            ph = item.child(0)
            if ph and ph.text(0) == "⏳":
                path = item.data(0, QtCore.Qt.UserRole)
                if not path:
                    return
                self._loading = True
                item.removeChild(ph)
                dirs = self._list_dirs(path)
                for dpath in dirs:
                    item.addChild(self._make_item(dpath))
                self._loading = False

    def _on_item_changed(self, item, col):
        """Mise à jour label quand une case est cochée."""
        if not self._loading:
            self._update_selection_label()

    def _update_selection_label(self):
        paths = self.selected_paths()
        if not paths:
            if self.multi_select:
                self.selection_lbl.setText("Cochez les dossiers à synchroniser")
            else:
                self.selection_lbl.setText("")
        elif len(paths) == 1:
            self.selection_lbl.setText(f"✅ {paths[0]}")
        else:
            names = ", ".join(os.path.basename(p) for p in paths)
            self.selection_lbl.setText(f"✅ {len(paths)} dossiers : {names}")

    # ─── Sélection ────────────────────────────────────────────────

    def selected_paths(self):
        """Retourne les chemins relatifs sélectionnés (sans /sdcard/)."""
        paths = []
        if self.multi_select:
            def collect(item):
                path = item.data(0, QtCore.Qt.UserRole)
                if path and path != "/sdcard":
                    if item.checkState(0) == QtCore.Qt.Checked:
                        rel = path.replace("/sdcard/", "", 1)
                        if rel:
                            paths.append(rel)
                for i in range(item.childCount()):
                    collect(item.child(i))
            for i in range(self.tree.topLevelItemCount()):
                collect(self.tree.topLevelItem(i))
        else:
            item = self.tree.currentItem()
            if item:
                path = item.data(0, QtCore.Qt.UserRole)
                if path and path != "/sdcard":
                    rel = path.replace("/sdcard/", "", 1)
                    if rel:
                        paths.append(rel)
        return paths

    def selected_path(self):
        """Compatibilité — premier chemin sélectionné."""
        paths = self.selected_paths()
        return paths[0] if paths else None
