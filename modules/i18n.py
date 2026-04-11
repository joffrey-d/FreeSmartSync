# modules/i18n.py
# Traductions FR / EN pour FreeSmartSync Beta

TRANSLATIONS = {
    "fr": {
        # Général
        "app_name": "FreeSmartSync Beta",
        "next": "Suivant →",
        "back": "← Retour",
        "finish": "🚀 Lancer FreeSmartSync",
        "cancel": "Annuler",
        "close": "✅ Fermer",
        "confirm": "Confirmer",
        "yes": "Oui",
        "no": "Non",
        "ok": "OK",
        "warning": "Avertissement",
        "error": "Erreur",

        # Wizard — Écran 1 : Langue
        "lang_title": "Bienvenue / Welcome",
        "lang_choose": "Choisissez votre langue\nChoose your language",
        "lang_fr": "🇫🇷  Français",
        "lang_en": "🇬🇧  English",

        # Wizard — Écran 2 : Accueil + Disclaimer
        "welcome_title": "Bienvenue dans FreeSmartSync Beta",
        "welcome_subtitle": "Synchronisation bidirectionnelle Android ↔ Linux",
        "welcome_desc": (
            "FreeSmartSync vous permet de sauvegarder et synchroniser les données "
            "de votre smartphone Android vers votre ordinateur Linux, "
            "et inversement."
        ),
        "disclaimer_title": "⚠️  Avertissement — À lire avant de continuer",
        "disclaimer_text": (
            "FreeSmartSync Beta est un logiciel en cours de développement, "
            "distribué gratuitement à titre expérimental.\n\n"
            "• L'utilisation de ce logiciel est entièrement à vos risques et périls.\n"
            "• L'auteur ne saurait être tenu responsable de toute perte de données, "
            "dysfonctionnement ou dommage résultant de l'utilisation de FreeSmartSync.\n"
            "• Il est fortement recommandé de vérifier vos données après chaque synchronisation.\n"
            "• Les suppressions effectuées sont irréversibles sur le téléphone.\n\n"
            "En continuant, vous acceptez ces conditions."
        ),
        "disclaimer_accept": "J'ai lu et j'accepte les conditions d'utilisation",

        # Wizard — Écran 3 : Dépendances
        "deps_title": "Vérification des dépendances",
        "deps_desc": "FreeSmartSync a besoin des outils suivants pour fonctionner :",
        "deps_adb": "ADB (Android Debug Bridge)",
        "deps_python": "Python 3",
        "deps_pyqt": "PyQt5",
        "deps_checking": "Vérification en cours...",
        "deps_ok": "✅ Installé",
        "deps_missing": "❌ Manquant",
        "deps_installing": "⏳ Installation en cours...",
        "deps_install_btn": "🔧 Installer les dépendances manquantes",
        "deps_distrib": "Distribution détectée :",
        "deps_all_ok": "✅ Toutes les dépendances sont installées !",
        "deps_error": "❌ Impossible d'installer automatiquement.\nInstallez manuellement : ",
        "deps_root_needed": "⚠️  Mot de passe administrateur requis pour l'installation.",

        # Wizard — Écran 4 : Téléphone
        "phone_title": "Connexion de votre téléphone",
        "phone_desc": (
            "Pour fonctionner, FreeSmartSync a besoin que le "
            "<b>débogage USB</b> soit activé sur votre téléphone."
        ),
        "phone_warning": (
            "⚠️  IMPORTANT : Sans le débogage USB activé, "
            "FreeSmartSync ne pourra pas détecter votre téléphone !"
        ),
        "phone_brand_label": "Sélectionnez la marque de votre téléphone :",
        "phone_brand_other": "Autre / Je ne sais pas",
        "phone_detected": "📱 Téléphone détecté :",
        "phone_not_detected": "❌ Aucun téléphone détecté",
        "phone_refresh": "🔄 Actualiser",
        "phone_connect_first": "Branchez votre téléphone puis cliquez sur Actualiser",
        "phone_steps_title": "Procédure d'activation du débogage USB :",

        # Wizard — Écran 5 : Dossiers
        "folders_title": "Choisissez les dossiers à synchroniser",
        "folders_desc": (
            "Sélectionnez les dossiers de votre téléphone "
            "que vous souhaitez sauvegarder."
        ),
        "folders_add": "➕ Ajouter un dossier",
        "folders_remove": "➖ Supprimer",
        "folders_hint": "Cliquez sur ℹ️ pour en savoir plus sur chaque dossier.",
        "folders_none_warning": "⚠️  Sélectionnez au moins un dossier.",

        # Wizard — Écran 6 : Destination
        "dest_title": "Répertoire de sauvegarde",
        "dest_desc": "Choisissez où seront enregistrées vos données sur cet ordinateur.",
        "dest_choose": "📂 Choisir un répertoire",
        "dest_current": "Répertoire sélectionné :",
        "dest_warning": "⚠️  Choisissez un répertoire avec suffisamment d'espace disque.",
        "dest_space": "Espace disponible :",

        # Wizard — Écran 7 : Résumé
        "summary_title": "Résumé de la configuration",
        "summary_ready": "✅ FreeSmartSync est prêt !",
        "summary_device": "Téléphone :",
        "summary_folders": "Dossiers sélectionnés :",
        "summary_dest": "Destination :",
        "summary_first_sync": (
            "ℹ️  Premier lancement : FreeSmartSync va d'abord copier "
            "tous vos fichiers vers le PC. "
            "Les synchronisations suivantes seront plus rapides."
        ),

        # Interface principale
        "main_title": "FreeSmartSync Beta",
        "main_device": "Smartphone détecté :",
        "main_refresh": "🔄 Actualiser",
        "main_scan": "Scan téléphone",
        "main_copy": "Copie / Sync",
        "main_status_ready": "Prêt",
        "main_file": "Fichier : -",
        "main_folders": "Dossiers synchronisés",
        "main_dest": "Répertoire de destination",
        "main_add": "➕ Ajouter",
        "main_remove": "➖ Supprimer",
        "main_dest_btn": "📂 Choisir destination",
        "main_start": "🟢 Démarrer",
        "main_pause": "⏸ Pause",
        "main_resume": "▶ Reprendre",
        "main_stop": "⛔ Stop",
        "main_quit": "🚪 Quitter",
        "main_settings": "⚙️ Paramètres",

        # Popups
        "close_warning_title": "⚠️ Synchronisation en cours",
        "close_warning_text": (
            "<b>Une synchronisation est en cours.</b><br><br>"
            "Fermer l'application maintenant pourrait corrompre des fichiers "
            "en cours de transfert.<br><br>"
            "Veuillez utiliser <b>⛔ Stop</b> pour arrêter proprement "
            "la synchronisation, puis <b>🚪 Quitter</b>."
        ),
        "close_warning_btn": "OK, je continue",

        "delete_confirm_title": "⚠️ Confirmation suppression sur le téléphone",
        "delete_confirm_text": (
            "<b>{count} fichier(s) vont être supprimés sur le téléphone.</b><br>"
            "Ces fichiers ont été supprimés localement sur le PC.<br>"
            "Cette action est <b>irréversible</b> sur le téléphone."
        ),
        "delete_confirm_btn": "🗑️ Confirmer la suppression",
        "delete_cancel_btn": "❌ Annuler",

        "summary_dialog_title": "📋 Résumé de la synchronisation",
        "summary_tab_global": "📊 Résumé",
        "summary_tab_copied": "🟢 Copiés",
        "summary_tab_deleted_pc": "🗑️ Supprimés PC",
        "summary_tab_deleted_tel": "🗑️ Supprimés Tel",
        "summary_start": "🕐 Début :",
        "summary_end": "🕑 Fin :",
        "summary_duration": "⏱️ Durée :",
        "summary_copied": "🟢 Copiés Tel→PC :",
        "summary_skipped": "🟡 Ignorés :",
        "summary_del_pc": "🗑️ Supprimés PC :",
        "summary_del_tel": "🗑️ Supprimés Tel :",
        "summary_errors": "❌ Erreurs :",
        "summary_del_tel_note": (
            "Ces fichiers ont été supprimés sur le téléphone "
            "(plus disponibles localement pour miniature)."
        ),

        # Log messages
        "log_start": "🕐 Début :",
        "log_scan": "🔍 Scan téléphone :",
        "log_scan_error": "⚠️ Erreur scan",
        "log_files_found": "📦 Fichiers détectés sur le téléphone :",
        "log_tel_to_pc": "⬇️  Synchronisation Téléphone → PC...",
        "log_pc_to_tel": "⬆️  Vérification suppressions PC → Téléphone...",
        "log_no_journal": "📋 Premier lancement — aucun journal trouvé.",
        "log_journal_loaded": "📋 Journal chargé :",
        "log_journal_files": "fichiers connus.",
        "log_first_sync_skip": "ℹ️  Premier lancement — PC→Tel ignoré.",
        "log_ignored": "🟡 Ignoré :",
        "log_copying": "🟢 Copie Tel→PC :",
        "log_copy_error": "❌ Erreur copie :",
        "log_cleaning": "🧹 Nettoyage PC (fichiers supprimés du téléphone)...",
        "log_deleted_pc": "🗑️ Supprimé PC :",
        "log_deleted_tel": "🗑️ Suppression Tel :",
        "log_del_tel_error": "❌ Erreur suppression tel :",
        "log_no_del_tel": "✅ Aucune suppression PC→Tel à effectuer.",
        "log_del_cancelled": "🚫 Suppression annulée par l'utilisateur.",
        "log_disconnected": "❌ Smartphone déconnecté !",
        "log_interrupted": "⛔ Interruption utilisateur",
        "log_journal_saved": "💾 Journal de sync mis à jour.",
        "log_done": "✅ SYNCHRONISATION TERMINÉE",
        "log_separator": "─" * 48,
        "log_no_device": "⚠️ Aucun smartphone détecté. Vérifiez le câble USB et le débogage ADB.",
        "log_device_found": "📱 smartphone(s) détecté(s) :",
    },

    "en": {
        # General
        "app_name": "FreeSmartSync Beta",
        "next": "Next →",
        "back": "← Back",
        "finish": "🚀 Launch FreeSmartSync",
        "cancel": "Cancel",
        "close": "✅ Close",
        "confirm": "Confirm",
        "yes": "Yes",
        "no": "No",
        "ok": "OK",
        "warning": "Warning",
        "error": "Error",

        # Wizard — Screen 1: Language
        "lang_title": "Bienvenue / Welcome",
        "lang_choose": "Choisissez votre langue\nChoose your language",
        "lang_fr": "🇫🇷  Français",
        "lang_en": "🇬🇧  English",

        # Wizard — Screen 2: Welcome + Disclaimer
        "welcome_title": "Welcome to FreeSmartSync Beta",
        "welcome_subtitle": "Bidirectional sync Android ↔ Linux",
        "welcome_desc": (
            "FreeSmartSync lets you backup and sync your Android smartphone data "
            "to your Linux computer, and vice versa."
        ),
        "disclaimer_title": "⚠️  Warning — Please read before continuing",
        "disclaimer_text": (
            "FreeSmartSync Beta is software under development, "
            "distributed free of charge on an experimental basis.\n\n"
            "• Use of this software is entirely at your own risk.\n"
            "• The author cannot be held responsible for any data loss, "
            "malfunction or damage resulting from the use of FreeSmartSync.\n"
            "• It is strongly recommended to verify your data after each sync.\n"
            "• Deletions performed are irreversible on the phone.\n\n"
            "By continuing, you accept these terms."
        ),
        "disclaimer_accept": "I have read and accept the terms of use",

        # Wizard — Screen 3: Dependencies
        "deps_title": "Checking dependencies",
        "deps_desc": "FreeSmartSync needs the following tools to work:",
        "deps_adb": "ADB (Android Debug Bridge)",
        "deps_python": "Python 3",
        "deps_pyqt": "PyQt5",
        "deps_checking": "Checking...",
        "deps_ok": "✅ Installed",
        "deps_missing": "❌ Missing",
        "deps_installing": "⏳ Installing...",
        "deps_install_btn": "🔧 Install missing dependencies",
        "deps_distrib": "Detected distribution:",
        "deps_all_ok": "✅ All dependencies are installed!",
        "deps_error": "❌ Cannot install automatically.\nPlease install manually: ",
        "deps_root_needed": "⚠️  Administrator password required for installation.",

        # Wizard — Screen 4: Phone
        "phone_title": "Connect your phone",
        "phone_desc": (
            "FreeSmartSync requires <b>USB debugging</b> "
            "to be enabled on your phone."
        ),
        "phone_warning": (
            "⚠️  IMPORTANT: Without USB debugging enabled, "
            "FreeSmartSync will not be able to detect your phone!"
        ),
        "phone_brand_label": "Select your phone brand:",
        "phone_brand_other": "Other / I don't know",
        "phone_detected": "📱 Phone detected:",
        "phone_not_detected": "❌ No phone detected",
        "phone_refresh": "🔄 Refresh",
        "phone_connect_first": "Connect your phone then click Refresh",
        "phone_steps_title": "How to enable USB debugging:",

        # Wizard — Screen 5: Folders
        "folders_title": "Choose folders to sync",
        "folders_desc": (
            "Select the folders on your phone "
            "that you want to back up."
        ),
        "folders_add": "➕ Add folder",
        "folders_remove": "➖ Remove",
        "folders_hint": "Click ℹ️ to learn more about each folder.",
        "folders_none_warning": "⚠️  Please select at least one folder.",

        # Wizard — Screen 6: Destination
        "dest_title": "Backup directory",
        "dest_desc": "Choose where your data will be saved on this computer.",
        "dest_choose": "📂 Choose directory",
        "dest_current": "Selected directory:",
        "dest_warning": "⚠️  Choose a directory with enough disk space.",
        "dest_space": "Available space:",

        # Wizard — Screen 7: Summary
        "summary_title": "Configuration summary",
        "summary_ready": "✅ FreeSmartSync is ready!",
        "summary_device": "Phone:",
        "summary_folders": "Selected folders:",
        "summary_dest": "Destination:",
        "summary_first_sync": (
            "ℹ️  First run: FreeSmartSync will first copy all your files to the PC. "
            "Subsequent syncs will be faster."
        ),

        # Main window
        "main_title": "FreeSmartSync Beta",
        "main_device": "Detected phone:",
        "main_refresh": "🔄 Refresh",
        "main_scan": "Phone scan",
        "main_copy": "Copy / Sync",
        "main_status_ready": "Ready",
        "main_file": "File: -",
        "main_folders": "Synced folders",
        "main_dest": "Backup directory",
        "main_add": "➕ Add",
        "main_remove": "➖ Remove",
        "main_dest_btn": "📂 Choose destination",
        "main_start": "🟢 Start",
        "main_pause": "⏸ Pause",
        "main_resume": "▶ Resume",
        "main_stop": "⛔ Stop",
        "main_quit": "🚪 Quit",
        "main_settings": "⚙️ Settings",

        # Popups
        "close_warning_title": "⚠️ Sync in progress",
        "close_warning_text": (
            "<b>A sync is currently in progress.</b><br><br>"
            "Closing the app now could corrupt files being transferred.<br><br>"
            "Please use <b>⛔ Stop</b> to safely stop the sync, "
            "then <b>🚪 Quit</b>."
        ),
        "close_warning_btn": "OK, keep going",

        "delete_confirm_title": "⚠️ Confirm deletion on phone",
        "delete_confirm_text": (
            "<b>{count} file(s) will be deleted on the phone.</b><br>"
            "These files were deleted locally on the PC.<br>"
            "This action is <b>irreversible</b> on the phone."
        ),
        "delete_confirm_btn": "🗑️ Confirm deletion",
        "delete_cancel_btn": "❌ Cancel",

        "summary_dialog_title": "📋 Sync summary",
        "summary_tab_global": "📊 Summary",
        "summary_tab_copied": "🟢 Copied",
        "summary_tab_deleted_pc": "🗑️ Deleted PC",
        "summary_tab_deleted_tel": "🗑️ Deleted Phone",
        "summary_start": "🕐 Start:",
        "summary_end": "🕑 End:",
        "summary_duration": "⏱️ Duration:",
        "summary_copied": "🟢 Copied Phone→PC:",
        "summary_skipped": "🟡 Skipped:",
        "summary_del_pc": "🗑️ Deleted PC:",
        "summary_del_tel": "🗑️ Deleted Phone:",
        "summary_errors": "❌ Errors:",
        "summary_del_tel_note": (
            "These files were deleted on the phone "
            "(no longer available locally for thumbnail)."
        ),

        # Log messages
        "log_start": "🕐 Start:",
        "log_scan": "🔍 Phone scan:",
        "log_scan_error": "⚠️ Scan error",
        "log_files_found": "📦 Files detected on phone:",
        "log_tel_to_pc": "⬇️  Phone → PC sync...",
        "log_pc_to_tel": "⬆️  Checking PC → Phone deletions...",
        "log_no_journal": "📋 First run — no journal found.",
        "log_journal_loaded": "📋 Journal loaded:",
        "log_journal_files": "known files.",
        "log_first_sync_skip": "ℹ️  First run — PC→Phone skipped.",
        "log_ignored": "🟡 Skipped:",
        "log_copying": "🟢 Copy Phone→PC:",
        "log_copy_error": "❌ Copy error:",
        "log_cleaning": "🧹 Cleaning PC (files deleted from phone)...",
        "log_deleted_pc": "🗑️ Deleted PC:",
        "log_deleted_tel": "🗑️ Delete Phone:",
        "log_del_tel_error": "❌ Phone deletion error:",
        "log_no_del_tel": "✅ No Phone→PC deletions needed.",
        "log_del_cancelled": "🚫 Deletion cancelled by user.",
        "log_disconnected": "❌ Phone disconnected!",
        "log_interrupted": "⛔ Interrupted by user",
        "log_journal_saved": "💾 Sync journal updated.",
        "log_done": "✅ SYNC COMPLETE",
        "log_separator": "─" * 48,
        "log_no_device": "⚠️ No phone detected. Check USB cable and ADB debugging.",
        "log_device_found": "📱 phone(s) detected:",
    }
}

# Procédures débogage USB par marque
USB_DEBUG_STEPS = {
    "Samsung": {
        "fr": [
            "1. Allez dans <b>Paramètres</b>",
            "2. Appuyez sur <b>À propos du téléphone</b>",
            "3. Appuyez <b>7 fois</b> sur <b>Numéro de build</b> "
            "(ou <b>Version du logiciel</b> / <b>Version de l'OS</b> selon votre modèle)",
            "4. Retournez dans <b>Paramètres → Options développeur</b>",
            "5. Activez <b>Débogage USB</b>",
            "6. Branchez le câble USB et acceptez la demande d'autorisation",
            "<br><b style='color:#e74c3c'>🔒 Après la synchronisation :</b> "
            "Retournez dans <b>Options développeur</b> → désactivez <b>Débogage USB</b> "
            "— FreeSmartSync le fait automatiquement mais vérifiez par sécurité.",
        ],
        "en": [
            "1. Go to <b>Settings</b>",
            "2. Tap <b>About phone</b>",
            "3. Tap <b>Build number</b> <b>7 times</b> "
            "(or <b>Software version</b> / <b>OS version</b> depending on your model)",
            "4. Go back to <b>Settings → Developer options</b>",
            "5. Enable <b>USB debugging</b>",
            "6. Plug in USB cable and accept the authorization prompt",
            "<br><b style='color:#e74c3c'>🔒 After sync:</b> "
            "Go back to <b>Developer options</b> → disable <b>USB debugging</b> "
            "— FreeSmartSync does it automatically but check for safety.",
        ],
    },
    "Xiaomi": {
        "fr": [
            "1. Allez dans <b>Paramètres → À propos du téléphone</b>",
            "2. Appuyez <b>7 fois</b> sur <b>Version MIUI</b>",
            "3. Allez dans <b>Paramètres → Paramètres supplémentaires → Options développeur</b>",
            "4. Activez <b>Débogage USB</b>",
            "5. Activez aussi <b>Débogage USB (Paramètres de sécurité)</b> si présent",
            "6. Branchez le câble USB et acceptez la demande d'autorisation",
        ],
        "en": [
            "1. Go to <b>Settings → About phone</b>",
            "2. Tap <b>MIUI version</b> <b>7 times</b>",
            "3. Go to <b>Settings → Additional settings → Developer options</b>",
            "4. Enable <b>USB debugging</b>",
            "5. Also enable <b>USB debugging (Security settings)</b> if present",
            "6. Plug in USB cable and accept the authorization prompt",
        ],
    },
    "Google Pixel": {
        "fr": [
            "1. Allez dans <b>Paramètres → À propos du téléphone</b>",
            "2. Appuyez <b>7 fois</b> sur <b>Numéro de build</b>",
            "3. Retournez dans <b>Paramètres → Système → Options développeur</b>",
            "4. Activez <b>Débogage USB</b>",
            "5. Branchez le câble USB et acceptez la demande d'autorisation",
            "<br><b style='color:#e74c3c'>🔒 Après la synchronisation :</b> Retournez dans <b>Options développeur</b> → désactivez <b>Débogage USB</b> — FreeSmartSync le fait automatiquement mais vérifiez par sécurité.",
        ],
        "en": [
            "1. Go to <b>Settings → About phone</b>",
            "2. Tap <b>Build number</b> <b>7 times</b>",
            "3. Go to <b>Settings → System → Developer options</b>",
            "4. Enable <b>USB debugging</b>",
            "5. Plug in USB cable and accept the authorization prompt",
            "<br><b style='color:#e74c3c'>🔒 After sync:</b> Go back to <b>Developer options</b> → disable <b>USB debugging</b> — FreeSmartSync does it automatically but check for safety.",
        ],
    },
    "OnePlus": {
        "fr": [
            "1. Allez dans <b>Paramètres → À propos du téléphone</b>",
            "2. Appuyez <b>7 fois</b> sur <b>Numéro de build</b>",
            "3. Allez dans <b>Paramètres → Système → Options développeur</b>",
            "4. Activez <b>Débogage USB</b>",
            "5. Branchez le câble USB et acceptez la demande d'autorisation",
            "<br><b style='color:#e74c3c'>🔒 Après la synchronisation :</b> Retournez dans <b>Options développeur</b> → désactivez <b>Débogage USB</b> — FreeSmartSync le fait automatiquement mais vérifiez par sécurité.",
        ],
        "en": [
            "1. Go to <b>Settings → About phone</b>",
            "2. Tap <b>Build number</b> <b>7 times</b>",
            "3. Go to <b>Settings → System → Developer options</b>",
            "4. Enable <b>USB debugging</b>",
            "5. Plug in USB cable and accept the authorization prompt",
            "<br><b style='color:#e74c3c'>🔒 After sync:</b> Go back to <b>Developer options</b> → disable <b>USB debugging</b> — FreeSmartSync does it automatically but check for safety.",
        ],
    },
    "Huawei": {
        "fr": [
            "1. Allez dans <b>Paramètres → À propos du téléphone</b>",
            "2. Appuyez <b>7 fois</b> sur <b>Numéro de build</b>",
            "3. Allez dans <b>Paramètres → Système → Options développeur</b>",
            "4. Activez <b>Débogage USB</b>",
            "5. Branchez le câble USB et acceptez la demande d'autorisation",
            "<br><b style='color:#e74c3c'>🔒 Après la synchronisation :</b> Retournez dans <b>Options développeur</b> → désactivez <b>Débogage USB</b> — FreeSmartSync le fait automatiquement mais vérifiez par sécurité.",
        ],
        "en": [
            "1. Go to <b>Settings → About phone</b>",
            "2. Tap <b>Build number</b> <b>7 times</b>",
            "3. Go to <b>Settings → System → Developer options</b>",
            "4. Enable <b>USB debugging</b>",
            "5. Plug in USB cable and accept the authorization prompt",
            "<br><b style='color:#e74c3c'>🔒 After sync:</b> Go back to <b>Developer options</b> → disable <b>USB debugging</b> — FreeSmartSync does it automatically but check for safety.",
        ],
    },
    "Sony": {
        "fr": [
            "1. Allez dans <b>Paramètres → À propos du téléphone</b>",
            "2. Appuyez <b>7 fois</b> sur <b>Numéro de build</b>",
            "3. Allez dans <b>Paramètres → Système → Options développeur</b>",
            "4. Activez <b>Débogage USB</b>",
            "5. Branchez le câble USB et acceptez la demande d'autorisation",
            "<br><b style='color:#e74c3c'>🔒 Après la synchronisation :</b> Retournez dans <b>Options développeur</b> → désactivez <b>Débogage USB</b> — FreeSmartSync le fait automatiquement mais vérifiez par sécurité.",
        ],
        "en": [
            "1. Go to <b>Settings → About phone</b>",
            "2. Tap <b>Build number</b> <b>7 times</b>",
            "3. Go to <b>Settings → System → Developer options</b>",
            "4. Enable <b>USB debugging</b>",
            "5. Plug in USB cable and accept the authorization prompt",
            "<br><b style='color:#e74c3c'>🔒 After sync:</b> Go back to <b>Developer options</b> → disable <b>USB debugging</b> — FreeSmartSync does it automatically but check for safety.",
        ],
    },
    "Motorola": {
        "fr": [
            "1. Allez dans <b>Paramètres → À propos du téléphone</b>",
            "2. Appuyez <b>7 fois</b> sur <b>Numéro de build</b>",
            "3. Allez dans <b>Paramètres → Système → Options développeur</b>",
            "4. Activez <b>Débogage USB</b>",
            "5. Branchez le câble USB et acceptez la demande d'autorisation",
            "<br><b style='color:#e74c3c'>🔒 Après la synchronisation :</b> Retournez dans <b>Options développeur</b> → désactivez <b>Débogage USB</b> — FreeSmartSync le fait automatiquement mais vérifiez par sécurité.",
        ],
        "en": [
            "1. Go to <b>Settings → About phone</b>",
            "2. Tap <b>Build number</b> <b>7 times</b>",
            "3. Go to <b>Settings → System → Developer options</b>",
            "4. Enable <b>USB debugging</b>",
            "5. Plug in USB cable and accept the authorization prompt",
            "<br><b style='color:#e74c3c'>🔒 After sync:</b> Go back to <b>Developer options</b> → disable <b>USB debugging</b> — FreeSmartSync does it automatically but check for safety.",
        ],
    },
}
USB_DEBUG_STEPS["Autre / Je ne sais pas"] = USB_DEBUG_STEPS["Google Pixel"]
USB_DEBUG_STEPS["Other / I don't know"]   = USB_DEBUG_STEPS["Google Pixel"]

# Descriptions des dossiers principaux
FOLDER_DESCRIPTIONS = {
    "DCIM": {
        "fr": "📷 Photos et vidéos prises avec l'appareil photo — présent sur tous les téléphones Android",
        "en": "📷 Photos and videos taken with the camera — present on all Android phones",
    },
    "Pictures": {
        "fr": "🖼️ Images sauvegardées depuis des applications (WhatsApp, réseaux sociaux, etc.)",
        "en": "🖼️ Images saved from apps (WhatsApp, social media, etc.)",
    },
    "Download": {
        "fr": "⬇️ Fichiers téléchargés depuis Internet ou des applications",
        "en": "⬇️ Files downloaded from the Internet or apps",
    },
    "Movies": {
        "fr": "🎬 Vidéos et films enregistrés sur le téléphone",
        "en": "🎬 Videos and movies stored on the phone",
    },
    "Music": {
        "fr": "🎵 Musiques et fichiers audio stockés sur le téléphone",
        "en": "🎵 Music and audio files stored on the phone",
    },
    "Documents": {
        "fr": "📄 Documents divers (PDF, Word, Excel, etc.)",
        "en": "📄 Various documents (PDF, Word, Excel, etc.)",
    },
    "Ringtones": {
        "fr": "🔔 Sonneries personnalisées ajoutées sur le téléphone",
        "en": "🔔 Custom ringtones added to the phone",
    },
    "Notifications": {
        "fr": "🔕 Sons de notification personnalisés",
        "en": "🔕 Custom notification sounds",
    },
    "Alarms": {
        "fr": "⏰ Sons d'alarme personnalisés",
        "en": "⏰ Custom alarm sounds",
    },
    "Bluetooth": {
        "fr": "📡 Fichiers reçus via Bluetooth",
        "en": "📡 Files received via Bluetooth",
    },
    "Podcasts": {
        "fr": "🎙️ Épisodes de podcasts téléchargés",
        "en": "🎙️ Downloaded podcast episodes",
    },
    "WhatsApp/Media": {
        "fr": "💬 Photos, vidéos et documents reçus via WhatsApp — "
              "⚠️ l'emplacement peut varier selon votre téléphone, "
              "utilisez l'explorateur ADB si ce dossier est introuvable",
        "en": "💬 Photos, videos and documents received via WhatsApp — "
              "⚠️ location may vary depending on your phone, "
              "use the ADB explorer if this folder is not found",
    },
    "Telegram": {
        "fr": "✈️ Médias reçus et partagés via Telegram",
        "en": "✈️ Media received and shared via Telegram",
    },
}


def t(key, lang="fr", **kwargs):
    """Retourne la traduction d'une clé dans la langue donnée."""
    text = TRANSLATIONS.get(lang, TRANSLATIONS["fr"]).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text
