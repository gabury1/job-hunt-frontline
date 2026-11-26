"""공고 보고서 — 판정 봇 판정에 남은 공고마다 공고 내용을 옵시디언 노트 한 장으로 정리한다.

회사 보고서(기업/)가 회사를 본다면, 공고 보고서(공고/)는 공고 자체다: 일정 · 전형 · 담당 업무 · 지원 자격 · 제출 서류 · 유의사항.
지원자가 공고를 보려고 사이트에 들어가지 않아도 되게 한다. 남긴 공고 전부를 만든다.

공고마다 source.py 로 원문 재료(글 · 이미지 조각)를 폴더에 모으고, 헤드리스 claude -p 하나에 읽혀 노트를 받는다.
claude 는 그 폴더 읽기 · 웹 읽기 · fetch.py 만 쓸 수 있다. 노트는 마지막 응답으로 받고 이 스크립트가 검사한 뒤 쓴다.

    python3 -I posting.py [날짜] [--all] [--only url,url] [--limit N] [--force]
      날짜   kept/<날짜>.json 의 공고(기본: 오늘)
      --all  kept/*.json 전부(마감 지난 공고는 뺀다)
      --force 이미 만든 공고도 다시 만든다
"""
import json
import os
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
STORE = Path("/opt/jobfeed/store")
DATA = STORE / "data"
SRC = DATA / "posting-src"
INDEX = DATA / "postings.json"  # 공고 url → 노트 파일 · 만든 시각 · 비용
NOTES = Path("/opt/jobfeed/notes/공고")
TODAY_NOTE = Path("/opt/jobfeed/notes/오늘의 공고.md")
EXPERIENCE = Path("/opt/jobfeed/notes/무기고/경험 은행/목록.md")
CLAUDE = "claude"
MODEL = "sonnet"  # 11-26 지원자: 토큰이 모자라 소넷으로(전에는 오푸스)
WORKERS = 16
TIMEOUT = 15 * 60
MAX_CAREER_MIN = 1  # collect.py · status.py 와 같은 기준. 기준이 바뀌기 전 판정분에 섞인 「2년 이상」은 만들지 않는다
REQUIRED_KEYS = ("company", "마감", "정리")
REQUIRED_HEADINGS = ("## 일정과 전형", "## 담당할 업무", "## 지원 자격", "## 제출 서류와 지원 방법", "## 메모")

lock = threading.Lock()


def log(message):
    with lock:
        print(f"{datetime.now():%F %T} {message}", flush=True)


def load(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def postings():
    found = {}
    for path in sorted((DATA / "new").glob("*.json")):
        for item in load(path, {"items": []})["items"]:
            found.setdefault(item["url"], item)
    return found


def file_name(item, used):
    """「<회사> <직무>.md」. 제목의 [ ] 태그 · 괄호 속 회사 이름 · 파일에 못 쓰는 글자를 뺀다."""
    company = item["company_key"]
    title = re.sub(r"\[[^\]]*\]", " ", item["title"])
    title = title.replace(company, " ").replace(item.get("company", company), " ")
    title = re.sub(r'[\\/:*?"<>|#^\[\]]', " ", title)
    title = re.sub(r"\s+", " ", title).strip(" -·") or "공고"
    name = f"{company} {title}"[:80].strip()
    if name in used:
        name = f"{name} ({item['url'].rstrip('/').rsplit('/', 1)[1][:8]})"
    return name


def build_prompt(item, src):
    judge = f"{item.get('category', '-')} · {item.get('role', '-')} · 특기 {'예' if item.get('special') else '아니오'}"
    return ((HERE / "posting-prompt.md").read_text()
            .replace("«COMPANY»", item.get("company", item["company_key"]))
            .replace("«TITLE»", item["title"])
            .replace("«KEY»", item["company_key"])
            .replace("«URL»", item["url"])
            .replace("«TODAY»", date.today().isoformat())
            .replace("«JUDGE»", judge)
            .replace("«SRC»", str(src))
            .replace("«EXPERIENCE»", EXPERIENCE.read_text() if EXPERIENCE.exists() else "(목록 파일 없음)"))


def clean(text):
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
    missing = [k for k in REQUIRED_KEYS if not isinstance(meta, dict) or not str(meta.get(k) or "").strip()]
    if missing:
        raise ValueError(f"frontmatter 에 {', '.join(missing)} 없음")
    lacking = [h for h in REQUIRED_HEADINGS if h not in parts[2]]
    if lacking:
        raise ValueError(f"제목 없음: {', '.join(lacking)}")
    return text + "\n"


def make(item, name):
    src = src_dir(item["url"])
    proc = subprocess.run(["/usr/bin/python3", "-I", str(HERE / "source.py"), item["url"], str(src)],
                          capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        raise RuntimeError(f"원문 못 모음: {(proc.stderr or proc.stdout)[-300:]}")
    env = {**os.environ, "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1", "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}
    cmd = [CLAUDE, "-p", "--output-format", "json", "--model", MODEL,
           "--strict-mcp-config", "--settings", json.dumps({"disableAllHooks": True}),
           "--tools", "Read,WebFetch,Bash",
           "--allowedTools", f"Read(/{src}/**),WebFetch,Bash(python3 -I {HERE}/fetch.py:*)"]
    started = time.time()
    proc = subprocess.run(cmd, input=build_prompt(item, src), capture_output=True, text=True, timeout=TIMEOUT, cwd=src, env=env)
    elapsed = time.time() - started
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"claude 출력이 JSON 이 아님 (exit {proc.returncode}): {proc.stderr[-300:] or proc.stdout[-300:]}")
    if result.get("is_error"):
        raise RuntimeError(f"claude 오류: {str(result.get('result'))[:300]}")
    (NOTES / f"{name}.md").write_text(clean(result.get("result", "")))
    return elapsed, result.get("total_cost_usd") or 0, result.get("num_turns")


def link_today_note(index):
    """「오늘의 공고」 표에 「공고 보고서」 칸을 「링크」 칸 앞에 넣고 채운다. 노트는 08:00 판정 봇이 칸 없이 새로 쓰므로 매번 넣는다.
    행은 「링크」 칸의 공고 url 로 찾는다. 보고서가 없으면 「만드는 중」."""
    if not TODAY_NOTE.exists():
        return 0
    posts = postings()
    split = re.compile(r"(?<!\\)\|")
    lines = TODAY_NOTE.read_text().split("\n")
    head, linked = None, 0
    for i, line in enumerate(lines):
        if not line.startswith("|"):
            head = None
            continue
        cells = [c.strip() for c in split.split(line)[1:-1]]
        if "링크" in cells:
            head = cells
            if "공고 보고서" not in head:
                cells.insert(head.index("링크"), "공고 보고서")
                lines[i] = "| " + " | ".join(cells) + " |"
            head = cells
            continue
        if head is None:
            continue
        if set(line) <= set("|-: "):
            if len(cells) < len(head):
                lines[i] = "|" + "---|" * len(head)
            continue
        col = head.index("공고 보고서")
        if len(cells) < len(head):
            cells.insert(col, "")
        m = re.search(r"\]\((\S+?)\)", cells[-1])
        done = index.get(m.group(1)) if m else None
        if done and (NOTES / f"{done['file']}.md").exists():
            cells[col] = f"[[취업최전선/공고/{done['file']}\\|공고 보고서]]"
            linked += 1
        elif m and (((posts.get(m.group(1)) or {}).get("career") or [0])[0] or 0) > MAX_CAREER_MIN:
            cells[col] = "안 만듦 (2년 이상)"
        else:
            cells[col] = "만드는 중"
        lines[i] = "| " + " | ".join(cells) + " |"
    TODAY_NOTE.write_text("\n".join(lines))
    return linked


STAGE = DATA / "backfill"  # 워크플로우 에이전트가 쓰는 곳: prompts/ 에 지시문, stage/posting/ 에 노트


def src_dir(url):
    return SRC / re.sub(r"[^0-9A-Za-z_-]", "_", url.rstrip("/").rsplit("/", 1)[1])


def find_item(url):
    for path in sorted(p for d in ("kept", "kept-public") for p in (DATA / d).glob("*.json")):
        for item in load(path, {"items": []})["items"]:
            if item["url"] == url:
                return item
    raise SystemExit(f"판정 기록에 없는 공고: {url}")


def prepare(url):
    """워크플로우 에이전트용: 원문 재료를 모으고 지시문 파일을 쓴다. 에이전트는 지시문대로 노트를 써서 stage 파일에 둔다."""
    item, src = find_item(url), src_dir(url)
    proc = subprocess.run(["/usr/bin/python3", "-I", str(HERE / "source.py"), url, str(src)], capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        raise SystemExit(f"원문 못 모음: {(proc.stderr or proc.stdout)[-300:]}")
    stage = STAGE / "stage" / "posting" / f"{src.name}.md"
    prompt = STAGE / "prompts" / f"posting-{src.name}.md"
    stage.parent.mkdir(parents=True, exist_ok=True)
    prompt.parent.mkdir(parents=True, exist_ok=True)
    prompt.write_text(build_prompt(item, src) + f"\n\n## 결과를 두는 곳\n\n노트 마크다운 전체를 마지막 응답 대신 {stage} 파일에 쓴다. 그 파일 말고는 아무것도 쓰지 않는다.\n")
    print(f"지시문: {prompt}\n결과 파일: {stage}\n{proc.stdout.strip()}")


def apply_staged():
    """stage/posting/*.md 를 검사해 공고 노트로 옮기고 postings.json 에 적는다."""
    index = load(INDEX, {})
    used = {v["file"] for v in index.values()} | {p.stem for p in NOTES.glob("*.md")}
    kept = {}
    for path in sorted(p for d in ("kept", "kept-public") for p in (DATA / d).glob("*.json")):
        for item in load(path, {"items": []})["items"]:
            kept[src_dir(item["url"]).name] = item
    moved, bad = 0, []
    for staged in sorted((STAGE / "stage" / "posting").glob("*.md")):
        item = kept.get(staged.stem)
        if not item:
            bad.append(f"{staged.name}: 판정 기록에 없음")
            continue
        try:
            text = clean(staged.read_text())
        except ValueError as error:
            bad.append(f"{staged.name}: {error}")
            continue
        done = index.get(item["url"])
        name = done["file"] if done else file_name(item, used)
        used.add(name)
        (NOTES / f"{name}.md").write_text(text)
        index[item["url"]] = {"file": name, "made": datetime.now().isoformat(timespec="minutes"), "via": "workflow"}
        staged.unlink()
        moved += 1
    INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=1))
    log(f"반영 · 공고 노트 {moved}건" + (f" · 검사 실패 {len(bad)}: " + " / ".join(bad[:20]) if bad else ""))
    return 1 if bad and not moved else 0


def main():
    args = sys.argv[1:]
    if "--prepare" in args:
        return prepare(args[args.index("--prepare") + 1])
    if "--apply-staged" in args:
        return apply_staged()
    today = next((a for a in args if re.fullmatch(r"\d{4}-\d{2}-\d{2}", a)), date.today().isoformat())
    only = next((args[i + 1].split(",") for i, a in enumerate(args) if a == "--only"), None)
    limit = next((int(args[i + 1]) for i, a in enumerate(args) if a == "--limit"), None)
    force = "--force" in args

    paths = sorted(p for d in ("kept", "kept-public") for p in (DATA / d).glob("*.json")) if "--all" in args else [p for p in (DATA / "kept" / f"{today}.json", DATA / "kept-public" / f"{today}.json") if p.exists()]
    kept = {}
    for path in paths:
        for item in load(path, {"items": []})["items"]:
            kept[item["url"]] = item
    if not kept:
        log(f"판정 기록 없음: {', '.join(map(str, paths))}")
        return 1
    posts = postings()
    index = load(INDEX, {})
    used = {v["file"] for v in index.values()} | {p.stem for p in NOTES.glob("*.md")}  # 손으로 만든 노트(카카오뱅크 등)와 겹치지 않게
    targets = []
    for url, item in kept.items():
        post = posts.get(url) or {}
        end = post.get("end") or "상시"
        if end != "상시" and end < date.today().isoformat():
            continue
        if ((post.get("career") or [0])[0] or 0) > MAX_CAREER_MIN:
            continue
        if only and url not in only:
            continue
        done = index.get(url)
        if done and (NOTES / f"{done['file']}.md").exists() and not force:
            continue
        name = done["file"] if done else file_name(item, used)
        used.add(name)
        targets.append((item, name))
    if limit is not None:
        targets = targets[:limit]
    NOTES.mkdir(parents=True, exist_ok=True)
    log(f"시작 · 판정 공고 {len(kept)} · 만들 것 {len(targets)}")

    ok, failed, spent = [], [], [0.0]

    def run(target):
        item, name = target
        try:
            elapsed, cost, turns = make(item, name)
        except Exception as error:
            failed.append(name)
            log(f"실패 · {name} · {str(error)[:300]}")
            return
        with lock:
            index[item["url"]] = {"file": name, "made": datetime.now().isoformat(timespec="minutes"),
                                  "seconds": round(elapsed), "cost_usd": cost, "turns": turns}
            tmp = INDEX.with_suffix(".tmp")
            tmp.write_text(json.dumps(index, ensure_ascii=False, indent=1))
            tmp.replace(INDEX)
            spent[0] += cost
        ok.append(name)
        log(f"성공 · {name} · {elapsed:.0f}초 · {turns}턴 · ${cost:.2f}")

    with ThreadPoolExecutor(WORKERS) as pool:
        list(pool.map(run, targets))
    linked = link_today_note(index)
    log(f"끝 · 오늘의 공고에 보고서 링크 {linked}줄 · 성공 {len(ok)} · 실패 {len(failed)}" + (f" ({', '.join(failed)})" if failed else "")
        + f" · 비용 추정 ${spent[0]:.2f}(API 단가 환산, 구독이라 실제 청구 아님) · 모델 {MODEL}")
    return 1 if failed and not ok else 0


if __name__ == "__main__":
    sys.exit(main())
