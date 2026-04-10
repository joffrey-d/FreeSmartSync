@echo off
chcp 65001 >nul
cd /d "%~dp0"
python freesmartsync.py
if errorlevel 1 (
    echo.
    echo Erreur au lancement. Verifiez que Python et PyQt5 sont installes.
    echo Relancez INSTALLER-Windows.bat si necessaire.
    pause
)
