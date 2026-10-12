@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m streamlit run app.py --server.address 127.0.0.1 --server.headless false
) else if exist "..\.venv_sim\Scripts\python.exe" (
  "..\.venv_sim\Scripts\python.exe" -m streamlit run app.py --server.address 127.0.0.1 --server.headless false
) else (
  echo Once README.md dosyasindaki Python kurulum adimlarini uygulayin.
  pause
)
endlocal
