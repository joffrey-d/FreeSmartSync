# modules/worker.py
# Thread de synchronisation ADB

import os
import subprocess
import time
from datetime import datetime
from PyQt5 import QtCore

from modules.config import load_sync_state, save_sync_state

REMOTE_BASE = "/sdcard"
DELETE_CONFIRM_THRESHOLD = 20


class Worker(QtCore.QThread):
    progress        = QtCore.pyqtSignal(int)
    scan_progress   = QtCore.pyqtSignal(int)
    status          = QtCore.pyqtSignal(str)
    current_file    = QtCore.pyqtSignal(str)
    log             = QtCore.pyqtSignal(str)
    done            = QtCore.pyqtSignal(dict)
    request_confirm = QtCore.pyqtSignal(list)

    def __init__(self, folders, local_base, device_id, lang="fr"):
        super().__init__()
        self.running    = True
        self.paused     = False
        self.folders    = folders
        self.local_base = local_base
        self.device_id  = device_id
        self.lang       = lang

        self._confirm_event  = QtCore.QWaitCondition()
        self._confirm_mutex  = QtCore.QMutex()
        self._confirm_result = None

        self.copied        = []
        self.deleted_pc    = []
        self.deleted_tel   = []
        self.count_skipped = 0
        self.count_errors  = 0

    def stop(self):
        self.running = False
        self._confirm_mutex.lock()
        self._confirm_result = False
        self._confirm_event.wakeAll()
        self._confirm_mutex.unlock()

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def confirm_result(self, accepted: bool):
        self._confirm_mutex.lock()
        self._confirm_result = accepted
        self._confirm_event.wakeAll()
        self._confirm_mutex.unlock()

    def run_cmd(self, cmd):
        return subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

    def check_device(self):
        result = self.run_cmd(["adb", "devices"])
        return self.device_id in result.stdout

    def get_remote_files(self):
        files = []
        total = len(self.folders)
        for i, folder in enumerate(self.folders):
            if not self.running:
                break
            self.log.emit(f"🔍 Scan : {folder}")
            path   = f"{REMOTE_BASE}/{folder}"
            result = self.run_cmd(
                ["adb", "-s", self.device_id, "shell", f"find \"{path}\" -type f"]
            )
            if result.returncode != 0:
                self.log.emit(f"⚠️ Erreur scan {folder}")
                continue
            for line in result.stdout.splitlines():
                line = line.strip()
                if line:
                    files.append(line)
            self.scan_progress.emit(int((i + 1) * 100 / total))
        return files

    def sync_pc_to_tel(self, remote_set, last_state):
        if last_state is None:
            self.log.emit("ℹ️  Premier lancement — PC→Tel ignoré.")
            return

        self.log.emit("⬆️  Vérification suppressions PC → Téléphone...")
        to_delete = []

        for rel in last_state:
            folder = rel.split("/")[0]
            if folder not in self.folders:
                continue
            local_path  = os.path.join(self.local_base, rel)
            remote_path = f"{REMOTE_BASE}/{rel}"
            if not os.path.exists(local_path) and rel in remote_set:
                to_delete.append((local_path, remote_path))

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

    def sync_tel_to_pc(self, remote_files, remote_set):
        self.log.emit("⬇️  Synchronisation Téléphone → PC...")
        total = len(remote_files)

        for i, file in enumerate(remote_files):
            if not self.running:
                break
            while self.paused:
                time.sleep(0.2)

            if not self.check_device():
                self.log.emit("❌ Smartphone déconnecté !")
                self.running = False
                break

            rel        = file.strip().replace(REMOTE_BASE + "/", "")
            local_file = os.path.join(self.local_base, rel)
            os.makedirs(os.path.dirname(local_file), exist_ok=True)
            self.current_file.emit(rel)

            if os.path.exists(local_file):
                try:
                    local_size = os.path.getsize(local_file)
                    remote     = self.run_cmd(
                        ["adb", "-s", self.device_id, "shell", f"stat -c %s \"{file}\""]
                    )
                    if remote.returncode == 0 and int(remote.stdout.strip()) == local_size:
                        self.log.emit(f"🟡 Ignoré : {rel}")
                        self.count_skipped += 1
                        self.progress.emit(int((i + 1) * 100 / total))
                        self.status.emit(f"Tel→PC  {i+1} / {total}")
                        continue
                except Exception as e:
                    self.log.emit(f"⚠️ Erreur stat : {e}")

            self.log.emit(f"🟢 Copie : {rel}")
            result = self.run_cmd(
                ["adb", "-s", self.device_id, "pull", file, local_file]
            )
            if result.returncode != 0:
                self.log.emit(f"❌ Erreur copie : {rel} — {result.stderr.strip()}")
                self.count_errors += 1
            else:
                self.copied.append((local_file, rel))

            self.progress.emit(int((i + 1) * 100 / total))
            self.status.emit(f"Tel→PC  {i+1} / {total}")

        # Nettoyage local
        self.log.emit("🧹 Nettoyage PC...")
        for folder in self.folders:
            folder_local = os.path.join(self.local_base, folder)
            if not os.path.exists(folder_local):
                continue
            for root, dirs, files in os.walk(folder_local):
                for f in files:
                    local_path = os.path.join(root, f)
                    rel_path   = os.path.relpath(local_path, self.local_base).replace("\\", "/")
                    if rel_path not in remote_set:
                        try:
                            os.remove(local_path)
                            self.log.emit(f"🗑️ Supprimé PC : {rel_path}")
                            self.deleted_pc.append(local_path)
                        except Exception as e:
                            self.log.emit(f"⚠️ Erreur : {rel_path} — {e}")
                            self.count_errors += 1

        # Dossiers vides
        for folder in self.folders:
            folder_local = os.path.join(self.local_base, folder)
            if not os.path.exists(folder_local):
                continue
            for root, dirs, files in os.walk(folder_local, topdown=False):
                for d in dirs:
                    dir_path = os.path.join(root, d)
                    try:
                        if not os.listdir(dir_path):
                            os.rmdir(dir_path)
                            self.log.emit(f"🗂️ Dossier vide supprimé : {os.path.relpath(dir_path, self.local_base)}")
                    except Exception:
                        pass

    def run(self):
        start_time = datetime.now()
        self.log.emit(f"🕐 Début : {start_time.strftime('%d/%m/%Y %H:%M:%S')}")

        os.makedirs(self.local_base, exist_ok=True)

        last_state = load_sync_state(self.local_base)
        if last_state is None:
            self.log.emit("📋 Premier lancement — aucun journal trouvé.")
        else:
            self.log.emit(f"📋 Journal chargé : {len(last_state)} fichiers connus.")

        self.log.emit("🔍 Scan du téléphone en cours...")
        remote_files = self.get_remote_files()
        total_files  = len(remote_files)
        self.log.emit(f"📦 Fichiers détectés : {total_files}")

        if total_files == 0:
            self.done.emit({})
            return

        remote_set = set(
            f.strip().replace(REMOTE_BASE + "/", "").replace("\\", "/")
            for f in remote_files
        )

        if self.running:
            self.sync_pc_to_tel(remote_set, last_state)

        if self.running:
            remote_files = self.get_remote_files()
            remote_set   = set(
                f.strip().replace(REMOTE_BASE + "/", "").replace("\\", "/")
                for f in remote_files
            )
            self.sync_tel_to_pc(remote_files, remote_set)

        if self.running:
            save_sync_state(self.local_base, remote_set)
            self.log.emit("💾 Journal de sync mis à jour.")

        end_time  = datetime.now()
        duration  = end_time - start_time
        total_sec = int(duration.total_seconds())
        h, rem    = divmod(total_sec, 3600)
        m, s      = divmod(rem, 60)
        dur_str   = f"{h:02d}h {m:02d}m {s:02d}s"

        self.log.emit("─" * 48)
        self.log.emit("✅ SYNCHRONISATION TERMINÉE")
        self.log.emit(f"   🕐 Début         : {start_time.strftime('%H:%M:%S')}")
        self.log.emit(f"   🕑 Fin           : {end_time.strftime('%H:%M:%S')}")
        self.log.emit(f"   ⏱️  Durée          : {dur_str}")
        self.log.emit(f"   🟢 Copiés        : {len(self.copied)}")
        self.log.emit(f"   🟡 Ignorés       : {self.count_skipped}")
        self.log.emit(f"   🗑️  Supprimés PC  : {len(self.deleted_pc)}")
        self.log.emit(f"   🗑️  Supprimés Tel : {len(self.deleted_tel)}")
        self.log.emit(f"   ❌ Erreurs       : {self.count_errors}")
        self.log.emit("─" * 48)

        self.done.emit({
            "start_time":   start_time.strftime("%d/%m/%Y %H:%M:%S"),
            "end_time":     end_time.strftime("%d/%m/%Y %H:%M:%S"),
            "duration_str": dur_str,
            "copied":       self.copied,
            "deleted_pc":   self.deleted_pc,
            "deleted_tel":  self.deleted_tel,
            "skipped":      self.count_skipped,
            "errors":       self.count_errors,
        })
