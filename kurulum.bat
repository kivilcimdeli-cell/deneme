@echo off
rem BOYDE Atolye kurulumu (bir kez): Python 3.11 sanal ortami, paketler, site onizlemeleri icin Chromium.
chcp 65001 >nul
title BOYDE Atolye kurulumu
cd /d "%~dp0"
set PY=
where py >nul 2>nul && py -3.11 --version >nul 2>nul && set PY=py -3.11
if not defined PY where python >nul 2>nul && set PY=python
if not defined PY (
  echo Python bulunamadi. https://www.python.org/downloads/ adresinden Python 3.11 kurun
  echo ve kurulumda "Add python.exe to PATH" kutusunu isaretleyin. Sonra bu dosyayi yeniden calistirin.
  pause
  exit /b 1
)
%PY% --version
if not exist .venv\Scripts\python.exe %PY% -m venv .venv || goto hata
.venv\Scripts\python.exe -m pip install --upgrade pip || goto hata
.venv\Scripts\python.exe -m pip install -r atolye\requirements.txt || goto hata
.venv\Scripts\python.exe -m playwright install chromium || goto hata
echo.
echo Kurulum tamam. Uygulamayi BOYDE_Atolye.bat ile acin.
pause
exit /b 0
:hata
echo.
echo Kurulumda hata oldu. Yukaridaki mesaji Claude'a iletin.
pause
exit /b 1
