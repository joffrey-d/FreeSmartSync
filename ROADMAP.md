# ROADMAP — FreeSmartSync

> Statut actuel : **v0.8.6.7** (develop) | **v0.8.6.5** (stable)

---

## ✅ Réalisé

### v0.8.x — Stabilisation & Fonctionnalités
- [x] Synchronisation bidirectionnelle Android ↔ Linux via ADB
- [x] Journal de synchronisation persistant (distinction nouveau/supprimé)
- [x] Prévisualisation complète avant chaque sync
- [x] Résumé visuel avec miniatures en fin de sync
- [x] Profils multiples (un profil par téléphone/utilisateur)
- [x] Explorateur ADB intégré avec sélection multiple
- [x] Protection anti-suppression massive (garde-fous)
- [x] Exclusion automatique fichiers système Android (.thumbnails, .trashed-*, .cache…)
- [x] Guide de connexion par marque (Samsung, Xiaomi, Pixel, OnePlus…)
- [x] Rappel désactivation débogage USB à la fermeture
- [x] Détection automatique du téléphone au démarrage
- [x] Vérification des mises à jour GitHub (automatique au démarrage + bouton manuel)
- [x] Support 9+ distributions Linux (apt, dnf, pacman, zypper, urpmi, nix)
- [x] Icône dans toutes les fenêtres via StartupWMClass + setApplicationName
- [x] Première version Windows (pre-alpha)

---

## 🚧 En cours

### v0.9.0 — AppImage universelle
- [ ] AppImage autonome (Python + PyQt5 embarqués)
- [ ] Zéro installation requise sur la machine cible
- [ ] Compatible Ubuntu 20.04+, Debian 11+, Fedora, Arch, Manjaro…
- [ ] Distribution directe depuis le site web

---

## 📋 Planifié

### v0.9.x — Améliorations UX
- [ ] **Double-clic universel** pour lancer l'installeur sur toutes les distros
  *(Zorin/Ubuntu : OK | Fedora/KDE : en cours)*
- [ ] Synchronisation partielle : sélectionner des sous-dossiers spécifiques
- [ ] Filtre par extension (ex: ne sync que les .jpg)
- [ ] Planification automatique (cron / systemd timer)
- [ ] Notification système (libnotify) en fin de sync

### v1.0.0 — Version stable majeure
- [ ] **Windows** — Installateur complet (wizard, toutes dépendances incluses)
- [ ] Sync Wi-Fi (ADB over TCP/IP) en complément USB
- [ ] Interface de gestion des conflits (choix fichier par fichier)
- [ ] Thème sombre / clair au choix
- [ ] Support macOS (expérimental)

---

## 💭 Idées futures

- Sync Cloud (Google Drive, Nextcloud) depuis le téléphone
- Plugin Nautilus / Dolphin pour sync directe depuis le gestionnaire de fichiers
- Mode CLI (sans interface graphique) pour les serveurs
- Sauvegarde chiffrée

---

*Contributions bienvenues ! Ouvrez une issue ou une PR sur GitHub.*
