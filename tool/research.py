"""회사 조사 — 그날 공고의 회사마다 보고서를 만든다.

아침 06:10 에는 사전 거르기 결과(candidates/<날짜>.json)의 회사를 조사하고(--from candidates),
08:00 판정 봇 판정이 그 보고서를 근거로 카테고리 · 특기를 정한다. 08:20 에는 판정 봇이 남긴 kept/<날짜>.json 에서
아직 보고서가 없는 회사만 이어서 조사하고(--from kept) 노트의 「조사 중」 칸을 채운다.

회사마다 헤드리스 claude -p 하나를 띄워 웹 검색 · 웹 읽기 · DART(dart.py)로 조사하게 하고,
그 마지막 응답(보고서 마크다운)을 옵시디언 취업최전선/기업/<회사>.md 에 쓴다.
같은 회사는 마지막 조사 뒤 RECHECK 가 지났을 때만 다시 조사한다(공고가 새로 떠야 kept 에 오른다).

    python3 research.py [날짜] [--from candidates|kept] [--stop-new-at HH:MM] [--wait 분] [--only 회사,회사] [--limit N] [--force]
"""
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
STORE = Path("/opt/jobfeed/store")
DATA = STORE / "data"
CACHE = DATA / "companies.json"
REPORTS = Path("/opt/jobfeed/notes/기업")
NOTE = Path("/opt/jobfeed/notes/오늘의 공고.md")
EXPERIENCE = Path("/opt/jobfeed/notes/무기고/경험 은행/목록.md")
CLAUDE = "claude"
MODEL = "opus"  # 지원자: 소넷은 별로, 오푸스로(11-24)
WORKERS = 16  # 지원자: 16개까지 너끈하다(11-24). claude 하나가 수백 MB 라 메모리는 지켜본다
TIMEOUT = 25 * 60
RECHECK = timedelta(days=7)
REQUIRED = ("researched", "summary", "business", "employees", "founded", "stage", "profit")  # 판정 봇 판정이 읽는 frontmatter
SKIP_CATEGORIES = {"헤드헌팅"}  # 회사 이름을 숨긴 대행 공고라 조사할 회사가 없다

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"

lock = threading.Lock()


def log(message):
    with lock:
        print(f"{datetime.now():%F %T} {message}", flush=True)


def load_cache():
    return json.loads(CACHE.read_text()) if CACHE.exists() else {}


def save_cache(cache):
    tmp = CACHE.with_suffix(".tmp")
    tmp.write_text(json.dumps(cache, ensure_ascii=False, indent=1))
    tmp.replace(CACHE)


def pick_targets(kept, cache, force):
    """kept 의 회사를 묶고, 조사할 회사만 고른다."""
    groups = {}
    for item in kept["items"]:
        if item.get("category") in SKIP_CATEGORIES:
            continue
        groups.setdefault(item["company_key"], []).append(item)
    targets, skipped = {}, []
    now = datetime.now()
    for key, items in groups.items():
        entry = cache.get(key)
        report = REPORTS / f"{key}.md"
        fresh = entry and report.exists() and now - datetime.fromisoformat(entry["last_research"]) < RECHECK
        if fresh and not force:
            skipped.append(key)
        else:
            targets[key] = items
    return targets, skipped


def posting_text(items, postings):
    lines = []
    for item in items:
        p = postings.get(item["url"], {})
        lines.append(f"### {p.get('title', item.get('title', '제목 없음'))}")
        if item.get("category"):
            lines.append(f"- 판정: {item['category']} · {item.get('role', '-')} · 특기 {'예' if item.get('special') else '아니오'}")
        lines.append(f"- 요구 경력: {p.get('career', '-')} · 마감: {p.get('end', '-')} · 지역: {p.get('regions', '-')} · 링크: {item['url']}")
        if p.get("body"):
            lines.append("- 본문 요약:\n" + p["body"][:2000])
    return "\n".join(lines)


def norm(name):
    return re.sub(r"\([^)]*\)|주식회사|㈜|[^0-9A-Za-z가-힣]", "", name or "").lower()


def hiring_data(key, names):
    """채용 빈도 판단의 근거: jobfeed 가 쌓은 공고 기록과 직행에 지금 열려 있는 그 회사 공고 전부."""
    lines = []
    mine = []
    for path in sorted((DATA / "new").glob("*.json")):
        for p in json.loads(path.read_text()).get("items", []):
            if p.get("company_key") == key or norm(p.get("company")) in {norm(n) for n in names}:
                mine.append(f"- {path.stem} · {p.get('site')} · {p['title']} · {', '.join(p.get('categories') or [])}")
    days = sorted(p.stem for p in (DATA / "new").glob("*.json"))
    lines.append(f"### jobfeed 기록 (수집 {len(days)}일치, {days[0] if days else '-'} ~ {days[-1] if days else '-'}, 개발 직무 공고만 모은다)")
    lines += mine or ["- 없음"]
    wanted = {norm(n) for n in names}
    found = {}
    for name in sorted(set(names)):
        for page in range(3):
            query = urllib.parse.urlencode({"keyword": name, "page": page, "size": 100})
            try:
                req = urllib.request.Request(f"https://api.zighang.com/api/recruitments?{query}", headers={"User-Agent": UA})
                content = json.load(urllib.request.urlopen(req, timeout=30))["data"]["content"]
            except Exception as error:
                lines.append(f"- 직행 검색 실패({name}): {error}")
                break
            for x in content:
                if norm(x["company"]["name"]) in wanted:
                    found[x["id"]] = x
            if len(content) < 100:
                break
    lines.append(f"\n### 직행에 지금 열려 있는 이 회사 공고 (모든 직무, {len(found)}건 · 마감된 공고는 직행 API 로 못 본다)")
    if found:
        groups = Counter(d for x in found.values() for d in (x.get("depthOnes") or ["기타"]))
        lines.append("- 직군별: " + " · ".join(f"{k} {v}" for k, v in groups.most_common()))
        lines.append(f"- 상시(마감일 없음): {sum(1 for x in found.values() if not x.get('endDate'))}건")
        titles = Counter(re.sub(r"\s+", " ", x["title"]).strip() for x in found.values())
        repeats = [f"{t} ×{n}" for t, n in titles.items() if n > 1]
        if repeats:
            lines.append("- 같은 제목이 여러 번: " + " · ".join(repeats[:10]))
        for x in sorted(found.values(), key=lambda x: x["createdAt"])[-40:]:
            lines.append(f"- 올림 {x['createdAt'][:10]} · 마감 {(x.get('endDate') or '상시')[:10]} · {x['title']} · {', '.join(x.get('depthTwos') or [])}")
    return "\n".join(lines)


def build_prompt(key, items, postings, today):
    existing = REPORTS / f"{key}.md"
    if existing.exists():
        old = ("## 지난 보고서\n\n이 회사는 전에 조사한 보고서가 있다. 아래를 바탕으로 다시 확인하고 새 사실로 고쳐 쓴다. "
               "확인이 안 되는 옛 내용은 그대로 두지 말고 다시 찾는다. 지난 보고서에 「못 찾음」 · 「403」으로 비어 있던 칸은 특히 다시 찾는다. "
               "지난 보고서의 모양이 아래 「보고서 형식」과 다르면 형식을 따른다.\n\n" + existing.read_text())
    else:
        old = ""
    template = (HERE / "research-prompt.md").read_text()
    return (template.replace("«KEY»", key)
            .replace("«NAME»", " · ".join(sorted({i.get("company", key) for i in items})))
            .replace("«TODAY»", today)
            .replace("«POSTINGS»", posting_text(items, postings))
            .replace("«HIRING»", hiring_data(key, [key] + [i.get("company", key) for i in items]))
            .replace("«EXISTING»", old)
            .replace("«EXPERIENCE»", EXPERIENCE.read_text() if EXPERIENCE.exists() else "(목록 파일 없음)"))


def clean_report(text):
    text = text.strip()
    fence = re.match(r"^```(?:markdown|md)?\n(.*)\n```$", text, re.S)
    if fence:
        text = fence.group(1).strip()
    start = text.find("---")
    if start < 0:
        raise ValueError("frontmatter 없음")
    text = text[start:]
    parts = text.split("---", 2)
    meta = yaml.safe_load(parts[1])
    missing = [k for k in REQUIRED if not isinstance(meta, dict) or not str(meta.get(k) or "").strip()]
    if missing:
        raise ValueError(f"frontmatter 에 {', '.join(missing)} 없음")
    if len(re.findall(r"^## ", parts[2], re.M)) < 9:
        raise ValueError("## 묶음이 아홉 개보다 적다")
    return text + "\n"


def research(key, items, postings, today):
    prompt = build_prompt(key, items, postings, today)
    env = {**os.environ, "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1", "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}
    cmd = [CLAUDE, "-p", "--output-format", "json", "--model", MODEL,
           "--strict-mcp-config", "--settings", json.dumps({"disableAllHooks": True}),
           "--tools", "WebSearch,WebFetch,Bash",
           "--allowedTools", f"WebSearch,WebFetch,Bash(python3 -I {HERE}/dart.py:*),Bash(python3 -I {HERE}/fetch.py:*)"]
    started = time.time()
    proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=TIMEOUT, cwd=STORE, env=env)
    elapsed = time.time() - started
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"claude 출력이 JSON 이 아님 (exit {proc.returncode}): {proc.stderr[-300:] or proc.stdout[-300:]}")
    if result.get("is_error"):
        raise RuntimeError(f"claude 오류: {str(result.get('result'))[:300]}")
    report = clean_report(result.get("result", ""))
    (REPORTS / f"{key}.md").write_text(report)
    return elapsed, result.get("total_cost_usd"), result.get("num_turns"), result.get("usage") or {}


def summary_of(key):
    report = REPORTS / f"{key}.md"
    if not report.exists():
        return None
    parts = report.read_text().split("---", 2)
    try:
        meta = yaml.safe_load(parts[1]) if len(parts) == 3 else None
    except yaml.YAMLError:
        return None
    text = str((meta or {}).get("summary") or "").strip().replace("|", "／")
    return text or None


def fill_note(today):
    """그날 「오늘의 공고」 노트에서 「조사 중」인 칸을 채운다. 채널에는 보내지 않는다.
    「회사 조사」 칸에는 보고서 링크만, 「회사 평가」 칸에는 보고서 frontmatter 의 summary(평가 한 줄)를 넣는다."""
    if not NOTE.exists():
        return 0
    lines = NOTE.read_text().split("\n")
    if f'date: "{today}"' not in "\n".join(lines[:5]):
        return 0
    split = re.compile(r"(?<!\\)\|")
    filled, research_col, eval_col = 0, None, None
    for i, line in enumerate(lines):
        if not line.startswith("|"):
            research_col = eval_col = None
            continue
        cells = [c.strip() for c in split.split(line)[1:-1]]
        if "회사 조사" in cells:
            research_col = cells.index("회사 조사")
            eval_col = cells.index("회사 평가") if "회사 평가" in cells else None
            continue
        if research_col is None or research_col >= len(cells):
            continue
        name = re.sub(r"^\[\[[^\]]*?\\?\|(.*)\]\]$", r"\1", cells[0])
        summary = summary_of(name)
        if not summary:
            continue
        changed = False
        if cells[research_col] == "조사 중":
            cells[research_col] = f"[[취업최전선/기업/{name}\\|보고서]]"
            changed = True
        if eval_col is not None and eval_col < len(cells) and cells[eval_col] == "조사 중":
            cells[eval_col] = summary
            changed = True
        if changed:
            lines[i] = "| " + " | ".join(cells) + " |"
            filled += 1
    if filled:
        NOTE.write_text("\n".join(lines))
    return filled


STAGE = DATA / "backfill"  # 워크플로우 에이전트가 쓰는 곳: prompts/ 에 지시문, stage/research/ 에 보고서


def prepare(key, today):
    """워크플로우 에이전트용: 회사 하나의 조사 지시문 파일을 쓴다. 에이전트는 지시문대로 조사해 보고서를 stage 파일에 둔다."""
    kept = json.loads((DATA / "kept" / f"{today}.json").read_text())
    items = [i for i in kept["items"] if i["company_key"] == key]
    if not items:
        raise SystemExit(f"kept/{today}.json 에 없는 회사: {key}")
    new_path = DATA / "new" / f"{today}.json"
    postings = {p["url"]: p for p in json.loads(new_path.read_text())["items"]} if new_path.exists() else {}
    stage = STAGE / "stage" / "research" / f"{key}.md"
    prompt = STAGE / "prompts" / f"research-{key}.md"
    stage.parent.mkdir(parents=True, exist_ok=True)
    prompt.parent.mkdir(parents=True, exist_ok=True)
    prompt.write_text(build_prompt(key, items, postings, today)
                      + f"\n\n## 결과를 두는 곳\n\n보고서 마크다운 전체를 마지막 응답 대신 {stage} 파일에 쓴다. 그 파일 말고는 아무것도 쓰지 않는다.\n")
    print(f"지시문: {prompt}\n결과 파일: {stage}")


def apply_staged():
    """stage/research/*.md 를 검사해 회사 보고서로 옮기고 조사 캐시에 적는다."""
    cache = load_cache()
    moved, bad = 0, []
    for staged in sorted((STAGE / "stage" / "research").glob("*.md")):
        key = staged.stem
        try:
            report = clean_report(staged.read_text())
        except Exception as error:
            bad.append(f"{key}: {error}")
            continue
        (REPORTS / f"{key}.md").write_text(report)
        cache[key] = {"last_research": datetime.now().isoformat(timespec="minutes"), "file": str(REPORTS / f"{key}.md"), "via": "workflow"}
        staged.unlink()
        moved += 1
    save_cache(cache)
    log(f"반영 · 회사 보고서 {moved}건" + (f" · 검사 실패 {len(bad)}: " + " / ".join(bad[:20]) if bad else ""))
    return 1 if bad and not moved else 0


def main():
    args = sys.argv[1:]
    if "--prepare" in args:
        i = args.index("--prepare")
        return prepare(args[i + 1], args[i + 2])
    if "--apply-staged" in args:
        return apply_staged()
    today = next((a for a in args if re.fullmatch(r"\d{4}-\d{2}-\d{2}", a)), date.today().isoformat())
    only = next((args[i + 1].split(",") for i, a in enumerate(args) if a == "--only"), None)
    limit = next((int(args[i + 1]) for i, a in enumerate(args) if a == "--limit"), None)
    force = "--force" in args
    source = next((args[i + 1] for i, a in enumerate(args) if a == "--from"), "kept")
    stop_at = next((args[i + 1] for i, a in enumerate(args) if a == "--stop-new-at"), None)
    wait = next((int(args[i + 1]) for i, a in enumerate(args) if a == "--wait"), 0)

    kept_path = DATA / source / f"{today}.json"
    deadline = time.time() + wait * 60
    while not kept_path.exists() and time.time() < deadline:
        time.sleep(30)
    if not kept_path.exists():
        log(f"{source} 파일 없음: {kept_path} (앞 단계가 안 돌았거나 실패)")
        return 1
    kept = json.loads(kept_path.read_text())
    new_path = DATA / "new" / f"{today}.json"
    postings = {p["url"]: p for p in json.loads(new_path.read_text())["items"]} if new_path.exists() else {}

    REPORTS.mkdir(parents=True, exist_ok=True)
    subprocess.run(["/usr/bin/python3", "-I", str(HERE / "dart.py"), "update"], check=False, capture_output=True)
    cache = load_cache()
    targets, skipped = pick_targets(kept, cache, force)
    total = len(targets) + len(skipped)
    if only:
        targets = {k: v for k, v in targets.items() if k in only}
    if limit is not None:
        targets = dict(list(targets.items())[:limit])
    log(f"시작({source}) · 회사 {total}곳(헤드헌팅 뺌) · 조사 {len(targets)} · 7일 안에 조사해 건너뜀 {len(skipped)}")

    ok, failed, late = [], [], []
    tokens = Counter()

    def run(key):
        if stop_at and datetime.now().strftime("%H:%M") >= stop_at:
            late.append(key)  # 판정 전에 못 끝낼 회사는 시작하지 않는다. 08:20 실행이 이어서 한다
            return
        try:
            elapsed, cost, turns, usage = research(key, targets[key], postings, today)
        except Exception as error:
            failed.append(key)
            log(f"실패 · {key} · {str(error)[:300]}")
            return
        with lock:
            cache[key] = {"last_research": datetime.now().isoformat(timespec="minutes"),
                          "last_url": targets[key][-1]["url"], "file": str(REPORTS / f"{key}.md"),
                          "seconds": round(elapsed), "cost_usd": cost, "turns": turns,
                          "tokens": {k: usage.get(k, 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")}}
            save_cache(cache)
            tokens.update(cache[key]["tokens"])
            tokens["cost_milli"] += round((cost or 0) * 1000)
        ok.append(key)
        log(f"성공 · {key} · {elapsed:.0f}초 · {turns}턴 · ${cost or 0:.2f}")

    with ThreadPoolExecutor(WORKERS) as pool:
        list(pool.map(run, targets))
    if ok:
        log(f"토큰 · 회사 {len(ok)} · 입력 {tokens['input_tokens']:,} · 캐시 쓰기 {tokens['cache_creation_input_tokens']:,} · "
            f"캐시 읽기 {tokens['cache_read_input_tokens']:,} · 출력 {tokens['output_tokens']:,} · "
            f"비용 추정 ${tokens['cost_milli'] / 1000:.2f}(API 단가 환산, 구독이라 실제 청구 아님) · 모델 {MODEL}")
    filled = fill_note(today)
    log(f"끝 · 성공 {len(ok)} · 실패 {len(failed)}" + (f" ({', '.join(failed)})" if failed else "") + f" · {stop_at} 넘어 시작 안 함 {len(late)}" * bool(late) + f" · 노트 「조사 중」 {filled}줄 채움")
    return 1 if failed and not ok else 0


if __name__ == "__main__":
    sys.exit(main())
