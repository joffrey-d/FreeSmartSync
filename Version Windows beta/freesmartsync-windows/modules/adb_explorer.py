# modules/adb_explorer.py — FreeSmartSync v0.8.6

import os
import subprocess
from PyQt5 import QtWidgets, QtCore


def adb_list_dirs(device_id, path, timeout=15):
    """
    Liste les sous-dossiers directs d'un chemin sur Android.
    Méthode universelle : for loop shell + test -d
    Fonctionne sur TOUS les Android/busybox sans exception.
    """
    # Shell for loop : seule méthode garantie universelle sur Android busybox
    cmd = (
        f'for f in "{path}"/*; do '
        f'  [ -d "$f" ] && echo "$f"; '
        f'done 2>/dev/null'
    )
    try:
        r = subprocess.run(
            ["adb", "-s", device_id, "shell", cmd],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, timeout=timeout
        )
        dirs = []
        for line in r.stdout.splitlines():
            line = line.strip()
            if not line or line == path:
                continue
            # Ignorer les dossiers cachés système
            name = os.path.basename(line)
            if name.startswith("."):
                continue
            dirs.append(line)
        return sorted(dirs)
    except Exception:
        return []


class ADBExplorer(QtWidgets.QDialog):

    def __init__(self, device_id, parent=None, multi_select=False):
        super().__init__(parent)
        self.device_id    = device_id
        self.multi_select = multi_select
        self._loading     = False

        self.setWindowTitle("Explorateur ADB — Sélection de dossiers")
        self.setMinimumSize(600, 520)

        # ── Info ──────────────────────────────────────────────────
        info_lbl = QtWidgets.QLabel(
            "📁 <b>Cochez</b> les dossiers à synchroniser, puis cliquez <b>Valider</b>.<br>"
            "Cliquez sur ▶ pour explorer les sous-dossiers."
            if multi_select else
            "📁 Cliquez sur un dossier pour le sélectionner.<br>"
            "Cliquez sur ▶ pour explorer les sous-dossiers."
        )
        info_lbl.setWordWrap(True)
        info_lbl.setStyleSheet(
            "font-size:13px; background:#eaf2ff; border:1px solid #3498db; "
            "border-radius:4px; padding:10px;"
        )

        # ── Arbre ─────────────────────────────────────────────────
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabel("📱 Téléphone — /sdcard")
        self.tree.setStyleSheet("font-size:13px;")
        self.tree.setAnimated(True)
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tree.itemExpanded.connect(self._on_expand)
        if not multi_select:
            self.tree.itemSelectionChanged.connect(self._update_label)

        # ── Label sélection ───────────────────────────────────────
        self.sel_lbl = QtWidgets.QLabel(
            "Cochez les dossiers à synchroniser" if multi_select else ""
        )
        self.sel_lbl.setWordWrap(True)
        self.sel_lbl.setStyleSheet(
            "font-size:12px; color:#27ae60; font-style:italic; min-height:18px;"
        )

        # ── Boutons ───────────────────────────────────────────────
        btn_ok = QtWidgets.QPushButton(
            "✅ Valider la sélection" if multi_select else "✅ Sélectionner"
        )
        btn_ok.setMinimumHeight(42)
        btn_ok.setStyleSheet(
            "background-color:#2ecc71; color:white; font-weight:bold; "
            "font-size:14px; padding:8px; border-radius:4px;"
        )
        btn_cancel = QtWidgets.QPushButton("Annuler")
        btn_cancel.setStyleSheet("font-size:13px; padding:6px;")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()
        btn_row.addWidget(btn_ok)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.addWidget(info_lbl)
        layout.addWidget(self.tree)
        layout.addWidget(self.sel_lbl)
        layout.addLayout(btn_row)
        self.setLayout(layout)

        # Charger l'arbre AVANT de connecter itemChanged
        self._load_root()

        if multi_select:
            self.tree.itemChanged.connect(self._on_checked)

    # ─── Chargement ───────────────────────────────────────────────

    def _load_root(self):
        self._loading = True
        self.tree.clear()

        root = QtWidgets.QTreeWidgetItem(["📱 /sdcard"])
        root.setData(0, QtCore.Qt.UserRole, "/sdcard")
        root.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tree.addTopLevelItem(root)

        dirs = adb_list_dirs(self.device_id, "/sdcard")

        if not dirs:
            msg = QtWidgets.QTreeWidgetItem([
                "⚠️ Aucun dossier trouvé — téléphone bien branché avec débogage USB ?"
            ])
            msg.setFlags(QtCore.Qt.ItemIsEnabled)
            root.addChild(msg)
        else:
            for d in dirs:
                root.addChild(self._make_item(d))

        self._loading = False
        root.setExpanded(True)

    def _make_item(self, path):
        """Crée un item pour un dossier avec placeholder d'expansion."""
        name  = os.path.basename(path)
        item  = QtWidgets.QTreeWidgetItem([f"📁 {name}"])
        item.setData(0, QtCore.Qt.UserRole, path)

        if self.multi_select:
            item.setFlags(
                QtCore.Qt.ItemIsEnabled |
                QtCore.Qt.ItemIsSelectable |
                QtCore.Qt.ItemIsUserCheckable
            )
            item.setCheckState(0, QtCore.Qt.Unchecked)
        else:
            item.setFlags(
                QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
            )

        # Placeholder : permet l'expand arrow
        ph = QtWidgets.QTreeWidgetItem(["⏳"])
        ph.setFlags(QtCore.Qt.ItemIsEnabled)
        item.addChild(ph)
        return item

    def _on_expand(self, item):
        """Chargement lazy au premier expand."""
        if self._loading:
            return
        # Vérifier qu'on a le placeholder
        if item.childCount() != 1:
            return
        ph = item.child(0)
        if not ph or ph.text(0) != "⏳":
            return

        path = item.data(0, QtCore.Qt.UserRole)
        if not path:
            return

        self._loading = True
        item.removeChild(ph)
        for d in adb_list_dirs(self.device_id, path):
            item.addChild(self._make_item(d))
        self._loading = False

    # ─── Signaux ──────────────────────────────────────────────────

    def _on_checked(self, item, col):
        if not self._loading:
            self._update_label()

    def _update_label(self):
        paths = self.selected_paths()
        if not paths:
            self.sel_lbl.setText(
                "Cochez les dossiers à synchroniser"
                if self.multi_select else ""
            )
        elif len(paths) == 1:
            self.sel_lbl.setText(f"✅ {paths[0]}")
        else:
            names = ", ".join(os.path.basename(p) for p in paths)
            self.sel_lbl.setText(f"✅ {len(paths)} dossiers : {names}")

    # ─── Résultats ────────────────────────────────────────────────

    def selected_paths(self):
        """Chemins relatifs à /sdcard des dossiers sélectionnés/cochés."""
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
            cur = self.tree.currentItem()
            if cur:
                path = cur.data(0, QtCore.Qt.UserRole)
                if path and path != "/sdcard":
                    rel = path.replace("/sdcard/", "", 1)
                    if rel:
                        paths.append(rel)

        return paths

    def selected_path(self):
        paths = self.selected_paths()
        return paths[0] if paths else None
