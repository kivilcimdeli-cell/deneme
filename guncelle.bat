@echo off
rem BOYDE Atolye guncelleme. Git ile indirildiyse son surumu ceker; ZIP ile kurulduysa yeni ZIP'in nasil acilacagini
rem yazar. Musteri kayitlari Belgeler\BOYDE Atolye klasorundedir, guncellemeden etkilenmez.
chcp 65001 >nul
title BOYDE Atolye guncelleme
cd /d "%~dp0"
if not exist .git goto zip
where git >nul 2>nul || goto zip
git pull || goto hata
if exist .venv\Scripts\python.exe .venv\Scripts\python.exe -m pip install -r atolye\requirements.txt || goto hata
echo.
echo Guncelleme tamam.
pause
exit /b 0
:zip
echo Bu kurulum ZIP ile yapilmis. Guncellemek icin:
echo   1. Yeni BOYDE_Atolye.zip dosyasini indirin.
echo   2. Bu klasorun uzerine acin (dosyalarin degistirilmesine izin verin).
echo   3. kurulum.bat dosyasini bir kez calistirin.
echo Musteri kayitlariniz Belgeler\BOYDE Atolye klasorunde kalir.
pause
exit /b 0
:hata
echo.
echo Guncellemede hata oldu. Yukaridaki mesaji Claude'a iletin.
pause
exit /b 1
