# modules/wizard.py
# Assistant de premier lancement FreeSmartSync v0.8.5.1

import os
import subprocess
from PyQt5 import QtWidgets, QtCore, QtGui

from modules.i18n import t, FOLDER_DESCRIPTIONS, USB_DEBUG_STEPS
from modules.deps import detect_distrib, get_deps_status, install_deps, all_deps_ok
from modules.config import get_free_space, format_size, save_config
from modules.profiles import load_profiles, save_profile, get_profile

FONT_SIZE_TITLE   = "font-size:22px;"
FONT_SIZE_NORMAL  = "font-size:14px;"
FONT_SIZE_SMALL   = "font-size:13px;"
FONT_SIZE_NOTE    = "font-size:12px;"


def _set_icon(widget):
    import os
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    p = os.path.join(base, 'assets', 'icon.png')
    if os.path.exists(p):
        from PyQt5 import QtGui
        widget.setWindowIcon(QtGui.QIcon(p))


class WizardWindow(QtWidgets.QDialog):
    # Icone appliquée dans _build_ui
    """
    Fenêtre principale du wizard — 8 écrans.
    0: Langue
    1: Accueil (présentation FreeSmartSync)
    2: Dépendances (avec disclaimer en haut)
    3: Procédure débogage USB (AVANT de brancher)
    4: Connexion USB animée (APRÈS la procédure)
    5: Choix des dossiers
    6: Destination
    7: Résumé
    """
    wizard_done = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang   = "fr"
        self.config = {}

        self.setWindowTitle("FreeSmartSync — Installation")
        _set_icon(self)
        self.setMinimumSize(750, 600)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        from PyQt5 import QtWidgets as _Qw
        _app = _Qw.QApplication.instance()
        if _app and not _app.windowIcon().isNull():
            self.setWindowIcon(_app.windowIcon())

        self.stack = QtWidgets.QStackedWidget()

        self.btn_back   = QtWidgets.QPushButton()
        self.btn_next   = QtWidgets.QPushButton()
        self.btn_cancel = QtWidgets.QPushButton()

        self.btn_back.setMinimumWidth(130)
        self.btn_back.setMinimumHeight(38)
        self.btn_next.setMinimumWidth(170)
        self.btn_next.setMinimumHeight(38)
        self.btn_next.setStyleSheet(
            "background-color:#2ecc71; color:white; font-weight:bold; "
            "font-size:14px; padding:8px;"
        )
        self.btn_back.setStyleSheet("font-size:13px; padding:6px;")
        self.btn_cancel.setStyleSheet("font-size:13px; padding:6px;")

        self.btn_back.clicked.connect(self.go_back)
        self.btn_next.clicked.connect(self.go_next)
        self.btn_cancel.clicked.connect(self.reject)

        nav = QtWidgets.QHBoxLayout()
        nav.addWidget(self.btn_cancel)
        nav.addStretch()
        nav.addWidget(self.btn_back)
        nav.addWidget(self.btn_next)

        self.progress_label = QtWidgets.QLabel()
        self.progress_label.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_label.setStyleSheet("color:#888; font-size:13px;")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.stack)
        layout.addWidget(self.progress_label)
        layout.addLayout(nav)
        self.setLayout(layout)

        self.pages = []
        self._build_pages()
        self.current = 0
        self._show_page(0)

    def _build_pages(self):
        self.page_lang     = PageLanguage(self)
        self.page_welcome  = PageWelcome(self)
        self.page_deps     = PageDeps(self)
        self.page_phone    = PagePhone(self)      # idx 3 — procédure débogage
        self.page_usb      = PageUSBConnect(self) # idx 4 — brancher tel
        self.page_profiles = PageProfiles(self)   # idx 5 — gestion profils
        self.page_folders  = PageFolders(self)    # idx 6
        self.page_dest     = PageDest(self)       # idx 7
        self.page_summary  = PageSummary(self)    # idx 8

        self.pages = [
            self.page_lang,     # 0
            self.page_welcome,  # 1
            self.page_deps,     # 2
            self.page_phone,    # 3
            self.page_usb,      # 4
            self.page_profiles, # 5 — NOUVEAU
            self.page_folders,  # 6
            self.page_dest,     # 7
            self.page_summary,  # 8
        ]
        for p in self.pages:
            self.stack.addWidget(p)

    def _show_page(self, idx):
        self.current = idx
        self.stack.setCurrentIndex(idx)
        total = len(self.pages)

        self.btn_back.setVisible(idx > 0)
        self.btn_cancel.setText(t("cancel", self.lang))
        self.btn_next.setText(t("finish", self.lang) if idx == total - 1 else t("next", self.lang))
        self.btn_back.setText(t("back", self.lang))
        self.progress_label.setText(f"{idx + 1} / {total}")

        # Refresh des pages
        if idx == 1: self.page_welcome.refresh(self.lang)
        if idx == 2: self.page_deps.refresh(self.lang)
        if idx == 3: self.page_phone.refresh(self.lang)
        if idx == 4: self.page_usb.refresh(self.lang)
        if idx == 5: self.page_profiles.refresh(self.lang)
        if idx == 6:
            device_id = self.page_usb.get_device_id() or self.config.get("device_id")
            self.page_folders.refresh(self.lang, device_id=device_id)
        if idx == 7: self.page_dest.refresh(self.lang)
        if idx == 8: self.page_summary.refresh(self.lang, self.config)

        # Timer USB actif seulement sur la page USB (idx=4)
        if idx == 4:
            self.page_usb.start_timers()
            self.btn_next.setEnabled(bool(self.page_usb.get_device_id()))
        else:
            self.page_usb.stop_timers()
            self.btn_next.setEnabled(True)

    def go_next(self):
        if self.current == 0:
            self.lang = self.page_lang.selected_lang()
            self.config["lang"] = self.lang

        elif self.current == 1:
            if not self.page_welcome.is_accepted():
                QtWidgets.QMessageBox.warning(
                    self, t("warning", self.lang),
                    "Vous devez accepter les conditions pour continuer.\n"
                    "You must accept the terms to continue."
                )
                return

        elif self.current == 2:
            if not all_deps_ok():
                QtWidgets.QMessageBox.warning(
                    self, t("warning", self.lang), t("deps_error", self.lang)
                )
                return

        elif self.current == 3:
            # Procédure débogage — pas de validation obligatoire, juste info
            pass

        elif self.current == 4:
            # Connexion USB — device_id obligatoire
            device_id = self.page_usb.get_device_id()
            if not device_id:
                QtWidgets.QMessageBox.warning(
                    self, t("warning", self.lang),
                    t("phone_connect_first", self.lang)
                )
                return
            self.config["device_id"] = device_id

        elif self.current == 5:
            # Profils — récupérer le profil sélectionné si applicable
            profile = self.page_profiles.get_selected_profile()
            if profile:
                self.config.update(profile["data"])
                self.config["active_profile"] = profile["name"]

        elif self.current == 6:
            folders = self.page_folders.get_folders()
            if not folders:
                QtWidgets.QMessageBox.warning(
                    self, t("warning", self.lang),
                    t("folders_none_warning", self.lang)
                )
                return
            self.config["folders"] = folders

        elif self.current == 7:
            dest = self.page_dest.get_dest()
            if not dest:
                QtWidgets.QMessageBox.warning(
                    self, t("warning", self.lang), t("dest_warning", self.lang)
                )
                return
            self.config["local_base"] = dest

        elif self.current == len(self.pages) - 1:
            self.config["setup_done"] = True
            save_config(self.config)
            self.wizard_done.emit(self.config)
            self.accept()
            return

        self._show_page(self.current + 1)

    def go_back(self):
        if self.current > 0:
            self._show_page(self.current - 1)


# ─────────────────────────────────────────────
# Page 1 : Langue
# ─────────────────────────────────────────────

class PageLanguage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setSpacing(20)

        title = QtWidgets.QLabel("Bienvenue / Welcome")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size:26px; font-weight:bold; margin:20px;")

        subtitle = QtWidgets.QLabel("Choisissez votre langue\nChoose your language")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        subtitle.setStyleSheet("font-size:16px; color:#555; margin-bottom:30px;")

        self.btn_fr = QtWidgets.QPushButton("🇫🇷  Français")
        self.btn_en = QtWidgets.QPushButton("🇬🇧  English")

        for btn in (self.btn_fr, self.btn_en):
            btn.setMinimumHeight(70)
            btn.setMinimumWidth(220)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton { font-size:18px; border:2px solid #ccc;
                              border-radius:10px; padding:12px; }
                QPushButton:checked { border-color:#2ecc71;
                                      background-color:#eafaf1; font-weight:bold; }
            """)

        self.btn_fr.setChecked(True)
        self.btn_fr.clicked.connect(lambda: self._select("fr"))
        self.btn_en.clicked.connect(lambda: self._select("en"))

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.setAlignment(QtCore.Qt.AlignCenter)
        btn_row.addWidget(self.btn_fr)
        btn_row.addSpacing(30)
        btn_row.addWidget(self.btn_en)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(btn_row)
        layout.addStretch()
        self.setLayout(layout)

    def _select(self, lang):
        self.btn_fr.setChecked(lang == "fr")
        self.btn_en.setChecked(lang == "en")

    def selected_lang(self):
        return "fr" if self.btn_fr.isChecked() else "en"


# ─────────────────────────────────────────────
# Page 2 : Accueil — Présentation FreeSmartSync + Disclaimer
# ─────────────────────────────────────────────

class PageWelcome(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = "fr"
        self._build()

    def _build(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(25, 15, 25, 15)

        self.title_lbl = QtWidgets.QLabel()
        self.title_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.title_lbl.setStyleSheet("font-size:22px; font-weight:bold; color:#2c3e50;")

        self.subtitle_lbl = QtWidgets.QLabel()
        self.subtitle_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.subtitle_lbl.setStyleSheet("font-size:15px; color:#2980b9; margin-bottom:8px;")

        # Présentation enrichie
        self.presentation_box = QtWidgets.QTextEdit()
        self.presentation_box.setReadOnly(True)
        self.presentation_box.setMinimumHeight(260)
        self.presentation_box.setStyleSheet(
            "background:#f8f9fa; border:1px solid #dee2e6; "
            "border-radius:6px; padding:12px; font-size:14px;"
        )

        # Avertissement ne pas brancher
        self.no_plug_lbl = QtWidgets.QLabel()
        self.no_plug_lbl.setWordWrap(True)
        self.no_plug_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.no_plug_lbl.setStyleSheet(
            "font-size:13px; color:#e67e22; font-weight:bold; "
            "background:#fef9e7; border:1px solid #e67e22; "
            "border-radius:6px; padding:10px; margin:4px 0;"
        )

        # Disclaimer
        self.disc_title_lbl = QtWidgets.QLabel()
        self.disc_title_lbl.setStyleSheet(
            "font-weight:bold; color:#e74c3c; font-size:13px; margin-top:6px;"
        )

        self.disc_text = QtWidgets.QTextEdit()
        self.disc_text.setReadOnly(True)
        self.disc_text.setMaximumHeight(110)
        self.disc_text.setStyleSheet(
            "background:#fdf2f2; border:1px solid #e74c3c; "
            "border-radius:4px; padding:8px; font-size:12px;"
        )

        self.check_accept = QtWidgets.QCheckBox()
        self.check_accept.setStyleSheet("font-size:13px; font-weight:bold; margin-top:6px;")

        layout.addWidget(self.title_lbl)
        layout.addWidget(self.subtitle_lbl)
        layout.addWidget(self.presentation_box)
        layout.addWidget(self.no_plug_lbl)
        layout.addWidget(self.disc_title_lbl)
        layout.addWidget(self.disc_text)
        layout.addWidget(self.check_accept)
        self.setLayout(layout)
        self.refresh("fr")

    def refresh(self, lang):
        self.lang = lang
        self.title_lbl.setText(t("welcome_title", lang))
        self.subtitle_lbl.setText(t("welcome_subtitle", lang))

        if lang == "fr":
            presentation = (
                "<p style='font-size:14px'><b>🔄 Synchronisation bidirectionnelle Android ↔ Linux</b><br>"
                "FreeSmartSync copie automatiquement vos fichiers du téléphone vers votre PC. "
                "Mais contrairement aux autres outils, il fonctionne dans les <b>deux sens</b> : "
                "supprimez une photo sur le PC → elle disparaît aussi du téléphone. "
                "Idéal pour trier vos photos directement depuis votre ordinateur !</p>"
                "<p style='font-size:14px'><b>🧠 Journal intelligent de synchronisation</b><br>"
                "Après chaque sync, FreeSmartSync mémorise l'état de vos fichiers. "
                "Il sait faire la différence entre un fichier <i>nouveau sur le téléphone</i> "
                "(→ à copier) et un fichier <i>supprimé volontairement sur le PC</i> "
                "(→ à supprimer du téléphone). Aucune confusion possible.</p>"
                "<p style='font-size:14px'><b>🔒 Rappel sécurité à la fermeture</b><br>"
                "À chaque fermeture de FreeSmartSync, un message vous rappelle "
                "de désactiver le débogage USB sur votre téléphone. "
                "Votre téléphone n'est jamais exposé à votre insu.</p>"
                "<p style='font-size:14px'><b>🛡️ Garde-fous contre les erreurs</b><br>"
                "Avant toute suppression massive, une fenêtre de confirmation affiche "
                "les miniatures des fichiers concernés. Un résumé visuel détaillé "
                "est affiché à la fin de chaque synchronisation.</p>"
                "<p style='font-size:14px'><b>📦 Compatible avec toutes les grandes distributions</b><br>"
                "Ubuntu, Debian, Fedora, Linux Mint, Zorin OS, Pop!_OS, "
                "Arch Linux, Manjaro, Mageia, openSUSE et plus.</p>"
            )
        else:
            presentation = (
                "<p style='font-size:14px'><b>🔄 Bidirectional sync Android ↔ Linux</b><br>"
                "FreeSmartSync automatically copies your files from phone to PC. "
                "But unlike other tools, it works <b>both ways</b>: "
                "delete a photo on PC → it disappears from the phone too. "
                "Perfect for sorting your photos directly from your computer!</p>"
                "<p style='font-size:14px'><b>🧠 Smart sync journal</b><br>"
                "After each sync, FreeSmartSync remembers the state of your files. "
                "It knows the difference between a <i>new file on the phone</i> "
                "(→ to copy) and a file <i>intentionally deleted on PC</i> "
                "(→ to delete from phone). No confusion possible.</p>"
                "<p style='font-size:14px'><b>🔒 Security reminder on close</b><br>"
                "Each time you close FreeSmartSync, a message reminds you "
                "to disable USB debugging on your phone. "
                "Your phone is never exposed without your knowledge.</p>"
                "<p style='font-size:14px'><b>🛡️ Safety guards against mistakes</b><br>"
                "Before any bulk deletion, a confirmation window shows "
                "thumbnails of the affected files. A detailed visual summary "
                "is displayed at the end of each sync.</p>"
                "<p style='font-size:14px'><b>📦 Compatible with all major distributions</b><br>"
                "Ubuntu, Debian, Fedora, Linux Mint, Zorin OS, Pop!_OS, "
                "Arch Linux, Manjaro, Mageia, openSUSE and more.</p>"
            )
        self.presentation_box.setHtml(presentation)

        self.no_plug_lbl.setText(
            "⚠️  <b>Ne branchez pas encore votre téléphone !</b><br>"
            "Nous allons d'abord vérifier les outils nécessaires. "
            "Vous serez guidé pour le brancher au moment opportun."
            if lang == "fr" else
            "⚠️  <b>Do not connect your phone yet!</b><br>"
            "We will first check the necessary tools. "
            "You will be guided to connect it at the right time."
        )
        self.disc_title_lbl.setText(t("disclaimer_title", lang))
        self.disc_text.setPlainText(t("disclaimer_text", lang))
        self.check_accept.setText(t("disclaimer_accept", lang))

    def is_accepted(self):
        return self.check_accept.isChecked()


# ─────────────────────────────────────────────
# Page 3 : Dépendances (avec disclaimer en haut)
# ─────────────────────────────────────────────

class PageDeps(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = "fr"
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 15, 20, 15)

        self.title_lbl = QtWidgets.QLabel()
        self.title_lbl.setStyleSheet("font-size:20px; font-weight:bold; margin-bottom:5px;")

        self.desc_lbl = QtWidgets.QLabel()
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setStyleSheet("font-size:13px; color:#555; margin-bottom:8px;")

        self.distrib_lbl = QtWidgets.QLabel()
        self.distrib_lbl.setStyleSheet(
            "font-size:13px; color:#2980b9; "
            "background:#eaf2ff; border:1px solid #3498db; "
            "border-radius:4px; padding:6px;"
        )

        self.status_adb  = QtWidgets.QLabel()
        self.status_py   = QtWidgets.QLabel()
        self.status_pyqt = QtWidgets.QLabel()

        for lbl in (self.status_adb, self.status_py, self.status_pyqt):
            lbl.setStyleSheet("font-size:14px; margin:4px 20px;")

        self.install_btn = QtWidgets.QPushButton()
        self.install_btn.setMinimumHeight(38)
        self.install_btn.setStyleSheet(
            "background-color:#3498db; color:white; font-weight:bold; "
            "font-size:13px; padding:8px;"
        )
        self.install_btn.clicked.connect(self.install)

        self.result_lbl = QtWidgets.QLabel()
        self.result_lbl.setWordWrap(True)
        self.result_lbl.setStyleSheet("font-size:13px; margin:8px;")

        layout.addWidget(self.title_lbl)
        layout.addWidget(self.desc_lbl)
        layout.addWidget(self.distrib_lbl)
        layout.addSpacing(8)
        layout.addWidget(self.status_adb)
        layout.addWidget(self.status_py)
        layout.addWidget(self.status_pyqt)
        layout.addSpacing(10)
        layout.addWidget(self.install_btn)
        layout.addWidget(self.result_lbl)
        layout.addStretch()
        self.setLayout(layout)

    def refresh(self, lang):
        self.lang = lang
        self.title_lbl.setText(t("deps_title", lang))
        self.desc_lbl.setText(t("deps_desc", lang))

        distrib_name, pkg_manager, install_cmd, use_su = detect_distrib()
        self._install_cmd  = install_cmd
        self._distrib_name = distrib_name
        self._use_su       = use_su
        self.distrib_lbl.setText(
            f"🐧 {t('deps_distrib', lang)} <b>{distrib_name}</b> ({pkg_manager})"
        )

        status = get_deps_status()
        ok  = t("deps_ok", lang)
        nok = t("deps_missing", lang)
        self.status_adb.setText(f"{t('deps_adb', lang)} : {ok if status['adb'] else nok}")
        self.status_py.setText(f"{t('deps_python', lang)} : {ok if status['python'] else nok}")
        self.status_pyqt.setText(f"{t('deps_pyqt', lang)} : {ok if status['pyqt5'] else nok}")

        all_ok = all(status.values())
        self.install_btn.setVisible(not all_ok)
        self.install_btn.setText(t("deps_install_btn", lang))

        if all_ok:
            self.result_lbl.setText(t("deps_all_ok", lang))
            self.result_lbl.setStyleSheet("color:#27ae60; font-size:14px; font-weight:bold;")

    def install(self):
        self.install_btn.setEnabled(False)
        self.install_btn.setText(t("deps_installing", self.lang))

        pwd, ok = QtWidgets.QInputDialog.getText(
            self, t("deps_root_needed", self.lang),
            t("deps_root_needed", self.lang),
            QtWidgets.QLineEdit.Password
        )
        if not ok:
            self.install_btn.setEnabled(True)
            self.install_btn.setText(t("deps_install_btn", self.lang))
            return

        success, output = install_deps(self._distrib_name, "", self._install_cmd, use_su=getattr(self, '_use_su', False), password=pwd)

        if success:
            self.result_lbl.setText(t("deps_all_ok", self.lang))
            self.result_lbl.setStyleSheet("color:#27ae60; font-weight:bold; font-size:14px;")
            self.install_btn.setVisible(False)
        else:
            self.result_lbl.setText(f"{t('deps_error', self.lang)}\n{output[:200]}")
            self.result_lbl.setStyleSheet("color:#e74c3c; font-size:13px;")
            self.install_btn.setEnabled(True)
            self.install_btn.setText(t("deps_install_btn", self.lang))


# ─────────────────────────────────────────────
# Page 4 : Procédure débogage USB (AVANT de brancher)
# ─────────────────────────────────────────────

class PagePhone(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang      = "fr"
        self.device_id = None

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(20, 15, 20, 15)

        self.title_lbl = QtWidgets.QLabel()
        self.title_lbl.setStyleSheet("font-size:20px; font-weight:bold;")

        self.desc_lbl = QtWidgets.QLabel()
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setStyleSheet("font-size:13px; color:#555;")

        # Explication pourquoi débogage USB
        self.why_debug_lbl = QtWidgets.QLabel()
        self.why_debug_lbl.setWordWrap(True)
        self.why_debug_lbl.setStyleSheet(
            "font-size:13px; color:#2c3e50; "
            "background:#eaf2ff; border:1px solid #3498db; "
            "border-radius:4px; padding:8px; margin:4px 0;"
        )

        self.warning_lbl = QtWidgets.QLabel()
        self.warning_lbl.setWordWrap(True)
        self.warning_lbl.setStyleSheet(
            "color:#e74c3c; font-weight:bold; font-size:13px; "
            "background:#fdf2f2; border:1px solid #e74c3c; "
            "border-radius:4px; padding:8px; margin:4px 0;"
        )

        self.brand_lbl   = QtWidgets.QLabel()
        self.brand_lbl.setStyleSheet("font-size:13px; font-weight:bold; margin-top:6px;")
        self.brand_combo = QtWidgets.QComboBox()
        self.brand_combo.setStyleSheet("font-size:13px; padding:4px;")
        brands = ["Samsung", "Xiaomi", "Google Pixel", "OnePlus",
                  "Huawei", "Sony", "Motorola"]
        self.brand_combo.addItems(brands)
        self.brand_combo.currentTextChanged.connect(self._update_steps)

        self.steps_title = QtWidgets.QLabel()
        self.steps_title.setStyleSheet("font-weight:bold; font-size:13px; margin-top:8px;")

        self.steps_widget = QtWidgets.QWidget()
        self.steps_layout = QtWidgets.QVBoxLayout(self.steps_widget)
        self.steps_layout.setSpacing(4)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.steps_widget)
        scroll.setMinimumHeight(180)

        layout.addWidget(self.title_lbl)
        layout.addWidget(self.desc_lbl)
        layout.addWidget(self.why_debug_lbl)
        layout.addWidget(self.warning_lbl)
        layout.addWidget(self.brand_lbl)
        layout.addWidget(self.brand_combo)
        layout.addWidget(self.steps_title)
        layout.addWidget(scroll)
        self.setLayout(layout)

    def refresh(self, lang):
        self.lang = lang
        self.title_lbl.setText(t("phone_title", lang))
        self.desc_lbl.setText(t("phone_desc", lang))
        self.why_debug_lbl.setText(
            "🔒 <b>Pourquoi activer le débogage USB ?</b><br>"
            "Android impose cette activation comme mesure de sécurité — "
            "sans elle, aucun logiciel ne peut accéder à vos données via USB. "
            "C'est une protection d'Android que FreeSmartSync respecte.<br><br>"
            "⚠️ <b>Important :</b> À la fermeture de FreeSmartSync, "
            "un message vous rappellera de <b>désactiver manuellement</b> "
            "le débogage USB sur votre téléphone pour le protéger."
            if lang == "fr" else
            "🔒 <b>Why enable USB debugging?</b><br>"
            "Android requires this as a security measure — "
            "without it, no software can access your data via USB. "
            "It's an Android protection that FreeSmartSync respects.<br><br>"
            "⚠️ <b>Important:</b> When closing FreeSmartSync, "
            "a message will remind you to <b>manually disable</b> "
            "USB debugging on your phone to protect it."
        )
        self.warning_lbl.setText(t("phone_warning", lang))
        self.brand_lbl.setText(t("phone_brand_label", lang))
        self.steps_title.setText(t("phone_steps_title", lang))

        other = t("phone_brand_other", lang)
        if self.brand_combo.findText(other) == -1:
            self.brand_combo.addItem(other)

        self._update_steps(self.brand_combo.currentText())

    def _update_steps(self, brand):
        for i in reversed(range(self.steps_layout.count())):
            w = self.steps_layout.itemAt(i).widget()
            if w: w.deleteLater()

        steps_data = USB_DEBUG_STEPS.get(brand, USB_DEBUG_STEPS.get("Google Pixel", {}))
        steps = steps_data.get(self.lang, steps_data.get("fr", []))

        for step in steps:
            lbl = QtWidgets.QLabel(step)
            lbl.setWordWrap(True)
            lbl.setStyleSheet("font-size:13px; margin:3px 10px;")
            self.steps_layout.addWidget(lbl)

    def get_device_id(self):
        return self.device_id


# ─────────────────────────────────────────────
# Page 5 : Connexion USB animée (APRÈS la procédure)
# ─────────────────────────────────────────────

class PageUSBConnect(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang      = "fr"
        self.device_id = None

        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 15, 20, 15)

        self.title_lbl = QtWidgets.QLabel()
        self.title_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.title_lbl.setStyleSheet("font-size:20px; font-weight:bold; color:#2c3e50;")

        self.desc_lbl = QtWidgets.QLabel()
        self.desc_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setStyleSheet("font-size:14px; color:#555;")

        self.anim_lbl = QtWidgets.QLabel()
        self.anim_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.anim_lbl.setMinimumHeight(80)
        self.anim_lbl.setStyleSheet("margin:8px;")

        # Frames d'animation HTML — belle représentation visuelle
        # sans emoji pour compatibilité universelle
        self._dot_pos = 0
        self._dot_count = 12
        self.anim_index = 0

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._animate)

        self.why_lbl = QtWidgets.QLabel()
        self.why_lbl.setWordWrap(True)
        self.why_lbl.setStyleSheet(
            "font-size:14px; color:#2c3e50; "
            "background:#eaf2ff; border:2px solid #3498db; "
            "border-radius:6px; padding:12px; margin:4px 0;"
        )

        self.cable_lbl = QtWidgets.QLabel()
        self.cable_lbl.setWordWrap(True)
        self.cable_lbl.setStyleSheet(
            "font-size:14px; color:#e67e22; "
            "background:#fef9e7; border:2px solid #e67e22; "
            "border-radius:6px; padding:12px; margin:4px 0;"
        )

        self.status_lbl = QtWidgets.QLabel()
        self.status_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.status_lbl.setWordWrap(True)
        self.status_lbl.setStyleSheet("font-size:15px; font-weight:bold; margin:6px;")

        self.refresh_btn = QtWidgets.QPushButton()
        self.refresh_btn.setMinimumHeight(40)
        self.refresh_btn.setStyleSheet(
            "background-color:#3498db; color:white; "
            "font-weight:bold; font-size:14px; padding:8px 30px; border-radius:6px;"
        )
        self.refresh_btn.clicked.connect(self._detect)

        self.faq_lbl = QtWidgets.QLabel()
        self.faq_lbl.setWordWrap(True)
        self.faq_lbl.setStyleSheet(
            "font-size:13px; color:#555; "
            "background:#f8f9fa; border:1px solid #dee2e6; "
            "border-radius:6px; padding:12px; margin:4px 0;"
        )

        # Variables de tracking pour éviter les mises à jour inutiles
        self._last_connected   = False
        self._last_charge_only = False

        self.detect_timer = QtCore.QTimer()
        self.detect_timer.timeout.connect(self._detect)

        # Zone animation centrée
        anim_container = QtWidgets.QWidget()
        anim_layout = QtWidgets.QHBoxLayout(anim_container)
        anim_layout.setContentsMargins(0, 0, 0, 0)
        anim_layout.addStretch()
        anim_layout.addWidget(self.anim_lbl)
        anim_layout.addStretch()

        layout.addWidget(self.title_lbl)
        layout.addWidget(self.desc_lbl)
        layout.addWidget(anim_container)
        # Les cadres info prennent toute la largeur
        layout.addWidget(self.why_lbl)
        layout.addWidget(self.cable_lbl)
        layout.addWidget(self.status_lbl)
        layout.addWidget(self.refresh_btn, 0, QtCore.Qt.AlignCenter)
        layout.addWidget(self.faq_lbl)
        layout.addStretch()
        self.setLayout(layout)
        self._update_status(False)

    def start_timers(self):
        if not self.timer.isActive():       self.timer.start(300)
        if not self.detect_timer.isActive(): self.detect_timer.start(2000)

    def stop_timers(self):
        self.timer.stop()
        self.detect_timer.stop()

    def refresh(self, lang):
        self.lang = lang
        self.title_lbl.setText("Branchez votre téléphone" if lang == "fr" else "Connect your phone")
        self.desc_lbl.setText(
            "Le débogage USB est maintenant activé sur votre téléphone.\n"
            "Branchez-le à cet ordinateur via le câble USB."
            if lang == "fr" else
            "USB debugging is now enabled on your phone.\n"
            "Connect it to this computer using the USB cable."
        )
        self.why_lbl.setText(
            "🔌 <b>Pourquoi via USB ?</b> FreeSmartSync utilise le protocole "
            "<b>ADB (Android Debug Bridge)</b> — rapide, fiable, "
            "et compatible sync bidirectionnelle complète. Le Wi-Fi seul ne suffit pas."
            if lang == "fr" else
            "🔌 <b>Why USB?</b> FreeSmartSync uses the "
            "<b>ADB (Android Debug Bridge)</b> protocol — fast, reliable, "
            "and supports full bidirectional sync. Wi-Fi alone is not enough."
        )
        self.cable_lbl.setText(
            "💡 <b>Important :</b> Utilisez le câble USB <b>d'origine</b> fourni avec votre "
            "téléphone. Les câbles bon marché sont souvent en mode <b>'charge seulement'</b> "
            "et ne transmettent pas les données !"
            if lang == "fr" else
            "💡 <b>Important:</b> Use the <b>original</b> USB cable provided with your phone. "
            "Cheap cables are often <b>'charge only'</b> and cannot transfer data!"
        )
        self.faq_lbl.setText(
            "<b>❓ Mon téléphone n'apparaît pas ?</b><br>"
            "1. Vérifiez votre <b>câble USB</b> — utilisez le câble d'origine.<br>"
            "2. Essayez un autre <b>port USB</b> de votre ordinateur.<br>"
            "3. Sur votre téléphone : glissez la barre de notifications → "
            "appuyez sur <b>'Charge USB'</b> → sélectionnez <b>'Transfert de fichiers'</b>."
            if lang == "fr" else
            "<b>❓ My phone doesn't appear?</b><br>"
            "1. Check your <b>USB cable</b> — use the original cable.<br>"
            "2. Try a different <b>USB port</b> on your computer.<br>"
            "3. On your phone: pull down notifications → "
            "tap <b>'USB Charging'</b> → select <b>'File Transfer'</b>."
        )
        self.refresh_btn.setText("🔄 Actualiser" if lang == "fr" else "🔄 Refresh")
        # Réinitialise le tracking pour forcer un rafraîchissement complet
        self._last_connected   = False
        self._last_charge_only = False
        self._detect()

    def _animate(self):
        """Animation visuelle de connexion USB — HTML, sans emoji."""
        if self.device_id:
            html = (
                "<div style='text-align:center; font-family:sans-serif;'>"
                "<span style='font-size:13px; font-weight:bold; color:#27ae60;"
                " background:#eafaf1; border:2px solid #27ae60;"
                " border-radius:6px; padding:5px 12px;'>SMARTPHONE</span>"
                "<span style='font-size:14px; color:#27ae60; font-weight:bold;"
                " padding:0 8px;'> ==================&gt; </span>"
                "<span style='font-size:13px; font-weight:bold; color:#27ae60;"
                " background:#eafaf1; border:2px solid #27ae60;"
                " border-radius:6px; padding:5px 12px;'>PC</span>"
                "<div style='font-size:13px; color:#27ae60; font-weight:bold;"
                " margin-top:6px;'>Connecte - OK</div>"
                "</div>"
            )
            self.anim_lbl.setText(html)
        else:
            self._dot_pos = (self._dot_pos + 1) % (self._dot_count + 1)
            before = "-" * self._dot_pos
            after  = "-" * (self._dot_count - self._dot_pos)
            html = (
                "<div style='text-align:center; font-family:monospace;'>"
                "<span style='font-size:13px; font-weight:bold; color:#3498db;"
                " background:#eaf2ff; border:2px solid #3498db;"
                " border-radius:6px; padding:5px 12px;'>SMARTPHONE</span>"
                f"<span style='font-size:14px; color:#3498db; font-weight:bold;"
                f" padding:0 6px; letter-spacing:1px;'> {before}&gt;{after} </span>"
                "<span style='font-size:13px; font-weight:bold; color:#3498db;"
                " background:#eaf2ff; border:2px solid #3498db;"
                " border-radius:6px; padding:5px 12px;'>PC</span>"
                "</div>"
            )
            self.anim_lbl.setText(html)

    def _detect(self):
        result = subprocess.run(
            ["adb", "devices"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        devices     = []
        charge_only = []

        for line in result.stdout.splitlines()[1:]:
            line = line.strip()
            if not line: continue
            if "device" in line and "offline" not in line:
                devices.append(line.split()[0])
            elif "no permissions" in line or "unauthorized" in line:
                charge_only.append(line.split()[0])

        wizard = self.parent()
        while wizard and not hasattr(wizard, "btn_next"):
            wizard = wizard.parent()

        if devices:
            new_device_id = devices[0]
            # Ne mettre à jour que si le statut a changé — évite le saut de texte
            if new_device_id != self.device_id or not self._last_connected:
                self.device_id = new_device_id
                self._last_connected = True
                self._last_charge_only = False
                brand = self._get_phone_name(self.device_id)
                self._update_status(True, brand)
            if wizard and wizard.current == 4:
                wizard.btn_next.setEnabled(True)
        elif charge_only:
            if not self._last_charge_only:
                self.device_id = None
                self._last_connected = False
                self._last_charge_only = True
                self._update_status_charge()
            if wizard and wizard.current == 4:
                wizard.btn_next.setEnabled(False)
        else:
            if self._last_connected or self._last_charge_only:
                self.device_id = None
                self._last_connected = False
                self._last_charge_only = False
                self._update_status(False)
            if wizard and wizard.current == 4:
                wizard.btn_next.setEnabled(False)

    def _get_phone_name(self, device_id):
        """Récupère marque + modèle du téléphone via ADB."""
        try:
            brand = subprocess.run(
                ["adb", "-s", device_id, "shell", "getprop ro.product.manufacturer"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            ).stdout.strip()
            model = subprocess.run(
                ["adb", "-s", device_id, "shell", "getprop ro.product.model"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            ).stdout.strip()
            if brand and model:
                return f"{brand} {model}"
            return device_id
        except Exception:
            return device_id

    def _update_status(self, connected, phone_name=None):
        if connected:
            name = phone_name or self.device_id
            self.status_lbl.setText(
                f"✅ Téléphone détecté : <b>{name}</b> ({self.device_id})"
                if self.lang == "fr" else
                f"✅ Phone detected: <b>{name}</b> ({self.device_id})"
            )
            self.status_lbl.setStyleSheet("font-size:14px; font-weight:bold; color:#27ae60;")
        else:
            self.status_lbl.setText(
                "⏳ En attente de connexion..."
                if self.lang == "fr" else "⏳ Waiting for connection..."
            )
            self.status_lbl.setStyleSheet("font-size:14px; font-weight:bold; color:#e74c3c;")

    def _update_status_charge(self):
        self.status_lbl.setText(
            "⚠️ Téléphone en mode <b>Charge seulement</b> — "
            "glissez la barre de notifications → <b>'Transfert de fichiers'</b>"
            if self.lang == "fr" else
            "⚠️ Phone in <b>Charge only</b> mode — "
            "pull down notifications → <b>'File Transfer'</b>"
        )
        self.status_lbl.setStyleSheet(
            "font-size:13px; font-weight:bold; color:#e67e22; "
            "background:#fef9e7; border:1px solid #e67e22; "
            "border-radius:4px; padding:6px; margin:4px 10px;"
        )

    def get_device_id(self):
        return self.device_id


# ─────────────────────────────────────────────
# Page 6 : Gestion des profils (NOUVEAU)
# ─────────────────────────────────────────────

class PageProfiles(QtWidgets.QWidget):
    """
    Page de gestion des profils dans le wizard.
    Permet de créer un nouveau profil, choisir un profil existant,
    ou continuer avec la configuration par défaut.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = "fr"
        self._selected = None  # {"name": ..., "data": {...}}

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 15, 20, 15)

        self.title_lbl = QtWidgets.QLabel()
        self.title_lbl.setStyleSheet("font-size:20px; font-weight:bold;")

        self.desc_lbl = QtWidgets.QLabel()
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setStyleSheet(
            "font-size:13px; background:#eaf2ff; border:1px solid #3498db; "
            "border-radius:4px; padding:10px;"
        )

        # Option 1 : Nouveau profil
        self.opt_new = QtWidgets.QRadioButton()
        self.opt_new.setStyleSheet("font-size:14px; font-weight:bold;")
        self.opt_new.setChecked(True)

        self.new_name_edit = QtWidgets.QLineEdit()
        self.new_name_edit.setStyleSheet("font-size:13px; padding:4px;")
        self.new_name_edit.setPlaceholderText(
            "Ex : Joffrey, Samsung Galaxy S24, Téléphone Marie..."
        )

        new_box = QtWidgets.QVBoxLayout()
        new_box.addWidget(self.opt_new)
        new_box.addWidget(self.new_name_edit)
        new_widget = QtWidgets.QWidget()
        new_widget.setLayout(new_box)
        new_widget.setStyleSheet(
            "background:#f8f9fa; border:1px solid #dee2e6; "
            "border-radius:4px; padding:6px;"
        )

        # Option 2 : Profil existant
        self.opt_existing = QtWidgets.QRadioButton()
        self.opt_existing.setStyleSheet("font-size:14px; font-weight:bold;")

        self.profile_combo = QtWidgets.QComboBox()
        self.profile_combo.setStyleSheet("font-size:13px; padding:4px;")
        self.profile_combo.setEnabled(False)

        existing_box = QtWidgets.QVBoxLayout()
        existing_box.addWidget(self.opt_existing)
        existing_box.addWidget(self.profile_combo)
        existing_widget = QtWidgets.QWidget()
        existing_widget.setLayout(existing_box)
        existing_widget.setStyleSheet(
            "background:#f8f9fa; border:1px solid #dee2e6; "
            "border-radius:4px; padding:6px;"
        )

        # Option 3 : Pas de profil (config par défaut)
        self.opt_none = QtWidgets.QRadioButton()
        self.opt_none.setStyleSheet("font-size:13px; color:#777;")

        # Connexions
        self.opt_new.toggled.connect(lambda v: self.new_name_edit.setEnabled(v))
        self.opt_existing.toggled.connect(lambda v: self.profile_combo.setEnabled(v))

        layout.addWidget(self.title_lbl)
        layout.addWidget(self.desc_lbl)
        layout.addSpacing(6)
        layout.addWidget(new_widget)
        layout.addWidget(existing_widget)
        layout.addWidget(self.opt_none)
        layout.addStretch()
        self.setLayout(layout)

    def refresh(self, lang):
        self.lang = lang
        self.title_lbl.setText(
            "👤 Gestion des profils" if lang == "fr" else "👤 Profile management"
        )
        self.desc_lbl.setText(
            "Un <b>profil</b> permet de sauvegarder les paramètres de synchronisation "
            "(dossiers + répertoire) pour un téléphone ou un utilisateur.<br>"
            "Pratique dans un foyer avec plusieurs smartphones !"
            if lang == "fr" else
            "A <b>profile</b> saves sync settings (folders + directory) "
            "for a phone or user.<br>"
            "Handy in a household with multiple smartphones!"
        )
        self.opt_new.setText(
            "✨ Créer un nouveau profil" if lang == "fr" else "✨ Create a new profile"
        )
        self.opt_existing.setText(
            "👤 Utiliser un profil existant" if lang == "fr" else "👤 Use an existing profile"
        )
        self.opt_none.setText(
            "⏭ Continuer sans profil (configuration par défaut)"
            if lang == "fr" else
            "⏭ Continue without profile (default config)"
        )
        self.new_name_edit.setPlaceholderText(
            "Ex : Joffrey, Samsung Galaxy S24, Téléphone Marie..."
            if lang == "fr" else
            "E.g.: John, Samsung Galaxy S24, Marie's phone..."
        )

        # Charger les profils existants
        self.profile_combo.clear()
        profiles = load_profiles()
        if profiles:
            for name in profiles:
                self.profile_combo.addItem(f"👤 {name}", name)
            self.opt_existing.setEnabled(True)
        else:
            self.opt_existing.setEnabled(False)
            self.opt_existing.setText(
                "👤 Utiliser un profil existant (aucun profil enregistré)"
                if lang == "fr" else
                "👤 Use an existing profile (no saved profiles)"
            )

    def get_selected_profile(self):
        """
        Retourne {"name": ..., "data": {...}} ou None si pas de profil.
        Crée automatiquement le profil si 'Nouveau profil' est sélectionné.
        """
        if self.opt_new.isChecked():
            name = self.new_name_edit.text().strip()
            if name:
                # Profil vide — sera rempli par les étapes suivantes
                return {"name": name, "data": {}}
        elif self.opt_existing.isChecked():
            name = self.profile_combo.currentData()
            if name:
                return {"name": name, "data": get_profile(name)}
        return None


# ─────────────────────────────────────────────
# Page 6 : Dossiers
# ─────────────────────────────────────────────

class PageFolders(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang      = "fr"
        self.device_id = None

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(20, 15, 20, 15)

        self.title_lbl = QtWidgets.QLabel()
        self.title_lbl.setStyleSheet("font-size:20px; font-weight:bold;")

        self.desc_lbl = QtWidgets.QLabel()
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setStyleSheet("font-size:13px; color:#555; margin-bottom:6px;")

        self.hint_lbl = QtWidgets.QLabel()
        self.hint_lbl.setStyleSheet("font-size:12px; color:#888;")

        self.folder_list = QtWidgets.QListWidget()
        self.folder_list.setAlternatingRowColors(True)
        self.folder_list.setStyleSheet("font-size:13px;")

        self.add_btn    = QtWidgets.QPushButton()
        self.remove_btn = QtWidgets.QPushButton()
        self.add_btn.setStyleSheet("font-size:13px; padding:5px;")
        self.remove_btn.setStyleSheet("font-size:13px; padding:5px;")
        self.add_btn.clicked.connect(self._add_folder)
        self.remove_btn.clicked.connect(self._remove_folder)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.remove_btn)
        btn_row.addStretch()

        self.desc_box = QtWidgets.QTextEdit()
        self.desc_box.setReadOnly(True)
        self.desc_box.setMaximumHeight(130)
        self.desc_box.setStyleSheet(
            "background:#f8f9fa; border:1px solid #dee2e6; "
            "border-radius:4px; font-size:13px;"
        )
        self.folder_list.currentRowChanged.connect(self._on_select)

        layout.addWidget(self.title_lbl)
        layout.addWidget(self.desc_lbl)
        layout.addWidget(self.hint_lbl)
        layout.addWidget(self.folder_list)
        layout.addLayout(btn_row)
        layout.addWidget(self.desc_box)
        self.setLayout(layout)

    def refresh(self, lang, device_id=None):
        self.lang = lang
        if device_id: self.device_id = device_id
        self.title_lbl.setText(t("folders_title", lang))

        if lang == "fr":
            desc = (
                "Choisissez ici les <b>dossiers de votre téléphone</b> à synchroniser.<br>"
                "Seuls les dossiers sélectionnés seront copiés et surveillés par FreeSmartSync.<br>"
                "Conseil : sélectionnez DCIM pour les photos, Download pour les téléchargements, etc.<br>"
                "<b>💡 Astuce :</b> Dans l'explorateur, vous pouvez sélectionner "
                "<b>plusieurs dossiers à la fois</b> en maintenant Ctrl enfoncé !"
            )
        else:
            desc = (
                "Choose here the <b>folders on your phone</b> to synchronize.<br>"
                "Only selected folders will be copied and monitored by FreeSmartSync.<br>"
                "Tip: select DCIM for photos, Download for downloads, etc.<br>"
                "<b>💡 Tip:</b> In the explorer, you can select "
                "<b>multiple folders at once</b> by holding Ctrl!"
            )
        self.desc_lbl.setText(desc)
        self.hint_lbl.setText(t("folders_hint", lang))
        self.add_btn.setText(t("folders_add", lang))
        self.remove_btn.setText(t("folders_remove", lang))
        self._fill_desc_box(lang)

    def _fill_desc_box(self, lang):
        lines = []
        for folder, desc in FOLDER_DESCRIPTIONS.items():
            lines.append(f"<b>{folder}</b> : {desc.get(lang, desc.get('fr', ''))}")
        self.desc_box.setHtml("<br>".join(lines))

    def _on_select(self, row):
        if row < 0: return
        folder = self.folder_list.item(row).text()
        desc   = FOLDER_DESCRIPTIONS.get(folder, {})
        if desc:
            self.desc_box.setHtml(
                f"<b style='font-size:14px'>{folder}</b><br>"
                f"<span style='font-size:13px'>{desc.get(self.lang, desc.get('fr', ''))}</span>"
            )

    def _add_folder(self):
        device_id = self.device_id
        if not device_id:
            parent = self.parent()
            while parent:
                if hasattr(parent, "page_usb"):
                    device_id = parent.page_usb.get_device_id()
                    break
                if hasattr(parent, "config"):
                    device_id = parent.config.get("device_id")
                    break
                parent = parent.parent()

        if not device_id:
            QtWidgets.QMessageBox.warning(
                self, "Erreur",
                "Aucun smartphone détecté.\nRevenez à l'étape précédente."
            )
            return

        self.device_id = device_id
        from modules.adb_explorer import ADBExplorer
        explorer = ADBExplorer(device_id, self, multi_select=True)
        if explorer.exec_():
            paths = explorer.selected_paths()
            added = 0
            for path in paths:
                if path and not self._folder_exists(path):
                    self.folder_list.addItem(path)
                    added += 1
            if added > 0:
                msg = (
                    f"{added} dossier(s) ajouté(s)."
                    if self.lang == "fr" else
                    f"{added} folder(s) added."
                )
                self.hint_lbl.setText(f"✅ {msg}")

    def _remove_folder(self):
        for item in self.folder_list.selectedItems():
            self.folder_list.takeItem(self.folder_list.row(item))

    def _folder_exists(self, path):
        return any(self.folder_list.item(i).text() == path
                   for i in range(self.folder_list.count()))

    def get_folders(self):
        return [self.folder_list.item(i).text() for i in range(self.folder_list.count())]


# ─────────────────────────────────────────────
# Page 7 : Destination
# ─────────────────────────────────────────────

class PageDest(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = "fr"
        self.dest = os.path.expanduser("~/FreeSmartSync-Backup/")

        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setSpacing(12)
        layout.setContentsMargins(25, 20, 25, 20)

        self.title_lbl = QtWidgets.QLabel(t("dest_title", "fr"))
        self.title_lbl.setStyleSheet("font-size:20px; font-weight:bold; color:#2c3e50;")

        self.desc_lbl = QtWidgets.QLabel(t("dest_desc", "fr"))
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setStyleSheet("font-size:13px; color:#555;")

        self.choose_btn = QtWidgets.QPushButton(t("dest_choose", "fr"))
        self.choose_btn.setMinimumHeight(42)
        self.choose_btn.setStyleSheet(
            "background-color:#3498db; color:white; "
            "font-weight:bold; font-size:14px; padding:8px; border-radius:4px;"
        )
        self.choose_btn.clicked.connect(self._choose)

        self.current_lbl = QtWidgets.QLabel(t("dest_current", "fr"))
        self.current_lbl.setStyleSheet("font-size:13px; color:#777; margin-top:8px;")

        self.path_lbl = QtWidgets.QLabel()
        self.path_lbl.setStyleSheet(
            "font-size:14px; font-weight:bold; color:#2c3e50; "
            "background:#eaf2ff; border:1px solid #3498db; "
            "border-radius:4px; padding:10px;"
        )
        self.path_lbl.setWordWrap(True)

        self.space_lbl = QtWidgets.QLabel()
        self.space_lbl.setStyleSheet("font-size:13px; color:#27ae60;")

        layout.addWidget(self.title_lbl)
        layout.addWidget(self.desc_lbl)
        layout.addSpacing(10)
        layout.addWidget(self.choose_btn)
        layout.addWidget(self.current_lbl)
        layout.addWidget(self.path_lbl)
        layout.addWidget(self.space_lbl)
        layout.addStretch()
        self.setLayout(layout)
        self._update_display()

    def refresh(self, lang):
        self.lang = lang
        self.title_lbl.setText(t("dest_title", lang))
        self.desc_lbl.setText(t("dest_desc", lang))
        self.choose_btn.setText(t("dest_choose", lang))
        self.current_lbl.setText(t("dest_current", lang))
        self._update_display()

    def _choose(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, t("dest_choose", self.lang))
        if folder:
            self.dest = folder
            self._update_display()

    def _update_display(self):
        self.path_lbl.setText(self.dest)
        check = self.dest
        while check and not os.path.exists(check):
            check = os.path.dirname(check)
        free = get_free_space(check) if check else 0
        if free > 0:
            self.space_lbl.setText(f"💾 {t('dest_space', self.lang)} {format_size(free)}")
        else:
            self.space_lbl.setText("")

    def get_dest(self):
        return self.dest


# ─────────────────────────────────────────────
# Page 8 : Résumé
# ─────────────────────────────────────────────

class PageSummary(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setSpacing(12)
        layout.setContentsMargins(25, 20, 25, 20)

        self.ready_lbl = QtWidgets.QLabel()
        self.ready_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.ready_lbl.setStyleSheet(
            "font-size:22px; font-weight:bold; color:#27ae60; margin:15px;"
        )

        self.summary_box = QtWidgets.QTextEdit()
        self.summary_box.setReadOnly(True)
        self.summary_box.setStyleSheet(
            "background:#f8f9fa; border:1px solid #dee2e6; "
            "border-radius:4px; font-size:14px; padding:12px;"
        )

        self.first_sync_lbl = QtWidgets.QLabel()
        self.first_sync_lbl.setWordWrap(True)
        self.first_sync_lbl.setStyleSheet(
            "font-size:13px; color:#2980b9; "
            "background:#eaf2ff; border:1px solid #3498db; "
            "border-radius:4px; padding:10px; margin-top:10px;"
        )

        layout.addWidget(self.ready_lbl)
        layout.addWidget(self.summary_box)
        layout.addWidget(self.first_sync_lbl)
        layout.addStretch()
        self.setLayout(layout)

    def refresh(self, lang, config):
        self.ready_lbl.setText(t("summary_ready", lang))
        self.first_sync_lbl.setText(t("summary_first_sync", lang))

        folders = config.get("folders", [])
        dest    = config.get("local_base", "—")
        device  = config.get("device_id", "—")

        html = (
            f"<b style='font-size:14px'>{t('summary_device', lang)}</b> {device}<br><br>"
            f"<b style='font-size:14px'>{t('summary_folders', lang)}</b><br>"
            + "".join(f"&nbsp;&nbsp;• {f}<br>" for f in folders)
            + f"<br><b style='font-size:14px'>{t('summary_dest', lang)}</b><br>"
            + f"&nbsp;&nbsp;{dest}"
        )
        self.summary_box.setHtml(html)
