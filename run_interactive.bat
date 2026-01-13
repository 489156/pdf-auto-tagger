@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
REM PDF 자동 태깅 시스템 대화형 실행 스크립트

echo ================================================
echo  PDF 자동 태깅 시스템 (APATS)
echo  AI-Powered PDF Auto-Tagging System
echo ================================================
echo.

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되지 않았습니다.
    echo Python 3.10 이상을 설치해주세요: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 가상환경 확인 및 생성
if not exist "venv" (
    echo [설정] 가상환경 생성 중...
    python -m venv venv
    if errorlevel 1 (
        echo [오류] 가상환경 생성 실패
        pause
        exit /b 1
    )
)

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM 의존성 설치 확인
python -c "import PyMuPDF" >nul 2>&1
if errorlevel 1 (
    echo [설정] 필요한 패키지 설치 중... (처음 실행 시 시간이 걸릴 수 있습니다)
    pip install --upgrade pip
    pip install -r requirements.txt
)

REM 개발 모드 설치
pip install -e . >nul 2>&1

REM API 키 확인
if "%OPENAI_API_KEY%"=="" (
    echo.
    set /p API_KEY="OpenAI API 키를 입력하세요: "
    if "!API_KEY!"=="" (
        echo [오류] API 키가 필요합니다.
        pause
        exit /b 1
    )
    set OPENAI_API_KEY=!API_KEY!
)

echo.
echo ================================================
echo  파일 선택
echo ================================================
set /p INPUT_FILE="입력 PDF 파일 경로를 입력하세요: "
if "!INPUT_FILE!"=="" (
    echo [오류] 입력 파일이 지정되지 않았습니다.
    pause
    exit /b 1
)

if not exist "!INPUT_FILE!" (
    echo [오류] 파일을 찾을 수 없습니다: !INPUT_FILE!
    pause
    exit /b 1
)

echo.
set /p OUTPUT_FILE="출력 PDF 파일 경로 (Enter로 기본값 사용): "
if "!OUTPUT_FILE!"=="" (
    for %%F in ("!INPUT_FILE!") do set OUTPUT_FILE=%%~dpnF_tagged.pdf
)

echo.
echo ================================================
echo  처리 시작
echo ================================================
echo 입력 파일: !INPUT_FILE!
echo 출력 파일: !OUTPUT_FILE!
echo.

REM 실행
python -m src.main "!INPUT_FILE!" "!OUTPUT_FILE!"

if errorlevel 1 (
    echo.
    echo [오류] 처리 중 오류가 발생했습니다.
    pause
    exit /b 1
) else (
    echo.
    echo ================================================
    echo  처리 완료!
    echo ================================================
    echo 출력 파일: !OUTPUT_FILE!
    echo.
)

pause
