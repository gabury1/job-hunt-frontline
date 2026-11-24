"""DART OpenAPI 도우미 — 회사 조사(research.py)와 조사하는 claude -p 가 부른다.

    python3 dart.py update            고유번호 목록(corpCode.xml)을 7일마다 받아 캐시한다
    python3 dart.py search <이름>      회사 이름(한글 · 영문 일부)으로 고유번호 후보를 찾는다
    python3 dart.py info <고유번호>    기업 개황 · 재무 · 직원 수 · 최근 공시를 글로 낸다

키는 같은 폴더 .env 의 DART_API_KEY 다. 출력에 키를 싣지 않는다.
"""
import html
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = Path("/opt/jobfeed/store/data/dart-corp.json")
REFRESH = timedelta(days=7)
API = "https://opendart.fss.or.kr/api"
ACCOUNTS = ("매출액", "영업이익", "당기순이익(손실)", "당기순이익", "자본금", "자본총계", "부채총계", "자산총계")


def key():
    if os.environ.get("DART_API_KEY"):
        return os.environ["DART_API_KEY"]
    for line in (HERE / ".env").read_text().splitlines():
        if line.startswith("DART_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit("DART_API_KEY 없음")


def call(endpoint, raw=False, **params):
    params["crtfc_key"] = key()
    endpoint = endpoint if "." in endpoint else endpoint + ".json"
    url = f"{API}/{endpoint}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=60) as res:
        body = res.read()
    return body if raw else json.loads(body)


def norm(name):
    name = re.sub(r"\([^)]*\)|（[^）]*）|주식회사|㈜|\(주\)", "", name or "")
    return re.sub(r"[^0-9A-Za-z가-힣]", "", name).lower()


def update(force=False):
    if not force and CACHE.exists() and time.time() - CACHE.stat().st_mtime < REFRESH.total_seconds():
        return f"고유번호 캐시 그대로 ({CACHE})"
    archive = zipfile.ZipFile(io.BytesIO(call("corpCode.xml", raw=True)))
    root = ET.fromstring(archive.read(archive.namelist()[0]))
    rows = [{c.tag: (c.text or "").strip() for c in e} for e in root.iter("list")]
    CACHE.write_text(json.dumps(rows, ensure_ascii=False))
    return f"고유번호 {len(rows)}건을 새로 받음"


def search(query):
    update()
    rows = json.loads(CACHE.read_text())
    q = norm(query)
    if not q:
        return "검색어가 비었다"
    exact = [r for r in rows if norm(r["corp_name"]) == q or norm(r["corp_eng_name"]) == q]
    partial = [r for r in rows if r not in exact and (q in norm(r["corp_name"]) or (len(q) >= 4 and q in norm(r["corp_eng_name"])))]
    found = exact + sorted(partial, key=lambda r: (not r["stock_code"], -int(r["modify_date"] or 0)))[:15]
    if not found:
        return f"「{query}」: DART 고유번호 목록에 없음"
    lines = [f"「{query}」 후보 {len(found)}건 (고유번호 · 이름 · 영문 이름 · 종목코드 · 갱신일)"]
    lines += [f"- {r['corp_code']} · {r['corp_name']} · {r['corp_eng_name'] or '-'} · {r['stock_code'] or '비상장'} · {r['modify_date']}" for r in found]
    return "\n".join(lines)


def won(text):
    text = (text or "").replace(",", "").strip()
    if not re.fullmatch(r"-?\d+", text):
        return text or "-"
    return f"{int(text) / 1e8:,.1f}억 원"


def structured(corp_code):
    """상장사 등 사업보고서가 있는 회사는 주요 계정 3년치를 표로 받는다."""
    this_year = date.today().year
    for year in (this_year - 1, this_year - 2):
        data = call("fnlttSinglAcnt", corp_code=corp_code, bsns_year=str(year), reprt_code="11011")
        if data["status"] != "000":
            continue
        rows = data["list"]
        div = "CFS" if any(r["fs_div"] == "CFS" for r in rows) else "OFS"
        picked, lines = set(), [f"### 재무 (사업보고서 {year}, {'연결' if div == 'CFS' else '별도'}, 단위 억 원)",
                                f"| 계정 | {year - 2} | {year - 1} | {year} |", "|---|---|---|---|"]
        for r in rows:
            name = r["account_nm"]
            if r["fs_div"] != div or name not in ACCOUNTS or name in picked:
                continue
            picked.add(name)
            lines.append(f"| {name} | {won(r.get('bfefrmtrm_amount'))} | {won(r.get('frmtrm_amount'))} | {won(r.get('thstrm_amount'))} |")
        emp = call("empSttus", corp_code=corp_code, bsns_year=str(year), reprt_code="11011")
        if emp["status"] == "000":
            total = sum(int((e.get("sm") or "0").replace(",", "") or 0) for e in emp["list"])
            lines.append(f"\n직원 수(사업보고서 {year} 직원 현황 합계): {total}명")
        return "\n".join(lines)
    return None


def audit_text(rcept_no, limit=8000):
    """감사보고서 원문에서 재무상태표 ~ 포괄손익계산서 부분만 글로 뽑는다."""
    archive = zipfile.ZipFile(io.BytesIO(call("document.xml", raw=True, rcept_no=rcept_no)))
    raw = max((archive.read(n) for n in archive.namelist()), key=len).decode("utf-8", "replace")
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    text = re.sub(r"[ \t ]+", " ", text)
    text = re.sub(r"\s*\n\s*", " | ", text)
    # 목차에도 같은 제목이 있으니, 바로 뒤에 금액(1,234,567 꼴)이 나오는 곳을 본문으로 본다
    start = next((m for m in re.finditer(r"재\s*무\s*상\s*태\s*표", text)
                  if re.search(r"\d{1,3}(,\d{3}){2,}", text[m.end(): m.end() + 600])), None)
    end = re.search(r"자\s*본\s*변\s*동\s*표", text[start.end():]) if start else None
    if not start:
        return None
    chunk = text[start.start(): start.end() + (end.start() if end else limit)]
    return chunk[:limit]


def info(corp_code):
    out = []
    c = call("company", corp_code=corp_code)
    if c["status"] != "000":
        return f"{corp_code}: 기업 개황 조회 실패 ({c.get('message')})"
    cls = {"Y": "유가증권 상장", "K": "코스닥 상장", "N": "코넥스 상장", "E": "비상장(기타 법인)"}.get(c.get("corp_cls"), c.get("corp_cls"))
    out.append(f"## DART {c['corp_name']} ({corp_code})")
    out.append(f"- 구분: {cls} · 설립일: {c.get('est_dt') or '-'} · 대표: {c.get('ceo_nm') or '-'}")
    out.append(f"- 주소: {c.get('adres') or '-'} · 홈페이지: {c.get('hm_url') or '-'} · 업종 코드: {c.get('induty_code') or '-'}")
    out.append(f"- DART 공시 검색: https://dart.fss.or.kr/dsab007/main.do?option=corp&textCrpNm={urllib.parse.quote(c['corp_name'])}")

    table = structured(corp_code)
    filings = call("list", corp_code=corp_code, bgn_de=(date.today() - timedelta(days=3 * 365)).strftime("%Y%m%d"), page_count=40)
    items = filings.get("list", []) if filings["status"] == "000" else []
    if table:
        out.append(table)
    else:
        audits = [f for f in items if "감사보고서" in f["report_nm"] and "연결" not in f["report_nm"]] or \
                 [f for f in items if "감사보고서" in f["report_nm"]]
        if not audits:
            out.append("### 재무\n재무 자료 없음 (사업보고서 · 감사보고서 공시가 없다)")
        for f in audits[:2]:  # 최근 두 해치면 세 해의 추이가 나온다(당기 · 전기)
            body = audit_text(f["rcept_no"])
            out.append(f"### 재무 원문 발췌 — {f['report_nm'].strip()} (접수 {f['rcept_dt']}, "
                       f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={f['rcept_no']})")
            out.append(body or "재무제표 부분을 찾지 못함")
    if items:
        out.append("### 최근 공시 (최대 10건)")
        out += [f"- {f['rcept_dt']} {f['report_nm'].strip()} — https://dart.fss.or.kr/dsaf001/main.do?rcpNo={f['rcept_no']}" for f in items[:10]]
    return "\n".join(out)


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("update", "search", "info"):
        raise SystemExit(__doc__)
    cmd, args = sys.argv[1], " ".join(sys.argv[2:])
    if cmd == "update":
        print(update(force=args == "--force"))
    elif cmd == "search":
        print(search(args))
    else:
        print(info(args.strip()))
