@echo off
chcp 65001 >nul
echo.
echo   === SongSnap — Real-time Song Recognizer ===
echo   Starting server... Browser will open automatically.
echo   To stop, click the [Stop Server] button on the website.
echo.
"%~dp0.venv\Scripts\python.exe" "%~dp0app.py"
