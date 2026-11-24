"""웹 페이지를 맥 크롬 User-Agent 로 받아 본문 글자만 낸다 — 조사하는 claude -p 가 웹 읽기 도구로 403 · 차단을 만날 때 쓴다.

    python3 -I fetch.py <url> [최대 글자 수, 기본 20000]

더브이씨(thevc.kr) · 혁신의숲(innoforest.co.kr)은 이 User-Agent 로 보내면 서버가 그린 HTML 에 본문이 들어 있다(2026-11-24 확인).
"""
import html
import random
import re
import sys
import time
import urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"


def fetch(url, limit):
    if not re.match(r"https?://", url):
        raise SystemExit("http(s) 주소만 받는다")
    time.sleep(random.uniform(1.0, 3.0))  # 사이트가 기계 요청으로 보고 막지 않게 무작위로 쉰다
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ko-KR,ko;q=0.9"})
    with urllib.request.urlopen(req, timeout=30) as res:
        status = res.status
        raw = res.read(5_000_000).decode(res.headers.get_content_charset() or "utf-8", "replace")
    title = re.search(r"<title[^>]*>(.*?)</title>", raw, re.S | re.I)
    text = re.sub(r"<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    text = re.sub(r"<br\s*/?>|</(p|div|li|tr|h\d|section|article)>", "\n", text, flags=re.I)
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    text = re.sub(r"[ \t ]+", " ", text)
    text = re.sub(r"\s*\n\s*", "\n", text).strip()
    head = f"[{status}] {url}\n제목: {html.unescape(title.group(1).strip()) if title else '-'}\n\n"
    return head + (text[:limit] + f"\n…(앞 {limit}자만, 전체 {len(text)}자)" if len(text) > limit else text)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    try:
        print(fetch(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 20000))
    except urllib.error.HTTPError as error:
        print(f"[{error.code}] {sys.argv[1]} — 받지 못함")
        sys.exit(1)
