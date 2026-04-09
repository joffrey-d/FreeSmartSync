# modules/dialogs.py — FreeSmartSync
# Popups : miniatures, confirmation, récap final, prévisualisation

import os
import subprocess
import tempfile
from PyQt5 import QtWidgets, QtCore, QtGui
from modules.i18n import t

THUMB_SIZE = 130
GRID_COLS  = 5

IMAGE_EXTENSIONS   = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".heic", ".tiff"}
VIDEO_EXTENSIONS   = {".mp4", ".mov", ".avi", ".mkv", ".3gp", ".wmv"}
AUDIO_EXTENSIONS   = {".mp3", ".flac", ".ogg", ".wav", ".aac", ".m4a"}
DOC_EXTENSIONS     = {".pdf", ".doc", ".docx", ".odt", ".xls", ".xlsx", ".ppt", ".pptx"}
TEXT_EXTENSIONS    = {".txt", ".md", ".log", ".csv"}
ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz", ".7z", ".rar", ".bz2"}


def _make_icon_pixmap(line1, line2="", bg="#7f8c8d", fg="#ffffff", size=THUMB_SIZE):
    pix     = QtGui.QPixmap(size, size)
    painter = QtGui.QPainter(pix)
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    painter.setBrush(QtGui.QColor(bg))
    painter.setPen(QtGui.QColor("#999999"))
    painter.drawRoundedRect(0, 0, size, size, 8, 8)
    painter.setPen(QtGui.QColor(fg))
    f1 = QtGui.QFont("sans-serif", 13, QtGui.QFont.Bold)
    painter.setFont(f1)
    painter.drawText(
        QtCore.QRect(0, 10, size, size // 2),
        QtCore.Qt.AlignCenter, line1
    )
    if line2:
        f2 = QtGui.QFont("sans-serif", 10)
        painter.setFont(f2)
        painter.drawText(
            QtCore.QRect(0, size // 2, size, size // 2 - 10),
            QtCore.Qt.AlignCenter, line2
        )
    painter.end()
    return pix


def _get_file_icon(ext):
    ext = ext.lower()
    if ext in VIDEO_EXTENSIONS:
        return _make_icon_pixmap("VIDEO", ext.upper().lstrip("."), "#1a1a2e", "#e94560")
    elif ext in AUDIO_EXTENSIONS:
        return _make_icon_pixmap("AUDIO", ext.upper().lstrip("."), "#1a1a2e", "#00d2ff")
    elif ext == ".pdf":
        return _make_icon_pixmap("PDF", "", "#c0392b", "#ffffff")
    elif ext in DOC_EXTENSIONS:
        return _make_icon_pixmap(ext.upper().lstrip("."), "", "#2980b9", "#ffffff")
    elif ext in TEXT_EXTENSIONS:
        return _make_icon_pixmap("TXT", ext.upper().lstrip("."), "#27ae60", "#ffffff")
    elif ext in ARCHIVE_EXTENSIONS:
        return _make_icon_pixmap("ZIP", ext.upper().lstrip("."), "#e67e22", "#ffffff")
    else:
        label = ext.upper().lstrip(".")[:6] if ext else "FILE"
        return _make_icon_pixmap(label, "", "#7f8c8d", "#ffffff")


def _get_thumb(path):
    """
    Retourne (QPixmap, kind) pour un fichier.
    kind = "image" | "video" | "icon"
    Utilise QImage (plus fiable que QPixmap direct) pour les images.
    """
    ext = os.path.splitext(path)[1].lower()

    # ── Images ──────────────────────────────────────────────
    if ext in IMAGE_EXTENSIONS and os.path.exists(path):
        try:
            # QImage est plus fiable que QPixmap pour le chargement direct
            img = QtGui.QImage(path)
            if not img.isNull():
                pix = QtGui.QPixmap.fromImage(img)
                if not pix.isNull():
                    return pix.scaled(
                        THUMB_SIZE, THUMB_SIZE,
                        QtCore.Qt.KeepAspectRatio,
                        QtCore.Qt.SmoothTransformation
                    ), "image"
            # Fallback : essayer avec format explicite
            for fmt in [b"JPEG", b"JPG", b"PNG", b"WEBP", b""]:
                img2 = QtGui.QImage()
                if img2.load(path, fmt.decode() if fmt else None):
                    pix = QtGui.QPixmap.fromImage(img2)
                    if not pix.isNull():
                        return pix.scaled(
                            THUMB_SIZE, THUMB_SIZE,
                            QtCore.Qt.KeepAspectRatio,
                            QtCore.Qt.SmoothTransformation
                        ), "image"
        except Exception:
            pass

    # ── Vidéos (via ffmpeg) ─────────────────────────────────
    if ext in VIDEO_EXTENSIONS and os.path.exists(path):
        try:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                tmp_path = tmp.name
            r = subprocess.run(
                ["ffmpeg", "-y", "-i", path,
                 "-vframes", "1", "-ss", "00:00:01",
                 "-vf", f"scale={THUMB_SIZE}:-1", tmp_path],
                capture_output=True, timeout=5
            )
            if r.returncode == 0 and os.path.exists(tmp_path):
                img = QtGui.QImage(tmp_path)
                if not img.isNull():
                    pix = QtGui.QPixmap.fromImage(img).scaled(
                        THUMB_SIZE, THUMB_SIZE,
                        QtCore.Qt.KeepAspectRatio,
                        QtCore.Qt.SmoothTransformation
                    )
                    os.remove(tmp_path)
                    return pix, "video"
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        except Exception:
            pass

    # ── Icône générique ─────────────────────────────────────
    return _get_file_icon(ext), "icon"


class FileGrid(QtWidgets.QWidget):
    """Grille de miniatures scrollable."""

    def __init__(self, file_paths, base_path=None, parent=None):
        super().__init__(parent)
        self.file_paths = file_paths
        self.base_path  = base_path
        self._build()

    def _build(self):
        scroll    = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        container = QtWidgets.QWidget()
        grid      = QtWidgets.QGridLayout(container)
        grid.setSpacing(12)

        for i, path in enumerate(self.file_paths):
            ext      = os.path.splitext(path)[1].lower()
            filename = os.path.basename(path)
            rel      = (os.path.relpath(path, self.base_path)
                        if self.base_path and os.path.exists(path) else filename)

            img_lbl = QtWidgets.QLabel()
            img_lbl.setFixedSize(THUMB_SIZE, THUMB_SIZE)
            img_lbl.setAlignment(QtCore.Qt.AlignCenter)

            pix, kind = _get_thumb(path)
            img_lbl.setPixmap(pix)

            if kind == "image":
                img_lbl.setStyleSheet("border:2px solid #3498db; border-radius:4px;")
            elif kind == "video":
                img_lbl.setStyleSheet("border:2px solid #e74c3c; border-radius:4px;")
            else:
                img_lbl.setStyleSheet("border:1px solid #ccc; border-radius:4px;")

            short = filename if len(filename) <= 18 else filename[:15] + "..."
            name_lbl = QtWidgets.QLabel(short)
            name_lbl.setAlignment(QtCore.Qt.AlignCenter)
            name_lbl.setWordWrap(True)
            name_lbl.setFixedWidth(THUMB_SIZE)
            name_lbl.setStyleSheet("font-size:10px; color:#555;")
            name_lbl.setToolTip(path)

            cell = QtWidgets.QVBoxLayout()
            cell.setSpacing(4)
            cell.addWidget(img_lbl)
            cell.addWidget(name_lbl)
            cw = QtWidgets.QWidget()
            cw.setLayout(cell)
            grid.addWidget(cw, i // GRID_COLS, i % GRID_COLS)

        scroll.setWidget(container)
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)


class DeleteConfirmDialog(QtWidgets.QDialog):
    def __init__(self, files_to_delete, lang="fr", parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("delete_confirm_title", lang))
        self.setMinimumSize(800, 560)

        count = len(files_to_delete)
        label = QtWidgets.QLabel(t("delete_confirm_text", lang, count=count))
        label.setWordWrap(True)
        label.setStyleSheet("font-size:13px;")

        local_paths = [lp for lp, rp in files_to_delete]
        grid = FileGrid(local_paths)

        btn_cancel = QtWidgets.QPushButton(t("cancel", lang))
        btn_ok     = QtWidgets.QPushButton(t("delete_confirm_btn", lang))
        btn_ok.setStyleSheet(
            "background-color:#e74c3c; color:white; font-weight:bold; "
            "font-size:13px; padding:6px;"
        )
        btn_cancel.setStyleSheet("font-size:13px; padding:6px;")

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()
        btn_row.addWidget(btn_ok)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(grid)
        layout.addLayout(btn_row)
        self.setLayout(layout)

        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)


class PreviewDialog(QtWidgets.QDialog):
    """
    Prévisualisation avant synchronisation.
    Affiche ce qui va être fait et demande confirmation.
    """
    confirmed = QtCore.pyqtSignal(bool)

    def __init__(self, preview_data, lang="fr", parent=None):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(
            "🔍 Prévisualisation de la synchronisation"
            if lang == "fr" else
            "🔍 Sync preview"
        )
        self.setMinimumSize(820, 580)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(10)

        # Titre + stats
        to_pc  = preview_data.get("to_copy_pc", [])
        to_tel = preview_data.get("to_copy_tel", [])
        to_del_pc  = preview_data.get("to_delete_pc", [])
        to_del_tel = preview_data.get("to_delete_tel", [])

        stats_text = (
            f"✅ {len(to_pc)} à copier Tel→PC   |   "
            f"📤 {len(to_tel)} à copier PC→Tel   |   "
            f"🗑️ {len(to_del_pc)} à supprimer PC   |   "
            f"🗑️ {len(to_del_tel)} à supprimer Tel"
            if lang == "fr" else
            f"✅ {len(to_pc)} to copy Tel→PC   |   "
            f"📤 {len(to_tel)} to copy PC→Tel   |   "
            f"🗑️ {len(to_del_pc)} to delete PC   |   "
            f"🗑️ {len(to_del_tel)} to delete Tel"
        )
        stats_lbl = QtWidgets.QLabel(stats_text)
        stats_lbl.setStyleSheet(
            "font-size:13px; font-weight:bold; color:#2c3e50; "
            "background:#eaf2ff; border:1px solid #3498db; "
            "border-radius:4px; padding:8px;"
        )
        layout.addWidget(stats_lbl)

        # Onglets
        tabs = QtWidgets.QTabWidget()
        tabs.setStyleSheet("font-size:13px;")

        if to_pc:
            tab = FileGrid(to_pc)
            tabs.addTab(tab, f"Tel→PC ({len(to_pc)})")
        if to_tel:
            tab = FileGrid(to_tel)
            tabs.addTab(tab, f"PC→Tel ({len(to_tel)})")
        if to_del_pc:
            tab = FileGrid(to_del_pc)
            tabs.addTab(tab, f"Suppr. PC ({len(to_del_pc)})")
        if to_del_tel:
            tab = FileGrid([lp for lp, rp in to_del_tel])
            tabs.addTab(tab, f"Suppr. Tel ({len(to_del_tel)})")

        if tabs.count() == 0:
            no_change = QtWidgets.QLabel(
                "✅ Aucun changement détecté — tout est à jour !"
                if lang == "fr" else
                "✅ No changes detected — everything is up to date!"
            )
            no_change.setAlignment(QtCore.Qt.AlignCenter)
            no_change.setStyleSheet(
                "font-size:15px; color:#27ae60; font-weight:bold; padding:30px;"
            )
            tabs.addTab(no_change, "✅ À jour")

        layout.addWidget(tabs)

        # Boutons
        btn_confirm = QtWidgets.QPushButton(
            "✅ Confirmer et synchroniser"
            if lang == "fr" else "✅ Confirm and sync"
        )
        btn_confirm.setMinimumHeight(42)
        btn_confirm.setStyleSheet(
            "background-color:#2ecc71; color:white; font-weight:bold; "
            "font-size:14px; padding:8px; border-radius:6px;"
        )

        btn_cancel = QtWidgets.QPushButton(
            "❌ Annuler" if lang == "fr" else "❌ Cancel"
        )
        btn_cancel.setMinimumHeight(42)
        btn_cancel.setStyleSheet(
            "background-color:#e74c3c; color:white; font-weight:bold; "
            "font-size:14px; padding:8px; border-radius:6px;"
        )

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()
        btn_row.addWidget(btn_confirm)

        btn_confirm.clicked.connect(lambda: self._close(True))
        btn_cancel.clicked.connect(lambda: self._close(False))

        layout.addLayout(btn_row)
        self.setLayout(layout)

    def _close(self, ok):
        self.confirmed.emit(ok)
        if ok:
            self.accept()
        else:
            self.reject()


class PreviewDialog(QtWidgets.QDialog):
    """Popup de prévisualisation avant sync."""
    confirmed = QtCore.pyqtSignal(bool)

    def __init__(self, changes, lang="fr", parent=None):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(
            "Prévisualisation — Que va faire la sync ?"
            if lang == "fr" else
            "Preview — What will the sync do?"
        )
        self.setMinimumSize(780, 520)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(16, 14, 16, 14)

        title = QtWidgets.QLabel(
            "Voici ce que FreeSmartSync va effectuer. Vérifiez avant de confirmer."
            if lang == "fr" else
            "Here is what FreeSmartSync will do. Please review before confirming."
        )
        title.setWordWrap(True)
        title.setStyleSheet(
            "font-size:14px; background:#eaf2ff; border:1px solid #3498db; "
            "border-radius:4px; padding:10px;"
        )

        n_copy_tel = len(changes.get("to_copy_tel_to_pc", []))
        n_push     = len(changes.get("to_push_pc_to_tel", []))
        n_update   = len(changes.get("to_update_pc_to_tel", []))
        n_del_tel  = len(changes.get("to_delete_tel", []))
        n_del_pc   = len(changes.get("to_delete_pc", []))

        stats_lbl = QtWidgets.QLabel(
            f"Tel->PC a copier: {n_copy_tel}   PC->Tel nouveaux: {n_push}   "
            f"PC->Tel modifies: {n_update}   Supprimer Tel: {n_del_tel}   Supprimer PC: {n_del_pc}"
        )
        stats_lbl.setStyleSheet("font-size:13px; font-weight:bold; color:#2c3e50;")

        tabs = QtWidgets.QTabWidget()
        tabs.setStyleSheet("font-size:12px;")

        def make_list_full(items, mode="tuple3"):
            """Liste avec chemin complet."""
            w = QtWidgets.QListWidget()
            w.setStyleSheet("font-size:11px; font-family:monospace;")
            for item in items[:500]:
                if mode == "tuple3" and isinstance(item, tuple) and len(item) >= 3:
                    # (local_path, remote_path, rel) — afficher rel (chemin relatif)
                    w.addItem(str(item[2]))
                elif mode == "tuple2" and isinstance(item, tuple) and len(item) == 2:
                    # (local_path, remote_path) — afficher remote_path
                    w.addItem(str(item[1]))
                elif mode == "path":
                    # chemin local complet
                    w.addItem(str(item))
                else:
                    w.addItem(str(item))
            if len(items) > 500:
                w.addItem(f"... et {len(items)-500} autres fichiers")
            return w

        if n_copy_tel:
            tabs.addTab(
                make_list_full(changes["to_copy_tel_to_pc"], "tuple3"),
                f"Tel->PC ({n_copy_tel})"
            )
        if n_push:
            tabs.addTab(
                make_list_full(changes["to_push_pc_to_tel"], "tuple3"),
                f"PC->Tel ({n_push})"
            )
        if n_update:
            tabs.addTab(
                make_list_full(changes["to_update_pc_to_tel"], "tuple3"),
                f"Modifies ({n_update})"
            )
        if n_del_tel:
            tabs.addTab(
                make_list_full(changes["to_delete_tel"], "tuple2"),
                f"Suppr Tel ({n_del_tel})"
            )
        if n_del_pc:
            tabs.addTab(
                make_list_full(changes["to_delete_pc"], "path"),
                f"Suppr PC ({n_del_pc})"
            )
        # Avertissement si suppressions PC bloquées par le garde de sécurité
        blocked = changes.get("_delete_pc_blocked", [])
        if blocked:
            reason = changes.get("_delete_pc_blocked_reason", "")
            w_blocked = QtWidgets.QListWidget()
            w_blocked.setStyleSheet("font-size:11px; color:#e74c3c; font-family:monospace;")
            header_item = QtWidgets.QListWidgetItem(
                f"BLOQUEES PAR SECURITE ({len(blocked)} fichiers) — {reason}"
            )
            header_item.setForeground(QtGui.QColor("#e74c3c"))
            w_blocked.addItem(header_item)
            for p in blocked[:500]:
                w_blocked.addItem(str(p))
            if len(blocked) > 500:
                w_blocked.addItem(f"... et {len(blocked)-500} autres")
            tabs.addTab(w_blocked, f"BLOQUEES ({len(blocked)})")

        btn_confirm = QtWidgets.QPushButton(
            "Oui, synchroniser maintenant" if lang == "fr" else "Yes, sync now"
        )
        btn_confirm.setMinimumHeight(42)
        btn_confirm.setStyleSheet(
            "background-color:#2ecc71; color:white; font-weight:bold; "
            "font-size:14px; padding:8px; border-radius:6px;"
        )

        btn_cancel = QtWidgets.QPushButton(
            "Non, annuler" if lang == "fr" else "No, cancel"
        )
        btn_cancel.setMinimumHeight(42)
        btn_cancel.setStyleSheet(
            "background-color:#e74c3c; color:white; font-weight:bold; "
            "font-size:14px; padding:8px; border-radius:6px;"
        )

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()
        btn_row.addWidget(btn_confirm)

        btn_confirm.clicked.connect(lambda: self._respond(True))
        btn_cancel.clicked.connect(lambda: self._respond(False))

        layout.addWidget(title)
        layout.addWidget(stats_lbl)
        if tabs.count() > 0:
            layout.addWidget(tabs)
        layout.addLayout(btn_row)
        self.setLayout(layout)

    def _respond(self, ok):
        self.confirmed.emit(ok)
        if ok: self.accept()
        else:  self.reject()


class SummaryDialog(QtWidgets.QDialog):
    """Resume de fin de synchronisation avec miniatures."""

    def __init__(self, summary, base_path=None, lang="fr", parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("summary_title", lang))
        self.setMinimumSize(860, 620)
        import os as _os; from PyQt5 import QtGui as _Gui
        _ip = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "assets", "icon.png")
        if _os.path.exists(_ip): self.setWindowIcon(_Gui.QIcon(_ip))

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(10)

        header_parts = []
        if summary.get("profile_name"):
            header_parts.append(f"Profil : {summary['profile_name']}")
        if summary.get("start_time"):
            header_parts.append(f"Debut : {summary['start_time']}")
        if summary.get("duration_str"):
            header_parts.append(f"Duree : {summary['duration_str']}")

        if header_parts:
            header = QtWidgets.QLabel(" | ".join(header_parts))
            header.setStyleSheet(
                "font-size:12px; color:#555; background:#f8f9fa; "
                "border:1px solid #dee2e6; border-radius:4px; padding:6px;"
            )
            layout.addWidget(header)

        copied_tp   = summary.get("copied_tel_to_pc", summary.get("copied", []))
        copied_pt   = summary.get("copied_pc_to_tel", [])
        modified    = summary.get("modified_pushed", [])
        deleted_pc  = summary.get("deleted_pc", [])
        deleted_tel = summary.get("deleted_tel", [])
        errors      = summary.get("errors", 0)
        errors_list = summary.get("errors_list", [])

        stats = QtWidgets.QLabel(
            f"Tel->PC: {len(copied_tp)}  PC->Tel: {len(copied_pt)}  "
            f"MAJ: {len(modified)}  Suppr PC: {len(deleted_pc)}  "
            f"Suppr Tel: {len(deleted_tel)}  Erreurs: {errors}"
        )
        stats.setStyleSheet("font-size:13px; font-weight:bold; color:#2c3e50;")
        layout.addWidget(stats)

        tabs = QtWidgets.QTabWidget()
        tabs.setStyleSheet("font-size:13px;")

        if copied_tp:
            paths = [lp for lp, rel in copied_tp]
            tabs.addTab(FileGrid(paths, base_path), f"Tel->PC ({len(copied_tp)})")

        if copied_pt:
            paths = [lp for lp, rel in copied_pt]
            tabs.addTab(FileGrid(paths, base_path), f"PC->Tel ({len(copied_pt)})")

        if modified:
            paths = [lp for lp, rel in modified]
            tabs.addTab(FileGrid(paths, base_path), f"Modifies ({len(modified)})")

        if deleted_pc:
            tabs.addTab(FileGrid(deleted_pc, base_path), f"Suppr PC ({len(deleted_pc)})")

        if deleted_tel:
            paths = [lp for lp, rp in deleted_tel]
            tabs.addTab(FileGrid(paths, base_path), f"Suppr Tel ({len(deleted_tel)})")

        if errors_list:
            err_w = QtWidgets.QListWidget()
            err_w.setStyleSheet("font-size:12px; color:#e74c3c;")
            for err in errors_list[:500]:
                err_w.addItem(err)
            if len(errors_list) > 500:
                err_w.addItem(f"... et {len(errors_list)-500} autres")
            tabs.addTab(err_w, f"Erreurs ({errors})")

        if tabs.count() > 0:
            layout.addWidget(tabs)
        else:
            nothing = QtWidgets.QLabel(
                "Tout etait a jour !" if lang == "fr" else "Everything was up to date!"
            )
            nothing.setAlignment(QtCore.Qt.AlignCenter)
            nothing.setStyleSheet("font-size:14px; color:#27ae60; font-weight:bold;")
            layout.addWidget(nothing)

        btn_close = QtWidgets.QPushButton(t("close", lang))
        btn_close.setStyleSheet(
            "background-color:#2ecc71; color:white; font-weight:bold; "
            "font-size:13px; padding:6px;"
        )
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, 0, QtCore.Qt.AlignRight)
        self.setLayout(layout)
