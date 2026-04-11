# Notes de version — FreeSmartSync

---

## v0.8.6.9 — Actuelle
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
