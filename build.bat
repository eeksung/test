@echo off
echo ============================================
echo   처방일수 계산기 - Windows 실행파일 빌드
echo ============================================
echo.

pip install pyinstaller
if errorlevel 1 (
    echo [오류] pyinstaller 설치에 실패했습니다.
    pause
    exit /b 1
)

echo.
echo 빌드를 시작합니다...
pyinstaller --onefile --windowed --name "처방일수계산기" --clean prescription_calculator.py

if errorlevel 1 (
    echo [오류] 빌드에 실패했습니다.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   빌드 완료!
echo   실행파일: dist\처방일수계산기.exe
echo ============================================
pause
