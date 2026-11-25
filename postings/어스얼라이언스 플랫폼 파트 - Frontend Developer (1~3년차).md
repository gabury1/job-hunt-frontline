---
tags: [취업, 공고, 어스얼라이언스]
company: 어스얼라이언스
공고번호: "396517"
마감: "2026-12-31"
정리: "2026-11-26"
url: https://www.wanted.co.kr/wd/396517
---

# 어스얼라이언스 · 플랫폼 파트 - Frontend Developer (1~3년차)

> [!summary] 한눈에
> - **마감**: 2026-12-31 (목)
> - **요구 경력**: 1 ~ 3년
> - **하는 일**: 구독형 금융 콘텐츠 플랫폼의 웹앱 5개와 Flutter 앱 안의 인앱웹뷰 개발 · 운영
> - **근무**: 공고에 없음
> - **근무지**: 서울 마포구 양화로 78-22 · 플랫폼 파트(프론트엔드 챕터)

**링크**: [원티드 공고](https://www.wanted.co.kr/wd/396517) · [원티드 회사 페이지](https://www.wanted.co.kr/company/22087)

---

## 일정과 전형

| 항목 | 날짜 |
|---|---|
| 접수 마감 | **2026-12-31 (목)** |

전형 단계: 공고에 없음

## 팀이 하는 일

> 어스얼라이언스의 Frontend Developer는 사용자 경험을 최우선으로 생각하며, 다양한 이용자와 콘텐츠 제공자 모두에게 더 나은 서비스를 제공하기 위해 끊임없이 고민합니다.

플랫폼 파트 프론트엔드 챕터는 pnpm 모노레포 위에서 웹앱 5개(사용자 서비스, 커머스, 파트너센터, 어드민, 스튜디오)와 Flutter 앱 안의 인앱웹뷰를 운영하고, 15만 명 이상이 쓰는 프로덕션 환경에서 웹과 네이티브 사이의 성능 · 품질 · 자동화 문제를 푼다. 회사는 "금융을 콘텐츠로 혁신합니다."라는 미션을 내건 금융 콘텐츠 · 플랫폼 기업이며, 소수몽키(115만명) 같은 금융 · 경제 유튜브 채널과 함께 교육 · 출판 · 컨퍼런스 · 커뮤니티로 콘텐츠를 넓히고 있다.

## 담당할 업무

| 업무 | 기술 |
|---|---|
| 구독형 금융 콘텐츠를 중심으로 사용자가 콘텐츠를 소비하고 교류하는 플랫폼 서비스 제품 개발 | |
| 콘텐츠 제공자의 콘텐츠 생성을 지원하는 제품 개발 | |
| 어스 플랫폼 서비스의 내부 운영을 위한 관리 제품 개발 | |
| 어스 플랫폼 라이브 스트리밍 서비스를 위한 라이브 스튜디오 제품 개발 | |
| 어스 플랫폼 서비스의 인앱웹뷰 개발 | Flutter |
| 웹앱 5개와 공용 패키지 6개(디자인 시스템, 에디터, 모달, Sentry 등) 운영, 빌드 의존 순서와 패키지 버전 관리 | pnpm, Turborepo |
| 서비스 특성에 맞춘 Next.js(App Router)와 Vite SPA 운영, Server Component와 Client Component 경계 설계 | React 19, TypeScript, Next.js, Vite |
| FSD 아키텍처로 코드 구성(읽기는 entities, 쓰기는 features) | FSD(Feature-Sliced Design) |
| 서버 상태 관리, Query Key Factory로 캐시 키 계층화, 하이드레이션 | TanStack Query |
| 사용자 행동 분석과 에러 모니터링을 공용 패키지로 묶어 이벤트 계약 통일 | Segment, Sentry |
| Flutter와 웹 사이의 타입 기반 브릿지 계약 관리, 인증 · 세션 전달과 화면 전환 개발 | Flutter |
| 웹뷰 엔진별 쿠키 · 세션, 미디어 재생, 키보드와 Safe Area 처리 | Android System WebView, iOS WKWebView |
| 실제 기기의 웹뷰 프로파일링으로 JavaScript 실행 · 렌더링 · 웹-네이티브 상호작용 병목 분석 | |
| 성능 개선(INP 측정 체계, Long Task 분할, 가상화, content-visibility, 브릿지 메시지 직렬화 비용 측정) | Android WebView(Chromium), iOS WKWebView(WebKit) |
| 위험도 기준 테스트, 외부 경계 mock, 타임존 매트릭스 검증, 웹 E2E | MSW, Playwright, CI |
| 실제 iOS/Android 기기 풀에서 인앱웹뷰 E2E 자동화 기반 설계 | AWS Device Farm, Appium |
| 에이전트용 컨텍스트 정리와 반복 작업 자동화 | CLAUDE.md, AGENTS.md |

현재 사용 중인 기술은 다음과 같다.

- 코어: React, TypeScript, Next.js ( App Router ), Flutter
- 상태 관리: Tastack Query, Jotai
- 스타일링: tailwindcss, shadcn/ui
- 패키지 매니저: pnpm
- 빌드: Webpack, SWC, Vite
- CI/CD: GitHub Actions
- 테스트: Vitest, Storybook
- 모니터링: Sentry
- 원티드 기술 스택 태그: Android, Firebase, iOS, MVVM, Rx, Flutter

## 지원 자격

### 필수 경험과 역량

- 경력 1 ~ 3년
- React, Vue와 같은 SPA 프레임워크 사용에 능숙함
- Frontend 영역과 웹 서비스 환경을 깊이 이해하고, 이를 토대로 제품 개발에 기여할 수 있음
- 고객의 문제에 집중하여 복잡한 도메인을 유연한 시스템으로 풀어내는 역량
- 속도 저하를 유발할 가능성이 있는 기술 부채를 인지하고, 타협하지 않고 해결을 주도한 경험
- TypeScript를 이용한 JavaScript 정적 타입 분석 경험
- 주어진 업무에서 나아가 주도적으로 문제를 정의하고 해결하려는 자세
- 다양한 문제와 요구사항을 추상화하고 코드로 표현하는 역량

### 졸업 · 학업 조건

공고에 없음

### 우대사항

- 로깅, 모니터링, 데이터 기반 개선 등 "관측 가능한 프론트엔드" 구축 경험
- 디자인 시스템, A/B 테스트, 사용자 행동 분석 도구 활용 경험
- 웹 프론트엔드 성능 최적화와 SSR · SEO에 대한 높은 경험과 이해도
- 서비스 도메인 구조를 고려한 FSD(Feature-Sliced Design) 아키텍처에 관심이 있거나 경험함
- 인앱웹뷰 기반의 개발과 프로세스 경험
- PA 도구를 활용해 제품과 유저 경험을 개선한 경험

## 제출 서류와 지원 방법

- 지원하는 곳: 공고에 없음(원티드에 올라온 공고이고, 공고 화면에 다른 지원처 안내는 없다)
- 처음에 내는 서류: 공고에 없음
- 전형 중에 내는 증빙 서류: 공고에 없음

## 유의사항

공고에 없음
