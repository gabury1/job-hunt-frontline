---
tags: [취업, 공고, 모레]
company: 모레
공고번호: "339701"
마감: "상시"
정리: "2026-11-24"
url: https://zighang.com/recruitment/751a864e-7209-482b-bdd5-6e80aa72a87d
---

# 모레 · LLM Platform Engineer

> [!summary] 한눈에
> - **마감**: **채용 시 마감** (상시)
> - **요구 경력**: 2년~8년 차, 학사 이상
> - **하는 일**: 분산 추론 프레임워크 MoAI Inference Framework 의 Performance Gateway · Inference Control Plane/Operator · Observability 중 하나 이상을 Rust/Go 로 설계 · 구현한다
> - **근무**: 정규직(경력직), 연봉 협의
> - **근무지**: 서울특별시 서초구, Product 팀

**링크**: [직행 공고](https://zighang.com/recruitment/751a864e-7209-482b-bdd5-6e80aa72a87d) · [리멤버 원래 공고](https://career.rememberapp.co.kr/job/posting/339701)

---

## 일정과 전형

| 항목 | 날짜 |
|---|---|
| 접수 기간 | 채용 시 마감 |

1. 서류 전형: 형식은 공고에 없음
2. 1차 면접: 형식은 공고에 없음
3. 최종 면접: 형식은 공고에 없음
4. 처우 협의
5. 최종 합격

포지션에 따라 전형이 변경되거나 추가될 수 있다.

## 팀이 하는 일

> Moreh는 특정 하드웨어에 종속되지 않고 다양한 AI 인프라를 효율적으로 활용할 수 있는 시스템을 개발합니다.

Product 팀은 고성능 분산 추론 프레임워크인 MoAI Inference Framework 를 개발하고, 이 포지션은 LLM API 요청 · 추론 엔진 · 클러스터 상태를 연결하는 프로덕션 소프트웨어를 설계하고 구현한다. 후보자의 강점과 경험에 따라 Performance Gateway, Inference Control Plane/Operator, Observability 중 하나 이상의 영역을 맡고, 경력과 역량에 따라 기술적 의사결정을 주도한다.

## 담당할 업무

| 업무 | 기술 |
|---|---|
| Performance Gateway 개발: LLM API 호환성, 요청 라우팅, fallback/retry, backpressure와 부하 분산 기능을 설계 · 구현하고 검증한다 | LLM API, fallback/retry, backpressure |
| Performance Gateway 개발: 분산 추론 기법을 실제 워크로드에 적용하고 성능과 안정성을 개선한다 | Disaggregated Inference, Prefix-cache-aware routing |
| Inference Autopilot 개발: 서비스 구성(Preset)을 선언적으로 관리하는 Kubernetes Operator 를 설계 · 개발한다 | Kubernetes Operator |
| Inference Autopilot 개발: 트래픽 패턴과 클러스터 상태에 따라 추론 서비스의 구성 변경과 스케일링을 자동화하고 변경의 안정성을 검증한다 | |
| High-Fidelity Observability 구축: traces, metrics, logs 를 설계하고, 분산 환경의 장애와 성능 저하를 재현하여 근본 원인을 분석한다 | OpenTelemetry |

## 지원 자격

### 필수 경험과 역량

- Production Engineering: 프로덕션 소프트웨어를 설계, 구현, 테스트, 배포하고 운영 중 문제를 디버깅 · 개선한 경험
- Programming: Rust 또는 Go 중 하나 이상의 언어를 사용한 소프트웨어 개발 역량
- Relevant Systems: API Gateway, 분산 시스템, Kubernetes controller/operator, ML/LLM serving 중 하나 이상의 영역에서 소프트웨어를 개발한 경험
- Engineering Judgment: 성능이나 신뢰성 문제를 지표와 재현 가능한 실험으로 정의하고 개선한 경험
- Engineering Ownership: 단위/E2E 테스트와 CI/CD 자동화로 변경 사항을 검증하고, 설계 결정 · 진행 상황 · 위험 요소와 결과를 구체적으로 공유하는 역량
- 경력 2년~8년 차

### 졸업 · 학업 조건

- 학사 이상

### 우대사항

- AI Infrastructure: vLLM, SGLang, llm-d, Dynamo 등 LLM serving 시스템의 내부 구조를 이해하거나 관련 오픈소스에 기여한 경험
- Distributed Inference: KV cache, continuous batching, disaggregated serving, prefix-aware routing 을 설계하거나 최적화한 경험
- Cloud Native: Kubernetes custom operator, scheduler 또는 OpenTelemetry 기반 observability 시스템을 개발한 경험
- AI-Native Engineering: AI Agent 를 개발 workflow 에 적용하고, 자동화된 테스트와 검증을 통해 개발 속도나 품질을 개선한 경험

## 제출 서류와 지원 방법

- 지원하는 곳: 리멤버 공고 페이지의 「간편 지원하기」
- 처음에 내는 서류: 공고에 없음
- 전형 중에 내는 증빙 서류: 공고에 없음

## 유의사항

- 포지션에 따라 전형이 변경 또는 추가될 수 있다.
- 리멤버를 통해 합격해 입사하면 리멤버가 합격 보상금 50만원을 준다.
- 기타 안내(복리후생): 복지포인트 연간 200만 원, 입사 시 장비지원금 지원, 유연출근제&재택근무, 연 1회 종합건강검진(본인 및 직계가족 1인), 생일 반차 휴가, 장기근속 휴가, 사내 동호회 지원(보드게임, 클라이밍 등), 오피스 간식 제공(과자, 음료수 등), 연말 오피스 클로징(매년 12/28-12/31 유급휴가 제공), 중소기업 청년 소득세 감면(연간 최대 200만 원)
- 문의처: 공고에 없음
