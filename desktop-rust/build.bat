@echo off
echo ========================================================
echo   Building Ayera Downloader Pro (Rust IDM Core)
echo ========================================================
cargo build --release --bin ayera_downloader
if %ERRORLEVEL% NEQ 0 (
    echo Error building ayera_downloader!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================================
echo   Building Standalone Setup Installer (installer.exe)
echo ========================================================
cargo build --release --bin ayera_setup
if %ERRORLEVEL% NEQ 0 (
    echo Error building ayera_setup!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================================
echo   Build Successful!
echo   App Binary : target\release\ayera_downloader.exe
echo   Installer  : target\release\ayera_setup.exe
echo ========================================================
