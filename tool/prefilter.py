"""사전 거르기 — 회사 조사 전에 공고 글만으로 확실히 빠지는 것만 뺀다. 애매하면 남긴다.

new/<날짜>.json → candidates/<날짜>.json (items: 남긴 공고, dropped: 뺀 공고와 이유)
회사 조사(research.py --from candidates)가 items 의 회사를 조사하고, 판정 봇 판정이 items 만 판정한다.

    python3 prefilter.py [날짜]
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

DATA = Path("/opt/jobfeed/store/data")

# 제목에 이것이 있으면 SI · SM · 파견으로 본다
SI_TITLE = re.compile(r"파견|상주|하도급|프리랜서|SI\s*/\s*SM|(?<![A-Za-z])(SI|SM)(?![A-Za-z])|운영인원|유지보수 인력")
# 본문은 담당 업무 부분(자격 · 우대 앞)에서만 본다. 우대사항의 「SI 프로젝트 경험」은 회사 성격을 말해 주지 않는다
SI_DUTY = re.compile(r"파견|상주|하도급")
DUTY_END = re.compile(r"##\s*(자격|지원 ?자격|필요 역량|우대|기술 스택|사용 기술|개발 환경)")
# 제목에 이것이 있으면 지원 직무 표 밖의 직무로 본다
OFF_ROLE = re.compile(r"헬프데스크|출장|수리|설치 기사|OA|방송기술|시설기술|총무|FAE|Field Application|PreSales|Pre-Sales")


def reason(item):
    title, body = item["title"], item.get("body") or ""
    if m := SI_TITLE.search(title):
        return f"SI · SM · 파견 신호(제목 「{m.group(0)}」)"
    duty = body[: m.start()] if (m := DUTY_END.search(body)) else body[:600]
    if m := SI_DUTY.search(duty):
        return f"SI · SM · 파견 신호(담당 업무 「{m.group(0)}」)"
    if m := OFF_ROLE.search(title):
        return f"지원 직무 밖(제목 「{m.group(0)}」)"
    return None


def main():
    today = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    src = DATA / "new" / f"{today}.json"
    if not src.exists():
        print(f"사전 거르기: {src} 없음")
        return 1
    data = json.loads(src.read_text())
    items, dropped = [], []
    for item in data["items"]:
        why = reason(item)
        if why:
            dropped.append({"company": item["company"], "company_key": item.get("company_key"), "title": item["title"],
                            "url": item["url"], "reason": why})
        else:
            items.append(item)
    out = DATA / "candidates" / f"{today}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"date": today, "count_new": len(data["items"]), "errors": data.get("errors", []),
                               "count": len(items), "items": items, "dropped": dropped}, ensure_ascii=False, indent=1))
    companies = len({i.get("company_key") for i in items})
    print(f"사전 거르기: 새 공고 {len(data['items'])} → 남김 {len(items)}(회사 {companies}) · 뺌 {len(dropped)} → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
