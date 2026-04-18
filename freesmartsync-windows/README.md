# FreeSmartSync

**Synchronisation bidirectionnelle Android ↔ Linux**

> ⚠️ **Compatible uniquement avec les smartphones Android.** Le support iPhone est prévu dans une version future.

---

## Qu'est-ce que FreeSmartSync ?

FreeSmartSync est un logiciel libre et gratuit qui synchronise votre smartphone **Android** avec votre ordinateur **Linux**, dans les deux sens, via le protocole ADB (Android Debug Bridge).

- **Free** = Libre et Gratuit
- **Smart** = Smartphone  
- **Sync** = Synchronisation

---

## Fonctionnalités

- 🔄 **Sync bidirectionnelle** — Tel→PC et PC→Tel
- 🧠 **Journal intelligent** — distingue nouveau fichier et fichier supprimé volontairement
- 👤 **Profils multiples** — un profil par téléphone ou par utilisateur
- 🛡️ **Garde-fous** — confirmation avant toute suppression massive
- 🔒 **Sécurité** — rappel de désactiver le débogage USB à la fermeture
- 🔔 **Notifications tray** — icône animée + résumé en fin de sync
- 🌍 **Français et Anglais**

---

## Distributions compatibles

| Distribution | Gestionnaire | Commande ADB |
|---|---|---|
| Ubuntu, Debian, Mint, Zorin, Pop!_OS | apt | `sudo apt install android-tools-adb` |
| Fedora, RHEL, Nobara | dnf | `sudo dnf install android-tools` |
| Arch, Manjaro, EndeavourOS | pacman | `sudo pacman -S android-tools` |
| Mageia, OpenMandriva | urpmi | `sudo urpmi android-tools` |
| openSUSE | zypper | `sudo zypper install android-tools` |
| GLF-OS, NixOS | nix | `nix-env -iA nixpkgs.android-tools` |

---

## Installation

### Méthode 1 — Double-clic (KDE/Fedora)
Double-cliquez sur `Double-clic-pour-installer-FreeSmartSync.desktop`

### Méthode 2 — Clic droit (GNOME/Zorin/Ubuntu/Cinnamon)
Clic droit sur `CLIC-DROIT-Executer-pour-installer-FreeSmartSync.sh` → **Exécuter comme programme**

### Méthode 3 — Terminal
```bash
bash CLIC-DROIT-Executer-pour-installer-FreeSmartSync.sh
```

---

## Guide d'utilisation

### Premier lancement — Wizard en 9 étapes

1. **Langue** — Français ou Anglais
2. **Présentation** — Fonctionnalités et disclaimer
3. **Dépendances** — Installation automatique ADB + Python + PyQt5
4. **Procédure débogage USB** — Guide par marque (Samsung, Xiaomi, Google, OnePlus, Huawei, Sony, Motorola)
5. **Connexion téléphone** — Branchez le câble USB
6. **Profils** — Créer ou choisir un profil de synchronisation
7. **Dossiers téléphone** — Sélectionnez les dossiers à synchroniser (Ctrl+clic = sélection multiple)
8. **Répertoire de sauvegarde** — Choisissez où sauvegarder sur le PC
9. **Résumé** — Vérification et lancement

### Lancement suivant

À chaque relancement, FreeSmartSync vous propose :
- **Oui, me guider** → Mini-assistant pour réactiver le débogage USB
- **Non, je sais le faire** → Accès direct à l'interface

### Synchronisation

1. Activez le **débogage USB** sur votre téléphone
2. Branchez le câble USB
3. Cliquez sur **🟢 Démarrer**
4. À la fermeture, pensez à **désactiver le débogage USB**

---

## Activation du débogage USB

### Samsung
Paramètres → À propos du téléphone → Appuyez 7 fois sur **Numéro de build** (ou Version du logiciel)  
→ Paramètres → Options développeur → **Débogage USB** → Activer

### Xiaomi
Paramètres → À propos du téléphone → Appuyez 7 fois sur **Version MIUI**  
→ Paramètres → Paramètres supplémentaires → Options développeur → **Débogage USB**

### Google Pixel
Paramètres → À propos du téléphone → Appuyez 7 fois sur **Numéro de build**  
→ Paramètres → Système → Options développeur → **Débogage USB**

> ⚠️ **Sécurité** : Désactivez le débogage USB après chaque session de synchronisation.

---

## Profils multiples

FreeSmartSync permet de gérer plusieurs profils (bouton 👤 Profils) :
- Chaque profil = **nom + dossiers téléphone + répertoire de sauvegarde**
- Idéal pour les foyers avec plusieurs smartphones
- Changement de profil en un clic depuis l'interface principale

---

## Mise à jour automatique

FreeSmartSync vérifie automatiquement au démarrage si une nouvelle version est disponible.  
Si oui, une popup propose de télécharger et installer la mise à jour.

---

## Désinstallation

Dans FreeSmartSync → bouton **🗑️ Désinstaller**  
Ou : relancez le script d'installation → choisissez **Désinstaller**

---

## Licence

GPL v3 — Logiciel libre et open source  
Code source : https://github.com/joffrey-d/FreeSmartSync

---

## Crédits

- **Idée originale & conception** : Joffrey
- **Développement** : Claude (Anthropic)
