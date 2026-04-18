# Notes de version — FreeSmartSync

---

## v0.8.8.3 — Actuelle
**Barre de progression Fedora/Mageia · GLF-OS PyQt5 · Menu Mageia**

Diagnostic précis grâce aux tests terrain :

- **Barre de progression kdialog (Fedora/Mageia KDE)** : kdialog utilise DBus,
  pas stdin — le FIFO était ignoré, d'où la fenêtre bloquée. Logique maintenant
  séparée : kdialog = lancé en arrière-plan + `kill $PID` à la fin ;
  zenity = FIFO stdin + `100` + `--auto-close` (inchangé, LM parfait)
- **GLF-OS PyQt5** : tentatives sur plusieurs attributs Nix
  (`python3Packages.pyqt5`, `python39Packages.pyqt5`, `python310Packages.pyqt5`,
  `python311Packages.pyqt5`) — le nom varie selon la version du channel
- **Menu réinstall/désinstall Mageia** : détection élargie avec vérification
  supplémentaire du `.desktop` dans `applications/`
- **Version stable `main`** : reste v0.8.6.9 (validée sur toutes distributions)

---

## v0.8.8.2
**Barre de progression · GLF-OS · Désinstallation**

- **Barre de progression** (Fedora/Mageia) : remplacement du `--pulsate` (infini)
  par un pipe nommé (FIFO). Le script envoie `10→30→60→90→100` via un descripteur
  dédié. À `100`, zenity/kdialog se ferment via `--auto-close`. Fermeture garantie.
- **GLF-OS** : commande corrigée `nix-env -i android-tools python3 python3Packages.pyqt5`
  (sans préfixe `nixpkgs.` — channel auto-détecté par nix-env)
- **Désinstallation** : message unifié et clair, avec affichage du chemin de sauvegarde
  configuré, rappel qu'ADB n'est pas supprimé (partagé avec d'autres logiciels)
- **Site** : guide d'installation revu — captures sans annotations mal positionnées,
  texte descriptif sous chaque image, suppression du mot "obligatoire" (les droits
  sont déjà corrects dans le zip)

---

## v0.8.8.1
**Barre de progression · Lancement blindé · Site avec captures**

- **Barre de progression** (Fedora/Mageia) : ajout de `pkill -f "zenity --progress"`
  et `pkill -f "kdialog --progressbar"` dans `close_progress()` — force la fermeture
  même si le PID a changé entre la création et la clôture
- **Lancement post-install** — 3 méthodes en cascade :
  1. `gtk-launch freesmartsync` si disponible et .desktop installé (meilleure intégration GNOME)
  2. `setsid nohup python3` (détachement complet, fix Zorin/GNOME)
  3. `nohup python3` (fallback universel)
- **Message d'avertissement** dans la popup finale : si le lancement auto échoue,
  l'utilisateur est informé de cliquer sur l'icône dans le menu
- **Site** : guide d'installation illustré avec captures d'écran annotées (flèches rouges)
  pour Zorin OS et Linux Mint

---

## v0.8.8.0
**Compatibilité GLF-OS · Barre de progression · Lancement Zorin**

Corrections basées sur les tests terrain (Fedora, Mageia, Zorin, LM, GLF-OS) :

- **GLF-OS** : `#!/bin/bash` remplacé par `#!/usr/bin/env bash` — le shell est
  trouvé là où il est réellement installé sur la distribution
- **Barre de progression** (Fedora/Mageia) : remplacement des `sleep` fixes par
  `--pulsate` (animation continue) + fermeture propre via `kill $PID`.
  Plus de barre figée ou vide : elle s'anime dès le début et se ferme exactement
  à la fin de l'installation
- **Lancement post-install** (Zorin/GNOME) : `setsid nohup python3` — `setsid`
  crée un nouveau groupe de processus totalement détaché du script parent.
  GNOME ne peut plus tuer FreeSmartSync quand le script se termine
- **Permissions** : `chmod +x freesmartsync.py` aussi dans le répertoire source

---

## v0.8.7.9
**Installation — simplification et fiabilité**
- **Suppression du fichier `.desktop`** installeur : source de problèmes sur toutes les
  distributions (KDE, GNOME, Nautilus, Nemo — chacun l'interprète différemment).
  Un seul fichier à lancer : `CLIC-DROIT-Executer-pour-installer-FreeSmartSync.sh`
- **Barre de progression** désormais visible dès le début de la copie des fichiers
  (évite l'impression de plantage signalée sur Mageia)
- **Lancement post-install** : `cd "$INSTALL_DIR" && python3 freesmartsync.py`
  — le changement de répertoire évite les erreurs d'imports relatifs sur Zorin/Mint
- Nettoyage des `sleep` et `update-desktop-database` en double dans le script

---

## v0.8.7.8
**Lanceur .desktop et lancement post-install**
- **Fichier .desktop** : `readlink -f "$0"` (bugué — retournait le chemin de bash)
  remplacé par `%k | sed 's|file://||'` — standard universel KDE et GNOME
- **Terminal=true** dans le .desktop : permet de voir les erreurs au double-clic
  au lieu d'un écran noir silencieux
- **Lancement post-install** : simplifié en `nohup python3` direct (plus fiable
  que `gtk-launch` dont le cache peut ne pas être à jour immédiatement)

---

## v0.8.7.7
**Corrections Mageia · Lancement universel · Permissions**
- **Mageia** : nom du paquet corrigé `python3-pyqt5` → `python3-qt5`
- **Script** : auto `chmod +x` au démarrage (perms parfois perdues à l'extraction du zip)
- **Lancement post-install** : utilise `gtk-launch freesmartsync` si disponible,
  sinon `nohup python3` — plus fiable que `setsid` sur tous les DE
- **Fichier .desktop installeur** : suppression de `%k` (variable KDE uniquement),
  remplacé par `readlink -f "$0"` universel
- **README.md** : section ⚠️ obligatoire sur `chmod +x` avant installation,
  tableau des distributions avec notes par distro

---

## v0.8.7.6
**Script d'installation — corrections mineures**
- Suppression de la popup intermédiaire avant pkexec (inutile, pkexec ouvre sa propre fenêtre)
- Fallback `cp -r` : nettoyage des .sh et .desktop dans le répertoire d'installation
- Logique Mageia/pkexec inchangée (stable depuis v0.8.7.5)

---

## v0.8.7.5
**Correction installation Mageia**
- Mageia : le script d'installation utilise désormais `su -c "urpmi ..."` directement,
  sans passer par `pkexec` (qui ne trouve pas `urpmi` dans son environnement restreint)
- Les autres distributions continuent d'utiliser `pkexec` (Polkit) avec vérification
  post-installation + fallback `sudo`
- Ajout d'un message d'erreur visible si PyQt5 est manquant au lancement

---

## v0.8.7.4
**Installation des dépendances — compatibilité Mageia/Fedora**
- Remplacement de `echo PASSWORD | sudo -S` (non sécurisé) par :
  1. `pkexec` (Polkit) en priorité — fenêtre native du système, universel
  2. `su -c "commande" root` — fallback pour Mageia (utilisateur non sudoer)
  3. `sudo` — dernier recours
- Détection du bureau avec `xdg-user-dir DESKTOP` (gère Bureau/Desktop/Escritorio)
- `kbuildsycoca5/6` sur le lanceur bureau pour KDE Plasma

---

## v0.8.7.3
**Correction définitive des profils + sécurité script**

- **Bug profils corrigé** : le script de désinstallation ne touche plus à `config.json`
  quand l'utilisateur choisit de conserver ses données. L'application retrouve son état
  exact (`setup_done=True`, profils intacts) sans passer par le wizard.
- **ReconnectDialog** redessinée : les profils sont affichés en premier, le profil
  unique est pré-sélectionné automatiquement. Bouton principal = "Lancer", secondaire = "Aide"
- **Sécurité .sh** : `rm -rf "$INSTALL_DIR"` protégé par
  `[ -n "$INSTALL_DIR" ] && [ "$INSTALL_DIR" != "/" ]`

---

## v0.8.7.2
**Désinstallation et profils**
- Dialog désinstallation reformulé : **OUI = conserver** la config et les profils
  (comportement naturel — l'user ne perd plus ses profils par erreur)
- Un seul lanceur `.desktop` universel (suppression des lanceurs multiples)
- Le wizard retrouve bien les profils existants si la config a été conservée

---

## v0.8.7.1
**Corrections**
- **Liens À propos vraiment cliquables** : remplacement du QLabel par QTextBrowser
  → ouvre le navigateur système sur tous les DE (GNOME, KDE, Cinnamon, XFCE)
- **Lancement Zorin/Ubuntu** : ajout de `installer.sh` (script minimal sans caractères
  spéciaux) et `.desktop` pointant vers lui avec `chmod +x` automatique
- **URL GitHub corrigée** : `https://github.com/joffrey-d/FreeSmartSync`

---

## v0.8.7
**Corrections majeures**

- **Liens cliquables dans À propos** : `setOpenExternalLinks(True)` +
  `TextBrowserInteraction` — email, site et GitHub sont maintenant vraiment cliquables
- **Profils retrouvés après désinstall/réinstall** :
  - La désinstallation met `setup_done=False` (sans supprimer les profils si l'user dit Non)
  - Au prochain lancement, le wizard se relance et les profils existants sont détectés
  - Le message de désinstallation est maintenant explicite sur ce qui est conservé
- **Icône KDE Plasma** : toutes les tailles PNG ajoutées au QIcon
  (`addFile` pour icon_256.png) — KDE Plasma utilise la meilleure résolution disponible

---

## v0.8.6.9
**Bugs corrigés · Email & site · Icône KDE**

- **Wizard profil existant** : après réinstallation, les profils existants sont maintenant
  détectés et auto-sélectionnés (l'option n'est plus grisée)
- **Désinstallation** : message clarifié — la config ET les profils sont conservés si
  l'utilisateur choisit "Non". Plus de surprise à la réinstallation
- **Icône KDE Plasma** : l'icône est installée dans `~/.local/share/icons/hicolor/256x256/apps/`
  → KDE la trouve via le thème d'icônes (`fromTheme("freesmartsync")`)
- **Lanceur Fedora/KDE** : détecte automatiquement konsole, gnome-terminal ou xterm
- **À propos** : email `freesmartsync@free.fr`, lien site web, lien GitHub ajoutés

---

## v0.8.6.8
**Icône verte lumineuse (icône 3) · README & ROADMAP complets · Lanceur Fedora/KDE**
- Icône 3 (vert clair radial, flèches blanches épaisses) adoptée définitivement
- Icône intégrée dans toutes les tailles : 512, 256, 128, 64, 48, 32, 16px + .ico Windows
- README.md entièrement réécrit : tableau distributions, structure projet, guide complet
- ROADMAP.md restructuré avec statuts clairs (réalisé / en cours / planifié)
- Ajout `Lancer-Installeur-FreeSmartSync-Fedora-KDE.desktop` pour faciliter le lancement sur Fedora/KDE
- Amélioration du double-clic lanceur : gestion `gio set trusted` multi-DE (GNOME, Cinnamon, KDE)

---

## v0.8.6.7
**StartupWMClass — Icône dans les fenêtres Linux**
- `StartupWMClass=freesmartsync` dans le .desktop installé
- `setApplicationName("freesmartsync")` avant QApplication()
- `setApplicationDisplayName("FreeSmartSync")` pour l'affichage utilisateur
- `Exec=python3 "$INSTALL_DIR/freesmartsync.py"` (simplifié, sans bash -c)
- Ces 3 valeurs sont cohérentes → le gestionnaire de fenêtres trouve l'icône

---

## v0.8.6.6
**Icône dans toutes les fenêtres via QApplication**
- `QApplication.setWindowIcon()` propagation automatique
- Icône ajoutée dans : MainWindow, WizardWindow, ReconnectDialog, MiniWizard,
  ProfileDialog, ProfileEditDialog, PreviewDialog, SummaryDialog, AboutDialog
- Bouton 🔔 Mises à jour : feedback "À jour ✅" si aucune nouvelle version

---

## v0.8.6.5
**Bouton Mises à jour · Nouvelle identité visuelle**
- Bouton 🔔 Mises à jour dans la barre principale
- Frames d'animation pour le tray (4 rotations)
- Nouvelle icône premium (émeraude dégradé)

---

## v0.8.6.2
**Restauration explorateur ADB fonctionnel**
- Code ADB restauré depuis v0.8.5.8-fix13 (version connue fonctionnelle)
- Détection automatique du téléphone au démarrage via `adb devices`
- freesmartsync.py nettoyé

---

## v0.8.6.1
**Tentative correction explorateur ADB**
- Réécriture avec shell POSIX for loop — remplacé par v0.8.6.2

---

## v0.8.6
**Nouvelle branche stable · Explorateur ADB · Corrections profils**
- Explorateur ADB : 3 méthodes en cascade (ls -F, find, ls+test -d)
- Profil actif sauvegardé avant de switcher (plus de perte de dossiers)
- Label profil mis à jour immédiatement après sélection
- Icône Fedora Cinnamon : Exec avec guillemets pour chemins avec espaces

---

## v0.8.5.8-fix14
**Corrections code (revue complète)**
- Doublon Tel↔PC corrigé
- on_done cancelled géré correctement
- wizard page_dest.refresh(lang) corrigé

---

## v0.8.5.8-fix13
**Profils : sauvegarde + ADB auto-detect**
- Profil actif sauvegardé dans profiles.json avant switch
- Explorateur ADB : détection auto du device connecté
- Icône Fedora Cinnamon corrigée

---

## v0.8.5.8-fix12
**Compatibilité Mageia et GLF-OS**
- Mageia : `su -c` au lieu de `sudo`
- GLF-OS : détection par `shutil.which("nix-env")`
- Fallback détection par binaire présent

---

## v0.8.5.8-fix11 et antérieures
Corrections multiples de la logique de sync, exclusions système Android,
protection anti-suppression massive, scan amélioré.
Voir historique Git pour le détail complet.

---
