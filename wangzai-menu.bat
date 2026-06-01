@echo off
setlocal
cd /d "%~dp0"

set "BUNDLED_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if exist "%BUNDLED_PYTHON%" (
  "%BUNDLED_PYTHON%" "%~dp0wangzai_menu.py"
) else (
  python "%~dp0wangzai_menu.py"
)

pause
