@echo off
chcp 65001 >nul
title TU DONG TAO ANH GEMINI WEB
cls
echo ============================================================
echo   TOOL TU DONG TAO VA TAI ANH THEO KICH BAN
echo ============================================================
echo.
echo LUU Y:
echo - Neu day la lan dau chay, ban phai chay file DANG_NHAP_GEMINI.bat truoc!
echo - Tool duoc cai dat che do "CHONG SPAM": nghi tu 20s - 28s moi anh
echo   de tai khoan luon AN TOAN 100%%, khong bi Google chan.
echo.
echo ============================================================
echo Chon so canh ban muon tao (Vi du: 1 den 10 de thu nghiem, hoac 1 den 70)
echo ============================================================
set /p START_SHOT="Nhap canh bat dau (mac dinh 1): "
if "%START_SHOT%"=="" set START_SHOT=1

set /p END_SHOT="Nhap canh ket thuc (mac dinh 70): "
if "%END_SHOT%"=="" set END_SHOT=70

echo.
echo Dang khoi chay Bot Playwright de tao tu canh %START_SHOT% den %END_SHOT%...
echo.

"C:\Users\tunga\AppData\Local\Programs\Python\Python311\python.exe" "C:\File D\Stickman\tools\auto_generate_images.py" %START_SHOT% %END_SHOT%

echo.
echo ============================================================
echo [BUOC TIEP THEO] Tu dong tay sach logo Gemini...
echo ============================================================
call "C:\File D\Stickman\XOA_LOGO_GEMINI.bat"

echo.
echo ============================================================
echo TAT CA DA HOAN TAT! ANH DA LUU TRONG THU MUC IMAGES/
echo ============================================================
pause
