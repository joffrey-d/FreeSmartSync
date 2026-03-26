# modules/dialogs.py
# Popups : miniatures, confirmation suppression, résumé final

import os
from PyQt5 import QtWidgets, QtCore, QtGui
from modules.i18n import t

THUMB_SIZE = 100
GRID_COLS  = 5

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".heic"}
FILE_ICONS = {
    ".mp4": "🎬", ".mov": "🎬", ".avi": "🎬", ".mkv": "🎬",
    ".mp3": "🎵", ".flac": "🎵", ".ogg": "🎵", ".wav": "🎵",
    ".pdf": "📄", ".gpx": "🗺️", ".kdbx": "🔑",
    ".zip": "📦", ".tar": "📦", ".gz": "📦",
    ".doc": "📝", ".docx": "📝", ".txt": "📝",
}


class FileGrid(QtWidgets.QWidget):
    """Grille scrollable avec miniatures ou icônes."""

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
        grid.setSpacing(10)

        for i, path in enumerate(self.file_paths):
            ext = os.path.splitext(path)[1].lower()
            rel = (os.path.relpath(path, self.base_path)
                   if self.base_path else os.path.basename(path))

            img_label = QtWidgets.QLabel()
            img_label.setFixedSize(THUMB_SIZE, THUMB_SIZE)
            img_label.setAlignment(QtCore.Qt.AlignCenter)

            if ext in IMAGE_EXTENSIONS and os.path.exists(path):
                pix = QtGui.QPixmap(path)
                if not pix.isNull():
                    pix = pix.scaled(THUMB_SIZE, THUMB_SIZE,
                                     QtCore.Qt.KeepAspectRatio,
                                     QtCore.Qt.SmoothTransformation)
                    img_label.setPixmap(pix)
                    img_label.setStyleSheet("border:1px solid #ccc;")
                else:
                    img_label.setText("🖼️")
                    img_label.setStyleSheet("border:1px solid #ccc; font-size:32px;")
            else:
                icon = FILE_ICONS.get(ext, "📁")
                img_label.setText(icon)
                img_label.setStyleSheet(
                    "border:1px solid #ccc; background:#f5f5f5; font-size:32px;"
                )

            name_label = QtWidgets.QLabel(rel)
            name_label.setAlignment(QtCore.Qt.AlignCenter)
            name_label.setWordWrap(True)
            name_label.setFixedWidth(THUMB_SIZE)
            name_label.setStyleSheet("font-size:9px; color:#555;")
            name_label.setToolTip(path)

            cell = QtWidgets.QVBoxLayout()
            cell.addWidget(img_label)
            cell.addWidget(name_label)
            cell_w = QtWidgets.QWidget()
            cell_w.setLayout(cell)
            grid.addWidget(cell_w, i // GRID_COLS, i % GRID_COLS)

        scroll.setWidget(container)
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)


class DeleteConfirmDialog(QtWidgets.QDialog):
    """Popup de confirmation avant suppression sur le téléphone."""

    def __init__(self, files_to_delete, lang="fr", parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("delete_confirm_title", lang))
        self.setMinimumSize(750, 520)

        count = len(files_to_delete)
        label = QtWidgets.QLabel(
            t("delete_confirm_text", lang, count=count)
        )
        label.setWordWrap(True)

        local_paths = [lp for lp, rp in files_to_delete]
        grid = FileGrid(local_paths)

        btn_confirm = QtWidgets.QPushButton(t("delete_confirm_btn", lang))
        btn_cancel  = QtWidgets.QPushButton(t("delete_cancel_btn", lang))
        btn_confirm.setStyleSheet(
            "background-color:#e74c3c; color:white; font-weight:bold; padding:6px;"
        )
        btn_cancel.setStyleSheet(
            "background-color:#2ecc71; color:white; font-weight:bold; padding:6px;"
        )
        btn_confirm.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_confirm)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(grid)
        layout.addLayout(btn_row)
        self.setLayout(layout)


class SummaryDialog(QtWidgets.QDialog):
    """Popup de résumé final avec onglets et miniatures."""

    def __init__(self, summary, base_path, lang="fr", parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("summary_dialog_title", lang))
        self.setMinimumSize(800, 600)

        tabs = QtWidgets.QTabWidget()
        s    = summary

        # Onglet résumé global
        tab_info    = QtWidgets.QWidget()
        info_layout = QtWidgets.QVBoxLayout(tab_info)
        info_text   = (
            f"<b>{t('summary_start', lang)}</b> {s['start_time']}<br>"
            f"<b>{t('summary_end', lang)}</b> {s['end_time']}<br>"
            f"<b>{t('summary_duration', lang)}</b> {s['duration_str']}<br><br>"
            f"<b>{t('summary_copied', lang)}</b> {len(s['copied'])}<br>"
            f"<b>{t('summary_skipped', lang)}</b> {s['skipped']}<br>"
            f"<b>{t('summary_del_pc', lang)}</b> {len(s['deleted_pc'])}<br>"
            f"<b>{t('summary_del_tel', lang)}</b> {len(s['deleted_tel'])}<br>"
            f"<b>{t('summary_errors', lang)}</b> {s['errors']}<br>"
        )
        lbl = QtWidgets.QLabel(info_text)
        lbl.setWordWrap(True)
        lbl.setStyleSheet("font-size:13px; padding:10px;")
        info_layout.addWidget(lbl)
        info_layout.addStretch()
        tabs.addTab(tab_info, t("summary_tab_global", lang))

        if s['copied']:
            local_paths = [lp for lp, rel in s['copied']]
            tabs.addTab(
                FileGrid(local_paths, base_path=base_path),
                f"{t('summary_tab_copied', lang)} ({len(s['copied'])})"
            )

        if s['deleted_pc']:
            tabs.addTab(
                FileGrid(s['deleted_pc'], base_path=base_path),
                f"{t('summary_tab_deleted_pc', lang)} ({len(s['deleted_pc'])})"
            )

        if s['deleted_tel']:
            tab_del    = QtWidgets.QWidget()
            del_layout = QtWidgets.QVBoxLayout(tab_del)
            lbl_note   = QtWidgets.QLabel(t("summary_del_tel_note", lang))
            lbl_note.setWordWrap(True)
            lbl_note.setStyleSheet("font-style:italic; color:#777; padding:4px;")
            list_w = QtWidgets.QListWidget()
            for lp, rp in s['deleted_tel']:
                list_w.addItem(rp)
            del_layout.addWidget(lbl_note)
            del_layout.addWidget(list_w)
            tabs.addTab(tab_del, f"{t('summary_tab_deleted_tel', lang)} ({len(s['deleted_tel'])})")

        btn_close = QtWidgets.QPushButton(t("close", lang))
        btn_close.setStyleSheet(
            "background-color:#2ecc71; color:white; font-weight:bold; padding:6px;"
        )
        btn_close.clicked.connect(self.accept)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(tabs)
        layout.addWidget(btn_close)
        self.setLayout(layout)
