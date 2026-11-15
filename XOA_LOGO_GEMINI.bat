@echo off
chcp 65001 >nul
title XOA LOGO GEMINI (Reverse Alpha Blending)
cls
echo ========================================================
echo     CONG CU XOA LOGO GEMINI - Reverse Alpha Blending
echo ========================================================
echo.

set "NODE=C:\Program Files\nodejs\node.exe"
set "CLI=C:\File D\Stickman\gemini-watermark-remover\gemini-watermark-remover\bin\gwr.mjs"
set "SOURCE=C:\File D\Stickman\caveman-story\images"
set "DEST=C:\File D\Stickman\caveman-story\images_clean"

if not exist "%DEST%" mkdir "%DEST%"

echo [*] Dang xoa logo trong thu muc: %SOURCE%
echo [*] Ket qua luu vao: %DEST%
echo.

set count=0
for %%F in ("%SOURCE%\*.png" "%SOURCE%\*.jpg" "%SOURCE%\*.jpeg" "%SOURCE%\*.webp") do (
    if exist "%%F" (
        echo [+] Xu ly %%~nxF
        "%NODE%" "%CLI%" remove "%%F" --out-dir "%DEST%" --overwrite
        set /a count+=1
    )
)

echo.
echo ========================================================
echo [DONE] Da xoa logo cho %count% buc anh
echo [OK] Anh da xoa logo o: %DEST%
echo ========================================================
echo.
pause

//.\XOA_LOGO_GEMINI.bat
