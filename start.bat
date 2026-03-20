@echo off
chcp 65001 >nul
echo.
echo   === Real-time Song Recognizer ===
echo   Starting server... Browser will open automatically.
echo   To stop, click the [Stop Server] button on the website.
echo.
python "%~dp0app.py"
