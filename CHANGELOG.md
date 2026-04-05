# Notes de version — FreeSmartSync

---

## v0.8.5.8-fix13 — Actuelle
**Corrections profils**
- Profil actif sauvegardé dans profiles.json AVANT de switcher → plus de perte de dossiers
- Label profil actif mis à jour immédiatement après sélection
- Explorateur ADB dans l'édition de profil : détection automatique du device connecté
  (plus besoin de saisir l'ID manuellement — branche direct sur le téléphone branché)

**Correction icône Fedora Cinnamon**
- Exec du .desktop installé entouré de guillemets + `cd "$INSTALL_DIR"`
  → fonctionne maintenant avec les chemins contenant des espaces

---

## v0.8.5.8-fix12
**Corrections compatibilité**
- Mageia : `su -c "commande" root` au lieu de `sudo` — fonctionne même sans sudoers
- GLF-OS : détection par `shutil.which("nix-env")` en plus de l'ID — plus fiable
- Fallback détection par binaire présent pour toute distro non reconnue
- Script AppImage v0.9 corrigé : Python 3.10.19 (URL fixe), AppRun PYTHONHOME/PYTHONPATH corrects

---

## v0.8.5.8-fix11
**Corrections compatibilité distributions**
- GLF-OS : détecté correctement (ID glf-os, base NixOS)
- Mageia : utilise `su -c "commande" root` au lieu de `sudo` (user peut ne pas être sudoer)
- Fallback automatique : si la distro n'est pas reconnue par ID, détection par binaire présent
  (apt-get, dnf, pacman, zypper, urpmi, nix-env)
- Message d'erreur enrichi si gestionnaire non reconnu (commandes manuelles affichées)

**AppImage v0.9.0**
- Méthode corrigée : Python portable niess/python-appimage + pip PyQt5 + appimagetool
- Testé et fonctionnel sur Mint, Fedora, GLF-OS

---

## v0.8.5.8-fix10
**Corrections**
- Exclusion des fichiers `.trashed-XXXXXX-*` (corbeille Android) et `.pending-*`
  → Ces fichiers ne seront plus copiés sur le PC ni supprimés lors de la sync
- Suppression dossiers vides sur le tel améliorée :
  - Utilisation de `find -empty -type d` (plus fiable que `ls | wc -l`)
  - Gère correctement les sous-dossiers avec `.nomedia` ou fichiers cachés
  - Log affiché pour chaque dossier vide supprimé
  - Appelé après toutes les suppressions Tel (pas seulement si to_delete_tel non vide)

---

## v0.8.5.8-fix9
**Corrections**
- Miniatures .jpg dans le récap : utilisation de `QImage` au lieu de `QPixmap` direct
  → chargement plus fiable sur toutes les distributions (Fedora, Ubuntu, Zorin, Mageia)
  → fallback automatique avec format explicite si chargement échoue

---

## v0.8.5.8-fix8
**Correction finale — Logique de sync bidirectionnelle**

Symptôme : supprimer des fichiers du PC puis relancer la sync les recopiait depuis le Tel.

Cause : fix7 avait supprimé la règle B (supprimer du Tel quand absent du PC + dans journal).

Règles maintenant mutuellement exclusives par construction :
- Fichier sur Tel + absent PC + PAS dans journal → Règle A → copier Tel→PC (nouveau)
- Fichier sur Tel + absent PC + DANS journal    → Règle B → supprimer du Tel (supprimé du PC)
- Fichier absent Tel + sur PC + DANS journal    → Règle G → supprimer du PC (supprimé du Tel)

Ces trois règles sont garanties sans chevauchement.

---

## v0.8.5.8-fix7
**Correction critique — Bug doublon Tel→PC / Suppr Tel**

Symptôme : relancer la sync juste après une sync donnait 119 Tel→PC + 117 Suppr Tel.

Cause : un fichier peut être à la fois :
- dans `to_copy_tel_to_pc` (présent sur Tel, absent du PC)
- dans `to_delete_tel` (dans le journal, absent du PC, présent sur Tel)
Ces deux conditions se vérifient pour le même fichier → action contradictoire !

Correction — Règles de sync mutuellement exclusives (A à H) :
- Si un fichier est sur Tel ET absent du PC → TOUJOURS copier Tel→PC (règle B)
  même s'il est dans le journal (récupération de sync échouée)
- `to_delete_tel` est volontairement vide — on ne supprime jamais du Tel un fichier
  qui s'y trouve encore
- Règle G (Suppr PC) : seulement si absent du Tel ET dans journal ET présent sur PC

---

## v0.8.5.8-fix6
**Corrections code (revue complète)**
- Fix doublon : un fichier ne peut plus être dans Tel→PC ET PC→Tel simultanément
- Fix on_done : gestion correcte du cas "sync annulée" (plus d'erreur après Non dans prévisualisation)
- Fix wizard : page_dest.refresh(lang) appelé correctement à l'idx 7

---

## v0.8.5.8-fix5
**Correction : Détection des fichiers modifiés Tel→PC**

Problème : le fichier KeePass modifié sur le téléphone n'était pas copié sur le PC.

Cause : la détection de modification ne fonctionnait que dans un sens (PC→Tel).
Pour les fichiers existant des deux côtés, seule la copie Tel→PC des fichiers absents était gérée.

Corrections :
- **Scan amélioré** : récupération de la taille ET du timestamp (`stat -c '%n|%s|%Y'`) en une seule
  passe par dossier — avec fallback individuel pour les petits dossiers
- **Détection Tel→PC** : si taille ou date différente et Tel plus récent → copié vers PC
  - Taille différente + Tel plus récent (mtime) → copie Tel→PC
  - Même taille + Tel plus récent de 60s+ → copie Tel→PC  
  - Taille différente sans mtime fiable + Tel plus gros → copie Tel→PC (cas KeePass ajout entrée)
- **Détection PC→Tel** affinée : taille ET date comparées (pas seulement la date)

---

## v0.8.5.8-fix4
**Correction critique — Dossiers absents = zéro suppression**

Problème identifié via log utilisateur :
- Dossiers (Movies, Music, GPX, etc.) absents du téléphone → scan échoue
- Leurs fichiers semblent "disparus du tel" → détectés à tort pour suppression PC
- 485 suppressions PC erronées détectées

Corrections :
- **Vérification préalable** : `test -d` avant le scan — distingue "dossier absent" de "erreur"
- **Règle absolue** : dossier absent ou scan échoué → ZÉRO suppression PC pour ce dossier
- **Journal conservé** : les fichiers des dossiers non scannés restent dans le journal
- Log clair : liste des dossiers ignorés et raison
- Seuil garde de sécurité abaissé à 50 fichiers (au lieu de 100)

---

## v0.8.5.8-fix3
**Correction critique — Faux positifs suppressions PC**
- Cause identifiée : le dossier `.thumbnails` (cache miniatures Android) contient des milliers
  de fichiers régénérés automatiquement — ils existaient dans le journal mais pas sur le tel
  après régénération → détectés à tort comme "supprimés du tel → supprimer du PC"
- **Exclusion automatique des dossiers/fichiers système Android** :
  `.thumbnails`, `.trash`, `.cache`, `.android_secure`, `LOST.DIR`, `__MACOSX`, fichiers `.tmp`
- L'exclusion s'applique aussi bien au scan du téléphone qu'au parcours des fichiers PC
- La protection anti-suppression massive (fix2) reste active comme filet de sécurité

---

## v0.8.5.8-fix2
**Correction critique**
- Bug scan Android/busybox : `find -exec stat` échoue silencieusement sur certains appareils
  → scan incomplet → des milliers de faux positifs "à supprimer du PC" détectés
  → **Nouveau scan en 2 étapes** : `find` simple (fiable) + `ls -la` pour les stats
- **Garde de sécurité anti-suppression massive** : si plus de 15% des fichiers locaux
  et plus de 100 fichiers sont détectés comme "à supprimer", les suppressions PC sont
  BLOQUÉES et signalées dans la prévisualisation
- **Chemins complets** dans la prévisualisation (plus seulement les noms de fichiers)
- Onglet "BLOQUEES" dans la prévisualisation si le garde de sécurité s'est déclenché

---

## v0.8.5.8-fix
**Nouveautés**
- Prévisualisation avant synchronisation : une popup récapitule TOUT ce qui va se passer (copier, supprimer, mettre à jour) avec 2 boutons Confirmer/Annuler
- Détail séparé Tel->PC et PC->Tel dans le résumé de fin
- Onglet Erreurs dans le résumé de fin
- Profil actif affiché dans l'interface principale
- Fichier LICENSE inclus dans chaque version

**Corrections performances critiques**
- Scan ADB : remplacement de N appels `stat` individuels par 1 appel `find + stat` par dossier → 10x plus rapide sur 14000 fichiers
- Faux positifs "fichiers modifiés" supprimés : comparaison date avec tolérance 60s pour les timezones Android/PC
- Erreur O(n²) dans le calcul des fichiers à pousser → corrigé

**Corrections**
- Explorateur ADB : checkboxes au lieu de Ctrl+clic pour sélection multiple universelle
- Miniatures vidéo via ffmpeg si disponible
- Désinstallation : option suppression outils système (ADB)
- .desktop Zorin/GNOME : création sur le Bureau + marquage trusted

---

## v0.8.5.8
**Corrections**
- Détection fichiers modifiés : comparaison date de modification en plus de la taille → les fichiers comme KeePass sont maintenant détectés et synchronisés si modifiés
- Explorateur ADB : remplacement Ctrl+clic par **checkboxes** — sélection multiple universelle compatible toutes distributions (GNOME, KDE, Cinnamon, XFCE)
- Miniatures vidéo : extraction d'une frame réelle via `ffmpeg` si disponible
- Désinstallation : option suppression outils système (ADB) avec avertissement
- `.desktop` Zorin/GNOME : création d'un lanceur sur le Bureau + marquage "trusted" via `gio`
- Lancement post-installation : `setsid python3` avec `DISPLAY=:0` — plus fiable sur toutes les distros

---

## v0.8.5.7-fix
**Corrections**
- Animation connexion USB : HTML pur sans emoji, compatible toutes distributions (fini les rectangles noirs "NO GLYPH")
- Miniatures : icônes colorées dessinées en Qt (PDF rouge, vidéos noir/rouge, audio bleu, texte vert, archives orange) — taille augmentée à 130px
- Explorateur ADB accessible depuis l'édition de profil avec sélection multiple
- Lancement après installation : méthodes multiples (gtk-launch + setsid)
- Désinstallation : suppression install_dir + desktop + autostart + config optionnelle
- `.desktop` : utilisation de `realpath` pour compatibilité améliorée

---

## v0.8.5.7
**Nouveautés**
- Suppression du mot "Beta" partout dans l'interface
- Mention "Android uniquement" dans la présentation et le README
- Nouvelle étape 6 dans le wizard : **Gestion des profils** (créer/choisir/ignorer)
- Sélection de profil dans l'écran de reconnexion au démarrage
- Barre de progression séparée **PC → Tel** dans l'interface principale
- Log réinitialisé à chaque synchronisation et changement de profil
- README.md complet — guide d'installation et d'utilisation
- Signal `push_progress` dans le worker pour la progression PC→Tel

**Corrections**
- `.desktop` Fedora/KDE : meilleur chemin d'exécution
- Désinstallation : suppression de l'autostart

---

## v0.8.5.6
**Nouveautés**
- Gestion de profils multiples (bouton 👤 Profils) — un profil par téléphone/utilisateur
- Sélection de profil dans l'écran de reconnexion

**Corrections**
- Bug critique : bouton "Lancer FreeSmartSync" du MiniWizard ne fonctionnait pas
- Sécurité anti-double-lancement dans le MiniWizard
- Fichier `.desktop` d'installation corrigé (Fedora Cinnamon)

---

## v0.8.5.5
**Nouveautés**
- Sélection multiple de dossiers dans l'explorateur ADB (Ctrl+clic)
- Vérification de mise à jour automatique via GitHub + popup Télécharger/Plus tard
- Texte explicatif enrichi sur l'étape de sélection des dossiers
- Cadres de la page connexion téléphone en pleine largeur

**Corrections**
- Texte qui sautait dans la page connexion USB

---

## v0.8.5.4
**Corrections majeures**
- Nouveaux fichiers/dossiers créés sur le PC maintenant copiés vers le téléphone
- Dossiers vides sur le téléphone supprimés après sync
- Texte qui sautait dans la page connexion USB

---

## v0.8.5.3
**Nouveautés**
- Assistant de reconnexion au relancement
- Mini-wizard de reconnexion
- Rappel manuel à la fermeture pour désactiver le débogage USB

**Corrections**
- Bouton Suivant du wizard bloqué → résolu
- Tray : clic gauche toggle affichage/masquage
- Tray : menu "Afficher FreeSmartSync" maintenant fonctionnel

---

## v0.8.5.2
**Nouveautés**
- Présentation FreeSmartSync enrichie dans le wizard
- À propos : crédits détaillés + section sécurité
- Marque + modèle du téléphone dans le combo

**Corrections**
- À propos illisible → police 13-14px, fenêtre scrollable
- Tray : minimisation vers le tray

---

## v0.8.5.1
**Corrections**
- Étapes 4 et 5 du wizard inversées
- Écran connexion USB : cadres plus larges, police plus grande
- Bug bouton Suivant bloqué

---

## v0.8.5
**Nouveautés**
- Détection installation existante dans le script
- Menu Réinstaller / Désinstaller
- Écran connexion USB animé avec FAQ

---

## v0.8.0
**Nouveautés**
- Fenêtre principale maximisée
- System Tray avec animation et notifications
- Rappel désactivation débogage USB à la fermeture

---

## v0.7.0 — Première version
- Wizard 7 écrans
- Sync bidirectionnelle Tel↔PC via ADB
- Journal intelligent
- Bouton Désinstaller intégré
- Support : Ubuntu, Debian, Fedora, Arch, Mageia, openSUSE, GLF-OS
- Français et Anglais
