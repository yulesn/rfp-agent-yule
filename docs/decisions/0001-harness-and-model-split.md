# 0001. 하네스 구성과 모델 역할 분리
- 상태: 확정됨 (Yule 요청 사항을 그대로 반영)
- 날짜: 2026-11-09
- 결정자: Yule

## 맥락
혼자 전 파트를 구현하면서, 계획 품질과 구현 속도/비용을 모두 챙기고 모든 과정을 기록으로 남겨야 함.

## 결정
- 계획·컨펌·리뷰는 Opus, 실구현은 Sonnet
  - 메인 세션: `.claude/settings.json` 에 `"model": "opusplan"` (plan mode에서 Opus, 그 외 Sonnet)
  - 서브에이전트: planner/reviewer = opus, implementer/researcher = sonnet
- 플랜 컨펌 전 구현 금지 (CLAUDE.md 규칙 1, `phase-gate` 스킬)
- 기록: docs/{conversations, decisions, trials, experiments, architecture, research}, `devlog`/`experiment-log` 스킬로 형식 통일

## 영향 / 되돌리는 방법
`opusplan` 이 불편하면 settings.json 에서 model 줄을 지우고 `/model` 로 수동 전환.
