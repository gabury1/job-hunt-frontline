---
tags: [취업, 공고, AMD]
company: AMD
공고번호: "96408"
마감: "상시"
정리: "2026-11-26"
url: https://zighang.com/recruitment/8a5502ad-8938-4d1d-85d6-04aa690cf537
---

# AMD · AI Software Development Engineer

> [!summary] 한눈에
> - **마감**: **상시 채용**
> - **요구 경력**: 신입(Fresh Graduates)
> - **하는 일**: 요청마다 어떤 모델이 어떤 비용으로, 어떤 안전 · 개인정보 정책 아래에서 답할지 정하는 vllm-sr의 라우터 · 서빙 엔진 · 결정 모델을 만들고 오픈소스 커뮤니티를 운영한다
> - **근무**: 정규직
> - **근무지**: Seoul, Korea(서울) · vllm-sr core team

**링크**: [직행 공고](https://zighang.com/recruitment/8a5502ad-8938-4d1d-85d6-04aa690cf537) · [AMD 채용 사이트 원래 공고](https://careers.amd.com/careers-home/jobs/96408?lang=en-us)

---

## 일정과 전형

| 항목 | 날짜 |
|---|---|
| 접수 기간 | 상시 채용 |

1. 전형 단계는 공고에 없음

## 팀이 하는 일

> We build the layer that makes that decision.

vllm-sr 핵심 팀은 라우터, 서빙 엔진, 결정 모델, 오픈소스 커뮤니티까지 스택 전체를 맡는다. AMD Instinct GPU에서 모델을 학습하고 서빙하며, ROCm을 지능형 라우팅에 알맞은 1급 플랫폼으로 만든다. 성과는 코드 · 공개 모델 · 논문의 형태로 upstream에 내보낸다.

## 담당할 업무

| 업무 | 기술 |
|---|---|
| 요청마다 알맞은 모델을 고르는 결정 모델부터 의미 기반 · 정책 기반 · 워크로드 인지 라우팅, 의미 캐싱, 안전 · 개인정보 · 도구 · 에이전트 라우팅까지 vllm-sr의 라우팅 지능을 구축한다 | vllm-sr |
| vllm-sr을 프로덕션에서 쉽게 배포 · 운영하도록 만들고, 주요 시스템과 1급 수준으로 연동한다 | vLLM, Kubernetes, Envoy, Gateway API, AI gateways |
| vllm-sr을 결정 모델용 범용 서빙 엔진으로 만든다. System One API를 제공하고 AMD Instinct GPU부터 CPU까지 효율적으로 실행되게 한다 | System One API, AMD Instinct GPUs, CPUs |
| 결정 모델 추론을 batching, memory, latency, throughput 전반에서 최적화하고, 필요한 곳은 GPU 커널까지 최적화한다 | HIP, Triton, ROCm |
| 여러 크기의 foundation 결정 모델을 학습하고 성능을 계속 끌어올린다. 데이터 · 학습 · 후처리 학습 · 평가를 직접 맡는다 | |
| 데이터 생성부터 학습 · 평가 · 분석까지 실험을 자동화해, 결정 모델을 계속 개선하는 auto research pipeline을 구축한다 | |
| 새 기능이 서빙 성능까지 갖춰 나가도록 결정 모델과 서빙 엔진을 함께 설계한다 | |
| 벤치마크와 평가를 만들고, end-to-end 시스템을 프로파일링하며, 라우팅 품질 · 지연시간 · 비용을 측정해 데이터로 결정한다 | |
| testing, CI, observability, reliability를 갖춘 production-quality 소프트웨어를 낸다 | CI |
| upstream을 우선한다. 커뮤니티 기여를 검토 · 병합하고, 이슈를 분류하고, 릴리스를 내며 커뮤니티 성장을 돕는다 | GitHub |
| 컨퍼런스 · 워크숍에서 AMD와 vllm-sr을 대표하고, 발표 · 데모 · 블로그 · 문서로 성과를 알린다 | |
| ROCm · 커널 · AI 프레임워크 팀과 병목을 없애고 새 AMD GPU 플랫폼에서 vllm-sr을 검증한다. Enterprise · IT 팀과 함께 vllm-sr로 AMD 사내 제품 · IT 서비스를 지원한다 | ROCm, AMD GPU |

## 지원 자격

### 필수 경험과 역량

- Python과 Go · Rust · C++ 중 하나 이상에 대한 뛰어난 프로그래밍 역량
- 대규모 언어 모델을 직접 다룬 경험: 서빙(vLLM, SGLang 또는 유사 도구), 학습, 또는 LLM 기반 제품 개발
- AI-native engineering: AI 코딩 에이전트와 agentic workflow를 설계 · 구축 · 테스트 · 배포에 매일 깊이 활용하고, 결과를 검증 · 수정하는 판단력
- AI를 중심에 두고 아이디어 · 설계부터 배포 · 운영까지 직접 만들어 낸 제품 경험
- systems 또는 machine learning(혹은 둘 다)의 탄탄한 기본기
- 공개 환경에서 일하는 데 익숙함: GitHub workflow, 공개 코드 리뷰, 명확한 영문 작성
- 대규모 언어 모델이 학습 · 서빙되는 방식에 대한 이해(THE PERSON 항목)

### 졸업 · 학업 조건

- Fresh Graduates 대상
- Computer Science, Computer Engineering, Electrical Engineering 또는 관련 분야 학사 · 석사 학위, 또는 그에 준하는 경험(equivalent experience)

### 우대사항

원문에는 별도의 제목 없이 Requirements 목록 뒤쪽에 아래 항목이 이어져 있다. 직행 요약은 이 항목을 우대사항으로 분류했다.

- vllm-sr, vLLM, SGLang, PyTorch, Hugging Face, Envoy, Kubernetes 같은 오픈소스 프로젝트 기여
- GPU 프로그래밍(HIP, CUDA, Triton) 경험 또는 AMD Instinct GPU에서 ROCm을 쓴 경험
- 모델 라우팅, API gateway, LLM 추론 최적화 경험
- classifier · reward model · multimodal model 같은 모델의 학습 또는 후처리 학습 경험
- 주요 machine learning · systems 학회 논문
- 기술 문서 작성, 공개 발표, 커뮤니티 구축 경험
- machine learning systems · distributed systems · high-performance computing 연구 경험(원문 ACADEMIC CREDENTIALS 항목에 「is a plus」로 표시됨)

## 제출 서류와 지원 방법

- 지원하는 곳: AMD 채용 사이트(careers.amd.com) 원래 공고에서 지원한다. 직행 「지원하기」 버튼도 이 주소로 연결된다
- 처음에 내는 서류: 공고에 없음
- 전형 중에 내는 증빙 서류: 공고에 없음

## 유의사항

- AMD는 헤드헌터, 채용 대행사, 유료 채용 서비스가 보낸 요청하지 않은 이력서를 받지 않는다.
- AMD와 자회사는 기회균등 고용주이며 나이 · 인종 · 장애 · 성별 · 병역 등 법으로 보호되는 특성과 관계없이 모든 지원자를 검토한다. 채용 전형의 모든 단계에서 관련 법에 따라 지원자에게 필요한 편의를 제공한다.
- AMD는 이 직무의 지원자를 선별 · 평가 · 선발할 때 인공지능을 쓸 수 있다. AMD의 「Responsible AI Policy」는 원래 공고의 링크에서 볼 수 있다.
- 이 공고는 실제 공석(existing vacancy)을 채우기 위한 것이다.
- 복리후생은 원래 공고의 「AMD benefits at a glance」 링크에 안내되어 있다.
- 채용 사칭 주의(AMD 채용 페이지 안내): AMD 리크루터는 개인 이메일을 쓰지 않고, 수수료를 요구하지 않으며, 문자로 제안하지 않고, 이력서 검토 비용을 받지 않으며, 지원 과정에서 개인 신분증 서류를 요구하지 않는다.
- 문의처: 공고에 없음
