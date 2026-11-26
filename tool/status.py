"""공고 현황 — 지금 접수 중인 공고를 한 노트에 모은다. 「오늘의 공고」가 그날 새로 뜬 것이라면, 이 노트는 지금 낼 수 있는 곳 전부다.

판정 봇 판정이 남긴 kept/*.json 전부를 모으고, new/*.json 에서 마감 · 요구 경력 · 올라온 날을 붙인다.
마감이 지난 공고는 뺀다. 마감이 없는 상시 채용은 하루 한 번 공고가 아직 열려 있는지 사이트 API 로 보고, 닫혔으면 뺀다.
노트는 매번 통째로 갈아 쓴다. 칸은 셋: 특기 · 나머지(둘 다 마감이 가까운 순) · 상시 채용(특기 먼저).

    python3 -I status.py [--no-check]   # --no-check: 상시 채용이 열려 있는지 사이트에 묻지 않는다
"""
import json
import random
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

import yaml

DATA = Path("/opt/jobfeed/store/data")
sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I 로 돌면 스크립트 폴더가 경로에 없다
import origins  # noqa: E402
NOTE = Path("/opt/jobfeed/notes/공고 현황.md")
REPORTS = Path("/opt/jobfeed/notes/기업")
POSTINGS = DATA / "postings.json"  # posting.py 가 남기는 공고 url → 공고 보고서 파일
POSTING_NOTES = Path("/opt/jobfeed/notes/공고")
CHECKS = DATA / "status-checks.json"  # 상시 채용 공고가 열려 있는지 마지막으로 본 날과 결과
MAX_CAREER_MIN = 1  # collect.py 와 같은 기준. 기준이 바뀌기 전에 판정된 공고(「2년 이상」 · 「3년 이상」)가 섞여 있어 여기서도 뺀다
RED_DAYS = 7
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
TODAY = date.today()


def load(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def postings():
    """url → 공고. 처음 수집된 보고일을 first_seen 으로 붙인다."""
    found = {}
    for path in sorted((DATA / "new").glob("*.json")):
        for item in load(path, {"items": []})["items"]:
            found.setdefault(item["url"], {**item, "first_seen": path.stem})
    return found


def judged(dirs=("kept",)):
    """url → 판정. 같은 공고가 여러 날 판정됐으면 나중 판정을 쓴다.
    kept 는 지원자 기준(판정 봇 판정), kept-public 은 공개판에만 더하는 판정(public_judge.py)이다."""
    found = {}
    for path in sorted(p for d in dirs for p in (DATA / d).glob("*.json")):
        for item in load(path, {"items": []})["items"]:
            found[item["url"]] = item
    return found


def still_open(post):
    """상시 채용이 아직 열려 있는지 사이트에 묻는다. 모르면(오류) 열려 있다고 본다."""
    site, pid = post.get("site"), post.get("id")
    try:
        if site == "직행":
            data = fetch(f"https://api.zighang.com/api/recruitments/{pid}").get("data")
            return bool(data) and data.get("status") == "ACTIVE"
        if site == "원티드":
            job = fetch(f"https://www.wanted.co.kr/api/v4/jobs/{pid}").get("job")
            return bool(job) and job.get("status") == "active"
        if site == "점핏":
            result = fetch(f"https://jumpit-api.saramin.co.kr/api/position/{pid}").get("result")
            if not result or result.get("invisible"):
                return False
            closed = result.get("closedAt")
            return result.get("alwaysOpen") or not closed or datetime.fromisoformat(closed[:19]) >= datetime.now()
    except urllib.error.HTTPError as error:
        return error.code not in (404, 410)
    except Exception:
        return True
    return True


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.load(res)


def summary_of(key):
    report = REPORTS / f"{key}.md"
    if not report.exists():
        return None
    parts = report.read_text().split("---", 2)
    try:
        meta = yaml.safe_load(parts[1]) if len(parts) == 3 else None
    except yaml.YAMLError:
        return None
    return str((meta or {}).get("summary") or "").strip() or None


def cell(text):
    return str(text or "").replace("|", "／").replace("\n", " ").strip()


def career(post):
    low, high = (list(post.get("career") or []) + [None, None])[:2]
    low = low or 0
    if not high or high >= 100:
        return "신입 이상" if low == 0 else f"{low}년 이상"
    if low == 0:
        return f"신입 ~ {high}년"
    return f"{low} ~ {high}년"


def deadline(end):
    if end == "상시":
        return "상시"
    if date.fromisoformat(end) <= TODAY + timedelta(days=RED_DAYS):
        return f'<span style="color:red">{end}</span>'
    return end


def research_cells(row):
    if row["category"] == "헤드헌팅":
        return "조사 안 함 (헤드헌팅)", "조사 안 함 (헤드헌팅)"
    summary = summary_of(row["company_key"])
    if not summary:
        return "조사 중", "조사 중"
    return cell(summary), f"[[취업최전선/기업/{row['company_key']}\\|보고서]]"


def table(head, rows):
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    return lines


def open_rows(check, public=False):
    """지금 접수 중인 공고 줄과 뺀 건수(마감 지남 · 상시 종료 · 2년 이상 · 다른 사이트 중복). share.py 도 이걸 쓴다(public=True: 공개판 판정까지)."""
    posts, kept = postings(), judged(("kept", "kept-public") if public else ("kept",))
    checks = load(CHECKS, {})
    rows, expired, closed, too_senior = [], 0, 0, 0
    for url, judge in kept.items():
        post = posts.get(url, {})
        end = post.get("end") or "상시"
        if (post.get("career") or [0])[0] and post["career"][0] > MAX_CAREER_MIN:
            too_senior += 1
            continue
        if end != "상시":
            if date.fromisoformat(end) < TODAY:
                expired += 1
                continue
        else:
            last = checks.get(url, {})
            if last.get("open") is False:
                closed += 1
                continue
            if check and last.get("checked") != TODAY.isoformat():
                checks[url] = {"checked": TODAY.isoformat(), "open": still_open(post)}
                time.sleep(random.uniform(1.0, 3.0))  # 사이트가 기계 요청으로 보고 막지 않게 무작위로 쉰다
                if not checks[url]["open"]:
                    closed += 1
                    continue
        rows.append({**judge, "end": end, "career_text": career(post),
                     "posted": post.get("posted") or post.get("first_seen") or "-", "first_seen": post.get("first_seen") or "-",
                     "company_key": judge.get("company_key") or post.get("company_key") or judge["company"]})
    CHECKS.write_text(json.dumps(checks, ensure_ascii=False, indent=1))
    # 원래 공고 주소가 같으면 사이트가 달라도 한 공고다(origins.py). 공고 노트가 있는 줄, 그다음 먼저 본 줄을 남긴다
    origin_of = load(DATA / "origins.json", {})
    notes = load(POSTINGS, {})
    taken, unique = set(), []
    for r in sorted(rows, key=lambda r: (r["url"] not in notes, r.get("first_seen") or "9")):
        found = origins.keys(origin_of.get(r["url"]), r["company_key"]) or {r["url"]}
        if found & taken:
            continue
        taken |= found
        unique.append(r)
    dups = len(rows) - len(unique)
    rows = unique
    return rows, expired, closed, too_senior, dups


def main():
    check = "--no-check" not in sys.argv
    reports = load(POSTINGS, {})
    rows, expired, closed, too_senior, dups = open_rows(check)
    if check:  # 공개판에만 있는 상시 공고도 열려 있는지 확인해 둔다(share.py 는 확인 기록만 읽는다)
        open_rows(True, public=True)

    dated = sorted((r for r in rows if r["end"] != "상시"), key=lambda r: (r["end"], r["company_key"]))
    always = sorted((r for r in rows if r["end"] == "상시"), key=lambda r: r["posted"], reverse=True)  # 최근에 올라온 것부터
    always.sort(key=lambda r: not r.get("special"))  # 특기를 위로. 정렬이 안정적이라 날짜 순서는 그대로 남는다
    special = [r for r in dated if r.get("special")]
    rest = [r for r in dated if not r.get("special")]

    def link(r):
        return f"[공고]({r['url']})"

    def posting_link(r):
        done = reports.get(r["url"])
        if done and (POSTING_NOTES / f"{done['file']}.md").exists():
            return f"[[취업최전선/공고/{done['file']}\\|공고 보고서]]"
        return "만드는 중"

    special_rows = []
    for r in special:
        evaluation, report = research_cells(r)
        special_rows.append([cell(r["company_key"]), cell(r["title"]), r["career_text"], deadline(r["end"]), r["posted"],
                             cell(r.get("reason")) or "-", evaluation, report, posting_link(r), link(r)])
    shift = any(r.get("shift") for r in rest)
    rest_rows = []
    for r in rest:
        evaluation, report = research_cells(r)
        row = [cell(r["company_key"]), cell(r["category"]), cell(r["role"]), cell(r["title"]), r["career_text"],
               deadline(r["end"]), r["posted"]]
        if shift:
            row.append("IDC 관제 · 교대" if r.get("shift") else "")
        rest_rows.append(row + [evaluation, report, posting_link(r), link(r)])
    always_rows = []
    for r in always:
        evaluation, report = research_cells(r)
        always_rows.append([cell(r["company_key"]), "특기" if r.get("special") else "", cell(r["category"]), cell(r["role"]),
                            cell(r["title"]), r["career_text"], r["posted"], evaluation, report, posting_link(r), link(r)])

    now = datetime.now()
    lines = ["---", "tags: [취업]", f'date: "{TODAY.isoformat()}"', "---", "",
             f"- 갱신: {now:%Y-%m-%d %H:%M}",
             f"- 접수 중: {len(rows)}건 (특기 {len(special)} · 나머지 {len(rest)} · 상시 채용 {len(always)})",
             f"- 이번에 뺀 공고: 마감 지남 {expired} · 상시 채용 종료 {closed} · 요구 경력 2년 이상 {too_senior} · 다른 사이트에 같은 공고 {dups}",
             "- 오늘 새로 뜬 공고만 보려면 [[취업최전선/오늘의 공고|오늘의 공고]]", ""]
    lines += ["## 특기", ""]
    lines += table(["회사", "제목", "요구 경력", "마감", "올라온 날", "특기 이유", "회사 평가", "회사 조사", "공고 보고서", "링크"], special_rows) if special_rows else ["없음"]
    lines += ["", "## 나머지 공고", ""]
    rest_head = ["회사", "카테고리", "직무", "제목", "요구 경력", "마감", "올라온 날"] + (["표시"] if shift else []) + ["회사 평가", "회사 조사", "공고 보고서", "링크"]
    lines += table(rest_head, rest_rows) if rest_rows else ["없음"]
    lines += ["", "## 상시 채용", ""]
    lines += table(["회사", "특기", "카테고리", "직무", "제목", "요구 경력", "올라온 날", "회사 평가", "회사 조사", "공고 보고서", "링크"], always_rows) if always_rows else ["없음"]
    NOTE.write_text("\n".join(lines) + "\n")
    print(f"공고 현황: 접수 중 {len(rows)}(특기 {len(special)} · 나머지 {len(rest)} · 상시 {len(always)}) · "
          f"뺌: 마감 {expired} · 상시 종료 {closed} · 2년 이상 {too_senior} · 중복 {dups} → {NOTE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
