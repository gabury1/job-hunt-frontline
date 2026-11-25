# AGENTS.md — 이 레포를 읽는 AI 에게

이 레포는 국내 개발 신입 · 주니어 채용 공고를 매일 아침 모아 정리한 데이터다. 사용자가 공고를 찾거나 고르거나 지원을 준비하는 것을 돕는다.

## 먼저 읽을 것

1. `postings.jsonl`(https://raw.githubusercontent.com/gabury1/newbie-job-hunt/main/postings.jsonl): 지금 접수 중인 공고 전부. 한 줄에 공고 하나인 JSON 이다.
   - `company` 회사 · `title` 공고 제목 · `category` 회사 분류 · `role` 직무 · `career` 요구 경력 · `deadline` 마감(YYYY-MM-DD 또는 「상시」)
   - `posted` 올라온 날 · `regions` 지역 · `url` 원문 · `big_company` 대형 IT · 핀테크 · 대기업 IT 계열사 · 금융이면 true · `new_today` 오늘 아침 새로 뜬 공고면 true
   - `note` 공고 노트 경로 · `company_note` 회사 노트 경로(없으면 null)
   - 회사 숫자(노트를 열기 전에 거르는 용도, 못 찾으면 null): `employees` 국민연금 가입자 수 · `employees_month` 그 기준 월 · `employees_1y` 12달 동안 늘고 준 인원 · `blind_rating` · `blind_reviews` 블라인드 평점 · 리뷰 수 · `stage` 상장 · 투자 단계
2. 사용자의 조건(직무 · 경력 · 지역 · 회사 규모 · 마감)으로 `postings.jsonl` 에서 먼저 고른다.
3. 고른 공고만 `note`(일정 · 전형 · 담당 업무 · 지원 자격 · 제출 서류) 와 `company_note`(사업 · 재무 · 인원 · 최근 이슈 · 리스크 · 개발 문화 · 처우)를 연다.
   경로는 레포 기준이다. 웹에서 읽는다면 앞에 https://raw.githubusercontent.com/gabury1/newbie-job-hunt/main/ 를 붙이고, 경로의 빈칸은 %20 으로 바꾼다.

## 할 수 있는 일

공고 고르기 · 지원 준비 · 회사 비교 · 마감 정리 · 내 기준으로 직접 돌리기의 순서와 규칙은 `.claude/skills/job-hunt/SKILL.md`(https://raw.githubusercontent.com/gabury1/newbie-job-hunt/main/.claude/skills/job-hunt/SKILL.md) 에 있다. 사용자가 이 중 하나를 원하면 그 파일을 먼저 읽고 따른다(Claude Code 는 자동으로 읽는다).

## 지킬 것

- 마감이 지난 공고는 이 레포에 없다. 그래도 `deadline` 이 오늘에 가까우면 그렇다고 알린다.
- 노트는 AI 가 원문을 정리한 것이라 틀릴 수 있다. 지원 자격 · 마감 · 제출 서류를 말할 때는 원문 `url` 을 확인하라고 덧붙인다.
- 이 레포의 공고는 만든 사람의 기준(서버 · 백엔드 · DevOps · 생성형 AI 서비스 개발, 요구 경력 1년 이하, SI · 초기 스타트업 · 공공기관 제외)으로 걸러져 있다.
  사용자의 조건이 이 범위 밖이면(프론트엔드 · 데이터 · 임베디드 · SI 등) 이 레포에 없는 공고가 많다고 먼저 말한다.
- 회사 노트의 블라인드 칸은 공개 점수와 장단점 요약뿐이다. 리뷰는 일부 직원의 의견이니 처우 · 분위기를 단정하지 않는다.
