# FreeSmartSync v0.8.6.7

**Synchronisation bidirectionnelle Android ↔ Linux**

> Idée & conception : Joffrey | Développement : Claude (Anthropic) | Licence : GPL v3

---

## Qu'est-ce que FreeSmartSync ?

FreeSmartSync synchronise automatiquement vos fichiers entre votre smartphone Android et votre PC Linux — dans les deux sens, avec prévisualisation complète avant chaque action.

**Free** = Libre & Gratuit | **Smart** = Smartphone | **Sync** = Synchronisation

---

## Fonctionnalités

- 🔄 **Sync bidirectionnelle** — Tel→PC et PC→Tel, propagation des suppressions
- 🧠 **Journal intelligent** — distingue "nouveau fichier" de "suppression volontaire"
- 🔍 **Prévisualisation** — liste de toutes les opérations avant confirmation
- 👤 **Profils multiples** — un profil par téléphone ou utilisateur
- 📁 **Explorateur ADB intégré** — sélection multiple de dossiers par cases à cocher
- 🛡️ **Protection anti-suppression** — garde-fou si suppressions anormalement nombreuses
- 🔔 **Vérification de mises à jour** — bouton dédié, vérification GitHub à la demande
- 🖼️ **Résumé visuel** — miniatures des fichiers copiés en fin de synchronisation
- 🔒 **Rappel sécurité USB** — invitation à désactiver le débogage à la fermeture
- 🐧 **Multi-distributions** — Ubuntu, Fedora, Mint, Zorin, Arch, Mageia, openSUSE, GLF-OS

---

## Installation rapide

### Ubuntu / Debian / Mint / Zorin OS ✅ Testé et stable
```bash
# Téléchargez le zip, extrayez, puis :
# Clic droit sur CLIC-DROIT-Executer-pour-installer-FreeSmartSync.sh
# → "Exécuter comme programme"
```

### Fedora / RHEL ✅ Testé (KDE Cinnamon)
```bash
# Depuis un terminal :
bash CLIC-DROIT-Executer-pour-installer-FreeSmartSync.sh
# Ou utilisez le fichier Lancer-Installeur-FreeSmartSync-Fedora-KDE.desktop
```

### Arch / Manjaro / Mageia / openSUSE / GLF-OS ⚠️ Supporté (manipulation terminal possible)
```bash
bash CLIC-DROIT-Executer-pour-installer-FreeSmartSync.sh
```

---

## Prérequis

| Composant | Version | Installation |
|-----------|---------|-------------|
| Python | 3.8+ | Installé automatiquement |
| PyQt5 | 5.15+ | Installé automatiquement |
| ADB | Tout | Installé automatiquement |
| Android | 8.0+ | Sur votre téléphone |
| OS | Linux 64 bits | — |

Le script d'installation installe automatiquement toutes les dépendances selon votre distribution.

---

## Lancement

Après installation, FreeSmartSync est accessible via :
- **Menu des applications** → chercher "FreeSmartSync"
- **Bureau** → double-clic sur l'icône (si créée par l'installeur)
- **Terminal** : `python3 /chemin/vers/freesmartsync.py`

---

## Premier lancement

1. **Activer le débogage USB** sur votre téléphone Android  
   → Le wizard vous guide selon votre marque (Samsung, Xiaomi, Pixel, OnePlus…)

2. **Brancher le téléphone** via câble USB  
   → Accepter la demande d'autorisation sur le téléphone

3. **Créer un profil** et sélectionner vos dossiers  
   → Explorateur ADB intégré avec sélection multiple

4. **Lancer la synchronisation**  
   → Prévisualisation complète avant tout changement

---

## Activer le débogage USB (procédure générale)

1. Aller dans **Paramètres** → **À propos du téléphone**
2. Appuyer **7 fois** sur **Numéro de build**
3. Retourner dans **Paramètres** → **Options développeur**
4. Activer **Débogage USB**
5. Brancher le câble USB → accepter l'autorisation ADB

⚠️ Désactivez le débogage USB après chaque utilisation.

---

## Distributions testées

| Distribution | Statut | Notes |
|---|---|---|
| Ubuntu 22.04/24.04 | ✅ Stable | Testé |
| Linux Mint 21/22 | ✅ Stable | Testé |
| Zorin OS 17/18 | ✅ Stable | Testé |
| Fedora 39/40 KDE | ✅ Stable | Testé, lancer via terminal |
| Fedora Cinnamon | ✅ Stable | Testé |
| Arch Linux | ⚠️ Supporté | Installation via terminal |
| Manjaro | ⚠️ Supporté | Installation via terminal |
| Mageia | ⚠️ Supporté | Utilise `su -c` au lieu de sudo |
| openSUSE | ⚠️ Supporté | Installation via terminal |
| GLF-OS | ⚠️ Supporté | Nécessite nix-env dans PATH |

---

## Versions disponibles

| Version | Branche | Statut |
|---|---|---|
| v0.8.6.5 | `main` | ✅ Stable — recommandée |
| v0.8.6.7 | `develop` | ⚙️ Développement — testeurs bienvenus |
| Windows | `develop` | 🚧 Pre-Alpha — non testé |
| AppImage | — | 🚧 En cours de développement |

---

## Structure du projet

```
freesmartsync/
├── freesmartsync.py              # Point d'entrée principal
├── modules/
│   ├── main_window.py            # Interface principale
│   ├── worker.py                 # Thread de synchronisation ADB
│   ├── wizard.py                 # Assistant de configuration
│   ├── profiles.py               # Gestion des profils multiples
│   ├── dialogs.py                # Fenêtres : preview, résumé, grille
│   ├── adb_explorer.py           # Explorateur de dossiers ADB
│   ├── updater.py                # Vérification des mises à jour GitHub
│   ├── deps.py                   # Détection distrib + installation deps
│   ├── config.py                 # Configuration locale
│   └── i18n.py                   # Traductions FR/EN
├── assets/
│   ├── icon.png                  # Icône principale (512px)
│   ├── icon_anim1-4.png          # Frames animation tray
│   └── icon.svg                  # Source vectorielle
├── CLIC-DROIT-Executer-pour-installer-FreeSmartSync.sh
├── Double-clic-pour-installer-FreeSmartSync.desktop
├── Lancer-Installeur-FreeSmartSync-Fedora-KDE.desktop
├── CHANGELOG.md
├── ROADMAP.md
├── LICENSE
└── version.json
```

---

## Contribute / Contribuer

- 🐛 **Bug ?** → Ouvrir une issue sur GitHub
- 💡 **Idée ?** → Discussions GitHub
- 🔧 **Pull Request** → Bienvenue !

---

## Licence

GPL v3 — [Voir le fichier LICENSE](LICENSE)

---

*FreeSmartSync — parce que votre téléphone mérite une vraie sauvegarde.*
