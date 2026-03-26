# modules/adb_explorer.py
# Explorateur de fichiers ADB

import os
import subprocess
from PyQt5 import QtWidgets, QtCore


class ADBExplorer(QtWidgets.QDialog):
    def __init__(self, device_id, parent=None):
        super().__init__(parent)
        self.device_id = device_id
        self.setWindowTitle("Explorateur ADB")
        self.resize(500, 400)

        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabel("Téléphone")

        btn_select = QtWidgets.QPushButton("Sélectionner / Select")
        btn_select.setStyleSheet(
            "background-color:#2ecc71; color:white; font-weight:bold; padding:6px;"
        )

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.tree)
        layout.addWidget(btn_select)
        self.setLayout(layout)

        btn_select.clicked.connect(self.accept)
        self.load_root()

    def run_cmd(self, cmd):
        return subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

    def load_root(self):
        root = QtWidgets.QTreeWidgetItem(["/sdcard"])
        root.setData(0, QtCore.Qt.UserRole, "/sdcard")
        self.tree.addTopLevelItem(root)
        self.load_children(root)

    def load_children(self, item):
        path   = item.data(0, QtCore.Qt.UserRole)
        result = self.run_cmd(
            ["adb", "-s", self.device_id, "shell", f"ls -d \"{path}\"/*/"]
        )
        if result.returncode != 0:
            return
        for line in result.stdout.splitlines():
            line  = line.strip().rstrip("/")
            name  = os.path.basename(line)
            child = QtWidgets.QTreeWidgetItem([name])
            child.setData(0, QtCore.Qt.UserRole, line)
            item.addChild(child)

    def selected_path(self):
        item = self.tree.currentItem()
        if item:
            return item.data(0, QtCore.Qt.UserRole).replace("/sdcard/", "")
        return None
