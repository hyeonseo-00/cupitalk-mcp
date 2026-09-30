# CupiTalk (큐피톡) — 관계 맥락을 이해하는 AI 연애 코칭 MCP

> 카카오 PlayMCP 공모전 「AGENTIC PLAYER 10」 · 2026.06 ~ 2026.09 · 4인 팀 프로젝트
> **예선 통과 · 본선 진출(상위 20팀) · Kakao Tools(ChatGPT for Kakao)에 공개되어 실사용자 투표 진행**

카카오톡에서 연인·썸 상대와 대화하다가 "뭐라고 답하지?", "이 사람 취향이 뭐였지?" 싶을 때, 대화 속 정보를 기억하고 관계를 분석해 답장과 선물을 코칭해 주는 MCP 서비스입니다. 사용자가 자연어로 말하면 AI가 의도를 해석해 큐피톡의 Tool을 호출하고, 결과를 카드형 Widget으로 보여 줍니다.

> **공개 범위 안내**: 큐피톡은 현재 운영 중인 서비스입니다. 서비스 보안을 위해 이 저장소에는 **제가 직접 개발한 Widget UI 렌더링 코드만** 공개했습니다. 서버, 인증(OAuth), 데이터베이스, 운영 관련 코드와 팀원이 작성한 코드는 포함하지 않았으며, 이 저장소만으로는 실행되지 않습니다.

## 팀 구성과 나의 역할

**팀 구성**: 기획·디자인 보조·프론트엔드 1(본인) · 디자인 1 · 백엔드 1 · AI 엔지니어 1

**나의 역할 — 팀장, MCP 설계 · Widget UI 디자인 · 프론트엔드 개발**

- 문제 정의, 사용자 인터뷰 설계와 진행 (썸·연애 초기·중기·장기 단계별 각 4명)
- 커뮤니티 데이터 수집: 블라인드 썸·연애 게시판 Selenium 크롤링, kiwipiepy 명사 추출
- MCP Tool 구조 설계: 기능 단위 Tool을 사용자 의도 기준 6종으로 재설계
- 사용자 시나리오와 QA 테스트 케이스 설계, 이슈 우선순위(P0~P2) 관리
- 관계 분석 리포트·멘트 코치 Widget의 정보 구조(IA)와 UI 디자인
- 전체 Widget UI 프론트엔드 개발 (100%) ← **이 저장소에 공개한 코드**
- OAuth 인증 연동, 검수 대응을 위한 아이디 기반 회원 체계 도입과 배포 검증

프로필·선물 추천 Widget의 UI 디자인은 디자인 팀원이 맡았고, 그 프론트엔드 구현과 연동은 본인이 했습니다.

## 핵심 설계 결정: 기능 중심에서 사용자 의도 중심으로

처음에는 기능별로 Tool 6개(Profile, Memory, Relationship Analysis, Gift Strategy, Gift Candidate, Reply Coach)를 설계했습니다. 그런데 사용자 시나리오 QA에서 **질문 하나를 처리하려고 여러 Tool과 점수 계산 단계가 반복 호출되는 문제**가 드러났습니다. 사용자는 기능이 아니라 목적을 기준으로 서비스를 쓴다는 점을 확인했고, 이에 맞춰 Tool 구조를 다시 짰습니다.

| 사용자 의도 | MCP Tool |
|---|---|
| 상대방 정보를 저장하고 관리하고 싶다 | `manage_partner_profile` |
| 대화 속 정보를 기억하고 싶다 | `manage_memory` |
| 지금 관계가 어떤 상태인지 알고 싶다 | `analyze_relationship` |
| 답장을 어떻게 해야 할지 모르겠다 | `coach_reply` |
| 상대에게 맞는 선물을 추천받고 싶다 | `plan_gift` |
| 서비스 기능과 계정 관리를 알고 싶다 | `show_capabilities` |

- 점수 중심 분석을 없애고, 서버는 검증과 저장만, LLM은 추론과 생성만 맡도록 역할을 나눴습니다.
- Widget은 **분석 → 해석 → 다음 행동** 순서로 정보 우선순위를 다시 정했습니다. 정보가 부족하면 추가 입력을 유도합니다.

## 공개한 코드

Tool 응답을 Kakao Tools에서 보이는 카드형 Widget JSON으로 바꾸는 렌더링 계층입니다.

| 파일 | 역할 |
|---|---|
| `src/tools/relationship_render.py` | 관계 분석 리포트 Widget (현재 상황 · 대화에서 보이는 신호 · 큐피톡 한마디) |
| `src/tools/coach_reply_render.py` | 멘트 코치 Widget (추천 답장 · 조심할 표현 · 전송 타이밍) |
| `src/tools/profile_render.py`, `profile_summary.py` | 상대 프로필 Widget과 프로필 요약 |
| `src/tools/gift_render.py` | 선물 전략 Widget |
| `src/tools/memory_render.py` | 메모 Widget |
| `src/tools/render_helpers.py`, `render_colors.py` | Widget 공통 카드 구성 요소와 색상 토큰 |

## 저작권

© 2026 신현서 외 팀원. 포트폴리오 열람 목적이며 무단 복제·사용을 금지합니다.
