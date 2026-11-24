"""아침 판정(판정 봇)이 읽는 회사 사실 요약 — 회사 보고서의 frontmatter 만 모아 한 줄씩 낸다.

    python3 -I facts.py [날짜] [시작 번호] [개수]

candidates/<날짜>.json 의 회사마다: company_key · 보고서 유무 · business · employees · founded · stage · profit · summary(평가 한 줄).
보고서가 없거나 그 값이 없으면 「조사 중」으로 낸다.
"""
import json
import sys
from datetime import date
from pathlib import Path

import yaml

DATA = Path("/opt/jobfeed/store/data")
REPORTS = Path("/opt/jobfeed/notes/기업")
FIELDS = ("business", "employees", "founded", "stage", "profit", "summary")


def facts(key):
    report = REPORTS / f"{key}.md"
    if not report.exists():
        return None
    parts = report.read_text().split("---", 2)
    try:
        meta = yaml.safe_load(parts[1]) if len(parts) == 3 else {}
    except yaml.YAMLError:
        meta = {}
    return {f: str((meta or {}).get(f) or "").strip() for f in FIELDS} | {"researched": str((meta or {}).get("researched") or "")}


def main():
    args = sys.argv[1:]
    today = args[0] if args else date.today().isoformat()
    start = int(args[1]) if len(args) > 1 else 0
    count = int(args[2]) if len(args) > 2 else 10_000
    items = json.loads((DATA / "candidates" / f"{today}.json").read_text())["items"]
    keys = list(dict.fromkeys(i["company_key"] for i in items))
    print(f"회사 {len(keys)}곳 중 {start}~{min(start + count, len(keys)) - 1}번")
    for n, key in enumerate(keys[start:start + count], start):
        f = facts(key)
        if not f or not f["summary"]:
            print(f"[{n}] {key} · 보고서: 조사 중")
            continue
        print(f"[{n}] {key} · 보고서: 있음(조사 {f['researched']}) · 하는 일: {f['business'] or '-'} · 임직원: {f['employees'] or '-'} · "
              f"설립: {f['founded'] or '-'} · 단계: {f['stage'] or '-'} · 손익: {f['profit'] or '-'} · 평가: {f['summary']}")


if __name__ == "__main__":
    main()
