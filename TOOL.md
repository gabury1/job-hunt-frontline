# 도구 설명

이 레포의 공고 · 회사 노트를 매일 만드는 스크립트를 `tool/` 에 **대충** 넣어 두었습니다. 만든 사람의 라즈베리파이에서 크론으로 돌던 것을
경로와 개인 기준만 지운 사본이라, 그대로는 안 돌 수 있습니다. 필요하면 AI 에게 「이 폴더를 내 환경에 맞게 세팅해 줘」라고 맡기세요.

## 흐름

| 시각 | 스크립트 | 하는 일 |
|---|---|---|
| 06:00 | `run.sh` → `collect.py` · `prefilter.py` | 직행 · 점핏 · 자소설닷컴 공개 API 에서 새 공고를 모으고(요청마다 무작위로 쉰다), SI · 파견 같은 확실한 것만 글로 거른다 |
| 06:10 | `research.sh --from candidates` → `research.py` | 회사마다 헤드리스 `claude -p` 하나가 웹 검색 · DART(`dart.py`) · 공개 페이지(`fetch.py`)로 조사 보고서를 쓴다. 지시문은 `research-prompt.md` |
| 08:00 | (판정 봇) | 지원자의 기준 문서(지원 대상 · 지원 직무 표)와 회사 보고서로 공고를 남기고 뺀다. 원래는 개인 비서 봇이 했다. `backfill.py` 의 판정 지시문을 대신 써도 된다 |
| 08:20 | `research.sh --from kept` → `research.py` · `posting.py` · `status.py` | 남은 회사 조사, 공고마다 노트(`source.py` 가 원문 글 · 이미지를 모으고 `posting-prompt.md` 대로 정리), 접수 중 공고 표. 그다음 개인 내용을 걷어 낸 사본을 이 레포에 올린다 |

## 필요한 것

- Python 3.11+, `PyYAML`, `Pillow`
- 헤드리스 크롬(`chromium`): 자소설닷컴 공고가 가리키는 회사 채용 페이지를 그릴 때
- Claude Code CLI(`claude -p`): 조사 · 판정 · 공고 정리
- DART 오픈 API 키(`.env` 의 `DART_API_KEY`): 재무 · 직원 수

## 바꿀 곳

- 각 스크립트 맨 위의 경로 상수(`/opt/jobfeed/...`)
- 지원 기준 문서와 경험 목록 경로(`research.py` · `posting.py` 의 `EXPERIENCE`, 판정 지시문의 기준 문서)
- `posting-prompt.md` 의 「«지원자 상황»」 자리
- 모델 · 동시 실행 수(`MODEL` · `WORKERS`). 회사 하나 조사에 API 환산 1~3달러, 공고 노트 하나에 0.3~0.5달러쯤 든다

## 예의

사이트가 기계 요청으로 보고 막지 않게 요청 사이에 무작위로 쉬도록 해 두었습니다. 동시 실행 수를 올려도 이 간격은 줄이지 마세요.
