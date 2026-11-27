#!/usr/bin/env bash
# 회사 조사 — 06:10(사전 거르기 결과에서 보고서 없는 회사만 짧은 확인, --from candidates --light)과 08:20(판정 봇 판정 결과, --from kept) 두 번 돈다.
# 두 실행이 겹치지 않게 잠금을 잡는다. 앞 실행이 길어지면 뒤 실행은 끝나기를 기다린다(최대 90분).
# 08:20 실행은 조사 전에 「공고 현황」 노트를 한 번 갱신하고(08:00 판정 반영), 조사가 끝나면 다시 갱신한다(회사 평가 반영).
set -uo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
LOCK=/opt/jobfeed/store/data/research.lock

status() {
  if out=$(/usr/bin/python3 -I "$DIR/status.py" "$@" 2>&1); then
    echo "$(date '+%F %T') 성공 · $out"
  else
    echo "$(date '+%F %T') 실패 (공고 현황, exit $?) · $out"
  fi
}

kept=0
[[ " $* " == *" --from kept "* || " $* " != *" --from "* ]] && kept=1
if (( kept )); then
  # 08:00 판정이 길어지면(제한 25분) 판정 기록이 아직 없다. 30분까지 기다렸다가 현황을 갱신한다
  for _ in $(seq 60); do [[ -f /opt/jobfeed/store/data/kept/$(date +%F).json ]] && break; sleep 30; done
  status
fi

if flock -w 5400 "$LOCK" /usr/bin/python3 -I "$DIR/research.py" "$@"; then
  echo "$(date '+%F %T') 성공 ($*)"
  code=0
else
  code=$?
  echo "$(date '+%F %T') 실패 (exit $code, $*)"
fi
if (( kept )); then
  # 공개판 추가 판정(지원자 기준에서 빠진 것 중 프론트엔드 · 풀스택 · 공공기관 · 비IT 사내 IT)과 그 회사 조사. 지원자 보고에는 섞이지 않는다
  day=$(printf '%s\n' "$@" | grep -m1 -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' || date +%F)
  if out=$(/usr/bin/python3 -I "$DIR/public_judge.py" "$day" 2>&1); then
    echo "$(date '+%F %T') 성공 (공개판 판정) · $out"
    [[ -f /opt/jobfeed/store/data/kept-public/$day.json ]] && \
      flock -w 5400 "$LOCK" /usr/bin/python3 -I "$DIR/research.py" "$day" --from kept-public && echo "$(date '+%F %T') 성공 (공개판 회사 조사)"
  else
    echo "$(date '+%F %T') 실패 (공개판 판정, exit $?) · $out"
  fi
  # 판정에 남은 공고마다 공고 보고서(취업최전선/공고/)를 만든다. 날짜 인자가 있으면 그날 것을 만든다
  day=$(printf '%s\n' "$@" | grep -m1 -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' || date +%F)
  if /usr/bin/python3 -I "$DIR/posting.py" "$day"; then
    echo "$(date '+%F %T') 성공 (공고 보고서 $day)"
  else
    echo "$(date '+%F %T') 실패 (공고 보고서 $day, exit $?)"
  fi
  status --no-check
  # 소마 공유용 정제본(store/jobfeed/share)을 다시 만들고 커밋한다. 원격이 걸려 있으면 올린다
  if out=$(/usr/bin/python3 -I "$DIR/share.py" --push 2>&1); then
    echo "$(date '+%F %T') 성공 · $out"
  else
    echo "$(date '+%F %T') 실패 (정제본, exit $?) · $out"
  fi
fi
exit "$code"
