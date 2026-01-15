#!/usr/bin/env bash
set -euo pipefail

echo "==============================================="
echo " PDF 자동 태깅 시스템 (APATS)"
echo "==============================================="
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "[오류] python3가 설치되지 않았습니다."
  exit 1
fi

if [ ! -d "venv" ]; then
  echo "[설정] 가상환경 생성 중..."
  python3 -m venv venv
fi

echo "[설정] 가상환경 활성화 중..."
source venv/bin/activate

if ! python -c "import fitz" >/dev/null 2>&1; then
  echo "[설정] 필요한 패키지 설치 중..."
  python -m pip install --upgrade pip setuptools wheel
  if ! pip install -r requirements.txt; then
    echo "[경고] 기본 설치 실패, 빌드 격리 없이 재시도합니다..."
    pip install -r requirements.txt --no-build-isolation
  fi
fi

pip install -e . >/dev/null 2>&1 || true

if [ -z "${OPENAI_API_KEY:-}" ]; then
  read -r -p "OpenAI API 키를 입력하세요: " API_KEY
  if [ -z "${API_KEY}" ]; then
    echo "[오류] API 키가 필요합니다."
    exit 1
  fi
  export OPENAI_API_KEY="${API_KEY}"
fi

INPUT_FILE="${1:-}"
OUTPUT_FILE="${2:-}"

if [ -z "${INPUT_FILE}" ]; then
  read -r -p "입력 PDF 파일 경로를 입력하세요: " INPUT_FILE
fi

if [ -z "${INPUT_FILE}" ]; then
  echo "[오류] 입력 경로가 비어있습니다."
  exit 1
fi

if [ -d "${INPUT_FILE}" ]; then
  if [ -z "${OUTPUT_FILE}" ]; then
    OUTPUT_FILE="outputs"
  fi
  mkdir -p "${OUTPUT_FILE}"
elif [ -f "${INPUT_FILE}" ]; then
  if [ -z "${OUTPUT_FILE}" ]; then
    OUTPUT_FILE="${INPUT_FILE%.*}_tagged.pdf"
  fi
else
  echo "[오류] 입력 파일 또는 폴더를 찾을 수 없습니다: ${INPUT_FILE}"
  exit 1
fi

echo
echo "입력 파일: ${INPUT_FILE}"
echo "출력 파일: ${OUTPUT_FILE}"
echo

python -m src.main "${INPUT_FILE}" "${OUTPUT_FILE}"
