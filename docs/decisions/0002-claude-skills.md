# 0002. Claude Code 스킬/서브에이전트 선정
- 상태: 확정됨 (2026-11-11, 플랜 v0.2 컨펌)
- 날짜: 2026-11-09

## 맥락
LangGraph/LangChain API는 버전마다 자주 바뀌어 모델 기억에 의존하면 틀린 코드를 쓰기 쉬움. 기록 형식도 매번 달라지면 보고서로 쓰기 어려움.

## 후보 비교
| 후보 | 내용 | 판단 |
| --- | --- | --- |
| langchain-ai/langchain-skills (공식, MIT) | LangGraph/LangChain/RAG/미들웨어/퍼시스턴스 스킬 14종 | 6종만 채택 (아래). deep-agents, swarm, TS용은 범위 밖이라 제외 |
| 커뮤니티 HWP 파서 스킬 | hwp 파싱 가이드 | 제외: 검증 어려움. Phase 5 파서 비교 실험으로 대체 |
| 직접 작성 스킬 | devlog, phase-gate, experiment-log | 채택: 이 프로젝트 규칙(기록/컨펌 게이트) 전용 |

## 결정
- 공식 스킬 6종: langgraph-fundamentals, langgraph-persistence, langgraph-human-in-the-loop, langchain-fundamentals, langchain-middleware, langchain-rag
  (출처 커밋 126c384, 원래는 `npx skills add langchain-ai/langchain-skills --agent claude-code` 로 설치하나 레포에 직접 복사)
- 직접 작성 스킬 3종 + 서브에이전트 4종(planner, reviewer, implementer, researcher)

## 영향
스킬 업데이트는 원본 레포에서 다시 복사. 필요해지면 deep-agents 계열 추가 검토.
