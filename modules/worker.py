# modules/worker.py — FreeSmartSync v0.8.5.8-fix7

import os
import subprocess
import time
from datetime import datetime
from PyQt5 import QtCore

from modules.config import load_sync_state, save_sync_state

REMOTE_BASE              = "/sdcard"
DELETE_CONFIRM_THRESHOLD = 20
MAX_PC_DELETE_RATIO      = 0.15
MAX_PC_DELETE_ABSOLUTE   = 50

# Dossiers/fichiers système Android à ignorer
EXCLUDED_DIRS = {
    ".thumbnails", ".trash", ".Trash", ".Trash-1000",
    ".android_secure", "LOST.DIR", ".cache", "__MACOSX",
}
EXCLUDED_EXTENSIONS = {".tmp", ".temp", ".part"}

def is_excluded(rel_path):
    """True si le chemin doit être exclu du scan."""
    parts = rel_path.replace("\\", "/").split("/")
    basename = parts[-1] if parts else ""

    for part in parts:
        if part in EXCLUDED_DIRS:
            return True
        # Dossiers cachés système (sans extension = dossier)
        if part.startswith(".") and not os.path.splitext(part)[1]:
            return True

    # Fichiers corbeille Android : .trashed-XXXXXXX-nom.ext
    if basename.startswith(".trashed-"):
        return True

    # Fichiers/dossiers Android temporaires courants
    if basename.startswith(".pending-"):
        return True

    ext = os.path.splitext(rel_path)[1].lower()
    return ext in EXCLUDED_EXTENSIONS


class Worker(QtCore.QThread):
    progress        = QtCore.pyqtSignal(int)
    scan_progress   = QtCore.pyqtSignal(int)
    push_progress   = QtCore.pyqtSignal(int)
    status          = QtCore.pyqtSignal(str)
    current_file    = QtCore.pyqtSignal(str)
    log             = QtCore.pyqtSignal(str)
    done            = QtCore.pyqtSignal(dict)
    request_confirm = QtCore.pyqtSignal(list)
    preview_ready   = QtCore.pyqtSignal(dict)

    def __init__(self, folders, local_base, device_id, lang="fr"):
        super().__init__()
        self.running    = True
        self.paused     = False
        self.folders    = folders
        self.local_base = local_base
        self.device_id  = device_id
        self.lang       = lang

        self._confirm_mutex  = QtCore.QMutex()
        self._confirm_event  = QtCore.QWaitCondition()
        self._confirm_result = None

        self._preview_mutex  = QtCore.QMutex()
        self._preview_event  = QtCore.QWaitCondition()
        self._preview_result = None

        self.copied_tel_to_pc = []
        self.copied_pc_to_tel = []
        self.deleted_pc       = []
        self.deleted_tel      = []
        self.modified_pushed  = []
        self.count_skipped    = 0
        self.count_errors     = 0
        self.errors_list      = []

    def stop(self):
        self.running = False
        for m, c, a in [
            (self._confirm_mutex, self._confirm_event, "_confirm_result"),
            (self._preview_mutex, self._preview_event, "_preview_result"),
        ]:
            m.lock(); setattr(self, a, False); c.wakeAll(); m.unlock()

    def pause(self):  self.paused = True
    def resume(self): self.paused = False

    def confirm_result(self, accepted: bool):
        self._confirm_mutex.lock()
        self._confirm_result = accepted
        self._confirm_event.wakeAll()
        self._confirm_mutex.unlock()

    def preview_confirm(self, confirmed: bool):
        self._preview_mutex.lock()
        self._preview_result = confirmed
        self._preview_event.wakeAll()
        self._preview_mutex.unlock()

    def run_cmd(self, cmd, timeout=60):
        try:
            return subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, timeout=timeout
            )
        except subprocess.TimeoutExpired:
            self.log.emit(f"⚠️ Timeout : {cmd[4] if len(cmd) > 4 else ''}")
            class R:
                returncode=1; stdout=""; stderr="timeout"
            return R()

    def check_device(self):
        r = self.run_cmd(["adb", "devices"], timeout=5)
        return self.device_id in r.stdout

    # ─── Scan ────────────────────────────────────────────────

    def get_remote_files(self):
        """
        Scanne le téléphone dossier par dossier.
        Retourne (remote_stats, failed_folders).
        failed_folders = dossiers absents ou dont le scan a échoué.
        """
        remote_stats   = {}
        failed_folders = set()
        total          = len(self.folders)

        for i, folder in enumerate(self.folders):
            if not self.running:
                break
            self.log.emit(f"🔍 Scan : {folder}")
            path = f"{REMOTE_BASE}/{folder}"

            # Vérifier existence du dossier
            test = self.run_cmd(
                ["adb", "-s", self.device_id, "shell",
                 f"test -d \"{path}\" && echo OK || echo MISSING"],
                timeout=10
            )
            if "MISSING" in test.stdout or (test.returncode != 0 and "OK" not in test.stdout):
                self.log.emit(f"   ℹ️  {folder} absent du téléphone — ignoré")
                failed_folders.add(folder)
                self.scan_progress.emit(int((i + 1) * 100 / total))
                continue

            # Étape 1 : find simple (toujours fiable)
            result = self.run_cmd(
                ["adb", "-s", self.device_id, "shell",
                 f"find \"{path}\" -type f 2>/dev/null"],
                timeout=120
            )

            if result.returncode != 0 and not result.stdout.strip():
                self.log.emit(f"⚠️ Échec scan {folder} — ignoré")
                failed_folders.add(folder)
                self.scan_progress.emit(int((i + 1) * 100 / total))
                continue

            excluded_count = 0
            found_count    = 0
            raw_files      = []

            for line in result.stdout.splitlines():
                line = line.strip()
                if not line or line.startswith("find:"):
                    continue
                rel = line.replace(REMOTE_BASE + "/", "")
                if is_excluded(rel):
                    excluded_count += 1
                    continue
                remote_stats[rel] = {"size": -1, "mtime": 0, "path": line}
                raw_files.append((rel, line))
                found_count += 1

            if excluded_count:
                self.log.emit(f"   → {excluded_count} fichiers système exclus (.thumbnails...)")

            # Étape 2 : récupérer taille + mtime via stat
            if raw_files:
                stat_result = self.run_cmd(
                    ["adb", "-s", self.device_id, "shell",
                     f"find \"{path}\" -type f "
                     f"-not -path \"*/.thumbnails/*\" "
                     f"-exec stat -c '%n|%s|%Y' {{}} \\; 2>/dev/null"],
                    timeout=120
                )
                if stat_result.returncode == 0 and stat_result.stdout.strip():
                    for sline in stat_result.stdout.splitlines():
                        sline = sline.strip()
                        if not sline or "|" not in sline:
                            continue
                        parts = sline.rsplit("|", 2)
                        if len(parts) == 3:
                            fpath_s, sz, mt = parts
                            rel2 = fpath_s.strip().replace(REMOTE_BASE + "/", "")
                            if rel2 in remote_stats:
                                try:
                                    remote_stats[rel2]["size"]  = int(sz)
                                    remote_stats[rel2]["mtime"] = int(mt)
                                except ValueError:
                                    pass
                else:
                    # Fallback individuel pour petits dossiers
                    if found_count <= 20:
                        for rel2, fpath2 in raw_files:
                            sr = self.run_cmd(
                                ["adb", "-s", self.device_id, "shell",
                                 f"stat -c '%s|%Y' \"{fpath2}\" 2>/dev/null"],
                                timeout=10
                            )
                            if sr.returncode == 0 and "|" in sr.stdout:
                                try:
                                    sz2, mt2 = sr.stdout.strip().split("|", 1)
                                    remote_stats[rel2]["size"]  = int(sz2)
                                    remote_stats[rel2]["mtime"] = int(mt2)
                                except ValueError:
                                    pass

            self.log.emit(f"   → {found_count} fichiers dans {folder}")
            self.scan_progress.emit(int((i + 1) * 100 / total))

<<<<<<< Updated upstream
    def sync_pc_to_tel(self, remote_set, last_state):
        if last_state is None:
            self.log.emit("ℹ️  Premier lancement — PC→Tel ignoré.")
            return

        self.log.emit("⬆️  Vérification suppressions PC → Téléphone...")
        to_delete = []

        for rel in last_state:
            folder = rel.split("/")[0]
            if folder not in self.folders:
=======
        return remote_stats, failed_folders

    # ─── Calcul des changements ──────────────────────────────

    def compute_changes(self, remote_stats, failed_folders, last_state):
        """
        Règles de sync — toutes mutuellement exclusives :

        A. Fichier sur Tel, PAS sur PC, PAS dans journal
           → Nouveau sur Tel → copier Tel→PC

        B. Fichier sur Tel, PAS sur PC, DANS journal
           → La sync précédente a peut-être échoué (ou l'utilisateur a supprimé du PC volontairement)
           → COMPORTEMENT SÛRET : copier Tel→PC (ne jamais supprimer du Tel si le fichier y est encore)
           → NE PAS mettre dans to_delete_tel

        C. Fichier sur Tel ET sur PC, Tel plus récent / taille différente
           → Modifié sur Tel → copier Tel→PC (écraser)

        D. Fichier sur Tel ET sur PC, PC plus récent / taille différente
           → Modifié sur PC → pousser PC→Tel

        E. Fichier PAS sur Tel, PAS sur PC, DANS journal
           → Supprimé des deux côtés → rien à faire (journal sera mis à jour)

        F. Fichier sur PC, PAS sur Tel, PAS dans journal
           → Nouveau sur PC → pousser PC→Tel

        G. Fichier PAS sur Tel, sur PC, DANS journal
           → Supprimé du Tel par l'utilisateur → supprimer du PC

        H. Fichier PAS sur PC, sur Tel, DANS journal
           → Traité par règle B (copier Tel→PC) — JAMAIS supprimer du Tel

        RÈGLE DE SÉCURITÉ ABSOLUE :
        Dossier absent ou scan échoué → ZÉRO suppression pour ce dossier.
        """
        changes = {
            "to_copy_tel_to_pc":   [],   # Règles A, B, C
            "to_push_pc_to_tel":   [],   # Règle F
            "to_update_pc_to_tel": [],   # Règle D
            "to_delete_tel":       [],   # (vide — on ne supprime jamais du Tel si fichier présent)
            "to_delete_pc":        [],   # Règle G
            "_skipped_folders":    list(failed_folders),
        }

        remote_set = set(remote_stats.keys())

        # ── Règle F + D : PC → Tel (nouveaux et modifiés côté PC) ──
        for folder in self.folders:
            if folder in failed_folders:
                continue
            folder_local = os.path.join(self.local_base, folder)
            if not os.path.exists(folder_local):
                continue
            for root, dirs, files in os.walk(folder_local):
                dirs[:] = [d for d in dirs if not is_excluded(d)]
                for f in files:
                    local_path  = os.path.join(root, f)
                    rel         = os.path.relpath(local_path, self.local_base).replace("\\", "/")
                    if is_excluded(rel):
                        continue
                    remote_path = f"{REMOTE_BASE}/{rel}"

                    if rel not in remote_set:
                        # Règle F : nouveau sur PC, jamais synchro
                        if last_state is not None and rel not in last_state:
                            changes["to_push_pc_to_tel"].append((local_path, remote_path, rel))
                        # Si dans journal mais absent du tel → règle G (traité plus bas)
                    else:
                        # Règle D : fichier des deux côtés, PC plus récent
                        stats     = remote_stats[rel]
                        tel_mtime = stats.get("mtime", 0)
                        tel_size  = stats.get("size", -1)
                        if tel_mtime > 0:
                            try:
                                local_mtime = os.path.getmtime(local_path)
                                local_size  = os.path.getsize(local_path)
                                if local_mtime > tel_mtime + 60:
                                    if tel_size < 0 or local_size != tel_size:
                                        changes["to_update_pc_to_tel"].append(
                                            (local_path, remote_path, rel))
                            except Exception:
                                pass

        # ─── Tel → PC ET Suppr Tel : mutuellement exclusifs par le journal ───
        #
        # Règle A : sur Tel + absent PC + PAS dans journal → nouveau → copier Tel→PC
        # Règle B : sur Tel + absent PC + DANS journal    → user a supprimé du PC
        #                                                 → supprimer du Tel
        # Règle C : sur Tel ET sur PC, Tel plus récent    → copier Tel→PC (écraser)

        already_pc_to_tel = set(
            rel for (_, _, rel) in changes["to_update_pc_to_tel"]
        )

        for rel, stats in remote_stats.items():
            folder = rel.split("/")[0]
            if folder not in self.folders or folder in failed_folders:
                continue
            if rel in already_pc_to_tel:
                continue

            local_path = os.path.join(self.local_base, rel)

            if not os.path.exists(local_path):
                # Fichier sur Tel, absent du PC
                if last_state is not None and rel in last_state:
                    # Règle B : dans journal → user a supprimé du PC → supprimer du Tel
                    remote_path = f"{REMOTE_BASE}/{rel}"
                    changes["to_delete_tel"].append((local_path, remote_path))
                else:
                    # Règle A : pas dans journal → nouveau sur Tel → copier Tel→PC
                    changes["to_copy_tel_to_pc"].append((stats["path"], local_path, rel))
            else:
                # Règle C : fichier des deux côtés → comparer dates/tailles
                try:
                    local_size  = os.path.getsize(local_path)
                    local_mtime = os.path.getmtime(local_path)
                    tel_size    = stats.get("size", -1)
                    tel_mtime   = stats.get("mtime", 0)

                    if tel_size > 0 and tel_size != local_size:
                        if tel_mtime > 0:
                            if tel_mtime > local_mtime + 2:
                                changes["to_copy_tel_to_pc"].append(
                                    (stats["path"], local_path, rel))
                        else:
                            if tel_size > local_size:
                                changes["to_copy_tel_to_pc"].append(
                                    (stats["path"], local_path, rel))
                    elif tel_mtime > 0 and tel_mtime > local_mtime + 60:
                        changes["to_copy_tel_to_pc"].append(
                            (stats["path"], local_path, rel))
                except Exception:
                    pass

        # ── Règle G : Suppr PC ──
        # Fichier dans journal + absent du Tel + présent sur PC
        # = user a supprimé du Tel → supprimer du PC
        candidate_delete_pc = []
        for folder in self.folders:
            if folder in failed_folders:
                continue
            folder_local = os.path.join(self.local_base, folder)
            if not os.path.exists(folder_local):
                continue
            for root, dirs, files in os.walk(folder_local):
                dirs[:] = [d for d in dirs if not is_excluded(d)]
                for f in files:
                    local_path = os.path.join(root, f)
                    rel = os.path.relpath(local_path, self.local_base).replace("\\", "/")
                    if is_excluded(rel):
                        continue
                    if rel in remote_set:
                        continue  # Encore sur Tel → pas de suppression PC
                    if last_state is not None and rel in last_state:
                        candidate_delete_pc.append(local_path)

        # Garde de sécurité anti-suppression massive
        total_local = 0
        for folder in self.folders:
            if folder in failed_folders:
>>>>>>> Stashed changes
                continue
            fl = os.path.join(self.local_base, folder)
            if not os.path.exists(fl):
                continue
            for root, dirs, files in os.walk(fl):
                dirs[:] = [d for d in dirs if not is_excluded(d)]
                total_local += sum(
                    1 for f in files
                    if not is_excluded(
                        os.path.relpath(
                            os.path.join(root, f), self.local_base
                        ).replace("\\", "/"))
                )

<<<<<<< Updated upstream
        if not to_delete:
            self.log.emit("✅ Aucune suppression PC→Tel à effectuer.")
            return

        self.log.emit(f"📋 {len(to_delete)} fichier(s) à supprimer sur le téléphone.")

        if len(to_delete) >= DELETE_CONFIRM_THRESHOLD:
            self.log.emit(f"⚠️ Seuil de {DELETE_CONFIRM_THRESHOLD} atteint — confirmation requise...")
            self._confirm_result = None
            self.request_confirm.emit(to_delete)

            self._confirm_mutex.lock()
            while self._confirm_result is None:
                self._confirm_event.wait(self._confirm_mutex)
            accepted = self._confirm_result
            self._confirm_mutex.unlock()

            if not accepted:
                self.log.emit("🚫 Suppression annulée par l'utilisateur.")
                return
        else:
            for lp, rp in to_delete:
                self.log.emit(f"   → {rp}")

        for local_path, remote_path in to_delete:
            if not self.running:
                break
            if not self.check_device():
                self.log.emit("❌ Smartphone déconnecté !")
                self.running = False
                break
            rel = remote_path.replace(REMOTE_BASE + "/", "")
            self.log.emit(f"🗑️ Suppression Tel : {rel}")
            result = self.run_cmd(
                ["adb", "-s", self.device_id, "shell", f"rm \"{remote_path}\""]
            )
            if result.returncode != 0:
                self.log.emit(f"❌ Erreur : {result.stderr.strip()}")
                self.count_errors += 1
            else:
                self.deleted_tel.append((local_path, remote_path))
=======
        n_del = len(candidate_delete_pc)
        ratio = n_del / max(total_local, 1)

        if n_del > MAX_PC_DELETE_ABSOLUTE and ratio > MAX_PC_DELETE_RATIO:
            self.log.emit(
                f"🛡️ SÉCURITÉ : {n_del} suppressions PC bloquées ({ratio*100:.1f}%). "
                f"Scan peut-être incomplet — relancez après vérification."
            )
            changes["to_delete_pc"]              = []
            changes["_delete_pc_blocked"]        = candidate_delete_pc
            changes["_delete_pc_blocked_reason"] = (
                f"{n_del} fichiers ({ratio*100:.1f}%)"
            )
        else:
            changes["to_delete_pc"] = candidate_delete_pc

        return changes

    # ─── Application ────────────────────────────────────────

    def apply_changes(self, changes, remote_stats):
        all_ops = sum(len(changes[k]) for k in [
            "to_copy_tel_to_pc", "to_push_pc_to_tel",
            "to_update_pc_to_tel", "to_delete_tel", "to_delete_pc"
        ])
        done_ops = 0

        def tick():
            nonlocal done_ops
            done_ops += 1
            self.progress.emit(int(done_ops * 100 / max(all_ops, 1)))

        # Tel → PC
        if changes["to_copy_tel_to_pc"]:
            self.log.emit(f"⬇️  Tel→PC : {len(changes['to_copy_tel_to_pc'])} fichier(s)")
        for remote_path, local_path, rel in changes["to_copy_tel_to_pc"]:
            if not self.running: break
            while self.paused: time.sleep(0.2)
            if not self.check_device():
                self.log.emit("❌ Smartphone déconnecté !"); self.running = False; break
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            self.current_file.emit(rel)
            r = self.run_cmd(["adb", "-s", self.device_id, "pull", remote_path, local_path])
            if r.returncode != 0:
                err = f"Tel→PC : {rel} — {r.stderr.strip()[:80]}"
                self.log.emit(f"❌ {err}"); self.count_errors += 1; self.errors_list.append(err)
            else:
                self.copied_tel_to_pc.append((local_path, rel))
                self.log.emit(f"🟢 Tel→PC : {rel}")
            tick()

        # PC → Tel nouveaux
        if changes["to_push_pc_to_tel"]:
            self.log.emit(f"⬆️  PC→Tel nouveaux : {len(changes['to_push_pc_to_tel'])} fichier(s)")
        for idx, (local_path, remote_path, rel) in enumerate(changes["to_push_pc_to_tel"]):
            if not self.running: break
            self.run_cmd(["adb", "-s", self.device_id, "shell",
                          f"mkdir -p \"{os.path.dirname(remote_path)}\""])
            r = self.run_cmd(["adb", "-s", self.device_id, "push", local_path, remote_path])
            if r.returncode != 0:
                err = f"PC→Tel : {rel}"
                self.log.emit(f"❌ {err}"); self.count_errors += 1; self.errors_list.append(err)
            else:
                self.copied_pc_to_tel.append((local_path, rel))
                self.log.emit(f"📤 PC→Tel (nouveau) : {rel}")
            self.push_progress.emit(
                int((idx + 1) * 100 / max(len(changes["to_push_pc_to_tel"]), 1))
            )
            tick()

        # PC → Tel modifiés
        if changes["to_update_pc_to_tel"]:
            self.log.emit(f"🔄  PC→Tel modifiés : {len(changes['to_update_pc_to_tel'])} fichier(s)")
        for local_path, remote_path, rel in changes["to_update_pc_to_tel"]:
            if not self.running: break
            r = self.run_cmd(["adb", "-s", self.device_id, "push", local_path, remote_path])
            if r.returncode != 0:
                err = f"MAJ : {rel}"
                self.log.emit(f"❌ {err}"); self.count_errors += 1; self.errors_list.append(err)
            else:
                self.modified_pushed.append((local_path, rel))
                self.log.emit(f"🔄 MAJ : {rel}")
            tick()

        # Suppressions Tel (si présentes — confirmation requise au-delà du seuil)
        to_del_tel = changes["to_delete_tel"]
        if to_del_tel:
            self.log.emit(f"🗑️  Suppressions Tel : {len(to_del_tel)} fichier(s)")
            if len(to_del_tel) >= DELETE_CONFIRM_THRESHOLD:
                self._confirm_result = None
                self.request_confirm.emit(to_del_tel)
                self._confirm_mutex.lock()
                while self._confirm_result is None:
                    self._confirm_event.wait(self._confirm_mutex)
                accepted = self._confirm_result
                self._confirm_mutex.unlock()
                if not accepted:
                    self.log.emit("🚫 Suppression Tel annulée."); to_del_tel = []

            for local_path, remote_path in to_del_tel:
                if not self.running: break
                rel = remote_path.replace(REMOTE_BASE + "/", "")
                r = self.run_cmd(
                    ["adb", "-s", self.device_id, "shell", f"rm \"{remote_path}\""])
                if r.returncode != 0:
                    self.count_errors += 1
                    self.errors_list.append(f"rm Tel : {rel}")
                else:
                    self.deleted_tel.append((local_path, remote_path))
                    self.log.emit(f"🗑️ Tel supprimé : {rel}")
                tick()

        # Nettoyer les dossiers vides sur le tel après toutes les suppressions
        if self.deleted_tel or changes.get("to_delete_tel"):
            self._clean_empty_dirs_tel()

        # Suppressions PC
        for local_path in changes["to_delete_pc"]:
            if not self.running: break
            rel = os.path.relpath(local_path, self.local_base).replace("\\", "/")
            try:
                os.remove(local_path)
                self.deleted_pc.append(local_path)
                self.log.emit(f"🗑️ PC supprimé : {rel}")
            except Exception as e:
                self.count_errors += 1
                self.errors_list.append(f"rm PC : {rel} — {e}")
            tick()

        # Dossiers vides PC
        for folder in self.folders:
            fl = os.path.join(self.local_base, folder)
            if not os.path.exists(fl): continue
            for root, dirs, files in os.walk(fl, topdown=False):
                for d in dirs:
                    dp = os.path.join(root, d)
                    try:
                        if not os.listdir(dp): os.rmdir(dp)
                    except Exception: pass

    def _clean_empty_dirs_tel(self):
        """
        Supprime les dossiers vides sur le téléphone.
        Utilise find -empty pour éviter les problèmes avec .nomedia et fichiers cachés.
        Traite du plus profond au plus haut pour ne pas bloquer les parents.
        """
        for folder in self.folders:
            rf = f"{REMOTE_BASE}/{folder}"
            # find -empty -type d : ne retourne que les vrais dossiers vides
            # sort -r : du plus profond au plus haut
            r = self.run_cmd(
                ["adb", "-s", self.device_id, "shell",
                 f"find \"{rf}\" -mindepth 1 -type d -empty 2>/dev/null | sort -r"],
                timeout=30
            )
            if r.returncode != 0 or not r.stdout.strip():
                continue
            for rd in r.stdout.splitlines():
                rd = rd.strip()
                if not rd or rd == rf:
                    continue
                # Supprimer le dossier vide (rmdir échoue si non vide = sécurité)
                result = self.run_cmd(
                    ["adb", "-s", self.device_id, "shell",
                     f"rmdir \"{rd}\" 2>/dev/null && echo OK || echo FAIL"],
                    timeout=10
                )
                if result.stdout.strip() == "OK":
                    self.log.emit(f"🗂️ Dossier vide supprimé Tel : {rd.replace(REMOTE_BASE+'/', '')}")
>>>>>>> Stashed changes

    # ─── Thread principal ────────────────────────────────────

    def run(self):
        start_time = datetime.now()
        self.log.emit(f"🕐 Début : {start_time.strftime('%d/%m/%Y %H:%M:%S')}")
        os.makedirs(self.local_base, exist_ok=True)

        last_state = load_sync_state(self.local_base)
        self.log.emit(
            f"📋 Journal : {len(last_state)} fichiers" if last_state
            else "📋 Premier lancement — aucun journal."
        )

        self.log.emit("🔍 Scan du téléphone en cours...")
        self.status.emit("Scan en cours...")
        remote_stats, failed_folders = self.get_remote_files()
        total_remote = len(remote_stats)
        self.log.emit(f"📦 {total_remote} fichiers scannés sur le téléphone")

        if failed_folders:
            self.log.emit(
                f"⚠️  {len(failed_folders)} dossier(s) absents du téléphone :\n"
                + "\n".join(f"   → {f}" for f in sorted(failed_folders))
                + "\n   ℹ️  Aucune suppression PC ne sera effectuée pour ces dossiers."
            )

        if not self.running or total_remote == 0:
            self.done.emit({}); return

        self.status.emit("Calcul des changements...")
        changes = self.compute_changes(remote_stats, failed_folders, last_state)

        blocked = changes.get("_delete_pc_blocked", [])
        if blocked:
            self.log.emit(
                f"🛡️ {len(blocked)} suppressions PC bloquées — "
                f"{changes.get('_delete_pc_blocked_reason', '')}"
            )

        skipped = changes.get("_skipped_folders", [])
        self.log.emit(
            f"⬇️  Tel→PC : {len(changes['to_copy_tel_to_pc'])}\n"
            f"⬆️  PC→Tel (new) : {len(changes['to_push_pc_to_tel'])}\n"
            f"🔄  PC→Tel (MAJ) : {len(changes['to_update_pc_to_tel'])}\n"
            f"🗑️  Suppr Tel    : {len(changes['to_delete_tel'])}\n"
            f"🗑️  Suppr PC     : {len(changes['to_delete_pc'])}"
            + (f"\n⏭️  Dossiers ignorés : {', '.join(skipped)}" if skipped else "")
            + (f"\n🛡️  Suppr PC bloquées : {len(blocked)}" if blocked else "")
        )

        # Prévisualisation
        self._preview_result = None
        self.preview_ready.emit({"changes": changes, "remote_stats": remote_stats})

        self._preview_mutex.lock()
        while self._preview_result is None and self.running:
            self._preview_event.wait(self._preview_mutex, 300000)
        confirmed = self._preview_result
        self._preview_mutex.unlock()

        if not confirmed or not self.running:
            self.log.emit("🚫 Sync annulée par l'utilisateur.")
            self.done.emit({"cancelled": True}); return

        self.status.emit("Synchronisation en cours...")
        self.apply_changes(changes, remote_stats)

        # Mise à jour journal
        if self.running:
            new_state = set(remote_stats.keys())
            for lp, rel in self.copied_pc_to_tel: new_state.add(rel)
            for lp, rel in self.modified_pushed:  new_state.add(rel)
            for lp, rp in self.deleted_tel:
                new_state.discard(rp.replace(REMOTE_BASE + "/", ""))
            # Conserver dans le journal les dossiers non scannés
            if last_state and failed_folders:
                for rel in last_state:
                    if rel.split("/")[0] in failed_folders:
                        new_state.add(rel)
            save_sync_state(self.local_base, new_state)
            self.log.emit("💾 Journal mis à jour.")

        end_time = datetime.now()
        dur_str  = str(end_time - start_time).split(".")[0]

        self.log.emit("─" * 48)
        self.log.emit("✅ SYNCHRONISATION TERMINÉE")
        self.log.emit(f"   ⏱️  Durée       : {dur_str}")
        self.log.emit(f"   ⬇️  Tel→PC      : {len(self.copied_tel_to_pc)}")
        self.log.emit(f"   ⬆️  PC→Tel      : {len(self.copied_pc_to_tel)}")
        self.log.emit(f"   🔄  MAJ         : {len(self.modified_pushed)}")
        self.log.emit(f"   🗑️  Suppr PC    : {len(self.deleted_pc)}")
        self.log.emit(f"   🗑️  Suppr Tel   : {len(self.deleted_tel)}")
        self.log.emit(f"   ❌ Erreurs     : {self.count_errors}")
        self.log.emit("─" * 48)

        self.done.emit({
            "start_time":       start_time.strftime("%d/%m/%Y %H:%M:%S"),
            "end_time":         end_time.strftime("%d/%m/%Y %H:%M:%S"),
            "duration_str":     dur_str,
            "copied_tel_to_pc": self.copied_tel_to_pc,
            "copied_pc_to_tel": self.copied_pc_to_tel,
            "modified_pushed":  self.modified_pushed,
            "deleted_pc":       self.deleted_pc,
            "deleted_tel":      self.deleted_tel,
            "skipped":          self.count_skipped,
            "errors":           self.count_errors,
            "errors_list":      self.errors_list,
            "copied":           self.copied_tel_to_pc,
        })
