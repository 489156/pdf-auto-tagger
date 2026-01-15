#!/usr/bin/env bash
set -euo pipefail

echo "==============================================="
echo " PDF 자동 태깅 시스템 (APATS) 설정"
echo "==============================================="
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "[오류] python3가 설치되지 않았습니다."
  echo "Python 3.10 이상을 설치해주세요: https://www.python.org/downloads/"
  exit 1
fi

echo "[확인] Python 버전"
python3 --version

if [ -d "venv" ]; then
  echo "[알림] 가상환경이 이미 존재합니다."
  read -r -p "기존 가상환경을 삭제하고 다시 생성하시겠습니까? (y/N) " choice
  if [[ "$choice" =~ ^[Yy]$ ]]; then
    rm -rf venv
  fi
fi

echo "[설정] 가상환경 생성 중..."
python3 -m venv venv

echo "[설정] 가상환경 활성화 중..."
source venv/bin/activate

echo "[설정] 빌드 도구 업그레이드 중..."
python -m pip install --upgrade pip setuptools wheel

echo "[설정] 필요한 패키지 설치 중..."
if ! pip install -r requirements.txt; then
  echo "[경고] 기본 설치 실패, 빌드 격리 없이 재시도합니다..."
  pip install -r requirements.txt --no-build-isolation
fi

echo "[설정] 개발 모드 설치 중..."
pip install -e .

echo
echo "==============================================="
echo " 설정 완료!"
echo "==============================================="
echo "다음 단계:"
echo "1. OpenAI API 키를 준비하세요"
echo "2. 환경변수 OPENAI_API_KEY를 설정하거나"
echo "3. ./run.sh를 실행하여 PDF를 처리하세요"
