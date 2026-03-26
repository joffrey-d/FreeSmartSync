import os
import sys
import subprocess
from PyQt5 import QtWidgets, QtCore, QtGui

from modules.i18n import t
from modules.config import save_config, load_config
from modules.worker import Worker
from modules.dialogs import DeleteConfirmDialog, SummaryDialog
from modules.adb_explorer import ADBExplorer

APP_VERSION = "v0.8.5.3"


class AboutDialog(QtWidgets.QDialog):
    """Fenêtre À propos de FreeSmartSync Beta."""

    def __init__(self, lang="fr", device_id=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(
            f"À propos — FreeSmartSync Beta {APP_VERSION}" if lang == "fr"
            else f"About — FreeSmartSync Beta {APP_VERSION}"
        )
        self.setMinimumSize(560, 580)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 15, 20, 15)

        # Titre
        title = QtWidgets.QLabel("FreeSmartSync Beta")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size:24px; font-weight:bold; color:#2c3e50; margin:8px;")

        version = QtWidgets.QLabel(APP_VERSION)
        version.setAlignment(QtCore.Qt.AlignCenter)
        version.setStyleSheet("font-size:15px; color:#2980b9; margin-bottom:4px;")

        subtitle = QtWidgets.QLabel(
            "Synchronisation bidirectionnelle Android ↔ Linux" if lang == "fr"
            else "Bidirectional sync Android ↔ Linux"
        )
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        subtitle.setStyleSheet("font-size:14px; color:#7f8c8d; margin-bottom:8px;")

        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        sep.setStyleSheet("color:#ecf0f1; margin:4px 0;")

        # ── Infos système ──
        sys_group = QtWidgets.QGroupBox(
            "🖥️  Informations système" if lang == "fr" else "🖥️  System information"
        )
        sys_group.setStyleSheet(
            "QGroupBox { font-size:14px; font-weight:bold; padding-top:8px; }"
            "QGroupBox::title { subcontrol-origin:margin; left:10px; }"
        )
        sys_layout = QtWidgets.QFormLayout()
        sys_layout.setSpacing(8)
        sys_layout.setContentsMargins(12, 10, 12, 10)

        def make_val(text):
            l = QtWidgets.QLabel(text)
            l.setStyleSheet("font-size:13px; font-weight:normal;")
            l.setWordWrap(True)
            return l

        py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        sys_layout.addRow(make_val("Python :"), make_val(py_ver))

        try:
            from PyQt5.Qt import PYQT_VERSION_STR
            pyqt_ver = PYQT_VERSION_STR
        except Exception:
            pyqt_ver = "?"
        sys_layout.addRow(make_val("PyQt5 :"), make_val(pyqt_ver))

        try:
            adb_r = subprocess.run(["adb", "version"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            adb_ver = adb_r.stdout.splitlines()[0].replace(
                "Android Debug Bridge version ", "") if adb_r.returncode == 0 else "Non détecté"
        except Exception:
            adb_ver = "Non détecté"
        sys_layout.addRow(make_val("ADB :"), make_val(adb_ver))

        try:
            distrib = "Linux"
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        distrib = line.split("=", 1)[1].strip().strip('"')
                        break
        except Exception:
            pass
        sys_layout.addRow(
            make_val("Système :" if lang == "fr" else "System :"),
            make_val(distrib)
        )

        if device_id:
            try:
                brand = subprocess.run(
                    ["adb", "-s", device_id, "shell", "getprop ro.product.manufacturer"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                ).stdout.strip()
                model = subprocess.run(
                    ["adb", "-s", device_id, "shell", "getprop ro.product.model"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                ).stdout.strip()
                phone_str = f"{brand} {model}".strip() or device_id
            except Exception:
                phone_str = device_id
        else:
            phone_str = "Non connecté" if lang == "fr" else "Not connected"
        sys_layout.addRow(
            make_val("Smartphone :" if lang == "fr" else "Phone :"),
            make_val(phone_str)
        )
        sys_group.setLayout(sys_layout)

        # ── Crédits ──
        credits_group = QtWidgets.QGroupBox(
            "👥  Crédits" if lang == "fr" else "👥  Credits"
        )
        credits_group.setStyleSheet(
            "QGroupBox { font-size:14px; font-weight:bold; padding-top:8px; }"
            "QGroupBox::title { subcontrol-origin:margin; left:10px; }"
        )
        credits_layout = QtWidgets.QVBoxLayout()
        credits_layout.setContentsMargins(12, 10, 12, 10)
        credits_layout.setSpacing(8)

        if lang == "fr":
            credits_html = (
                "<b style='font-size:14px'>💡 Idée originale & conception : Joffrey</b><br>"
                "<span style='font-size:13px; color:#555;'>"
                "Vision du projet, choix fonctionnels, tests terrain, "
                "direction du développement et retours utilisateur.</span><br><br>"
                "<b style='font-size:14px'>🤖 Développement intégral : Claude (Anthropic)</b><br>"
                "<span style='font-size:13px; color:#555;'>"
                "L'ensemble du code source a été généré par intelligence artificielle "
                "sur la base des spécifications et retours de Joffrey.</span><br><br>"
                "<b style='font-size:14px'>📜 Licence : GPL v3</b><br>"
                "<span style='font-size:13px; color:#555;'>"
                "Logiciel libre et open source — code source disponible et auditable.</span>"
            )
        else:
            credits_html = (
                "<b style='font-size:14px'>💡 Original idea & conception: Joffrey</b><br>"
                "<span style='font-size:13px; color:#555;'>"
                "Project vision, functional choices, field testing, "
                "development direction and user feedback.</span><br><br>"
                "<b style='font-size:14px'>🤖 Full development: Claude (Anthropic)</b><br>"
                "<span style='font-size:13px; color:#555;'>"
                "The entire source code was generated by artificial intelligence "
                "based on Joffrey's specifications and feedback.</span><br><br>"
                "<b style='font-size:14px'>📜 License: GPL v3</b><br>"
                "<span style='font-size:13px; color:#555;'>"
                "Free and open source software — source code available and auditable.</span>"
            )
        credits_lbl = QtWidgets.QLabel(credits_html)
        credits_lbl.setWordWrap(True)
        credits_lbl.setStyleSheet("font-size:13px; padding:4px;")
        credits_layout.addWidget(credits_lbl)
        credits_group.setLayout(credits_layout)

        # ── Sécurité ADB ──
        security_group = QtWidgets.QGroupBox(
            "🔒  Sécurité du débogage USB" if lang == "fr"
            else "🔒  USB debugging security"
        )
        security_group.setStyleSheet(
            "QGroupBox { font-size:14px; font-weight:bold; padding-top:8px; }"
            "QGroupBox::title { subcontrol-origin:margin; left:10px; }"
        )
        security_layout = QtWidgets.QVBoxLayout()
        security_layout.setContentsMargins(12, 10, 12, 10)

        if lang == "fr":
            sec_html = (
                "À chaque fermeture de FreeSmartSync, "
                "un <b>message de rappel</b> s'affiche pour vous inviter à "
                "<b>désactiver manuellement le débogage USB</b> sur votre téléphone.<br><br>"
                "⚠️ Pour chaque nouvelle session de synchronisation, vous devrez "
                "<b>réactiver</b> le débogage USB sur votre téléphone.<br><br>"
                "<i>Cette approche garantit que votre téléphone n'est jamais "
                "accessible à votre insu via un câble USB.</i>"
            )
        else:
            sec_html = (
                "Each time FreeSmartSync closes, "
                "a <b>reminder message</b> appears asking you to "
                "<b>manually disable USB debugging</b> on your phone.<br><br>"
                "⚠️ For each new sync session, you will need to "
                "<b>re-enable</b> USB debugging on your phone.<br><br>"
                "<i>This approach ensures your phone is never "
                "accessible without your knowledge via a USB cable.</i>"
            )
        security_lbl = QtWidgets.QLabel(sec_html)
        security_lbl.setWordWrap(True)
        security_lbl.setStyleSheet(
            "font-size:13px; padding:8px; background:#eafaf1; border-radius:4px;"
        )
        security_layout.addWidget(security_lbl)
        security_group.setLayout(security_layout)

        # ── Disclaimer ──
        disclaimer = QtWidgets.QLabel(
            "⚠️  Logiciel fourni sans garantie. Utilisation à vos risques et périls."
            if lang == "fr" else
            "⚠️  Software provided without warranty. Use at your own risk."
        )
        disclaimer.setWordWrap(True)
        disclaimer.setStyleSheet(
            "font-size:13px; color:#e74c3c; background:#fdf2f2; "
            "border:1px solid #fadbd8; border-radius:4px; padding:8px;"
        )

        btn_close = QtWidgets.QPushButton("✅ Fermer" if lang == "fr" else "✅ Close")
        btn_close.setMinimumHeight(38)
        btn_close.setStyleSheet(
            "background-color:#2ecc71; color:white; font-weight:bold; "
            "font-size:14px; padding:6px;"
        )
        btn_close.clicked.connect(self.accept)

        layout.addWidget(title)
        layout.addWidget(version)
        layout.addWidget(subtitle)
        layout.addWidget(sep)
        layout.addWidget(sys_group)
        layout.addWidget(credits_group)
        layout.addWidget(security_group)
        layout.addWidget(disclaimer)
        layout.addStretch()

        scroll.setWidget(container)

        outer = QtWidgets.QVBoxLayout()
        outer.addWidget(scroll)
        outer.addWidget(btn_close)
        self.setLayout(outer)


class MainWindow(QtWidgets.QWidget):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config           = config
        self.lang             = config.get("lang", "fr")
        self.local_base       = config.get("local_base", "")
        self.folders          = config.get("folders", [])
        self.is_running       = False
        self._active_device_id = None  # Mémorisé au lancement sync

        self._build_ui()
        self._setup_tray()
        self._connect_signals()
        self.detect_devices()
        self.showMaximized()

    def _get_icon_path(self, name="icon.png"):
        return os.path.join(os.path.dirname(__file__), "..", "assets", name)

    def _build_ui(self):
        self.setWindowTitle(f"FreeSmartSync Beta {APP_VERSION}")
        icon_path = self._get_icon_path()
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))

        self.scan_bar   = QtWidgets.QProgressBar()
        self.copy_bar   = QtWidgets.QProgressBar()
        self.status     = QtWidgets.QLabel(t("main_status_ready", self.lang))
        self.status.setStyleSheet("font-size:13px;")
        self.file_label = QtWidgets.QLabel(t("main_file", self.lang))
        self.file_label.setStyleSheet("font-size:12px; color:#555;")
        self.dest_label = QtWidgets.QLabel(self.local_base)
        self.dest_label.setWordWrap(True)
        self.dest_label.setStyleSheet("font-size:12px; color:#555;")

        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("font-family: monospace; font-size:12px;")

        self.device_combo = QtWidgets.QComboBox()
        self.device_combo.setMinimumWidth(240)
        self.device_combo.setStyleSheet("font-size:13px;")
        self.detect_btn = QtWidgets.QPushButton(t("main_refresh", self.lang))
        self.detect_btn.setStyleSheet("font-size:13px;")
        self.detect_btn.clicked.connect(self.detect_devices)

        self.folder_list = QtWidgets.QListWidget()
        self.folder_list.addItems(self.folders)
        self.folder_list.setAlternatingRowColors(True)
        self.folder_list.setStyleSheet("font-size:13px;")

        self.add_btn    = QtWidgets.QPushButton(t("main_add", self.lang))
        self.remove_btn = QtWidgets.QPushButton(t("main_remove", self.lang))
        self.dest_btn   = QtWidgets.QPushButton(t("main_dest_btn", self.lang))
        self.start_btn  = QtWidgets.QPushButton(t("main_start", self.lang))
        self.pause_btn  = QtWidgets.QPushButton(t("main_pause", self.lang))
        self.resume_btn = QtWidgets.QPushButton(t("main_resume", self.lang))
        self.stop_btn   = QtWidgets.QPushButton(t("main_stop", self.lang))
        self.quit_btn   = QtWidgets.QPushButton(t("main_quit", self.lang))
        self.about_btn  = QtWidgets.QPushButton(
            "ℹ️ À propos" if self.lang == "fr" else "ℹ️ About"
        )
        self.uninstall_btn = QtWidgets.QPushButton(
            "🗑️ Désinstaller" if self.lang == "fr" else "🗑️ Uninstall"
        )

        for btn in (self.add_btn, self.remove_btn, self.dest_btn,
                    self.pause_btn, self.resume_btn, self.quit_btn):
            btn.setStyleSheet("font-size:13px; padding:5px;")

        self.start_btn.setStyleSheet(
            "background-color:#2ecc71; color:white; font-weight:bold; font-size:14px; padding:6px;"
        )
        self.stop_btn.setStyleSheet(
            "background-color:#e74c3c; color:white; font-weight:bold; font-size:14px; padding:6px;"
        )
        self.about_btn.setStyleSheet("background-color:#95a5a6; color:white; font-size:13px;")
        self.uninstall_btn.setStyleSheet(
            "background-color:#c0392b; color:white; font-weight:bold; font-size:13px;"
        )
        self.pause_btn.setStyleSheet("background-color:#f1c40f; font-size:13px; padding:5px;")
        self.resume_btn.setStyleSheet(
            "background-color:#3498db; color:white; font-size:13px; padding:5px;"
        )

        layout = QtWidgets.QVBoxLayout()

        top_row = QtWidgets.QHBoxLayout()
        device_row = QtWidgets.QHBoxLayout()
        device_row.addWidget(QtWidgets.QLabel(t("main_device", self.lang)))
        device_row.addWidget(self.device_combo)
        device_row.addWidget(self.detect_btn)
        top_row.addLayout(device_row)
        top_row.addStretch()
        top_row.addWidget(self.about_btn)
        layout.addLayout(top_row)

        scan_lbl = QtWidgets.QLabel(t("main_scan", self.lang))
        scan_lbl.setStyleSheet("font-size:13px;")
        copy_lbl = QtWidgets.QLabel(t("main_copy", self.lang))
        copy_lbl.setStyleSheet("font-size:13px;")

        layout.addWidget(scan_lbl)
        layout.addWidget(self.scan_bar)
        layout.addWidget(copy_lbl)
        layout.addWidget(self.copy_bar)
        layout.addWidget(self.status)
        layout.addWidget(self.file_label)

        folders_lbl = QtWidgets.QLabel(t("main_folders", self.lang))
        folders_lbl.setStyleSheet("font-size:13px; font-weight:bold;")
        layout.addWidget(folders_lbl)
        layout.addWidget(self.folder_list)

        btn_folder = QtWidgets.QHBoxLayout()
        btn_folder.addWidget(self.add_btn)
        btn_folder.addWidget(self.remove_btn)
        layout.addLayout(btn_folder)

        dest_lbl = QtWidgets.QLabel(t("main_dest", self.lang))
        dest_lbl.setStyleSheet("font-size:13px; font-weight:bold;")
        layout.addWidget(dest_lbl)
        layout.addWidget(self.dest_label)
        layout.addWidget(self.dest_btn)
        layout.addWidget(self.log)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.resume_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.quit_btn)
        layout.addLayout(btn_layout)

        bottom_row = QtWidgets.QHBoxLayout()
        bottom_row.addStretch()
        bottom_row.addWidget(self.uninstall_btn)
        layout.addLayout(bottom_row)

        self.setLayout(layout)

    def _setup_tray(self):
        if not QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
            self.tray = None
            return

        icon_path = self._get_icon_path()
        icon = QtGui.QIcon(icon_path) if os.path.exists(icon_path) else QtGui.QIcon()

        self.tray = QtWidgets.QSystemTrayIcon(icon, self)
        self.tray.setToolTip(f"FreeSmartSync Beta {APP_VERSION}")

        tray_menu = QtWidgets.QMenu()
        show_action = tray_menu.addAction(
            "🖥️ Afficher FreeSmartSync" if self.lang == "fr" else "🖥️ Show FreeSmartSync"
        )
        show_action.triggered.connect(self._show_from_tray)

        self.sync_tray_action = tray_menu.addAction(
            "🔄 Lancer une synchronisation" if self.lang == "fr" else "🔄 Start sync"
        )
        self.sync_tray_action.triggered.connect(self._sync_from_tray)

        tray_menu.addSeparator()
        quit_action = tray_menu.addAction("🚪 Quitter" if self.lang == "fr" else "🚪 Quit")
        quit_action.triggered.connect(self._quit_app)

        self.tray.setContextMenu(tray_menu)
        self.tray.activated.connect(self._tray_activated)
        self.tray.show()

        self._tray_anim_index  = 0
        self._tray_anim_frames = [
            self._get_icon_path("icon_anim1.png"),
            self._get_icon_path("icon_anim2.png"),
            self._get_icon_path("icon_anim3.png"),
            self._get_icon_path("icon_anim4.png"),
        ]
        self._tray_anim_timer = QtCore.QTimer()
        self._tray_anim_timer.timeout.connect(self._animate_tray)

    def _animate_tray(self):
        if self.tray is None: return
        frame_path = self._tray_anim_frames[self._tray_anim_index]
        if os.path.exists(frame_path):
            self.tray.setIcon(QtGui.QIcon(frame_path))
        self._tray_anim_index = (self._tray_anim_index + 1) % len(self._tray_anim_frames)

    def _start_tray_animation(self):
        if self.tray:
            self._tray_anim_timer.start(400)
            self.tray.setToolTip(
                "FreeSmartSync — Sync en cours..." if self.lang == "fr"
                else "FreeSmartSync — Syncing..."
            )

    def _stop_tray_animation(self):
        if self.tray:
            self._tray_anim_timer.stop()
            icon_path = self._get_icon_path()
            if os.path.exists(icon_path):
                self.tray.setIcon(QtGui.QIcon(icon_path))
            self.tray.setToolTip(f"FreeSmartSync Beta {APP_VERSION}")

    def _tray_activated(self, reason):
        """Clic gauche sur icône tray → toggle affichage/masquage."""
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            if self.isHidden() or self.isMinimized():
                self._show_from_tray()
            else:
                # Fenêtre visible → on la cache dans le tray
                self._hide_to_tray()

    def _show_from_tray(self):
        """Réaffiche la fenêtre depuis le tray — gère hidden ET minimized."""
        if self.isHidden():
            self.show()
        if self.isMinimized():
            self.setWindowState(
                self.windowState() & ~QtCore.Qt.WindowMinimized
                | QtCore.Qt.WindowActive
            )
        self.showMaximized()
        self.raise_()
        self.activateWindow()
        # Force le focus sur KDE/GNOME
        QtCore.QTimer.singleShot(50, self.activateWindow)

    def _sync_from_tray(self):
        self._show_from_tray()
        self.start()

    def _quit_app(self):
        self._show_usb_reminder()
        if self.tray:
            self.tray.hide()
        QtWidgets.QApplication.quit()

    def _connect_signals(self):
        self.add_btn.clicked.connect(self.add_folder)
        self.remove_btn.clicked.connect(self.remove_folder)
        self.dest_btn.clicked.connect(self.choose_dest)
        self.start_btn.clicked.connect(self.start)
        self.pause_btn.clicked.connect(self.pause)
        self.resume_btn.clicked.connect(self.resume)
        self.stop_btn.clicked.connect(self.stop)
        self.quit_btn.clicked.connect(self.close)
        self.about_btn.clicked.connect(self.show_about)
        self.uninstall_btn.clicked.connect(self.uninstall)
        self.folder_list.model().rowsInserted.connect(self._auto_save)
        self.folder_list.model().rowsRemoved.connect(self._auto_save)

    def changeEvent(self, event):
        """Intercepte la minimisation → cache dans le tray."""
        super().changeEvent(event)
        if (event.type() == QtCore.QEvent.WindowStateChange
                and self.isMinimized()
                and self.tray is not None):
            # Cache la fenêtre après que Qt ait terminé la minimisation
            QtCore.QTimer.singleShot(150, self._hide_to_tray)

    def _hide_to_tray(self):
        """Cache la fenêtre et affiche une notification tray."""
        self.hide()
        if self.tray:
            self.tray.showMessage(
                "FreeSmartSync Beta",
                "FreeSmartSync est dans la barre système. Cliquez sur l'icône pour le rouvrir."
                if self.lang == "fr" else
                "FreeSmartSync is in the system tray. Click the icon to reopen it.",
                QtWidgets.QSystemTrayIcon.Information,
                2500
            )

    def _show_usb_reminder(self):
        """Affiche un rappel pour désactiver manuellement le débogage USB."""
        dlg = QtWidgets.QMessageBox(self)
        dlg.setWindowTitle(
            "🔒 Sécurité — Débogage USB" if self.lang == "fr"
            else "🔒 Security — USB Debugging"
        )
        dlg.setIcon(QtWidgets.QMessageBox.Information)

        if self.lang == "fr":
            msg = (
                "<p style='font-size:14px; font-weight:bold;'>"
                "🔒 N'oubliez pas de désactiver le débogage USB !</p>"
                "<p style='font-size:14px;'>"
                "Pour protéger votre téléphone, pensez à désactiver "
                "le <b>débogage USB</b> dans les options développeur.<br><br>"
                "Sur votre téléphone :<br>"
                "<b>Paramètres → Options développeur → Débogage USB → Désactiver</b><br><br>"
                "<i>Cela empêche tout accès non autorisé à vos données via un câble USB.</i>"
                "</p>"
            )
        else:
            msg = (
                "<p style='font-size:14px; font-weight:bold;'>"
                "🔒 Remember to disable USB Debugging!</p>"
                "<p style='font-size:14px;'>"
                "To protect your phone, please disable "
                "<b>USB debugging</b> in the developer options.<br><br>"
                "On your phone:<br>"
                "<b>Settings → Developer options → USB Debugging → Disable</b><br><br>"
                "<i>This prevents unauthorized access to your data via a USB cable.</i>"
                "</p>"
            )

        dlg.setText(msg)
        dlg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        dlg.button(QtWidgets.QMessageBox.Ok).setText(
            "✅ Compris, je vais le désactiver" if self.lang == "fr"
            else "✅ Got it, I'll disable it"
        )
        dlg.setStyleSheet("QLabel { font-size:14px; min-width: 420px; }")
        dlg.exec_()

    def closeEvent(self, event):
        if self.is_running:
            dlg = QtWidgets.QMessageBox(self)
            dlg.setWindowTitle(t("close_warning_title", self.lang))
            dlg.setIcon(QtWidgets.QMessageBox.Warning)
            dlg.setText(t("close_warning_text", self.lang))
            dlg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            dlg.button(QtWidgets.QMessageBox.Ok).setText(t("close_warning_btn", self.lang))
            dlg.exec_()
            event.ignore()
        else:
            self._show_usb_reminder()
            if self.tray:
                self.tray.hide()
            event.accept()

    def _auto_save(self):
        folders = [self.folder_list.item(i).text() for i in range(self.folder_list.count())]
        self.config["folders"] = folders
        save_config(self.config)
        self.log.append("💾 Configuration sauvegardée.")

    def detect_devices(self):
        self.device_combo.clear()
        result = subprocess.run(
            ["adb", "devices"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        devices = []
        for line in result.stdout.splitlines()[1:]:
            line = line.strip()
            if line and "device" in line and "offline" not in line:
                device_id = line.split()[0]
                # Récupère marque + modèle
                try:
                    brand = subprocess.run(
                        ["adb", "-s", device_id, "shell", "getprop ro.product.manufacturer"],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3
                    ).stdout.strip()
                    model = subprocess.run(
                        ["adb", "-s", device_id, "shell", "getprop ro.product.model"],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3
                    ).stdout.strip()
                    label = f"{brand} {model} ({device_id})" if brand else device_id
                except Exception:
                    label = device_id
                devices.append(device_id)
                self.device_combo.addItem(label, device_id)

        if devices:
            self.log.append(
                f"📱 {len(devices)} {t('log_device_found', self.lang)} {', '.join(devices)}"
            )
        else:
            self.log.append(t("log_no_device", self.lang))

    def _get_current_device_id(self):
        """Retourne l'ID ADB du device sélectionné (data), pas le label affiché."""
        idx = self.device_combo.currentIndex()
        if idx >= 0:
            data = self.device_combo.itemData(idx)
            return data if data else self.device_combo.currentText()
        return ""

    def add_folder(self):
        device_id = self._get_current_device_id()
        if not device_id:
            QtWidgets.QMessageBox.warning(
                self, t("error", self.lang), "Aucun smartphone sélectionné."
            )
            return
        explorer = ADBExplorer(device_id, self)
        if explorer.exec_():
            path = explorer.selected_path()
            if path:
                self.folder_list.addItem(path)

    def remove_folder(self):
        for item in self.folder_list.selectedItems():
            self.folder_list.takeItem(self.folder_list.row(item))

    def choose_dest(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, t("dest_choose", self.lang))
        if folder:
            self.local_base = folder
            self.dest_label.setText(folder)
            self.config["local_base"] = folder
            save_config(self.config)
            self.log.append("💾 Configuration sauvegardée.")

    def show_about(self):
        device_id = self._get_current_device_id() or None
        dlg = AboutDialog(lang=self.lang, device_id=device_id, parent=self)
        dlg.exec_()

    def uninstall(self):
        import shutil
        lang = self.lang

        dlg1 = QtWidgets.QMessageBox(self)
        dlg1.setWindowTitle(
            "🗑️ Désinstaller FreeSmartSync Beta" if lang == "fr"
            else "🗑️ Uninstall FreeSmartSync Beta"
        )
        dlg1.setIcon(QtWidgets.QMessageBox.Warning)
        dlg1.setText(
            "<b>Êtes-vous sûr de vouloir désinstaller FreeSmartSync Beta ?</b><br><br>"
            "• Le logiciel FreeSmartSync sera supprimé<br>"
            "• Le raccourci dans le menu d'applications sera supprimé<br><br>"
            "<b>Vos données de sauvegarde ne seront PAS supprimées.</b>"
            if lang == "fr" else
            "<b>Are you sure you want to uninstall FreeSmartSync Beta?</b><br><br>"
            "• FreeSmartSync software will be removed<br>"
            "• Application menu shortcut will be removed<br><br>"
            "<b>Your backup data will NOT be deleted.</b>"
        )
        dlg1.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        dlg1.button(QtWidgets.QMessageBox.Yes).setText(
            "Oui, désinstaller" if lang == "fr" else "Yes, uninstall"
        )
        dlg1.button(QtWidgets.QMessageBox.No).setText("Annuler" if lang == "fr" else "Cancel")
        dlg1.setDefaultButton(QtWidgets.QMessageBox.No)
        if dlg1.exec_() != QtWidgets.QMessageBox.Yes:
            return

        delete_config = False
        dlg2 = QtWidgets.QMessageBox(self)
        dlg2.setWindowTitle("🗑️ Configuration")
        dlg2.setIcon(QtWidgets.QMessageBox.Question)
        dlg2.setText(
            "Voulez-vous également supprimer votre configuration ?<br>"
            "(dossiers sélectionnés, répertoire de sauvegarde)"
            if lang == "fr" else
            "Do you also want to delete your configuration?<br>"
            "(selected folders, backup directory)"
        )
        dlg2.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        dlg2.button(QtWidgets.QMessageBox.Yes).setText(
            "Oui, tout supprimer" if lang == "fr" else "Yes, delete all"
        )
        dlg2.button(QtWidgets.QMessageBox.No).setText(
            "Non, garder ma config" if lang == "fr" else "No, keep my config"
        )
        if dlg2.exec_() == QtWidgets.QMessageBox.Yes:
            delete_config = True

        install_dir  = os.path.expanduser("~/.local/share/freesmartsync")
        desktop_file = os.path.expanduser("~/.local/share/applications/freesmartsync.desktop")
        config_dir   = os.path.expanduser("~/.config/freesmartsync")

        try:
            if os.path.exists(install_dir):  shutil.rmtree(install_dir)
            if os.path.exists(desktop_file): os.remove(desktop_file)
            if delete_config and os.path.exists(config_dir): shutil.rmtree(config_dir)
            subprocess.run(
                ["update-desktop-database", os.path.expanduser("~/.local/share/applications/")],
                capture_output=True
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Erreur" if lang == "fr" else "Error",
                f"{'Erreur lors de la désinstallation' if lang == 'fr' else 'Uninstall error'}:\n{e}"
            )
            return

        QtWidgets.QMessageBox.information(
            self,
            "✅ Désinstallé" if lang == "fr" else "✅ Uninstalled",
            "FreeSmartSync Beta a été désinstallé avec succès.\n\nMerci de l'avoir utilisé ! 👋"
            if lang == "fr" else
            "FreeSmartSync Beta has been successfully uninstalled.\n\nThank you for using it! 👋"
        )
        if self.tray:
            self.tray.hide()
        QtWidgets.QApplication.quit()

    def set_ui_running(self, running: bool):
        self.is_running = running
        self.start_btn.setEnabled(not running)
        self.detect_btn.setEnabled(not running)
        self.add_btn.setEnabled(not running)
        self.remove_btn.setEnabled(not running)
        self.dest_btn.setEnabled(not running)
        self.device_combo.setEnabled(not running)
        self.folder_list.setEnabled(not running)
        if self.tray:
            self.sync_tray_action.setEnabled(not running)

    def show_confirm_dialog(self, files_to_delete):
        dlg      = DeleteConfirmDialog(files_to_delete, lang=self.lang, parent=self)
        accepted = dlg.exec_() == QtWidgets.QDialog.Accepted
        self.worker.confirm_result(accepted)

    def show_summary_dialog(self, summary):
        if not summary:
            return
        if not (summary.get("copied") or summary.get("deleted_pc") or summary.get("deleted_tel")):
            return
        dlg = SummaryDialog(summary, base_path=self.local_base, lang=self.lang, parent=self)
        dlg.exec_()

    def start(self):
        device_id = self._get_current_device_id()
        if not device_id:
            QtWidgets.QMessageBox.warning(
                self, t("error", self.lang), "Aucun smartphone sélectionné."
            )
            return

        self._active_device_id = device_id  # Mémorise pour désactivation ADB
        self.scan_bar.setValue(0)
        self.copy_bar.setValue(0)
        self.status.setText("Démarrage...")
        self.file_label.setText(t("main_file", self.lang))

        folders = [self.folder_list.item(i).text() for i in range(self.folder_list.count())]

        self.worker = Worker(folders, self.local_base, device_id, self.lang)
        self.worker.scan_progress.connect(self.scan_bar.setValue)
        self.worker.progress.connect(self.copy_bar.setValue)
        self.worker.status.connect(self.status.setText)
        self.worker.current_file.connect(self.file_label.setText)
        self.worker.log.connect(self.log.append)
        self.worker.done.connect(self.on_done)
        self.worker.request_confirm.connect(self.show_confirm_dialog)

        self.set_ui_running(True)
        self._start_tray_animation()
        self.worker.start()

    def on_done(self, summary):
        self._stop_tray_animation()
        self.set_ui_running(False)
        self.status.setText("Terminé ✅")

        if self.tray and summary:
            copied  = len(summary.get("copied", []))
            deleted = len(summary.get("deleted_pc", [])) + len(summary.get("deleted_tel", []))
            errors  = summary.get("errors", 0)
            msg = (
                f"{copied} fichier(s) copié(s), {deleted} supprimé(s)"
                + (f", {errors} erreur(s)" if errors else "")
                if self.lang == "fr" else
                f"{copied} file(s) copied, {deleted} deleted"
                + (f", {errors} error(s)" if errors else "")
            )
            self.tray.showMessage(
                "✅ FreeSmartSync — " + (
                    "Synchronisation terminée" if self.lang == "fr" else "Sync complete"
                ),
                msg, QtWidgets.QSystemTrayIcon.Information, 4000
            )
        self.show_summary_dialog(summary)

    def pause(self):
        if hasattr(self, "worker"): self.worker.pause()

    def resume(self):
        if hasattr(self, "worker"): self.worker.resume()

    def stop(self):
        if hasattr(self, "worker"): self.worker.stop()
