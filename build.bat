@echo off
cd /d "%~dp0"
echo === Ayeraa Save Downloader - Build .exe ===
python -m pip install -U -r requirements.txt pyinstaller || goto :error
python tools\make_icon.py || goto :error

python -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name "Ayeraa Save Downloader" ^
  --icon "assets\icon.ico" ^
  --add-data "assets;assets" ^
  --collect-all customtkinter ^
  --collect-all imageio_ffmpeg ^
  --collect-all yt_dlp_ejs ^
  --collect-all webview ^
  --collect-all pythonnet ^
  --collect-submodules yt_dlp ^
  main.py || goto :error

echo.
echo Selesai! File: dist\Ayeraa Save Downloader.exe
pause
exit /b 0

:error
echo.
echo Build GAGAL.
pause
exit /b 1
