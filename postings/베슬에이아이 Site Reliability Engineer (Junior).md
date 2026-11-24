---
tags: [취업, 공고, 베슬에이아이]
company: 베슬에이아이
공고번호: "30293d6c-3552-43c9-b6a4-75adfa890c40"
마감: "상시"
정리: "2026-11-24"
url: https://zighang.com/recruitment/b29ed9ef-e90e-4019-8a06-99507cadc14c
---

# 베슬에이아이 · Site Reliability Engineer (Junior)

> [!summary] 한눈에
> - **마감**: **상시채용**
> - **요구 경력**: 2년 이상의 Software Engineering 경험
> - **하는 일**: VESSL GPU 클라우드 플랫폼의 가용성과 성능을 책임진다(Observability 구축 · On-call 장애 대응 · 운영 자동화 · 인프라 설계 · 운영)
> - **근무**: 정규직(수습 3개월, 수습 피드백 기간 후 업무 성과와 평가 결과에 따라 최종 합류 여부 결정)
> - **근무지**: 서울

**링크**: [직행 공고](https://zighang.com/recruitment/b29ed9ef-e90e-4019-8a06-99507cadc14c) · [Ashby 원래 공고(VESSL AI 채용 페이지)](https://jobs.ashbyhq.com/vessl-ai/30293d6c-3552-43c9-b6a4-75adfa890c40)

---

## 일정과 전형

| 항목 | 날짜 |
|---|---|
| 접수 기간 | 상시채용 |
| 수습 기간 | 3개월 |

1. 서류전형: 지원서(경력 세부 기술)와 포트폴리오(또는 Git 링크)를 필수로 낸다. 양식은 자유다.
2. Coding Test: 형식은 공고에 없음.
3. Technical Interview: 개발 실무자가 참여한다. 구조 설계와 구현 방식 등 기술 중심의 대화로 문제 해결 역량을 파악하며, 최대 2시간 정도 걸린다.
4. Resume/Culture Interview: 유관 경험 중심의 기술 역량과 문화적 핏을 알아보는 시간이다. 소속 매니저와 팀 멤버가 참여하며 각 1시간 정도 걸린다.
5. CEO Interview: 형식은 공고에 없음.
6. Reference Check: 경력직만 인터뷰 마지막 단계 이후에 진행한다.

위 절차는 베슬에이아이코리아 경력 채용 기본 프로세스이며, 경우에 따라 가감될 수 있다.

## 팀이 하는 일

> 메트릭·로그·트레이스 기반의 Observability 체계를 구축해 이상 징후를 조기에 탐지하고, 장애 발생 시 On-call 대응과 Root Cause Analysis를 통해 신속하게 복구하며, 반복적인 운영 작업은 자동화로 대체해 시스템 전반의 안정성과 운영 효율을 함께 끌어올립니다.

대규모 GPU 클러스터, InfiniBand·RoCE 기반 고성능 네트워크, Kubernetes·Slurm 기반 스케줄링 시스템으로 이루어진 VESSL GPU 클라우드 플랫폼에서 GPU, NIC, 드라이버, 커널부터 스케줄러, 네트워크 패브릭까지 전 레이어의 상태를 모니터링하고, 장애 원인을 빠르게 좁혀 복구하며, 반복 운영 작업을 자동화로 줄여 나간다. GPU 워크로드는 몇 시간에서 몇 주까지 이어지는 경우가 많아 일반적인 웹 서비스보다 훨씬 높은 수준의 안정성이 요구된다.

## 담당할 업무

| 업무 | 기술 |
|---|---|
| Reliability & Observability: 메트릭·로그·트레이스 등 Observability 스택을 구축하고, SLI/SLO를 정의해 플랫폼의 안정성을 정량적으로 추적 | SLI/SLO |
| Incident Response: On-call 로테이션에 참여해 장애 상황에 대응하고, Root Cause Analysis와 Postmortem을 통해 재발 방지 | On-call, Root Cause Analysis, Postmortem |
| Automation: 반복되는 운영 작업(Toil)을 자동화 스크립트·파이프라인·IaC로 대체해 운영 효율 개선 | IaC |
| Infra 설계 및 운영: Kubernetes, GPU 클러스터, 네트워크 등 인프라 레이어의 설계·운영에 참여하고 지속적으로 개선 | Kubernetes, GPU 클러스터 |
| Capacity 검증 지원: 신규 인프라 배포 시 East-West/North-South 네트워크 구성, 스토리지 처리량, BIOS·펌웨어 설정 등 운영 관점의 요구사항을 정의하고 검증에 참여 | East-West/North-South 네트워크, BIOS·펌웨어 |

## 지원 자격

### 필수 경험과 역량

- 2년 이상의 Software Engineering 경험
- Linux 시스템에 대한 이해와 트러블슈팅 경험
- Python, Go 등의 언어로 자동화 스크립트나 도구를 작성해 본 경험
- Kubernetes, Docker 등 컨테이너 오케스트레이션에 대한 기본적인 이해
- 온프레미스 또는 퍼블릭 클라우드 인프라 운영 경험, 혹은 이에 준하는 학습·실습 경험
- 장애 상황에서 데이터를 기반으로 원인을 좁혀 나가는 문제 해결 능력
- On-call 로테이션에 참여 가능함

### 졸업 · 학업 조건

- 컴퓨터공학, 전자공학, AI 등 관련 전공 학사 이상 학위 혹은 이에 준하는 실무 경험

### 우대사항

- GPU/TPU/NPU 등 가속기 기반으로 상용 학습/인퍼런스 시스템을 구축/운영해 본 경험
- Slurm, Kubernetes 기반 대규모 GPU 스케줄링 환경 운영 경험
- NVIDIA GPU Operator를 활용해 Kubernetes 클러스터의 GPU 드라이버·패브릭 버전을 관리해 본 경험
- Prometheus, Grafana, OpenTelemetry 등 Observability 스택을 구축해 본 경험
- InfiniBand/RoCEv2 등 고성능 네트워크 기반 멀티노드 클러스터 환경 운영 경험
- Terraform, Ansible 등 IaC(Infrastructure as Code) 툴 활용 경험

## 제출 서류와 지원 방법

- 지원하는 곳: 원래 공고(Ashby) 페이지의 Apply for this Job
- 처음에 내는 서류: 지원서(경력 세부 기술 포함)와 포트폴리오 또는 Git 링크를 필수로 낸다. 양식은 자유다.
- 전형 중에 내는 증빙 서류: 공고에 없음

## 유의사항

- 이력서 및 제출서류에 허위 사실이 발견될 경우, 합격 발표 후라도 입사가 취소될 수 있다.
- 전형 절차는 경우에 따라 가감될 수 있다.
- 문의처: 공고에 없음
