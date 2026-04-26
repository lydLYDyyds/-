@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

echo 正在启动「命运回响」本地前后端版...

where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py -3"
) else (
  where python >nul 2>nul
  if %errorlevel%==0 (
    set "PY=python"
  ) else (
    echo 未检测到 Python。请先安装 Python 3.10 或更高版本。
    pause
    exit /b 1
  )
)

if not exist ".venv\Scripts\python.exe" (
  echo 首次运行：正在创建本地运行环境...
  %PY% -m venv .venv
)

echo 正在安装或检查依赖...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo 依赖安装失败，请检查网络连接后重试。
  pause
  exit /b 1
)

echo 浏览器即将打开：http://127.0.0.1:8787
start "" "http://127.0.0.1:8787"
".venv\Scripts\python.exe" -m uvicorn api_server:api --host 127.0.0.1 --port 8787

pause
