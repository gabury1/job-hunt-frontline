---
tags: [취업, 공고, 뉴로코어]
company: 뉴로코어
공고번호: "50330709"
마감: "2026-12-09 23:59"
정리: "2026-11-26"
url: https://zighang.com/recruitment/483dfdae-bbc8-4790-bbf7-a0fa279d9af1
---

# 뉴로코어 · AI Engineer (LLM, Knowledge)

> [!summary] 한눈에
> - **마감**: 2026-12-09 (수) 23:59
> - **요구 경력**: 연차 무관(신입 · 경력)이다. 신입도 지원할 수 있다.
> - **하는 일**: 공급망(SCM) 솔루션 위에서 자연어 질문에 데이터로 답하는 AI 에이전트를 만든다. 에이전트의 Agentic Workflow, Text-to-SQL, Hybrid Retrieval, LLM Evaluation, 지식 파이프라인을 다룬다.
> - **근무**: 정규직(수습 3개월), 병역특례(현역, 보충역, 전문연구요원, 전직가능)이다. 이 포지션은 병역특례(전문연구요원)만 채용한다.
> - **근무지**: 서울 강남구 테헤란로 322 (역삼동, 한신인터밸리24) 동관 1101호(서울 강남구 본사)이다. 공고 머리표는 AI PLATFORM이다.

**링크**: [직행 공고](https://zighang.com/recruitment/483dfdae-bbc8-4790-bbf7-a0fa279d9af1) · [잡코리아 원래 공고](https://www.jobkorea.co.kr/Recruit/GI_Read/50330709)

---

## 일정과 전형

| 항목 | 날짜 |
|---|---|
| 접수 시작 | 2026-11-09 (월) |
| 접수 마감 | **2026-12-09 (수) 23:59** |
| 면접 일정 | 추후 통보 |

1. 서류 전형: 이력서(간단한 자기소개 포함)와 포트폴리오를 낸다.
2. 1차 면접: 기술 면접과 실무진 면접이다. 면접 중에 간단한 코딩 테스트가 있을 수 있다(언어 무관). 화상인지 대면인지는 공고에 없다.
3. 2차 면접: 임원 면접이다.
4. 3차 대표님 면담: 처우 협의를 한다.
5. 최종 합격

## 팀이 하는 일

> 지식을 담고, 그 지식으로 답하는 AI 에이전트를 함께 만듭니다.

이 팀은 대형 제조 고객사의 공급망(SCM) 솔루션 위에 AI 에이전트를 올린다. 현업이 자연어로 물으면 에이전트가 질문을 쪼개고, 스스로 SQL을 만들어 데이터를 조회한 뒤 근거와 함께 답한다.

## 담당할 업무

| 업무 | 기술 |
|---|---|
| 자연어 질문에 데이터로 답하는 에이전트의 Agentic Workflow 설계 · 개선(라우팅 설계, 재시도 · 중단 조건 설계 등) | Agentic Workflow, Tool Calling, Human in the Loop |
| 스키마 컨텍스트 조달부터 실행 결과 검증까지 이어지는 Text-to-SQL 파이프라인 구축 | Text-to-SQL |
| Hybrid Retrieval과 지식 그래프 기반 Multi-hop 경로 탐색 구현 | Hybrid Retrieval(Sparse + Dense), 지식 그래프, Multi-hop |
| LLM Evaluation 체계 구축(Golden Dataset, 회귀 격자, 지표 설계, Observability) | LLM Evaluation, Golden Dataset, Observability |
| 도메인 전문가가 직접 쓸 수 있는 지식 스키마와 Ontology · Semantic Layer 설계 | DSL, Ontology, Semantic Layer |
| 어떤 지식을 어디에 얼마나 넣을지 정하는 일, 지식이 틀렸을 때 물러나는 규칙 설계 | Context Engineering, Grounding, Fallback |
| 저작 → 검증 → 패키징 → 배포 → 주입으로 이어지는 지식 파이프라인 구축(버전 · 롤백 · 고객사별 격리 포함) | |

원문에 실린 개발 환경은 아래와 같다.

| 분류 | 기술 |
|---|---|
| 주요 기술 | Python, LangGraph, LangChain, MCP, FastAPI, Pydantic, SQLAlchemy, SQL(MySQL, PostgreSQL), sqlglot, Docker, Linux |
| 검색 · 임베딩 | FAISS, rank-bm25, sentence-transformers, Transformers / PyTorch, KoNLPy |
| LLM 운영 | Langfuse(프롬프트 관리 · 트레이싱), AG-UI Protocol(SSE 스트리밍) |
| 데이터 저장 | MySQL, PostgreSQL, S3 / MinIO |
| 빌드 · 배포 자동화 | GitHub Actions, Docker, Kubernetes(EKS), Helm, GitOps |
| 모니터링 | Grafana, Grafana Alloy, Prometheus, Loki(로그), Tempo(트레이스), Mimir(메트릭), Pyroscope(Continuous Profiling) |
| 업무 도구 | GitHub, Dooray, PyCharm, Lucidchart, Claude · ChatGPT |

## 지원 자격

### 필수 경험과 역량

- 무엇을 스스로 정해서 만들어 봤는지, 그때 왜 그렇게 했는지 설명할 수 있는지를 본다.
- Python으로 돌아가는 것을 직접 만들어 본 경험이 필요하다. 회사 업무, 개인 프로젝트, 연구 중 어느 것이든 된다. 남이 짠 코드를 고쳐 본 경험보다 스스로 구조를 잡아 본 경험이 좋다.
- SQL로 데이터를 조회하고 검증할 수 있는 수준이 필요하다.
- 다음 둘 중 하나 이상이 필요하다.
  - LLM API 또는 오픈소스 모델로 서비스 · 도구를 만들어 본 경험
  - 데이터 모델링 또는 스키마 설계 경험
- 알고리즘, 자료구조, 데이터베이스 등 기본 전산 지식을 이해함
- 유관부서 · 도메인 전문가와 소통하며 업무를 진행하고 결과를 효과적으로 전달한 경험

### 졸업 · 학업 조건

- 학력 · 전공: 자연계열(이학, 공학 등) 석사 학위 이상이어야 한다. IT 관련 전공자는 누구나 지원할 수 있다.
- 잡코리아 모집요강에는 학력이 대학원(석사) 이상(졸업예정자 가능)으로 적혀 있다.
- 병역: 이 포지션은 병역특례(전문연구요원)만 채용한다.

### 우대사항

- 산업공학 · 소프트웨어공학 · 컴퓨터공학 · 인공지능 관련 전공
- RAG 운영 경험: Chunking · Reranking · Query Rewriting
- LangGraph · LangChain 등 Agent Framework 사용 경험
- Text-to-SQL(NL2SQL) 경험 또는 생성된 SQL을 검증해 본 경험
- LLM Evaluation 설계 경험: 평가 데이터셋, 회귀 격자, 지표
- Knowledge Graph · Ontology · Semantic Layer(dbt, Cube 등) 경험
- Structured Output · Tool Calling · LLM Context 설계 경험
- 도메인 전문가가 직접 쓰는 비개발자용 내부 도구를 만들어 본 경험
- 도메인 전문가 인터뷰로 지식을 구조화해 본 경험
- 컨테이너화 기술(Docker, Kubernetes 등)에 대한 이해
- 한국어 처리(형태소 분석 · 색인) 경험
- 논문을 읽고 회사의 문제에 맞는지 판단하는 역량
- 물류 및 SCM(공급망 관리) 도메인에 대한 이해
- 잡코리아 기본우대: 영어가능자, 컴퓨터활용능력 우수자, 프리젠테이션 능력우수자, 유관업무 경험자(인턴·알바), 지방근무 가능 등이다. 화면에서 뒷부분이 잘려 있다.

## 제출 서류와 지원 방법

- 지원하는 곳: 잡코리아 즉시지원으로 지원한다. 지원양식은 잡코리아 이력서이다.
- 처음에 내는 서류(원문은 「꼭 제출해주세요」라고 적었다)
  - 이력서: 간단한 자기소개를 함께 담는다. 별도 자기소개서는 받지 않는다.
  - 포트폴리오: 형식은 자유이다. 문서, 슬라이드, 노션, GitHub 저장소, 블로그 글 무엇이든 된다.
- 별도 경력기술서는 받지 않는다. 그 대신 직접 정해서 만든 것을 포트폴리오에 녹이면 검토에 큰 도움이 된다고 안내한다. 무슨 문제였는지, 어떤 선택지 중에 왜 그것을 골랐는지, 좋아졌다는 것을 무엇으로 확인했는지가 드러나도록 쓰기를 권한다.
- 전형 중에 내는 증빙 서류: 공고에 없음

## 유의사항

- 1차 면접 중에 간단한 코딩 테스트가 있을 수 있다(언어 무관).
- 면접 일정은 추후 통보된다.
- 허위 사실이 발견될 경우 채용이 취소될 수 있다.
- 이 포지션은 병역특례(전문연구요원)만 채용한다.
- 마감일은 기업의 사정으로 조기 마감되거나 변경될 수 있다(잡코리아 안내).
- 급여는 회사 내규에 따르며 면접 후 결정한다. 모집인원은 O명이다.
- 문의처: 공고에 없음. 공고 끝에는 회사 이름 (주)뉴로코어와 홈페이지 주소 neurocore.ai만 적혀 있다.
