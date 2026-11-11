---
name: phase-gate
description: 새 Phase나 큰 기능을 시작하거나 끝낼 때 사용. 계획→컨펌→구현→리뷰→기록 게이트를 순서대로 통과시킨다.
---

# phase-gate

## 시작 게이트
1. `docs/PLAN.md` 에서 해당 Phase 범위와 완료 기준을 확인한다.
2. `planner` 서브에이전트(Opus)로 세부 계획을 만든다. 기술 선택이 있으면 후보 비교 + 추천안.
3. Yule에게 계획과 질문을 보여주고 컨펌을 받는다. 컨펌 전에는 코드를 쓰지 않는다.
4. 컨펌 내용을 `devlog` 로 기록 (대화 로그 + 확정된 ADR).
5. `phase<N>/<설명>` 브랜치를 만든다.

## 구현
6. `implementer` 서브에이전트(Sonnet)에 계획의 단계를 하나씩 맡긴다.
7. 시행착오는 즉시 `docs/trials/` 에.

## 종료 게이트
8. `reviewer` 서브에이전트(Opus)로 리뷰 → 지적 사항 수정.
9. `uv run ruff check . && uv run pytest` 통과, 평가가 있는 Phase면 `experiment-log` 로 결과 기록.
10. `docs/PLAN.md` 상태 갱신(✅), PR 생성.
