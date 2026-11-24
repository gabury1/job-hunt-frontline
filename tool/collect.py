"""직행 · 점핏 · 자소설닷컴에서 새로 올라온 공고를 모아 store/jobfeed/data/new/<날짜>.json 에 쓴다.

판정(지원 · 특기)은 하지 않는다. 사람이 정한 범위로 거르고, 이미 본 공고는 뺀다.
판정과 보고는 판정 봇 예약 「취업 공고 아침 보고」가 이 파일을 읽어서 한다.
범위의 정본은 옵시디언 취업최전선/취업 준비 지도.md 의 「지원 대상」 · 「지원 직무」 표다.
"""
import json
import random
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

UA = "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
DATA = Path("/opt/jobfeed/store/data")
SEEN = DATA / "seen.json"
NOW = datetime.now()
MAX_CAREER_MIN = 1  # 요구 경력 하한 1년까지. 「2년 이상」부터 뺀다. 「3년 이하」 같은 상한형(하한 0~1)은 남긴다
FIRST_RUN_LOOKBACK = timedelta(days=1)
# --backfill: 기간 제한 없이 지금 접수 중인 공고를 모은다. 첫 실행이 하루치만 봐서 그 전에 올라온 공고가 빠졌다(11-24).
# 「공고 현황」에만 들어갈 공고라 아침 보고와 따로 돌린다
BACKFILL = "--backfill" in sys.argv
BACKFILL_LOOKBACK = timedelta(days=365)

ZIGHANG_CATEGORIES = ["서버_백엔드", "소프트웨어엔지니어", "DevOps_SRE", "시스템_네트워크", "생성형AI", "RAG", "LLM"]
JUMPIT_CATEGORIES = {1: "서버/백엔드", 8: "인공지능/머신러닝", 9: "devops/시스템 엔지니어", 15: "SW/솔루션"}
# 자소설 직무 그룹: 웹개발 · 시스템프로그래머 · 응용프로그래머 · 네트워크·보안·운영 · 빅데이터·AI · SW·솔루션·ERP
JASOSEOL_DUTIES = {162: "웹개발", 164: "시스템프로그래머", 165: "응용프로그래머", 166: "네트워크·보안·운영", 167: "빅데이터·AI", 170: "SW·솔루션·ERP"}
JASOSEOL_LATE = timedelta(days=2)  # 자소설은 접수 시작일(대개 00:00)로 올라오고 늦게 등록되기도 해서 이만큼 더 거슬러 본다
JASOSEOL_DIVISIONS = {1: "신입", 3: "인턴"}
JASOSEOL_SIZE = {"big_business": "대기업", "middle_market": "중견", "public_institution": "공공기관"}


LOG = Path("/opt/jobfeed/store/logs/run.log")


def progress(site, done, total):
    """본문을 받는 동안 100건마다 진행을 로그에 바로 남긴다. run.sh 는 끝난 뒤에야 출력을 쓰므로 여기서 직접 쓴다."""
    if done % 100 == 0 or done == total:
        with LOG.open("a") as f:
            f.write(f"{datetime.now():%F %T} 진행 · {site} 본문 {done}/{total}\n")


# 요청 사이 쉬는 시간은 고정값 대신 무작위(지터)로 준다. 사이트가 기계 요청으로 보고 막지 않게
def get(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.load(res)


def doc_text(node):
    """직행 요약 문서(prosemirror 모양)를 줄글로 편다."""
    if isinstance(node, list):
        return "\n".join(filter(None, (doc_text(n) for n in node)))
    if not isinstance(node, dict):
        return ""
    if node.get("type") == "text":
        return node.get("text", "")
    inner = node.get("content") or []
    if node.get("type") in ("paragraph", "heading"):
        line = "".join(doc_text(n) for n in inner)
        return ("## " + line) if node.get("type") == "heading" and line else line
    return doc_text(inner)


def is_open(end):
    return not end or datetime.fromisoformat(end[:19]) >= NOW


def zighang(since, seen):
    found = {}
    for category in ZIGHANG_CATEGORIES:
        for page in range(40):
            query = urllib.parse.urlencode({"depthTwos": category, "sortCondition": "LATEST", "page": page, "size": 50})
            content = get(f"https://api.zighang.com/api/recruitments?{query}")["data"]["content"]
            for item in content:
                key = f"zighang:{item['id']}"
                created = datetime.fromisoformat(item["createdAt"][:19])
                if created < since or key in seen or key in found:
                    continue
                if "해외" in item["regions"] or (item["careerMin"] or 0) > MAX_CAREER_MIN or not is_open(item["endDate"]):
                    continue
                found[key] = {
                    "key": key, "site": "직행", "id": item["id"],
                    "company": item["company"]["name"], "title": item["title"],
                    "career": [item["careerMin"], item["careerMax"]],
                    "end": (item["endDate"] or "")[:10] or "상시",
                    "posted": item["createdAt"][:10],
                    "regions": item["regions"], "types": item["employeeTypes"],
                    "categories": item["depthTwos"],
                    "url": f"https://zighang.com/recruitment/{item['id']}",
                }
            if not content or datetime.fromisoformat(content[-1]["createdAt"][:19]) < since:
                break
            time.sleep(random.uniform(0.5, 1.5))
    for done, item in enumerate(found.values(), 1):
        progress("직행", done, len(found))
        try:
            detail = get(f"https://api.zighang.com/api/recruitments/{item['id']}")["data"]
            item["body"] = doc_text(detail.get("summary"))[:3000]
        except Exception as error:
            item["body"] = f"(본문을 못 가져옴: {error})"
        time.sleep(random.uniform(1.0, 2.5))
    return list(found.values())


def jumpit(since, seen):
    found = {}
    for category_id, category in JUMPIT_CATEGORIES.items():
        for page in range(1, 20):
            positions = get(f"https://jumpit-api.saramin.co.kr/api/positions?jobCategory={category_id}&sort=reg_dt&page={page}")["result"]["positions"]
            for p in positions:
                key = f"jumpit:{p['id']}"
                if key in seen or key in found or (p["minCareer"] or 0) > MAX_CAREER_MIN:
                    continue
                if not p["alwaysOpen"] and not is_open(p["closedAt"]):
                    continue
                found[key] = {
                    "key": key, "site": "점핏", "id": p["id"],
                    "company": p["companyName"], "title": p["title"],
                    "career": [p["minCareer"], p["maxCareer"]],
                    "end": "상시" if p["alwaysOpen"] else (p["closedAt"] or "")[:10],
                    "regions": p["locations"], "categories": [category],
                    "stacks": p["techStacks"],
                    "url": f"https://jumpit.saramin.co.kr/position/{p['id']}",
                }
            if not positions:
                break
            time.sleep(random.uniform(0.5, 1.5))
    fresh = []
    for done, item in enumerate(found.values(), 1):
        progress("점핏", done, len(found))
        try:
            detail = get(f"https://jumpit-api.saramin.co.kr/api/position/{item['id']}")["result"]
        except Exception as error:
            item["body"] = f"(본문을 못 가져옴: {error})"
            fresh.append(item)
            continue
        published = datetime.fromisoformat(detail["publishedAt"][:19]) if detail.get("publishedAt") else NOW
        if published < since:
            seen[item["key"]] = "old"  # 처음 보는 공고라도 since 보다 오래된 것은 넘기고, 다음부터 상세를 다시 받지 않는다
            continue
        item["posted"] = published.date().isoformat()
        item["body"] = "\n\n".join(filter(None, (detail.get("responsibility"), detail.get("qualifications"), detail.get("preferredRequirements"))))[:3000]
        fresh.append(item)
        time.sleep(random.uniform(1.0, 2.5))
    return fresh


def jasoseol(since, seen):
    start = (NOW - timedelta(days=60)).strftime("%Y-%m-%dT15:00:00.000Z")
    end = (NOW + timedelta(days=120)).strftime("%Y-%m-%dT15:00:00.000Z")
    body = json.dumps({"start_time": start, "end_time": end}).encode()
    data = get("https://jasoseol.com/employment/calendar_list.json", data=body, headers={"Content-Type": "application/json"})
    found = []
    for e in data["employment"]:
        key = f"jasoseol:{e['id']}"
        if key in seen or not is_open(e["end_time"]):
            continue
        if datetime.fromisoformat(e["start_time"][:19]) < since - JASOSEOL_LATE:
            continue
        wanted = [em for em in e["employments"] if em["division"] in JASOSEOL_DIVISIONS
                  and JASOSEOL_DUTIES.keys() & {g["group_id"] for g in em["duty_groups"]}]
        if not wanted:
            continue
        divisions = sorted({JASOSEOL_DIVISIONS[em["division"]] for em in wanted})
        duties = sorted({JASOSEOL_DUTIES[g["group_id"]] for em in wanted for g in em["duty_groups"] if g["group_id"] in JASOSEOL_DUTIES})
        found.append({
            "key": key, "site": "자소설", "id": e["id"],
            "company": e["name"], "title": e["title"],
            "size": JASOSEOL_SIZE.get(e["business_size"], "기타"),
            "divisions": divisions, "categories": duties,
            "end": e["end_time"][:10],
            "posted": e["start_time"][:10],
            "body": f"자소설닷컴 달력 공고라 본문이 없다. 모집 구분 {'·'.join(divisions)}, 직무 그룹 {'·'.join(duties)}",
            "url": f"https://jasoseol.com/recruit/{e['id']}",
        })
    return found


def company_key(name):
    """회사 보고서 파일 이름 · 조사 캐시 키 · 노트 링크가 함께 쓰는 회사 이름. 법인 표기와 괄호를 뺀다."""
    name = re.sub(r"\([^)]*\)|（[^）]*）|\[[^\]]*\]|주식회사|㈜", "", name)
    name = re.sub(r'[\\/:*?"<>|#^\[\]]', " ", name)
    return re.sub(r"\s+", " ", name).strip() or "이름 없음"


def same_posting(item):
    """사이트가 달라도 같은 회사 · 같은 제목이면 한 공고로 본다.
    제목 속 회사 이름 · 괄호 · 태그 · 「채용」 같은 군말은 빼고 견준다. 한쪽이 다른 쪽을 품는 정도로는 묶지 않는다
    (지역 · 근무 형태만 다른 별개 공고가 그렇게 생겼다)."""
    company = re.sub(r"\([^)]*\)|주식회사|㈜|[^0-9A-Za-z가-힣]", "", item["company"]).lower()
    title = re.sub(r"\[[^\]]*\]|\([^)]*\)|#\S+", "", item["title"])
    title = re.sub(r"[^0-9A-Za-z가-힣]", "", title).lower().replace(company, "")
    title = re.sub(r"채용|모집|공고|공개|직원|사원|인원", "", title) or title
    return company + "|" + title


def report_day():
    """하루는 06시에 자른다. 06시 전에 손으로 돌린 것은 전날 보고에 들어가야 아침 보고에 다시 안 나온다."""
    return (NOW - timedelta(hours=6)).date().isoformat()


def main():
    seen = json.loads(SEEN.read_text()) if SEEN.exists() else {}
    last = seen.get("_last_run")
    since = datetime.fromisoformat(last) - timedelta(hours=6) if last else NOW - FIRST_RUN_LOOKBACK
    lookup = seen
    if BACKFILL:
        since = NOW - BACKFILL_LOOKBACK
        lookup = {k: v for k, v in seen.items() if v != "old"}  # 점핏이 「오래돼서 넘김」으로 적어 둔 공고도 다시 본다

    items, errors = [], []
    for name, fetch in (("직행", zighang), ("점핏", jumpit), ("자소설", jasoseol)):
        try:
            items += fetch(since, lookup)
        except Exception as error:
            errors.append(f"{name}: {error}")

    unique, titles = {}, list(seen.get("_titles", []))
    known = set(titles)
    for item in items:
        item["company_key"] = company_key(item["company"])
        if BACKFILL:
            item["backfill"] = True
        signature = same_posting(item)
        if signature in known:
            seen[item["key"]] = report_day()
            continue
        known.add(signature)
        titles.append(signature)
        unique[item["key"]] = item

    today = report_day()
    out = DATA / "new" / f"{today}.json"
    # 같은 보고일에 두 번 돌면(06시 뒤에 손으로 다시 돌린 때) 앞서 모은 공고를 지우지 않고 뒤에 붙인다
    earlier = json.loads(out.read_text()) if out.exists() else {"since": since.isoformat(timespec="minutes"), "items": []}
    merged = earlier["items"] + list(unique.values())
    out.write_text(json.dumps({"date": today, "since": earlier["since"], "errors": errors,
                               "count": len(merged), "items": merged}, ensure_ascii=False, indent=1))
    for key in unique:
        seen[key] = today
    seen["_titles"] = titles[-20000:]  # 오래된 것부터 버린다
    seen["_last_run"] = NOW.isoformat(timespec="minutes")
    SEEN.write_text(json.dumps(seen, ensure_ascii=False))
    print(f"새 공고 {len(unique)}건 → {out}" + (f" · 오류 {errors}" if errors else ""))
    return 1 if len(errors) == 3 else 0


if __name__ == "__main__":
    sys.exit(main())
