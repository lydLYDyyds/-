@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

echo 正在准备打包环境...
where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py -3"
) else (
  set "PY=python"
)

if not exist ".venv\Scripts\python.exe" (
  %PY% -m venv .venv
)

".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt pyinstaller

echo 正在生成 Windows 启动程序...
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --onedir --name "命运回响" --add-data "app.py;." --add-data "requirements.txt;." launcher.py

echo.
echo 打包完成后，请打开 dist\命运回响 文件夹。
echo 其中的 命运回响.exe 可用于启动项目。
pause
