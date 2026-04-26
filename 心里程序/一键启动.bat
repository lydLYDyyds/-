@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

echo 正在启动「命运回响」...

where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py -3"
) else (
  where python >nul 2>nul
  if %errorlevel%==0 (
    set "PY=python"
  ) else (
    echo.
    echo 未检测到 Python。
    echo 请先安装 Python 3.10 或更高版本，然后重新双击本文件。
    echo 下载地址：https://www.python.org/downloads/
    echo 安装时请勾选 Add python.exe to PATH。
    echo.
    pause
    exit /b 1
  )
)

if not exist ".venv\Scripts\python.exe" (
  echo 首次运行：正在创建本地运行环境...
  %PY% -m venv .venv
  if errorlevel 1 (
    echo 创建运行环境失败。
    pause
    exit /b 1
  )
)

echo 正在安装或检查依赖...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo 依赖安装失败，请检查网络连接后重试。
  pause
  exit /b 1
)

echo 浏览器即将打开：http://localhost:8501
start "" "http://localhost:8501"
".venv\Scripts\python.exe" -m streamlit run app.py --server.headless true --server.port 8501

pause
