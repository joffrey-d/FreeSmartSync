@echo off
chcp 65001 >nul
title FreeSmartSync v0.8.6.2 — Installation Windows

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║   FreeSmartSync v0.8.6.2 — Installation Windows  ║
echo ╚══════════════════════════════════════════════════╝
echo.

:: Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python 3 n'est pas installe.
    echo Telechargez Python sur https://www.python.org/downloads/
    echo Cochez "Add Python to PATH" lors de l'installation.
    pause
    exit /b 1
)

:: Vérifier PyQt5
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo Installation de PyQt5...
    pip install PyQt5
    if errorlevel 1 (
        echo [ERREUR] Impossible d'installer PyQt5.
        pause
        exit /b 1
    )
)

echo [OK] PyQt5 disponible.

:: Vérifier ADB
adb version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ATTENTION] ADB non detecte dans le PATH.
    echo.
    echo Pour installer ADB :
    echo   1. Telechargez Android Platform Tools :
    echo      https://developer.android.com/studio/releases/platform-tools
    echo   2. Extrayez dans C:\Android\platform-tools\
    echo   3. Ajoutez ce dossier a votre variable PATH
    echo   4. Relancez ce script
    echo.
    echo Vous pouvez aussi copier adb.exe dans le dossier tools\ ici.
    echo.
    pause
)

:: Créer raccourci sur le Bureau
echo Création du raccourci...
set SCRIPT_DIR=%~dp0
set SHORTCUT=%USERPROFILE%\Desktop\FreeSmartSync.lnk

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = 'python'; $s.Arguments = '\"%SCRIPT_DIR%freesmartsync.py\"'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.IconLocation = '%SCRIPT_DIR%assets\icon.ico'; $s.Description = 'FreeSmartSync v0.8.6.2'; $s.Save()" 2>nul

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║   Installation terminée !                        ║
echo ║   Lancez FreeSmartSync depuis le Bureau          ║
echo ╚══════════════════════════════════════════════════╝
echo.
pause

:: Lancer FreeSmartSync
start "" python "%SCRIPT_DIR%freesmartsync.py"
