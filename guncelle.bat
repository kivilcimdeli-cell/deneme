@echo off
rem BOYDE Atolye guncelleme: depodaki son surumu ceker, paketleri gunceller. Musteri kayitlari (atolye_veri) korunur.
chcp 65001 >nul
title BOYDE Atolye guncelleme
cd /d "%~dp0"
where git >nul 2>nul || (
  echo Git bulunamadi: https://git-scm.com/download/win adresinden kurun ya da depoyu yeniden indirin.
  pause
  exit /b 1
)
git pull || goto hata
if exist .venv\Scripts\python.exe .venv\Scripts\python.exe -m pip install -r atolye\requirements.txt || goto hata
echo.
echo Guncelleme tamam.
pause
exit /b 0
:hata
echo.
echo Guncellemede hata oldu. Yukaridaki mesaji Claude'a iletin.
pause
exit /b 1
