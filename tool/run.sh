#!/usr/bin/env bash
# 취업 공고 수집 + 사전 거르기 — 매일 06:00 크론.
# 수집 결과는 store/jobfeed/data/new/<날짜>.json, 사전 거르기 결과는 candidates/<날짜>.json.
# 다음 단계: 06:10 회사 조사(research.sh --from candidates) → 08:00 판정 봇 판정 · 보고 → 08:20 남은 회사 조사(--from kept)
set -uo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
if out=$(/usr/bin/python3 -I "$DIR/collect.py" 2>&1); then
  echo "$(date '+%F %T') 성공 · $out"
else
  code=$?
  echo "$(date '+%F %T') 실패 (exit $code) · $out"
  exit "$code"
fi
if out=$(/usr/bin/python3 -I "$DIR/prefilter.py" 2>&1); then
  echo "$(date '+%F %T') 성공 · $out"
else
  code=$?
  echo "$(date '+%F %T') 실패 (exit $code) · $out"
  exit "$code"
fi
