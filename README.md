# FreeSmartSync v0.8.8.3

**Synchronisation bidirectionnelle Android ↔ Linux**

> Idée & conception : Joffrey | Développement : Claude (Anthropic) | Licence : GPL v3

🌐 **Site officiel** : [joffrey-d.github.io/FreeSmartSync](https://joffrey-d.github.io/FreeSmartSync/)
✉️ **Contact** : freesmartsync@free.fr

---

## Qu'est-ce que FreeSmartSync ?

FreeSmartSync synchronise automatiquement vos fichiers entre votre smartphone Android et votre PC Linux — dans les deux sens, avec prévisualisation complète avant chaque action.

**Free** = Libre & Gratuit | **Smart** = Smartphone | **Sync** = Synchronisation

---

## ⚠️ Étape obligatoire : rendre le script exécutable

Après extraction du zip, le script d'installation **doit être rendu exécutable** :

```bash
chmod +x CLIC-DROIT-Executer-pour-installer-FreeSmartSync.sh
```

**Ou depuis le gestionnaire de fichiers :**
> Clic droit sur le fichier `.sh` → Propriétés → onglet Permissions → cocher "Autoriser l'exécution"

---

## Installation

### Ubuntu / Debian / Mint / Zorin OS ✅ Testé
```bash
chmod +x CLIC-DROIT-Executer-pour-installer-FreeSmartSync.sh
# Puis : clic droit → Exécuter comme programme
# Ou :
bash CLIC-DROIT-Executer-pour-installer-FreeSmartSync.sh
```

### Fedora ✅ Testé (KDE & Cinnamon)
```bash
chmod +x CLIC-DROIT-Executer-pour-installer-FreeSmartSync.sh
bash CLIC-DROIT-Executer-pour-installer-FreeSmartSync.sh
```

### Mageia ⚠️ Le mot de passe root est demandé (utilisateur non sudoer par défaut)
```bash
chmod +x CLIC-DROIT-Executer-pour-installer-FreeSmartSync.sh
bash CLIC-DROIT-Executer-pour-installer-FreeSmartSync.sh
# → Entrez le mot de passe root quand demandé
```

### Arch / Manjaro / openSUSE / GLF-OS ⚠️ Supporté
```bash
chmod +x CLIC-DROIT-Executer-pour-installer-FreeSmartSync.sh
bash CLIC-DROIT-Executer-pour-installer-FreeSmartSync.sh
```

---

## Fonctionnalités

- 🔄 **Sync bidirectionnelle** — Tel→PC et PC→Tel, propagation des suppressions
- 🧠 **Journal intelligent** — distingue "nouveau fichier" de "suppression volontaire"
- 🔍 **Prévisualisation** — liste de toutes les opérations avant confirmation
- 👤 **Profils multiples** — un profil par téléphone ou utilisateur
- 📁 **Explorateur ADB intégré** — sélection multiple de dossiers par cases à cocher
- 🛡️ **Protection anti-suppression** — garde-fou si suppressions anormalement nombreuses
- 🔔 **Mises à jour à la demande** — bouton dédié, vérification GitHub à la demande
- 🖼️ **Résumé visuel** — miniatures des fichiers copiés en fin de synchronisation

---

## Distributions testées

| Distribution | Statut | Notes |
|---|---|---|
| Ubuntu 22.04/24.04 | ✅ Stable | Testé |
| Linux Mint 21/22 | ✅ Stable | Testé |
| Zorin OS 17/18 | ✅ Stable | Testé |
| Fedora 39/40 KDE | ✅ Stable | Testé |
| Fedora Cinnamon | ✅ Stable | Testé |
| Mageia | ⚠️ Supporté | Mot de passe root requis, paquet python3-qt5 |
| Arch / Manjaro | ⚠️ Supporté | Via terminal |
| openSUSE | ⚠️ Supporté | Via terminal |
| GLF-OS | ⚠️ Supporté | nix-env dans PATH requis |

---

## Prérequis

| Composant | Version | Installation |
|---|---|---|
| Python | 3.8+ | Automatique |
| PyQt5 | 5.15+ | Automatique |
| ADB | Tout | Automatique |
| Android | 8.0+ | Sur votre téléphone |
| OS | Linux 64 bits | — |

---

## Versions disponibles

| Version | Branche | Statut |
|---|---|---|
| v0.8.6.9 | `main` | ✅ Stable — recommandée |
| v0.8.8.3 | `develop` | ⚙️ Développement |
| Windows | `develop` | 🚧 Pre-Alpha |
| AppImage | — | 🚧 En cours |

---

## Licence

GPL v3 — [Voir le fichier LICENSE](LICENSE)
