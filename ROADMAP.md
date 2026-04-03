# Feuille de route — FreeSmartSync Beta

> Ce document présente les évolutions prévues et les idées à l'étude pour les prochaines versions de FreeSmartSync.
> L'ordre n'est pas définitif — les priorités peuvent évoluer selon les retours utilisateurs.

---

## 🚀 Prochaine version — v0.9.0

### AppImage universelle
Distribution en un seul fichier `.AppImage` autonome — Python + PyQt5 embarqués.
Objectif : double-clic et ça tourne, sans aucune installation, sur toutes les distributions Linux.
*En cours de développement — compatibilité Debian/Ubuntu/Mageia en cours de résolution.*

### Site web
Hébergement chez Free (Joffrey) — page de présentation, téléchargement de l'AppImage, FAQ.
L'URL du site alimentera le système de mise à jour automatique.

### Fonctionnalités v0.9.0
- Vitesse de transfert en temps réel (Mo/s)
- Estimation du temps restant pendant la sync
- Historique des synchronisations consultable depuis l'interface
- Son de notification optionnel en fin de sync (configurable)

---

## 📱 Application mobile — FreeSmartSync App
*Projet en cours de réflexion*

Une application Android compagnon pour FreeSmartSync permettrait :
- D'activer/désactiver le débogage USB directement depuis l'app (contournement de la manipulation manuelle)
- De suivre l'état d'une synchronisation en cours depuis le téléphone
- De déclencher une sync à distance

---

## 🪟 Portage Windows — v1.x
*Projet prévu après stabilisation de la version Linux*

FreeSmartSync sera porté sur Windows avec :
- Installeur `.exe` natif (Inno Setup)
- Interface identique — même expérience utilisateur
- Embarquage Python + PyQt5 via PyInstaller
- Détection ADB Windows automatique

Le portage sera réalisé une fois la version Linux v1.0 jugée stable et diffusée.

---

## 🔮 Idées à l'étude (non planifiées)

### Support iPhone
Intégration de `libimobiledevice` pour synchroniser les iPhones.
- Wizard avec choix Android/iPhone dès l'écran 2
- Même interface, moteur de transfert différent (ifuse/idevicebackup2)
- *Note : Apple restreint de plus en plus l'accès externe — fiabilité à évaluer*

### Synchronisation Wi-Fi
Connexion ADB via Wi-Fi (sans câble USB) une fois le débogage activé.
- Plus pratique pour les syncs quotidiennes
- Requiert une configuration initiale via USB

### Planification automatique
Lancer une synchronisation automatiquement quand le téléphone est détecté.
- Détection de connexion USB en arrière-plan
- Popup de confirmation avant lancement automatique

### Profils de synchronisation
Plusieurs configurations sauvegardées (ex: "Backup complet", "Photos seulement").
- Changement de profil en un clic
- Utile pour synchroniser plusieurs téléphones

### Flathub
Publication sur Flathub pour une installation standardisée sur toutes les distributions.
Requiert : tests validés sur 5+ distributions, documentation complète.

---

## ✅ Déjà réalisé

- Sync bidirectionnelle Tel↔PC
- Journal intelligent (distinction nouveau fichier / suppression volontaire)
- Wizard guidé 8 étapes avec procédures par marque
- Garde-fous (confirmation avant suppression massive)
- System Tray avec icône animée
- Rappel sécurité débogage USB à la fermeture
- Assistant de reconnexion au relancement
- Sélection multiple de dossiers
- Mise à jour automatique (détection GitHub)
- Support FR/EN
- Compatibilité : Ubuntu, Debian, Fedora, Mint, Zorin, Arch, Mageia, openSUSE, GLF-OS

---

*FreeSmartSync est un projet open source sous licence GPL v3.*
*Idée originale et conception : Joffrey — Développement : Claude (Anthropic)*
