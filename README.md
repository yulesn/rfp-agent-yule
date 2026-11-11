# RFP 에이전트 (솔로)

B2G 입찰지원 컨설팅 스타트업 '입찰메이트'의 사내 RFP(제안요청서) RAG 에이전트를 혼자 처음부터 끝까지 만드는 프로젝트입니다.
팀 프로젝트([rfp-agent-part3-team1](https://github.com/yulesn/rfp-agent-part3-team1))의 솔로 버전입니다.

- 전체 계획: [docs/PLAN.md](docs/PLAN.md)
- 결정 기록(ADR): [docs/decisions/](docs/decisions/)
- 대화 기록: [docs/conversations/](docs/conversations/)
- 시행착오: [docs/trials/](docs/trials/) · 실험: [docs/experiments/](docs/experiments/)
- Claude Code 작업 규칙: [CLAUDE.md](CLAUDE.md)

## 상태

Phase 0 (하네스 & 계획) 진행 중. 플랜 v0.2 컨펌 대기라 코드는 아직 없습니다.

## Claude Code 사용법

- 계획/리뷰는 Opus, 구현은 Sonnet. `.claude/settings.json` 의 `opusplan` 설정으로 plan mode(Shift+Tab)에서는 Opus, 실행 시에는 Sonnet이 쓰입니다.
- 서브에이전트: `planner`, `reviewer` (Opus) / `implementer`, `researcher` (Sonnet)
- 스킬: `devlog`, `phase-gate`, `experiment-log` + LangChain 공식 스킬 6종
