@echo off
rem BOYDE Atolye: yerel paneli acar (tarayicida http://127.0.0.1:8765). Bu pencere kapaninca uygulama kapanir.
chcp 65001 >nul
title BOYDE Atolye
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Once kurulum.bat dosyasini calistirin.
  pause
  exit /b 1
)
echo BOYDE Atolye calisiyor. Panel tarayicida acilacak. Kapatmak icin bu pencereyi kapatin.
.venv\Scripts\python.exe -m atolye
pause
