"""빠진 공고 판정 — 첫 실행이 하루치만 봐서 빠진 공고(collect.py --backfill)를 워크플로우 에이전트가 나눠 판정하게 돕는다.

아침 판정은 판정 봇이 한 번에 160건 안팎을 하지만, 메우기는 천 건이 넘어 여러 에이전트로 나눈다. 판정 기준은 아침 판정과 같다(취업 준비 지도).
결과는 「공고 현황」에만 들어간다. 「오늘의 공고」와 채널 보고는 건드리지 않는다.

    python3 -I backfill.py --prepare <날짜> [묶음 크기]   candidates/<날짜>.json 의 backfill 공고를 묶음 파일로 나누고 판정 지시문을 쓴다
    python3 -I backfill.py --apply <날짜>                stage/judge/*.json 을 모아 kept/<날짜>.json 에 더하고, 조사할 회사 · 노트를 만들 공고를 낸다
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

DATA = Path("/opt/jobfeed/store/data")
STAGE = DATA / "backfill"
REPORTS = Path("/opt/jobfeed/notes/기업")
GUIDE = Path("/opt/jobfeed/notes/취업 준비 지도.md")

RULES = """판정 기준의 정본은 {guide} 다. 이 파일을 먼저 읽고 「전략」 문단, 「지원 대상」 표, 「지원 직무」 표와 그 아래 설명대로 가른다. 아래는 그 표를 읽는 순서일 뿐이고, 표와 어긋나면 표를 따른다.

- 회사마다 「지원 대상」 표의 카테고리를 하나 정한다. 공고 본문 · 제목 · 회사 이름으로 정한다. 어느 칸에도 딱 맞지 않으면 「기타」로 두지 말고 가장 가까운 칸에 넣는다.
- 회사 이름을 숨긴 헤드헌팅 대행 공고는 카테고리를 「헤드헌팅」으로 따로 표시하고 지원 대상으로 둔다. 특기로는 올리지 않는다.
- 표의 지원 칸이 X 인 카테고리는 뺀다.
- 직무는 「지원 직무」 표로 가른다. 제목이 아니라 본문의 담당 업무를 보고 정한다. 지원 X 인 직무, 표에 없는 직무, 개발이 아닌 직무는 뺀다. 표의 「이유」 칸에 적힌 조건(남기는 범위와 빼는 조건)도 판정 기준이다. 생성형 AI 계열은 LLM API 연동 · 에이전트 · RAG 를 붙이는 서비스 개발만 남기고, 모델을 학습시키는 연구 · 비개발 직무는 뺀다. DevOps 와 인프라는 본문을 보고 가른다. 인프라 직무는 특기 O 회사의 공고만 남긴다.
- 특기: 「지원 대상」 표의 특기 칸이 O 인 카테고리는 전부, △ 인 카테고리는 「특기 조건」 칸의 조건을 공고 본문에서 확인했을 때만 특기다. 특기마다 그 이유를 한 줄로 적는다.
- IDC 관제 · 교대 근무 자리는 남기는 공고라도 따로 표시한다(shift).
- 지어내지 않는다. 본문에 없는 것은 없다고 본다. 자소설닷컴 공고는 본문이 없으니 회사와 제목만으로 가른다."""

PROMPT = """너는 취업 준비생가 지원할 공고를 고르는 판정을 맡았다. 공고 묶음 하나를 판정한다.

## 기준

{rules}

## 할 일

1. {guide} 를 읽는다.
2. {chunk} 를 읽는다. JSON 배열이고, 공고마다 url · site · company · company_key · title · career[하한, 상한] · end · regions · categories · body 가 있다. 상한 100 은 상한 없음이다.
3. 모든 공고를 하나도 빠짐없이 판정한다.
4. 결과를 {out} 파일에 JSON 으로 쓴다. 최상위는 items 배열이고, 공고마다 아래 키를 넣는다. 이 파일 말고는 아무것도 쓰지 않는다.
   - url: 입력 값 그대로
   - keep: 남기면 true, 빼면 false
   - category: 정한 카테고리(빼는 공고도 적는다)
   - role: 정한 직무(빼는 공고도 적는다. 지원 직무 표에 없으면 공고의 직무 이름)
   - special: 특기면 true
   - reason: 특기면 특기 이유 한 줄, 아니면 빈 문자열
   - shift: IDC 관제 · 교대 근무 자리면 true
   - drop_reason: 빼는 공고면 빼는 이유 한 줄, 남기면 빈 문자열
5. 파일을 쓴 뒤 python3 로 다시 읽어 JSON 으로 파싱되는지, items 건수가 입력 건수와 같은지 확인한다."""


def prepare(day, size):
    data = json.loads((DATA / "candidates" / f"{day}.json").read_text())
    items = [i for i in data["items"] if i.get("backfill")]
    chunks = STAGE / "judge-in"
    chunks.mkdir(parents=True, exist_ok=True)
    (STAGE / "stage" / "judge").mkdir(parents=True, exist_ok=True)
    (STAGE / "prompts").mkdir(parents=True, exist_ok=True)
    keys = ("url", "site", "company", "company_key", "title", "career", "end", "regions", "categories", "body")
    names = []
    for n in range(0, len(items), size):
        name = f"chunk-{n // size:03d}"
        chunk = chunks / f"{name}.json"
        chunk.write_text(json.dumps([{k: (i.get(k) or "")[:2000] if k == "body" else i.get(k) for k in keys} for i in items[n:n + size]],
                                    ensure_ascii=False, indent=1))
        out = STAGE / "stage" / "judge" / f"{name}.json"
        (STAGE / "prompts" / f"judge-{name}.md").write_text(
            PROMPT.format(rules=RULES.format(guide=GUIDE), guide=GUIDE, chunk=chunk, out=out))
        names.append(name)
    print(json.dumps({"items": len(items), "chunks": names}, ensure_ascii=False))


def apply(day):
    data = json.loads((DATA / "candidates" / f"{day}.json").read_text())
    by_url = {i["url"]: i for i in data["items"] if i.get("backfill")}
    judged, missing = {}, []
    for path in sorted((STAGE / "stage" / "judge").glob("*.json")):
        for j in json.loads(path.read_text())["items"]:
            judged[j["url"]] = j
    missing = [u for u in by_url if u not in judged]
    kept_path = DATA / "kept" / f"{day}.json"
    kept = json.loads(kept_path.read_text()) if kept_path.exists() else {"date": day, "items": []}
    have = {i["url"] for i in kept["items"]}
    added = []
    for url, j in judged.items():
        if not j.get("keep") or url in have or url not in by_url:
            continue
        p = by_url[url]
        added.append({"company": p["company"], "company_key": p["company_key"], "category": j.get("category", ""),
                      "role": j.get("role", ""), "special": bool(j.get("special")), "reason": j.get("reason", "") if j.get("special") else "",
                      "shift": bool(j.get("shift")), "url": url, "title": p["title"], "backfill": True})
    kept["items"] += added
    kept_path.write_text(json.dumps(kept, ensure_ascii=False, indent=1))
    drops = {}
    for j in judged.values():
        if not j.get("keep"):
            drops[j.get("drop_reason") or "-"] = drops.get(j.get("drop_reason") or "-", 0) + 1
    # 회사 조사는 매일 흐름과 같다: 헤드헌팅은 빼고, 7일 안에 조사해 보고서가 있는 회사는 건너뛴다
    cache = json.loads((DATA / "companies.json").read_text()) if (DATA / "companies.json").exists() else {}
    fresh = {k for k, v in cache.items() if (REPORTS / f"{k}.md").exists()
             and datetime.now() - datetime.fromisoformat(v["last_research"]) < timedelta(days=7)}
    companies = sorted({i["company_key"] for i in added if i["category"] != "헤드헌팅"} - fresh)
    print(json.dumps({"judged": len(judged), "missing": len(missing), "kept": len(added),
                      "special": sum(1 for i in added if i["special"]), "companies": companies,
                      "urls": [i["url"] for i in added]}, ensure_ascii=False))


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--prepare"]:
        prepare(args[1], int(args[2]) if len(args) > 2 else 40)
    elif args[:1] == ["--apply"]:
        apply(args[1])
    else:
        raise SystemExit(__doc__)
