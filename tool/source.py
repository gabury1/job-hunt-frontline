"""공고 원문 모으기 — 공고 보고서를 쓰는 claude -p 가 읽을 재료를 폴더 하나에 모은다.

    python3 -I source.py <공고 url> <폴더>

폴더에 남는 것: 원문.md(사이트 API · 페이지에서 받은 글과 공고 정보), img-NN.jpg(공고 이미지를 읽을 수 있는 높이로 자른 것).
- 직행: 상세 API. 본문은 대개 원래 채용 사이트의 공고를 통째로 찍은 이미지 한 장이고, 원래 공고 주소(redirectUrl)가 따로 있다.
- 점핏: 상세 API 의 글 칸(주요 업무 · 자격 · 우대 · 복지 · 채용 절차 등).
- 자소설닷컴: 공고 페이지에 적힌 회사 채용 페이지(employment_page_url)를 헤드리스 크롬으로 그려 글과 큰 이미지를 받는다.
"""
import html
import io
import json
import random
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from PIL import Image

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
CHROMIUM = "/usr/bin/chromium"
MAX_IMAGES = 8
MIN_HEIGHT = 400  # 이보다 낮은 이미지는 로고 · 아이콘으로 보고 버린다


def jitter(low=1.0, high=3.0):
    """사이트가 기계 요청으로 보고 막지 않게, 요청마다 무작위로 쉰다."""
    time.sleep(random.uniform(low, high))


def get(url, binary=False):
    jitter()
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ko-KR,ko;q=0.9"})
    with urllib.request.urlopen(req, timeout=30) as res:
        raw = res.read(20_000_000)
    return raw if binary else raw.decode("utf-8", "replace")


def doc_text(node):
    """직행 문서(prosemirror 모양)를 줄글로 편다."""
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


def doc_images(node):
    if isinstance(node, list):
        return [src for n in node for src in doc_images(n)]
    if not isinstance(node, dict):
        return []
    if node.get("type") == "image" and (node.get("attrs") or {}).get("src"):
        return [node["attrs"]["src"]]
    return doc_images(node.get("content") or [])


def page_text(raw):
    text = re.sub(r"<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    text = re.sub(r"<br\s*/?>|</(p|div|li|tr|h\d|section|article|dd|dt)>", "\n", text, flags=re.I)
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    text = re.sub(r"[ \t ]+", " ", text)
    return re.sub(r"\s*\n\s*", "\n", text).strip()


def save_images(urls, out):
    """이미지를 받아 MIN_HEIGHT 이상인 것만 읽을 수 있는 높이로 잘라 저장한다. 저장한 파일 수를 낸다."""
    saved = 0
    for url in urls:
        if saved >= MAX_IMAGES * 4:
            break
        try:
            im = Image.open(io.BytesIO(get(url, binary=True))).convert("RGB")
        except Exception:
            continue
        w, h = im.size
        if h < MIN_HEIGHT or w < 300:
            continue
        if w > 1400:
            im = im.resize((1400, round(h * 1400 / w)))
            w, h = im.size
        for y in range(0, h, 1600):
            im.crop((0, y, w, min(h, y + 1600))).save(out / f"img-{saved:02d}.jpg", quality=85)
            saved += 1
    return saved


def render(url):
    jitter()
    proc = subprocess.run([CHROMIUM, "--headless", "--no-sandbox", "--disable-gpu", "--virtual-time-budget=15000",
                           f"--user-agent={UA}", "--dump-dom", url], capture_output=True, text=True, timeout=120)
    return proc.stdout


def zighang(pid, out):
    d = json.loads(get(f"https://api.zighang.com/api/recruitments/{pid}"))["data"]
    lines = [f"- 제목: {d['title']}", f"- 회사: {d['company']['name']}",
             f"- 마감: {d.get('endDate') or d.get('deadlineType') or '-'}",
             f"- 요구 경력: {d.get('careerMin')} ~ {d.get('careerMax')}년(100 은 상한 없음)",
             f"- 지역: {', '.join(d.get('regions') or [])}", f"- 고용 형태: {', '.join(d.get('employeeTypes') or [])}",
             f"- 학력: {', '.join(d.get('educations') or [])}",
             f"- 원래 공고(직행이 긁어 온 곳: {d.get('affiliate') or '-'}): {d.get('redirectUrl') or '-'}",
             f"- 지원 방법: {d.get('applyMethod') or '-'} {d.get('applicationEmail') or ''}",
             "", "## 직행 요약(직행이 원문을 요약한 것. 원문 이미지와 다르면 원문을 따른다)", "", doc_text(d.get("summary")),
             "", "## 본문 글", "", doc_text(d.get("content")) or "(본문은 이미지뿐이다. img-*.jpg 를 읽는다)"]
    return lines, doc_images(d.get("content"))


def jumpit(pid, out):
    d = json.loads(get(f"https://jumpit-api.saramin.co.kr/api/position/{pid}"))["result"]
    lines = [f"- 제목: {d['title']}", f"- 회사: {d['companyName']}",
             f"- 마감: {'상시' if d.get('alwaysOpen') else d.get('closedAt')}", f"- 올라온 날: {d.get('publishedAt')}",
             f"- 요구 경력: {d.get('minCareer')} ~ {d.get('maxCareer')}년", f"- 학력: {d.get('educationName') or '-'}",
             f"- 근무지: {', '.join(w.get('address', '') for w in d.get('workingPlaces') or []) or d.get('location') or '-'}",
             f"- 기술 스택: {', '.join(s.get('stack', '') for s in d.get('techStacks') or [])}"]
    for key, name in (("serviceInfo", "회사 · 서비스 소개"), ("responsibility", "주요 업무"), ("qualifications", "자격 요건"),
                      ("preferredRequirements", "우대 사항"), ("welfares", "복지"), ("recruitProcess", "채용 절차 · 기타")):
        if d.get(key):
            lines += ["", f"## {name}", "", d[key].replace("\r\n", "\n")]
    return lines, []


def jasoseol(pid, out):
    raw = get(f"https://jasoseol.com/recruit/{pid}")
    m = re.search(r'employment_page_url":"([^"]+)"', raw)
    page = m.group(1).encode().decode("unicode_escape") if m else None
    lines = [f"- 자소설닷컴 공고: https://jasoseol.com/recruit/{pid}", f"- 회사 채용 페이지: {page or '자소설닷컴에 없음'}"]
    images = []
    if page:
        dom = render(page)
        lines += ["", "## 회사 채용 페이지 글(헤드리스 크롬으로 그린 것)", "", page_text(dom)[:30000] or "(글 없음)"]
        for src in re.findall(r'<img[^>]+src="([^"]+)"', dom):
            src = html.unescape(src)
            if src.startswith("//"):
                src = "https:" + src
            if src.startswith("http") and not src.lower().endswith(".svg"):
                images.append(src)
    lines += ["", "## 자소설닷컴 공고 페이지 글", "", page_text(raw)[:8000]]
    return lines, images[:MAX_IMAGES * 3]


def wanted(pid, out):
    d = json.loads(get(f"https://www.wanted.co.kr/api/v4/jobs/{pid}"))["job"]
    detail, address = d.get("detail") or {}, d.get("address") or {}
    lines = [f"- 제목: {d['position']}", f"- 회사: {d['company']['name']}", f"- 마감: {d.get('due_time') or '상시'}",
             f"- 요구 경력: {d.get('annual_from')} ~ {d.get('annual_to')}년(100 은 상한 없음)",
             f"- 근무지: {address.get('full_location') or address.get('location') or '-'}",
             f"- 기술 스택: {', '.join(t.get('title', '') for t in d.get('skill_tags') or [])}"]
    for key, name in (("intro", "회사 · 포지션 소개"), ("main_tasks", "주요 업무"), ("requirements", "자격 요건"),
                      ("preferred_points", "우대 사항"), ("benefits", "혜택 · 복지"), ("hire_rounds", "채용 전형")):
        if detail.get(key):
            lines += ["", f"## {name}", "", detail[key]]
    return lines, []


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    url, out = sys.argv[1], Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("img-*.jpg"):
        old.unlink()
    pid = url.rstrip("/").rsplit("/", 1)[1]
    if "zighang.com" in url:
        lines, images = zighang(pid, out)
    elif "jumpit" in url:
        lines, images = jumpit(pid, out)
    elif "wanted.co.kr" in url:
        lines, images = wanted(pid, out)
    elif "jasoseol.com" in url:
        lines, images = jasoseol(pid, out)
    else:
        raise SystemExit(f"모르는 사이트: {url}")
    count = save_images(images, out)
    (out / "원문.md").write_text(f"# 공고 원문 재료\n\n- 공고 주소: {url}\n" + "\n".join(lines) + f"\n\n(이미지 조각 {count}개: img-00.jpg ~)\n")
    print(f"원문 {len(''.join(lines))}자 · 이미지 조각 {count}개 → {out}")


if __name__ == "__main__":
    main()
